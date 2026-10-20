"""Version 3, stage 1 (framework and joints).
Cricoid: lamina extended down, arch lowered, ring widened (SX) and deepened (F_AP).  Thyroid inferior horns follow the
cricothyroid facets.  Arytenoids (with corniculates) scaled anisotropically about their facets toward published size,
then rocked about the cricoarytenoid facet axis into the quiet-breathing position; attached soft tissue blended.
Hyo-epiglottic ligament rebuilt as a band.  Posterior cricoarytenoid ligaments added.
Reads src_XX.ply, writes part_XX.ply + grid.npy."""
import sys, os, json, numpy as np, trimesh, igl
from scipy import ndimage
sys.path.insert(0, os.path.dirname(__file__))
from partsconfig import PARTS
B = os.environ['BUILD']
E = lambda k, d: float(os.environ.get(k, d))
F_AP = E('F_AP', '1.32')      # AP deepening of the cricoid ring (about CY)
SX = E('SX', '1.10')          # transverse widening of the cricoid (about CX)
SA = np.array([E('SA_X', '1.4'), E('SA_Y', '1.55'), E('SA_Z', '1.85')])   # arytenoid scale (ML, AP, vertical) about its facet
BASE0 = 1366.05
CX, CY = -0.65, -100.6
Z_NEW = BASE0 + E('Z_NEW', '15.0')     # new inferior border of the cricoid
ARCH_DROP = 6.0
Z_VL = BASE0 + 38.5
Z_THY_LOW = BASE0 + 30.2
Z_ARCH_TOP = BASE0 + 27.5
Z_APEX, Z_EP = BASE0 + 44.9, BASE0 + 62.0
Y_ANT = -112.0
P = 0.1
src = lambda i: trimesh.load(f'{B}/src_{i:02d}.ply', process=False)

def ang(x, y): return (np.degrees(np.arctan2(y - CY, x - CX)) + 360) % 360
def cosw(d, a, b): return np.where(d <= a, 1.0, np.where(d >= b, 0.0, 0.5 * (1 + np.cos(np.pi * (d - a) / (b - a)))))
def adist(th, c): return np.abs(((th - c + 180) % 360) - 180)
def arch_w(th):
    d = adist(th, 270)
    A0, A1 = E('ARCH_A0', '20'), E('ARCH_A1', '100')
    return cosw(d, A0, A1)
def smooth01(t):
    t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)

# ---------------- cricoid warp ----------------
cr = src(3)
thy = src(2)
facet_angles = []; horn_tips = []
for sd in (-1, 1):
    q = thy.vertices[sd * (thy.vertices[:, 0] - CX) > 5]; tip = q[np.argmin(q[:, 2])]
    facet_angles.append(float(ang(tip[0:1], tip[1:2])[0])); horn_tips.append(tip)
NB = 72; tv = ang(cr.vertices[:, 0], cr.vertices[:, 1]); bi = (tv / (360 / NB)).astype(int) % NB
zb_bin = np.full(NB, np.inf); np.minimum.at(zb_bin, bi, cr.vertices[:, 2])
zb_bin = ndimage.gaussian_filter1d(zb_bin, 1.5, mode='wrap'); centers = (np.arange(NB) + 0.5) * 360 / NB
FW0, FW1 = E('FW0', '6'), E('FW1', '16'); HF, HL = E('HF', '1.5'), E('HL', '5.0')
def warp_cricoid(v):
    """displacement of source-cricoid points under the stage-1 cricoid warp"""
    th = ang(v[:, 0], v[:, 1]); zb = np.interp(th, centers, zb_bin, period=360)
    A = arch_w(th); Pw = cosw(adist(th, 90), 20, 45)
    Fw = np.maximum(cosw(adist(th, facet_angles[0]), FW0, FW1), cosw(adist(th, facet_angles[1]), FW0, FW1))
    h = HF * Fw + (1 - Fw) * (HL + (7.0 - HL) * Pw + 1.0 * A)
    mrg = 0.3 * Fw + (1 - Fw) * (0.8 + 2.2 * Pw)
    g = 1 - smooth01((v[:, 2] - (zb + mrg)) / h)
    dz_top = -ARCH_DROP * A; dz_bot = Z_NEW - zb
    return np.c_[(v[:, 0] - CX) * (SX - 1), (v[:, 1] - CY) * (F_AP - 1), dz_top + (dz_bot - dz_top) * g]
def d_cricoid(p):   # for soft tissue attached to the ring: scaling plus arch drop only (no lamina stretch)
    th = ang(p[:, 0], p[:, 1])
    return np.c_[(p[:, 0] - CX) * (SX - 1), (p[:, 1] - CY) * (F_AP - 1), -ARCH_DROP * arch_w(th)]
