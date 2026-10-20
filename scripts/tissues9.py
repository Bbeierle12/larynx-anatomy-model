"""Stage 3c (part 1): the piriform fossae and the lateral pharyngeal walls below them.
sinus:   the fossa lumen S (per side) is carved out of the soft tissue that currently fills it (false fold, ventricle wall,
         vestibular mucosa, thyro-epiglottic muscle), and a MUC_T lining (76/77) is laid on its walls where no part is.
latwall: a 1 mm mucosal sheet (78/79) from the thyroid's posterior border / inferior horn to the cricoid and arytenoid,
         from the cricoid's lower border up to the fossa apex, closing the paraglottic space behind.
Runs after tissues7/8 in BUILD.  Sections: sinus latwall."""
import sys, os, numpy as np, trimesh, igl, edt
from scipy import ndimage
sys.path.insert(0, os.path.dirname(__file__))
from musclelib import *
from partsconfig import PARTS
B = os.environ['BUILD']; E = lambda k, d: float(os.environ.get(k, d))
grid = Grid(f'{B}/grid.npy'); Z0 = grid.z_cut; CX = -0.65; P = grid.P
G_ = np.load(f'{B}/grid.npy'); LO = G_[:3]; NG = G_[4:7].astype(int)
L = lambda i: trimesh.load(f'{B}/part_{i:02d}.ply', process=False)
NAME = {p[0]: p[1] for p in PARTS}
which = sys.argv[1:] or ['sinus', 'latwall', 'lining']
def occ_to_phi(occ):
    return np.where(occ, -edt.edt(occ, anisotropy=(P,)*3, black_border=True), edt.edt(~occ, anisotropy=(P,)*3, black_border=False)).astype(np.float32)
def box_points(a, b):
    return [LO[i] + P * np.arange(a[i], b[i]) for i in range(3)]
def side_lookup(mesh, axis, sign, binw=0.3):
    v, _ = trimesh.sample.sample_surface(mesh, 800000, seed=0); v = np.vstack([v, mesh.vertices])
    o = [i for i in range(3) if i != axis]; lo0 = v[:, o].min(0) - 1; n = ((v[:, o].max(0) - lo0) / binw).astype(int) + 3
    X = np.full(tuple(n), -np.inf); ij = ((v[:, o] - lo0) / binw).astype(int); np.maximum.at(X, (ij[:, 0], ij[:, 1]), sign * v[:, axis])
    has = np.isfinite(X)
    for _ in range(2):
        Xf = ndimage.maximum_filter(np.where(has, X, -np.inf), size=3); X = np.where(has, X, Xf); has = np.isfinite(X)
    def f(pts):
        jj = ((pts[:, o] - lo0) / binw).astype(int); ok = (jj[:, 0] >= 0) & (jj[:, 0] < n[0]) & (jj[:, 1] >= 0) & (jj[:, 1] < n[1])
        out = np.full(len(pts), np.nan); out[ok] = X[jj[ok, 0], jj[ok, 1]]; out[~np.isfinite(out)] = np.nan; return out
    return f
def write(pid, occ, a, b, name, smooth=0.25):
    phi = occ_to_phi(occ)
    if smooth > 0: phi = ndimage.gaussian_filter(phi, smooth / P, mode='nearest')
    return write_part(grid, B, pid, phi, a, b, name)
def load_occ(pid):
    d = np.load(f'{B}/occ_{pid:02d}.npz'); return d['occ'], d['a'], d['b']
def carve(pid, S, a, b, label):
    """remove the voxels of S (box a..b on the grid) from part pid"""
    f = f'{B}/occ_{pid:02d}.npz'
    if not os.path.exists(f): return
    o, oa, ob = load_occ(pid); qa = np.maximum(a, oa); qb = np.minimum(b, ob)
    if not np.all(qb > qa): return
    sub = S[qa[0]-a[0]:qb[0]-a[0], qa[1]-a[1]:qb[1]-a[1], qa[2]-a[2]:qb[2]-a[2]]
    o2 = o.copy(); o2[qa[0]-oa[0]:qb[0]-oa[0], qa[1]-oa[1]:qb[1]-oa[1], qa[2]-oa[2]:qb[2]-oa[2]] &= ~sub
    n = o.sum() - o2.sum()
    if n == 0: return
    lab, k = ndimage.label(o2)
    if k > 1:
        sizes = np.bincount(lab.ravel()); sizes[0] = 0; keep = sizes >= 20 / P ** 3; keep[0] = False; o2 = keep[lab]      # drop crumbs under 20 mm3
    phi = ndimage.gaussian_filter(occ_to_phi(o2), 0.15 / P, mode='nearest')
    write_part(grid, B, pid, phi, oa, ob, NAME[pid] + f' ({label} carved)')
    print(f'     {label}: {n*P**3:.0f} mm3 carved out of part {pid}')

