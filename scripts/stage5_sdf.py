"""Stage 5 (replaces 3-4): exact signed-distance fields from the smoothed source meshes, per-part offsets for
printability, trachea hollowing/seating, priority CSG, and marching cubes per part + union."""
import sys, json, time, numpy as np, trimesh, igl, edt, pymeshlab
from scipy import ndimage
from skimage import measure
sys.path.insert(0, '/tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad/scripts')
from partsconfig import PARTS
import os
B = os.environ.get('BUILD', '/tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad/build')
g = np.load(f'{B}/grid.npy'); lo = g[:3]; P = g[3]; shape = tuple(int(x) for x in g[4:7]); z_cut = g[7]
MIN_T = 1.2; WALL = 2.0; ENV = 2.5; BIG = 50.0
A3 = (P, P, P)
# per-part radial offset (mm) to reach the 1.2 mm print minimum; from the measured median thickness
DELTA = {6: 0.20, 7: 0.25, 10: 0.25, 14: 0.35, 15: 0.35, 16: 0.20, 17: 0.20, 18: 0.20, 19: 0.20,
         22: 0.30, 23: 0.10, 31: 0.10, 32: 0.10,
         56: 0.30, 57: 0.30, 64: 0.20, 65: 0.20, 76: 0.20, 77: 0.20}   # v6 sheets: membrane 0.6, mucosa 0.8; capsules (72-75) get no offset: a 0.8 mm sleeve bounded by cartilage on both sides
OFFSCALE = float(os.environ.get('OFFSCALE', '1.0'))      # <1 when the print is enlarged (e.g. 0.5 at 2x)
DELTA = {k: v * OFFSCALE for k, v in DELTA.items()}
ONE_SIDED = {14, 15, 16}
HE_SCULPT = os.environ.get('HE_SCULPT') == '1'           # hyo-epiglottic ligament already sculpted as a band
LIG_H = float(os.environ.get('LIG_H', '0'))              # cricotracheal ligament height (0 = none, v2 behaviour)
MERGE = {} if os.environ.get('NO_MERGE') == '1' else {24: 26, 25: 27}            # v1-v3: vocalis merged into the thyro-arytenoid; stage 2 keeps it as its own part
MERGED_INTO = set(MERGE.values())

def zc(k):  return lo[2] + k * P

prot = np.load(f'{B}/airway_protect.npy') if os.path.exists(f'{B}/airway_protect.npy') else None
# airway axis per slice (for the outward direction of one-sided growth)
axis_xy = np.tile([-0.65, -101.5], (shape[2], 1))
if prot is not None:
    ks = np.nonzero(prot.any(axis=(0, 1)))[0]
    last = None
    for k in range(shape[2]):
        if prot[:, :, k].any():
            ii = np.argwhere(prot[:, :, k]); last = lo[:2] + ii.mean(0) * P
        if last is not None: axis_xy[k] = last
    axis_xy[:ks.min()] = axis_xy[ks.min()]
del prot

def occ(pid):
    d = np.load(f'{B}/occ_{pid:02d}.npz'); return d['occ'], d['a'], d['b']

def exact_sdf(pid, margin, box=None):
    """signed distance (mm, negative inside) on the part's box expanded by margin (or on a given box)"""
    O, a, b = occ(pid)
    m = int(np.ceil(margin / P))
    a2 = np.maximum(a - m, 0); b2 = np.minimum(b + m, shape)
    if box is not None:
        a2, b2 = box
        oa = np.maximum(a, a2); ob = np.minimum(b, b2)
        O = O[oa[0]-a[0]:ob[0]-a[0], oa[1]-a[1]:ob[1]-a[1], oa[2]-a[2]:ob[2]-a[2]]; a = oa
    Oe = np.zeros(tuple(b2 - a2), bool)
    Oe[a[0]-a2[0]:a[0]-a2[0]+O.shape[0], a[1]-a2[1]:a[1]-a2[1]+O.shape[1], a[2]-a2[2]:a[2]-a2[2]+O.shape[2]] = O
    din = edt.edt(Oe, anisotropy=A3, black_border=True, parallel=2)
    dout = edt.edt(~Oe, anisotropy=A3, black_border=False, parallel=2)
    sdf = np.where(Oe, -din, dout).astype(np.float32)
    band = np.abs(sdf) < margin + 0.3
    idx = np.argwhere(band)
    pts = lo + (idx + a2) * P
    mesh = trimesh.load(f'{B}/part_{pid:02d}.ply')
    V = np.ascontiguousarray(mesh.vertices, np.float64); F = np.ascontiguousarray(mesh.faces, np.int64)
    d2 = np.empty(len(pts))
    for c in range(0, len(pts), 2_000_000):
        d2[c:c + 2_000_000] = igl.point_mesh_squared_distance(np.ascontiguousarray(pts[c:c + 2_000_000]), V, F)[0]
    dd = np.sqrt(d2).astype(np.float32)
    sdf[tuple(idx.T)] = np.where(Oe[tuple(idx.T)], -dd, dd)
    return sdf, a2, b2