v, f = trimesh.remesh.subdivide_to_size(cr.vertices, cr.faces, max_edge=0.25, max_iter=20)
crn = trimesh.Trimesh(v + warp_cricoid(v), f, process=False)
assert crn.is_watertight
crn.export(f'{B}/part_03.ply')
print(f'cricoid: facet angles {facet_angles[0]:.0f}/{facet_angles[1]:.0f}; volume {cr.volume:.0f} -> {crn.volume:.0f} mm3; '
      f'z {cr.bounds[0,2]-BASE0:.1f}..{cr.bounds[1,2]-BASE0:.1f} -> {crn.bounds[0,2]-BASE0:.1f}..{crn.bounds[1,2]-BASE0:.1f}; '
      f'width {np.ptp(cr.vertices[:,0]):.1f} -> {np.ptp(crn.vertices[:,0]):.1f}; AP {np.ptp(cr.vertices[:,1]):.1f} -> {np.ptp(crn.vertices[:,1]):.1f}')

# ---------------- thyroid: inferior horns follow the cricothyroid facets ----------------
crV = np.ascontiguousarray(cr.vertices, np.float64); crF = np.ascontiguousarray(cr.faces, np.int64)
tv_ = thy.vertices.copy(); disp = np.zeros_like(tv_)
crnV = np.ascontiguousarray(crn.vertices, np.float64); crnF = np.ascontiguousarray(crn.faces, np.int64)
for sd, tip in zip((-1, 1), horn_tips):
    d0, _, cp = igl.point_mesh_squared_distance(np.ascontiguousarray(tip[None, :]), crV, crF)
    cp0 = np.asarray(cp).reshape(3); dfac = warp_cricoid(cp0[None, :])[0]
    # keep the original joint clearance: move the tip so it sits at the same distance from the moved facet surface
    for _ in range(3):
        tip2 = tip + dfac
        d1, _, cp1 = igl.point_mesh_squared_distance(np.ascontiguousarray(tip2[None, :]), crnV, crnF)
        cp1 = np.asarray(cp1).reshape(3); nrm = (tip2 - cp1); nrm /= np.linalg.norm(nrm) + 1e-9
        dfac = dfac + nrm * (np.sqrt(d0[0]) - np.sqrt(d1[0]))
    side = (sd * (tv_[:, 0] - CX) > 2) & (tv_[:, 1] > -103)
    w = 1 - smooth01((tv_[:, 2] - (tip[2] + 2.0)) / 10.0)
    disp[side] += (w[side])[:, None] * dfac
    print(f'thyroid inferior horn ({"R" if sd < 0 else "L"}): tip moves {np.round(dfac, 2)} mm (joint clearance {np.sqrt(d0[0]):.2f} -> {np.sqrt(d1[0]):.2f})')
thn = trimesh.Trimesh(tv_ + disp, thy.faces, process=False); thn.export(f'{B}/part_02.ply')

# ---------------- arytenoids: scale about the facet, then rock about the facet axis ----------------
ALPHA = E('ALPHA', '22'); AX_EL = E('AX_EL', '35'); AX_AZ = E('AX_AZ', '45'); AX_R = E('AX_R', '3.0')
samp = cr.sample(150000)
def facet_patch(a):
    d2, _, _ = igl.point_mesh_squared_distance(np.ascontiguousarray(samp), np.ascontiguousarray(a.vertices, np.float64), np.ascontiguousarray(a.faces, np.int64))
    p = samp[np.sqrt(d2) < 1.0]; c = p.mean(0); n = np.linalg.svd(p - c, full_matrices=False)[2][2]
    return c, n * np.sign(n[2])
T = trimesh.transformations.translation_matrix
def ary_transform(pid, lat):
    a = src(pid)
    c, n = facet_patch(a)
    t = warp_cricoid(c[None, :])[0]                                   # facet moves with the cricoid
    c2 = c + t
    S = np.eye(4); S[0, 0], S[1, 1], S[2, 2] = SA
    Msc = T(c2) @ S @ T(-c2) @ T(t)                                    # translate, then scale about the moved facet
    el, az = np.radians(AX_EL), np.radians(AX_AZ)
    d = np.array([lat * np.cos(el) * np.sin(az), -np.cos(el) * np.cos(az), -np.sin(el)])
    pt = c2 - AX_R * n
    vs = a.vertices[np.argmin(a.vertices[:, 1])]                        # vocal process tip (source)
    best = None
    for s in (1, -1):
        M = trimesh.transformations.rotation_matrix(np.radians(s * ALPHA), d, point=pt) @ Msc
        vp2 = M[:3, :3] @ vs + M[:3, 3]
        if best is None or lat * vp2[0] > lat * best[1][0]: best = (M, vp2)
    D = best[1] - vs
    apex = a.vertices[np.argmax(a.vertices[:, 2])]; apex2 = best[0][:3, :3] @ apex + best[0][:3, 3]
    print(f'arytenoid {pid}: facet {np.round(c - [0, 0, BASE0], 1)} -> {np.round(c2 - [0, 0, BASE0], 1)}; vocal process {np.round(vs - [0, 0, BASE0], 1)} -> {np.round(best[1] - [0, 0, BASE0], 1)}; apex z {apex[2]-BASE0:.1f} -> {apex2[2]-BASE0:.1f}')
    return best[0], a.vertices.mean(0), vs, D, c2