thy = L(2); epi = L(10)
def y_ant(z):
    """anterior wall of the fossa (its 'anterior angle') by height, mm above the base"""
    zz = np.array([47.0, 50.0, 54.0, 60.0, 66.0, 72.0, 80.0]); yy = np.array([-90.0, -93.0, -96.0, -98.0, -99.0, -100.0, -101.0]) + E('SIN_YOFF', '0.0')
    return np.interp(z, zz, yy)

if 'sinus' in which:
    # lateral wall: inner surface of the thyroid lamina and the thyrohyoid membrane / lateral thyrohyoid ligament
    outer = trimesh.util.concatenate([thy, L(17), L(18), L(20), L(21)])
    for lat, pid in ((-1, 76), (1, 77)):
        half = outer.slice_plane([CX, 0, 0], [lat, 0, 0], cap=True); x_lam = side_lookup(half, 0, -lat)          # max(-lat*x): inner face
        medial = trimesh.util.concatenate([L(i) for i in ((56, 58, 48, 4, 6, 8, 31, 29, 40, 42, 61, 28, 3, 38) if lat < 0 else (57, 59, 49, 5, 7, 9, 32, 30, 41, 43, 61, 28, 3, 39))])
        x_in = side_lookup(medial, 0, lat)                                                                          # max(lat*x): lateral face of the medial structures
        zA = Z0 + E('SIN_Z0', '47.5'); zT = LO[2] + (NG[2] - 2) * P
        lo_mm = np.array([CX if lat > 0 else thy.bounds[0, 0], -103.0, zA - 1.5]); hi_mm = np.array([thy.bounds[1, 0] if lat > 0 else CX, thy.bounds[1, 1] + 1.0, zT])
        a, b = grid.box(lo_mm, hi_mm, margin=0.3); xs, ys, zs = box_points(a, b)
        G = np.stack(np.meshgrid(xs, ys, zs, indexing='ij'), -1).reshape(-1, 3)
        xl = x_lam(G); xi = x_in(G)
        T = E('MUC_T', '0.8')
        inS = np.isfinite(xl) & np.isfinite(xi) & (G[:, 1] >= y_ant(G[:, 2] - Z0)) & (G[:, 2] >= zA) \
              & (lat * G[:, 0] >= xi + T) & (-lat * G[:, 0] >= xl + T)                   # between the medial structures and the lamina, a lining's width off each
        inS &= ~((G[:, 1] > E('SIN_YPOST', '-88.0')) & (lat * (G[:, 0] - CX) < E('SIN_XMIN', '7.0')))   # behind the arytenoid front stay lateral of its body: the midline postcricoid region is the pharynx, not the fossa
        S = inS.reshape(len(xs), len(ys), len(zs))
        # only the part connected to the inlet above (drop pockets)
        lab, n = ndimage.label(S)
        if n > 1:
            top = np.unique(lab[:, :, -1]); top = top[top > 0]
            sizes = np.bincount(lab.ravel()); sizes[0] = 0
            keep = top if len(top) else [sizes.argmax()]
            S = np.isin(lab, keep)
        S = ndimage.gaussian_filter(occ_to_phi(S), E('SIN_SMOOTH', '0.5') / P, mode='nearest') <= 0          # smooth the lookup-bin terraces
        print(f'     fossa {"R" if lat < 0 else "L"}: lumen {S.sum()*P**3:.0f} mm3, z {zA-Z0:.1f} up, anterior wall y {y_ant(50):.0f} (z 50) .. {y_ant(70):.0f} (z 70)')
        Sd = ndimage.binary_dilation(S, iterations=int(round(T / P)))                # the lumen plus a lining's width
        for cp in (52, 53, 62, 63, 64, 65, 69, 70, 68):               # the thyro-epiglottic muscle lies in the fold, medial to the fossa
            carve(cp, Sd, a, b, f'piriform fossa {"R" if lat < 0 else "L"}')
        np.savez_compressed(f'{B}/sinus_{pid:02d}.npz', S=S, Sd=Sd, a=a, b=b)