def box_coords(a, b):
    zs = lo[2] + P * np.arange(a[2], b[2])
    return zs

OH, aH, bH = occ(1)
_hx = lo[0] + P * np.arange(aH[0], bH[0]); _mid = np.abs(_hx + 0.65) < 5
Z_HYO_LOW = lo[2] + P * (aH[2] + np.argmax(OH[_mid].any(axis=(0, 1)))) - 0.5
print('hyoid lower border at midline: %.1f mm above base' % (Z_HYO_LOW - z_cut))
t0 = time.time()
# ---------- trachea field: hollow, seated under the cricoid ----------
sT, aT, bT = exact_sdf(11, 1.0)
OT = sT <= 0
env = ndimage.maximum_filter1d(OT, size=int(2 * ENV / P) + 1, axis=2)
inside2d = edt.edt(env, anisotropy=(P, P, 1e6), black_border=False, parallel=2)
lumen_sdf = ndimage.gaussian_filter((WALL - inside2d).astype(np.float32), 1.0)      # <0 inside the lumen
# cricoid inferior border as a function of angle around the airway axis (in trachea box)
OC, aC, bC = occ(3)
full = np.zeros(shape, bool); full[aC[0]:bC[0], aC[1]:bC[1], aC[2]:bC[2]] = OC
Cf = full[aT[0]:bT[0], aT[1]:bT[1], aT[2]:bT[2]]; del full
xsT = lo[0] + P * np.arange(aT[0], bT[0]); ysT = lo[1] + P * np.arange(aT[1], bT[1])
CX, CY = -0.65, -100.6
ci = np.argwhere(Cf)
ang = np.degrees(np.arctan2(ysT[ci[:, 1]] - CY, xsT[ci[:, 0]] - CX)) % 360
NB = 180
zmin_bin = np.full(NB, np.inf)
np.minimum.at(zmin_bin, (ang / (360 / NB)).astype(int) % NB, ci[:, 2].astype(float))
good = np.isfinite(zmin_bin)
idx = np.arange(NB)
zmin_bin = np.interp(idx, idx[good], zmin_bin[good], period=NB)
zmin_bin = ndimage.gaussian_filter1d(zmin_bin, 1.5, mode='wrap')
AX, AY = np.meshgrid(xsT, ysT, indexing='ij')
abin = ((np.degrees(np.arctan2(AY - CY, AX - CX)) % 360) / (360 / NB)).astype(int) % NB
zb_mm = lo[2] + (aT[2] + zmin_bin[abin]) * P
LUMEN_BLEND = float(os.environ.get('LUMEN_BLEND', '0'))   # mm over which the tracheal lumen morphs into the cricoid lumen (0 = off)
if LUMEN_BLEND > 0:
    kC = int(round((np.max(zb_mm) + 1.5 - lo[2]) / P)) - aT[2]
    ring = Cf[:, :, kC]; hole = ndimage.binary_fill_holes(ring) & ~ring
    sdfH = (edt.edt(~hole, anisotropy=(P, P), black_border=False) - edt.edt(hole, anisotropy=(P, P), black_border=True)).astype(np.float32)
    zsT_ = box_coords(aT, bT)
    wB = np.clip((zsT_[None, None, :] - (zb_mm[:, :, None] - LUMEN_BLEND)) / LUMEN_BLEND, 0, 1).astype(np.float32)
    lumen_sdf = ((1 - wB) * lumen_sdf + wB * sdfH[:, :, None]).astype(np.float32)
    del wB
    print('tracheal lumen morphed into the cricoid lumen over %.0f mm' % LUMEN_BLEND)
foot = np.ones(zb_mm.shape, bool)
zs = box_coords(aT, bT)
trim_sdf = np.where(foot[:, :, None], zs[None, None, :] - (zb_mm[:, :, None] + float(os.environ.get('SEAM', '0.6'))), -BIG).astype(np.float32)
lumen_clear = np.where(foot[:, :, None], np.maximum(lumen_sdf, zs[None, None, :] - zb_mm[:, :, None]), lumen_sdf).astype(np.float32)
phiT = np.maximum(np.maximum(sT, -lumen_sdf), trim_sdf)
# tissue split: posterior membranous wall (outward normal of the groove-filled envelope points posteriorly) and
# annular ligaments (wall behind the ring grooves, groove depth > 0.3 mm); the rest is cartilage ring
gy = np.gradient(ndimage.gaussian_filter(inside2d.astype(np.float32), 2.0), axis=1)
gx = np.gradient(ndimage.gaussian_filter(inside2d.astype(np.float32), 2.0), axis=0)
ny = -gy / (np.sqrt(gx**2 + gy**2) + 1e-6)          # outward normal, y component (posterior = +y)
memb_f = ((0.70 - ny) * 4.0).astype(np.float32)        # <0 inside the membranous sector
it2 = edt.edt(OT, anisotropy=(P, P, 1e6), black_border=False, parallel=2)
gdep = ndimage.gaussian_filter((inside2d - it2).astype(np.float32), 1.0)
ann_f = (0.30 - gdep).astype(np.float32)               # <0 behind a ring groove
del it2, gx, gy, ny