MR, cR, VPR, DR, FR = ary_transform(4, -1)
ML, cL, VPL, DL, FL = ary_transform(5, +1)
def apply(M, p): return (M[:3, :3] @ p.T).T + M[:3, 3]
def d_side(p):
    dR = apply(MR, p) - p; dL = apply(ML, p) - p
    return np.where((p[:, 0] < CX)[:, None], dR, dL)
def d_fold(p, zfade=False):
    right = (p[:, 0] < CX)
    vpy = np.where(right, VPR[1], VPL[1]); D = np.where(right[:, None], DR, DL)
    t = (p[:, 1] - Y_ANT) / (vpy - Y_ANT)
    tl = np.clip(t, 0, 1)[:, None]
    s = smooth01((t - 0.8) / 0.2)[:, None]
    d = (1 - s) * tl * D + s * d_side(p)
    if zfade: d *= np.clip((Z_EP - p[:, 2]) / (Z_EP - (Z_VL + 6)), 0, 1)[:, None]
    return d
def zhi_cricoid(th):
    Vc = cr.vertices; tvv = ang(Vc[:, 0], Vc[:, 1]); b = (tvv / 5).astype(int) % 72
    zh = np.full(72, -1e9); np.maximum.at(zh, b, Vc[:, 2])
    return zh[(th / 5).astype(int) % 72]

out = {}
for pid, name, concepts, grp, pri, kind in PARTS:
    if not concepts or pid in (2, 3, 22): continue
    m = src(pid); p = m.vertices.copy()
    if pid in (4, 6):   p = apply(MR, p)
    elif pid in (5, 7): p = apply(ML, p)
    elif pid in (12, 13, 26, 27): p = p + d_fold(p)
    elif pid in (24, 25): p = p + d_fold(p, zfade=True)
    elif pid in (14, 15):
        th = ang(p[:, 0], p[:, 1]); zh = zhi_cricoid(th)
        wc = np.clip((Z_VL - p[:, 2]) / np.maximum(Z_VL - zh, 1.0), 0, 1)[:, None]
        p = p + wc * d_cricoid(p) + (1 - wc) * d_fold(p)
    elif pid == 16:
        wc = np.clip((Z_THY_LOW - p[:, 2]) / (Z_THY_LOW - Z_ARCH_TOP), 0, 1)[:, None]
        p = p + wc * d_cricoid(p)
    elif pid in (28, 29, 30):
        wl = np.clip((p[:, 0] - cR[0]) / (cL[0] - cR[0]), 0, 1)[:, None]
        p = p + (1 - wl) * (apply(MR, p) - p) + wl * (apply(ML, p) - p)
    elif pid in (31, 32, 8, 9):
        wa = np.clip((Z_EP - p[:, 2]) / (Z_EP - Z_APEX), 0, 1)[:, None]
        p = p + wa * d_side(p)
    if pid == 11: p = p - [0, 0, E('TRACHEA_DZ', '2.2')]
    m = trimesh.Trimesh(p, m.faces, process=False)
    out[pid] = m; m.export(f'{B}/part_{pid:02d}.ply')