if 'lining' in which:                      # after the fat exists (it backs the anterior wall): the MUC_T shell around each lumen wherever tissue lies behind it
    for lat, pid in ((-1, 76), (1, 77)):
        d = np.load(f'{B}/sinus_{pid:02d}.npz'); S, a, b = d['S'], d['a'], d['b']; T = E('MUC_T', '0.8'); Sd = d['Sd'] if 'Sd' in d.files else ndimage.binary_dilation(S, iterations=int(round(T / P)))
        shell = Sd & ~S
        occ_all = np.zeros(S.shape, bool)
        for pp, *_ in PARTS:
            f = f'{B}/occ_{pp:02d}.npz'
            if pp in (76, 77, 78, 79) or not os.path.exists(f): continue
            o, oa, ob = load_occ(pp); qa = np.maximum(a, oa); qb = np.minimum(b, ob)
            if np.all(qb > qa): occ_all[qa[0]-a[0]:qb[0]-a[0], qa[1]-a[1]:qb[1]-a[1], qa[2]-a[2]:qb[2]-a[2]] |= o[qa[0]-oa[0]:qb[0]-oa[0], qa[1]-oa[1]:qb[1]-oa[1], qa[2]-oa[2]:qb[2]-oa[2]]
        backed = ndimage.binary_dilation(occ_all, iterations=int(round((T + 0.15) / P)))               # lining only where it lies on tissue: the open top and back stay open
        lining = shell & ~occ_all & backed
        write(pid, lining, a, b, f'Piriform fossa lining {"R" if lat < 0 else "L"}', smooth=0.25)

if 'latwall' in which:
    cr = L(3); tv = thy.vertices
    for lat, pid in ((-1, 78), (1, 79)):
        med = trimesh.util.concatenate([L(i) for i in ((3, 4, 38, 40, 42) if lat < 0 else (3, 5, 39, 41, 43))]); mv = med.vertices
        zlo = cr.bounds[0, 2] + E('LW_Z0', '0.0'); zhi = Z0 + E('SIN_Z0', '47.5') + 1.0
        segs = []
        for z in np.arange(zlo, zhi, 0.5):
            t = tv[(np.abs(tv[:, 2] - z) < 0.5) & (lat * (tv[:, 0] - CX) > 5.0)]
            m = mv[(np.abs(mv[:, 2] - z) < 0.5) & (mv[:, 1] > -94.0) & (lat * (mv[:, 0] - CX) > 2.0)]
            if len(t) == 0 or len(m) == 0: continue
            Pl = t[np.argmax(t[:, 1])]; Pm = m[np.argmax(lat * (m[:, 0] - CX))]
            segs.append((Pl, Pm, z))
        if not segs: print('     no lateral wall segments'); continue
        allp = np.array([q for s in segs for q in s[:2]])
        lo_mm = allp.min(0) - 1.5; hi_mm = allp.max(0) + 1.5
        a, b = grid.box(lo_mm, hi_mm, margin=0.3); xs, ys, zs = box_points(a, b)
        G = np.stack(np.meshgrid(xs, ys, zs, indexing='ij'), -1).reshape(-1, 3)
        T = E('LW_T', '1.0'); occ = np.zeros(len(G), bool)
        for Pl, Pm, z in segs:
            sel = np.abs(G[:, 2] - z) <= 0.3
            if not sel.any(): continue
            Q = G[sel]; A2 = Pl[:2]; B2 = Pm[:2]; d = B2 - A2; L2 = d @ d
            t = np.clip(((Q[:, :2] - A2) @ d) / L2, -0.05, 1.05)
            proj = A2 + t[:, None] * d; dist = np.linalg.norm(Q[:, :2] - proj, axis=1)
            occ[np.nonzero(sel)[0][dist <= T / 2]] = True
        occ = occ.reshape(len(xs), len(ys), len(zs))
        write(pid, occ, a, b, f'Lateral pharyngeal wall {"R" if lat < 0 else "L"}', smooth=0.2)
        print(f'     lateral wall {"R" if lat < 0 else "L"}: {len(segs)} levels z {segs[0][2]-Z0:.1f}..{segs[-1][2]-Z0:.1f}, thyroid border -> cricoid/arytenoid, {T} mm')