env_keep = env.copy()
del env, OT
print('trachea field ready (%.0fs)' % (time.time() - t0))

def apply_common(phi, a, b):
    """base cut and keep the tracheal lumen clear (for every part overlapping the trachea box)"""
    zs = box_coords(a, b)
    phi = np.maximum(phi, (z_cut - zs)[None, None, :])
    # overlap with trachea box
    o_a = np.maximum(a, aT); o_b = np.minimum(b, bT)
    if np.all(o_b > o_a):
        s1 = tuple(slice(o_a[i] - a[i], o_b[i] - a[i]) for i in range(3))
        s2 = tuple(slice(o_a[i] - aT[i], o_b[i] - aT[i]) for i in range(3))
        phi[s1] = np.maximum(phi[s1], -lumen_clear[s2])
    return phi

def one_sided(sdf, a, b, d2):
    gx, gy, _ = np.gradient(sdf, P)
    xs = lo[0] + P * np.arange(a[0], b[0]); ys = lo[1] + P * np.arange(a[1], b[1])
    ax = axis_xy[a[2]:b[2]]
    rx = xs[:, None, None] - ax[None, None, :, 0]; ry = ys[None, :, None] - ax[None, None, :, 1]
    rn = np.sqrt(rx**2 + ry**2) + 1e-6
    outward = (gx * rx + gy * ry) / rn            # >0 on the side of the sheet facing away from the airway axis
    grow = np.maximum(sdf - d2, (0.25 - outward) * 2.0)
    return np.minimum(sdf, grow)

def decimate(v, f, ratio):
    ms = pymeshlab.MeshSet(); ms.add_mesh(pymeshlab.Mesh(v, f))
    ms.meshing_decimation_quadric_edge_collapse(targetfacenum=max(int(len(f) * ratio), 500), qualitythr=0.4,
        preserveboundary=True, preservenormal=True, preservetopology=True, optimalplacement=True, planarquadric=True)
    ms.meshing_remove_duplicate_vertices(); ms.meshing_remove_unreferenced_vertices()
    m = ms.current_mesh(); return m.vertex_matrix(), m.face_matrix()

def mc(phi, a, ratio=0.08, min_body=0.5):
    pad = 1
    ph = np.pad(phi, pad, constant_values=BIG)
    v, f, _, _ = measure.marching_cubes(ph, 0.0, spacing=A3)
    v += lo + (np.array(a) - pad) * P
    v2, f2 = decimate(v, f, ratio)
    m = trimesh.Trimesh(v2, f2, process=True)
    if m.volume < 0: m.invert()
    bodies = [x for x in m.split(only_watertight=False) if abs(x.volume) >= min_body]
    m = trimesh.util.concatenate(bodies)
    near = m.vertices[:, 2] < z_cut + 0.5 * P
    m.vertices[near, 2] = np.maximum(m.vertices[near, 2], z_cut)
    dev = trimesh.proximity.closest_point(m, v[::40])[1]
    return m, dev