# ---------------- hyo-epiglottic ligament: a band from the hyoid body (posterior surface, just below the upper border) to the epiglottis ----------------
import shapely
hy = src(1).vertices; ep = src(10).vertices
hb = hy[np.abs(hy[:, 0] - CX) < 5]
sel = hb[(hb[:, 2] > hb[:, 2].max() - 3.5) & (hb[:, 2] < hb[:, 2].max() - 1.5)]
A = sel[sel[:, 1] > np.percentile(sel[:, 1], 70)].mean(0)                                     # posterior face, 1.5-3.5 mm below the top
em = ep[np.abs(ep[:, 0] - CX) < 4]; band = em[np.abs(em[:, 2] - (A[2] - E('HE_DROP', '2.0'))) < 1.5]
Bp = band[band[:, 1] < np.percentile(band[:, 1], 30)].mean(0)                                 # anterior face of the epiglottis
u = (Bp - A); L = np.linalg.norm(u); u /= L
A0 = A - E('HE_IN_HY', '0.8') * u; B0_ = Bp + 1.5 * u
W, TH = E('HE_W', '9.0'), E('HE_T', '2.5')
poly = shapely.geometry.box(-(W / 2 - TH / 2), -TH / 2 * 0, (W / 2 - TH / 2), TH / 2 * 0).buffer(TH / 2)   # stadium section W x TH
band_m = trimesh.creation.extrude_polygon(poly, np.linalg.norm(B0_ - A0))
ez = u; ex = np.array([1.0, 0, 0]); ey = np.cross(ez, ex); ey /= np.linalg.norm(ey); ex = np.cross(ey, ez)
R = np.eye(4); R[:3, 0], R[:3, 1], R[:3, 2] = ex, ey, ez; R[:3, 3] = A0
band_m.apply_transform(R)
# clip the epiglottic end to a plane 0.4 mm behind the epiglottis' anterior face (the plate is only ~1 mm thick here)
epm = src(10)
pts = []
for dz in np.arange(-4, 5, 1.0):
    sec = epm.section(plane_origin=[0, 0, Bp[2] + dz], plane_normal=[0, 0, 1])
    if sec is None: continue
    vv = sec.vertices; mm_ = vv[np.abs(vv[:, 0] - CX) < 1.0]
    if len(mm_): pts.append([mm_[:, 1].min(), Bp[2] + dz])
pts = np.array(pts); k_, c_ = np.polyfit(pts[:, 1], pts[:, 0], 1)        # y_ant = k*z + c
n_ = np.array([0.0, -1.0, k_]); n_ /= np.linalg.norm(n_)                # points anteriorly, perpendicular to the plate
p0 = np.array([CX, k_ * Bp[2] + c_ + E('HE_IN_EP', '0.4'), Bp[2]])
band_m = band_m.slice_plane(p0, n_, cap=True)
band_m.export(f'{B}/part_22.ply')
print(f'hyo-epiglottic ligament: hyoid {np.round(A - [0,0,BASE0],1)} -> epiglottis {np.round(Bp - [0,0,BASE0],1)}, length {L:.1f} mm, {W} x {TH} mm stadium section')

# ---------------- posterior cricoarytenoid ligaments ----------------
for pid, M, lat, Fc in ((35, MR, -1, FR), (36, ML, 1, FL)):
    a = apply(M, src(4 if pid == 35 else 5).vertices)
    base = a[a[:, 2] < a[:, 2].min() + 2.5]
    pa = base[np.argmax(base[:, 1] - 0.5 * lat * (base[:, 0] - CX))]          # posterior-medial point of the base
    target = Fc + np.array([-lat * 2.0, 2.5, 0.5])                               # medial-posterior of the facet, on the lamina top
    _, _, cp = igl.point_mesh_squared_distance(np.ascontiguousarray(target[None, :]), crnV, crnF)
    pc = np.asarray(cp).reshape(3)
    seg = pc - pa; Ls = np.linalg.norm(seg)
    cap = trimesh.creation.capsule(height=Ls + 1.0, radius=E('PCL_R', '0.8'))
    zax = seg / Ls; xax = np.cross([0, 1, 0], zax); xax /= np.linalg.norm(xax); yax = np.cross(zax, xax)
    Rm = np.eye(4); Rm[:3, 0], Rm[:3, 1], Rm[:3, 2] = xax, yax, zax; Rm[:3, 3] = (pa + pc) / 2
    cap.apply_transform(Rm); cap.export(f'{B}/part_{pid:02d}.ply')
    print(f'posterior cricoarytenoid ligament {pid}: {np.round(pa-[0,0,BASE0],1)} -> {np.round(pc-[0,0,BASE0],1)} ({Ls:.1f} mm)')

# ---------------- grid ----------------
z_cut = crn.bounds[0, 2] - 22.0
Tm = trimesh.load(f'{B}/part_11.ply', process=False)
Tm = Tm.slice_plane([0, 0, z_cut - 4], [0, 0, 1], cap=True); Tm.export(f'{B}/part_11.ply')
ids = [p[0] for p in PARTS if p[2] or p[5] == 'sculpt']
allb = [trimesh.load(f'{B}/part_{i:02d}.ply', process=False).bounds for i in ids]
lo_g = np.min([b[0] for b in allb], 0) - 2.0; hi_g = np.max([b[1] for b in allb], 0) + 2.0
lo_g[2] = z_cut - 4; lo_g = np.floor(lo_g / P) * P
shape_g = tuple(int(np.ceil((h - l) / P)) + 1 for l, h in zip(lo_g, hi_g))
np.save(f'{B}/grid.npy', np.array([*lo_g, P, *shape_g, z_cut]))
print('new z_cut %.2f (old base %.2f); grid %s' % (z_cut, BASE0, shape_g))