H = np.full(shape, BIG, np.float32)        # running min of higher-priority fields
order = sorted(PARTS, key=lambda p: -p[4])
stats = {}
for pid, name, concepts, grp, pri, kind in order:
    t = time.time()
    dlt = DELTA.get(pid, 0.0)
    if pid in MERGED_INTO or pid in (33, 34, 37): continue
    if pid == 11:
        phi, a, b = phiT, aT, bT
    elif pid in MERGE:
        s1, a1, b1 = exact_sdf(pid, 0.6); s2, a2_, b2_ = exact_sdf(MERGE[pid], 0.6)
        a = np.minimum(a1, a2_); b = np.maximum(b1, b2_)
        phi = np.minimum(exact_sdf(pid, 0.6, (a, b))[0], exact_sdf(MERGE[pid], 0.6, (a, b))[0])
    else:
        sdf, a, b = exact_sdf(pid, 2 * dlt + 0.6)
        if dlt == 0: phi = sdf
        elif pid in ONE_SIDED: phi = one_sided(sdf, a, b, 2 * dlt)
        else: phi = sdf - dlt
    if pid == 22 and not HE_SCULPT:   # hyo-epiglottic ligament: keep only the band at hyoid level (below it is the fat-filled pre-epiglottic space)
        zs_ = box_coords(a, b)
        phi = np.maximum(phi, (Z_HYO_LOW - zs_)[None, None, :])
    phi = apply_common(phi, a, b)
    sl = tuple(slice(a[i], b[i]) for i in range(3))
    psi = np.maximum(phi, -H[sl])
    if pid == 11:      # split the trachea into rings / membranous wall / annular ligaments
        subs = [(11, np.maximum(psi, -np.minimum(memb_f, ann_f))), (33, np.maximum(psi, memb_f)), (34, np.maximum(np.maximum(psi, ann_f), -memb_f))]
        for spid, sp in subs:
            m, dev = mc(sp, a)
            m.export(f'{B}/final_{spid:02d}.ply')
            stats[spid] = dict(name={11: 'Trachea - cartilage rings', 33: 'Trachea - membranous wall (trachealis)', 34: 'Trachea - annular ligaments'}[spid], faces=len(m.faces), watertight=bool(m.is_watertight), volume=float(m.volume), delta=0)
            print(f'   {spid:2d} {stats[spid]["name"]:38s} faces {len(m.faces):6d} watertight {m.is_watertight} vol {m.volume:7.1f}')
        H[sl] = np.minimum(H[sl], phi)
        if LIG_H > 0:   # cricotracheal ligament: tube from the cricoid lower border down to ring 1; inner = lumen, outer blends cricoid -> ring
            zs_ = box_coords(a, b)
            kC = int(round((np.max(zb_mm) + 1.0 - lo[2]) / P)) - a[2]; kT = int(round((np.min(zb_mm) - LIG_H - lo[2]) / P)) - a[2]
            OCd = ndimage.binary_fill_holes(Cf[:, :, kC]); OTd = env_keep[:, :, kT]
            sC = (edt.edt(~OCd, anisotropy=(P, P), black_border=False) - edt.edt(OCd, anisotropy=(P, P), black_border=True)).astype(np.float32)
            sTd = (edt.edt(~OTd, anisotropy=(P, P), black_border=False) - edt.edt(OTd, anisotropy=(P, P), black_border=True)).astype(np.float32)
            u = np.clip((zb_mm[:, :, None] - zs_[None, None, :]) / LIG_H, 0, 1).astype(np.float32)
            outer = (1 - u) * sC[:, :, None] + u * sTd[:, :, None]
            band = np.maximum(zs_[None, None, :] - (zb_mm[:, :, None] + 0.3), (zb_mm[:, :, None] - LIG_H) - zs_[None, None, :])
            phiL = np.maximum(np.maximum(outer, -lumen_sdf), band).astype(np.float32)
            psiL = np.maximum(phiL, -H[sl])
            m, dev = mc(psiL, a)
            m.export(f'{B}/final_37.ply')
            stats[37] = dict(name='Cricotracheal ligament', faces=len(m.faces), watertight=bool(m.is_watertight), volume=float(m.volume), delta=0)
            print(f'   37 Cricotracheal ligament                  faces {len(m.faces):6d} watertight {m.is_watertight} vol {m.volume:7.1f}')
            H[sl] = np.minimum(H[sl], phiL)
        continue
    if (psi <= 0).sum() == 0:
        print('  !! part fully covered by higher-priority parts:', name); continue
    m, dev = mc(psi, a, min_body=(10.0 if grp == 5 else (2.0 if (grp == 6 or kind == 'sculpt') else 0.5)))     # crumbs left by the trim are dropped from constructed parts
    m.export(f'{B}/final_{pid:02d}.ply')
    H[sl] = np.minimum(H[sl], phi)
    stats[pid] = dict(name=name, faces=len(m.faces), watertight=bool(m.is_watertight), volume=float(m.volume), delta=dlt)
    print(f'{pid:2d} {name:30s} offset {dlt:.2f}{" one-sided x2" if pid in ONE_SIDED else ""}  faces {len(m.faces):6d}  watertight {m.is_watertight}  vol {m.volume:8.1f}  dev p99 {np.percentile(dev,99):.3f}  ({time.time()-t:.0f}s)')
np.save(f'{B}/union_sdf_min.npy', H)
json.dump(stats, open(f'{B}/final_stats.json', 'w'), indent=1)
if os.environ.get('UNION_SEPARATE') != '1':
    k0 = int(np.floor((z_cut - lo[2]) / P)) - 2
    um, _ = mc(H[:, :, max(k0, 0):], np.array([0, 0, max(k0, 0)]), 0.12)
    um.export(f'{B}/final_union.ply')
    print('union: faces', len(um.faces), 'watertight', um.is_watertight, 'vol %.0f' % um.volume, 'bodies', len(um.split(only_watertight=False)), 'bounds', np.round(um.bounds, 1).tolist())
else:
    print('union deferred to union_only.py')
print('total %.0fs' % (time.time() - t0))
