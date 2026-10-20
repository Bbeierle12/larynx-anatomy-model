"""Stage 3: fold cover, vestibular folds and ligaments, quadrangular membranes, aryepiglottic folds with tubercles,
epiglottic tubercle, interarytenoid mucosa.  Constructed on the framework + muscles (part_XX.ply in BUILD).
Writes occ/part for 50-61.  All dimensions in life-size mm; published values in the notes."""
import sys, os, numpy as np, trimesh, igl, edt
from scipy import ndimage
sys.path.insert(0, os.path.dirname(__file__))
from musclelib import *
B = os.environ['BUILD']; E = lambda k, d: float(os.environ.get(k, d))
grid = Grid(f'{B}/grid.npy'); Z0 = grid.z_cut; CX = -0.65; P = grid.P
L = lambda i: trimesh.load(f'{B}/part_{i:02d}.ply', process=False)
thy, epi, tra = L(2), L(10), L(28)
ARY = {-1: L(4), 1: L(5)}; VL = {-1: L(12), 1: L(13)}; CO = {-1: L(14), 1: L(15)}; TA = {-1: L(24), 1: L(25)}; VO = {-1: L(26), 1: L(27)}
AE = {-1: L(31), 1: L(32)}; CU = {-1: L(8), 1: L(9)}; CORN = {-1: L(6), 1: L(7)}
which = sys.argv[1:] or ['cover', 'false', 'quad', 'ae', 'tub', 'ia', 'grid']
COVER = E('COVER', '1.0')              # fold cover (epithelium + superficial lamina propria), mm
def occ_to_phi(occ):
    return np.where(occ, -edt.edt(occ, anisotropy=(P,)*3, black_border=True), edt.edt(~occ, anisotropy=(P,)*3, black_border=False)).astype(np.float32)
def box_points(a, b):
    xs, ys, zs = [grid.lo[i] + P * np.arange(a[i], b[i]) for i in range(3)]
    return xs, ys, zs
def raster(mesh, a, b):
    xs, ys, zs = box_points(a, b)
    G = np.stack(np.meshgrid(xs, ys, zs, indexing='ij'), -1).reshape(-1, 3)
    w = igl.fast_winding_number(np.ascontiguousarray(mesh.vertices, np.float64), np.ascontiguousarray(mesh.faces, np.int64), np.ascontiguousarray(G))
    return (w > 0.5).reshape(len(xs), len(ys), len(zs))
def side_lookup(mesh, axis, sign, binw=0.3):
    """per bin of the other two coords: most extreme sign*coord of the mesh surface (NaN where none)"""
    v, _ = trimesh.sample.sample_surface(mesh, 600000, seed=0); v = np.vstack([v, mesh.vertices])
    o = [i for i in range(3) if i != axis]; lo0 = v[:, o].min(0) - 1; n = ((v[:, o].max(0) - lo0) / binw).astype(int) + 3
    X = np.full(tuple(n), -np.inf); ij = ((v[:, o] - lo0) / binw).astype(int); np.maximum.at(X, (ij[:, 0], ij[:, 1]), sign * v[:, axis])
    has = np.isfinite(X)
    for _ in range(2):
        Xf = ndimage.maximum_filter(np.where(has, X, -np.inf), size=3); X = np.where(has, X, Xf); has = np.isfinite(X)
    def f(pts):
        jj = ((pts[:, o] - lo0) / binw).astype(int); ok = (jj[:, 0] >= 0) & (jj[:, 0] < n[0]) & (jj[:, 1] >= 0) & (jj[:, 1] < n[1])
        out = np.full(len(pts), np.nan); out[ok] = X[jj[ok, 0], jj[ok, 1]]; out[~np.isfinite(out)] = np.nan; return out
    return f
def fold_frame(lat):
    vl = VL[lat].vertices; A = vl[np.argmin(vl[:, 1])]; Pp = vl[np.argmax(vl[:, 1])]
    d = Pp - A; d[2] = 0; d /= np.linalg.norm(d); m = np.array([-lat * abs(d[1]), -lat * 0.0, 0.0])    # medial: toward the midline, perpendicular to the fold in the axial plane
    m = np.array([lat * d[1], -lat * d[0], 0.0]); m = m if (m[0] * (-lat)) > 0 else -m
    return A, Pp, d, m
def medial_edge(lat):
    """x of the vocal ligament's medial edge as a function of y (lookup), and z of the ligament"""
    vl = VL[lat]; v = vl.vertices
    ys = np.arange(v[:, 1].min(), v[:, 1].max() + 0.01, 0.5); xe, ze = [], []
    for y in ys:
        s = v[np.abs(v[:, 1] - y) < 0.6]
        if len(s) == 0: xe.append(np.nan); ze.append(np.nan); continue
        k = np.argmax(-lat * s[:, 0]); xe.append(s[k, 0]); ze.append(s[:, 2].mean())
    xe = np.array(xe); ze = np.array(ze); ok = np.isfinite(xe)
    return lambda y: np.interp(y, ys[ok], xe[ok]), lambda y: np.interp(y, ys[ok], ze[ok]), ys[ok].min(), ys[ok].max()
def write(pid, occ, a, b, name, smooth=0.25, clip_parts=()):
    phi = occ_to_phi(occ)
    if smooth > 0: phi = ndimage.gaussian_filter(phi, smooth / P, mode='nearest')
    return write_part(grid, B, pid, phi, a, b, name)

# ---------------------------------------------------------------- vocal fold cover (50 R, 51 L)
if 'cover' in which:
    for lat, pid in ((-1, 50), (1, 51)):
        xedge, zlig, y0, y1 = medial_edge(lat); A, Pp, d, m = fold_frame(lat)
        core = trimesh.util.concatenate([VL[lat], TA[lat], VO[lat], CO[lat]])
        zt = max(TA[lat].bounds[1, 2], VO[lat].bounds[1, 2])                       # muscle top = ventricle floor level
        lo_mm = np.array([core.bounds[0, 0] - COVER - 1, y0 - 2.5, zlig(y0) - E('COVER_DOWN', '6.0') - 1]); hi_mm = np.array([core.bounds[1, 0] + COVER + 1, y1 + 2.0, zt + COVER + 1])
        a, b = grid.box(lo_mm, hi_mm, margin=0.5); xs, ys, zs = box_points(a, b)
        G = np.stack(np.meshgrid(xs, ys, zs, indexing='ij'), -1).reshape(-1, 3)
        Vc = np.ascontiguousarray(core.vertices, np.float64); Fc = np.ascontiguousarray(core.faces, np.int64)
        d2, _, _ = igl.point_mesh_squared_distance(G, Vc, Fc); dist = np.sqrt(d2)
        inside_core = igl.fast_winding_number(Vc, Fc, np.ascontiguousarray(G)) > 0.5
        near = (dist <= COVER + 0.05) & ~inside_core
        # only on the airway side: line of sight from the voxel to the airway axis (same z) must not cross the core or the thyroid
        cand = np.nonzero(near)[0]; Gc = G[cand]
        axis = np.array([CX, E('AXIS_Y', '-101.0')])
        K = 14; ts = (np.arange(1, K + 1) / (K + 1))[None, :, None]
        seg = Gc[:, None, :].repeat(K, 1); seg[:, :, 0] = Gc[:, None, 0] + (axis[0] - Gc[:, None, 0]) * ts[:, :, 0]; seg[:, :, 1] = Gc[:, None, 1] + (axis[1] - Gc[:, None, 1]) * ts[:, :, 0]
        segf = np.ascontiguousarray(seg.reshape(-1, 3))
        blocked = igl.fast_winding_number(Vc, Fc, segf) > 0.5
        thyV = np.ascontiguousarray(thy.vertices, np.float64); thyF = np.ascontiguousarray(thy.faces, np.int64)
        blocked |= igl.fast_winding_number(thyV, thyF, segf) > 0.5
        blocked = blocked.reshape(len(cand), K).any(1)
        near[cand[blocked]] = False
        # restrict to the fold: between 1 mm in front of the anterior commissure and 1.5 mm behind the vocal process; down to z0 - COVER_DOWN
        near &= (G[:, 1] >= y0 - 1.0) & (G[:, 1] <= y1 + 1.5) & (G[:, 2] >= zlig(np.clip(G[:, 1], y0, y1)) - E('COVER_DOWN', '6.0'))
        occ = near.reshape(len(xs), len(ys), len(zs))
        # drop crumbs
        lab, n = ndimage.label(occ)
        if n > 1:
            sizes = np.bincount(lab.ravel()); sizes[0] = 0; occ = lab == sizes.argmax()
        # closed cavities inside the fold (e.g. between the ligament and the vocalis) become part of the cover
        solid = occ.copy()
        for wid in (2, 3, 4, 5, 12, 13, 14, 15, 16, 24, 25, 26, 27, 38, 39, 42, 43):
            f = f'{B}/occ_{wid:02d}.npz'
            if not os.path.exists(f): continue
            dd = np.load(f); o, oa, ob = dd['occ'], dd['a'], dd['b']
            qa = np.maximum(a, oa); qb = np.minimum(b, ob)
            if np.all(qb > qa): solid[qa[0]-a[0]:qb[0]-a[0], qa[1]-a[1]:qb[1]-a[1], qa[2]-a[2]:qb[2]-a[2]] |= o[qa[0]-oa[0]:qb[0]-oa[0], qa[1]-oa[1]:qb[1]-oa[1], qa[2]-oa[2]:qb[2]-oa[2]]
        lab, n = ndimage.label(~solid); edge = set(np.unique(np.concatenate([lab[0].ravel(), lab[-1].ravel(), lab[:, 0].ravel(), lab[:, -1].ravel(), lab[:, :, 0].ravel(), lab[:, :, -1].ravel()])))
        cav = np.isin(lab, [i for i in range(1, n + 1) if i not in edge]); occ |= cav
        print(f'     filled {cav.sum() * P**3:.1f} mm3 of closed cavities inside the fold into the cover')
        m_, vol = write(pid, occ, a, b, f'Vocal fold cover {"R" if lat < 0 else "L"}')
        print(f'     fold edge y {y0:.1f}..{y1:.1f}, ligament z {zlig(y0)-Z0:.1f}..{zlig(y1)-Z0:.1f}, muscle top z {zt-Z0:.1f}; cover {COVER} mm')

# ---------------------------------------------------------------- vestibular folds (52 R, 53 L) and vestibular ligaments (54 R, 55 L)
def thy_inner_point(y, z, lat):
    """point on the inner surface of the thyroid at (y, z): the most medial thyroid vertex in a 1 mm band on this side"""
    v = thy.vertices; s = v[(np.abs(v[:, 1] - y) < 0.8) & (np.abs(v[:, 2] - z) < 0.8) & (lat * (v[:, 0] - CX) > 0)]
    if len(s) == 0: return None
    return s[np.argmin(lat * s[:, 0])]
if 'false' in which:
    for lat, pid, pidl in ((-1, 52, 54), (1, 53, 55)):
        thy_half = thy.slice_plane([CX, 0, 0], [lat, 0, 0], cap=True); thy_inner = side_lookup(thy_half, 0, -lat)      # most medial x of this lamina per (y, z)
        xedge, zlig, y0, y1 = medial_edge(lat); ary = ARY[lat]; av = ary.vertices
        OFF = E('FF_OFF', '2.4'); ZLO = E('FF_ZLO', '5.6'); ZHI = E('FF_ZHI', '10.2')      # false-fold medial edge: OFF mm lateral of the true fold edge; underside at z0+ZLO, top at z0+ZHI
        zc = 0.5 * (ZLO + ZHI); rz = 0.5 * (ZHI - ZLO)
        # fold length: from the thyroid angle (0.8 mm into the inner surface) to the anterolateral arytenoid above the vocal process
        yA = y0 - 1.5; yP = y1 + 1.0
        zP = zlig(y1) + zc
        ap = av[(av[:, 1] < -91) & (av[:, 2] > zP - 2) & (av[:, 2] < zP + 2)]
        ins = ap[np.argmin(ap[:, 1])] if len(ap) else np.array([xedge(y1) + lat * (OFF + 1.5), y1 + 2.0, zP])
        bundles = []
        for off, zoff, r in ((OFF + 1.9, zc, 1.9), (OFF + 3.6, zc - 0.2, 2.2), (OFF + 5.6, zc - 0.4, 2.4), (OFF + 7.4, zc - 0.5, 2.3)):
            pts = []
            for y in np.linspace(yA, yP, 14):
                yc = np.clip(y, y0, y1); pts.append([xedge(yc) + lat * off, y, zlig(yc) + zoff])
            pts = np.array(pts)
            # anterior end into the thyroid inner surface, posterior end toward the arytenoid insertion
            tp = thy_inner_point(pts[0, 1], pts[0, 2], lat)
            if tp is not None and lat * (tp[0] - CX) < lat * (pts[0, 0] - CX) + 0.5: pts[0, 0] = tp[0] + lat * 0.3   # do not start lateral of the lamina
            pts[-1] = ins + (pts[-1] - ins) * 0.15 + np.array([0, 0, 0])
            bundles.append((pts, r, r, 'const', 1.0))
        phi, a, b = build_body(grid, bundles, k=0.5)
        # nothing medial of the fold's intended free edge (keeps the vestibule open)
        xs, ys, zs = box_points(a, b); Gy = np.clip(ys, y0, y1)
        edge = np.array([xedge(y) + lat * OFF for y in Gy])
        X = xs[:, None, None]; medial = lat * (X - edge[None, :, None]) < 0
        phi = np.where(medial, np.maximum(phi, 0.01), phi).astype(np.float32)
        # nothing lateral of the thyroid's inner surface (the fold ends on the lamina)
        G = np.stack(np.meshgrid(xs, ys, zs, indexing='ij'), -1).reshape(-1, 3)
        xin = thy_inner(G); outside = np.isfinite(xin) & (-lat * G[:, 0] < xin + 0.3)      # xin is max(-lat*x): the lamina inner surface
        phi = np.where(outside.reshape(phi.shape), np.maximum(phi, 0.01), phi).astype(np.float32)
        phi = ndimage.gaussian_filter(phi, 0.3 / P, mode='nearest')
        write_part(grid, B, pid, phi, a, b, f'Vestibular fold {"R" if lat < 0 else "L"}')
        # vestibular ligament: a cord along the lower part of the fold, from the thyroid angle to the arytenoid
        pts = np.array([[xedge(np.clip(y, y0, y1)) + lat * (OFF + 1.3), y, zlig(np.clip(y, y0, y1)) + ZLO + 0.9] for y in np.linspace(yA - 0.3, yP + 0.5, 14)])
        tp = thy_inner_point(pts[0, 1], pts[0, 2], lat)
        if tp is not None: pts[0] = tp + np.array([lat * (-0.5), 0.3, 0])
        pts[-1] = ins + (pts[-1] - ins) * 0.05
        phi, a, b = build_body(grid, [(pts, 0.55, 0.55, 'const', 1.0)], k=0.2)
        write_part(grid, B, pidl, phi, a, b, f'Vestibular ligament {"R" if lat < 0 else "L"}')
        print(f'     false fold edge {OFF} mm lateral of the true fold edge, z0+{ZLO}..+{ZHI}; from y {yA:.1f} (thyroid) to the arytenoid at {np.round(ins-[0,0,Z0],1)}')

# ---------------------------------------------------------------- aryepiglottic line, quadrangular membrane (56/57), aryepiglottic fold (58/59)
def ae_line(lat, n=16):
    """centreline of the source aryepiglotticus strip from the arytenoid apex to the epiglottis margin (sorted by height)"""
    v = AE[lat].vertices; order = np.argsort(v[:, 2]); vs = v[order]
    zs_ = np.linspace(vs[:, 2].min(), vs[:, 2].max(), n); pts = []
    for z in zs_:
        s = vs[np.abs(vs[:, 2] - z) < 1.0]
        pts.append(s.mean(0) if len(s) else pts[-1])
    pts = np.array(pts)
    apex = ARY[lat].vertices[np.argmax(ARY[lat].vertices[:, 2])]
    ev = epi.vertices; em = ev[(lat * (ev[:, 0] - CX) > 4) & (ev[:, 2] > pts[-1, 2] - 3) & (ev[:, 2] < pts[-1, 2] + 3)]
    etop = em[np.argmax(lat * (em[:, 0] - CX))] if len(em) else pts[-1]
    return np.vstack([apex, pts, etop])
if 'quad' in which:
    import shapely
    for lat, pid in ((-1, 56), (1, 57)):
        xedge, zlig, y0, y1 = medial_edge(lat)
        OFF = E('FF_OFF', '2.4'); ZLO = E('FF_ZLO', '5.6')
        lower = np.array([[xedge(np.clip(y, y0, y1)) + lat * (OFF + 1.3), y, zlig(np.clip(y, y0, y1)) + ZLO + 0.9] for y in np.linspace(y0 - 1.5, y1 + 1.0, 16)])   # the vestibular ligament line
        upper = ae_line(lat, 16); upper = upper[::-1]                     # epiglottis (anterior) -> apex (posterior), same direction as lower (anterior -> posterior)
        # ruled surface mesh between the two edges
        n = 16; V = []; F = []
        for i in range(n):
            s = i / (n - 1)
            lo_ = lower[int(round(s * (len(lower) - 1)))]; up_ = upper[int(round(s * (len(upper) - 1)))]
            for j in range(8):
                u = j / 7; V.append(lo_ + (up_ - lo_) * u)
        V = np.array(V)
        for i in range(n - 1):
            for j in range(7):
                k = i * 8 + j; F += [[k, k + 1, k + 8], [k + 1, k + 9, k + 8]]
        sheet = trimesh.Trimesh(V, np.array(F), process=False)
        TH = E('QM_T', '0.6')
        lo_mm = V.min(0) - TH - 1; hi_mm = V.max(0) + TH + 1
        a, b = grid.box(lo_mm, hi_mm, margin=0.3); xs, ys, zs = box_points(a, b)
        G = np.stack(np.meshgrid(xs, ys, zs, indexing='ij'), -1).reshape(-1, 3)
        d2, _, _ = igl.point_mesh_squared_distance(G, np.ascontiguousarray(V, np.float64), np.ascontiguousarray(sheet.faces, np.int64))
        phi = (np.sqrt(d2) - TH / 2).reshape(len(xs), len(ys), len(zs)).astype(np.float32)
        write_part(grid, B, pid, phi, a, b, f'Quadrangular membrane {"R" if lat < 0 else "L"}')
        print(f'     from the vestibular ligament line up to the aryepiglottic line (apex {np.round(upper[-1]-[0,0,Z0],1)} .. epiglottis margin {np.round(upper[0]-[0,0,Z0],1)}), {TH} mm')
if 'ae' in which:
    for lat, pid in ((-1, 58), (1, 59)):
        line = ae_line(lat, 18)
        R = E('AE_R', '1.4')
        bundles = [(line, R, R, 'const', 1.0)]
        # cuneiform tubercle: a bulge over the upper end of the cuneiform cartilage; corniculate tubercle over the corniculate
        cu = CU[lat].vertices; ctop = cu[np.argmax(cu[:, 2])]; cc = CORN[lat].vertices.mean(0)
        bundles.append((np.array([ctop + [0, 0.6, -1.0], ctop + [0, 0.8, 1.0]]), E('CUN_R', '2.0'), E('CUN_R', '2.0'), 'const', 1.0))
        bundles.append((np.array([cc + [0, 0.6, -0.8], cc + [0, 0.8, 0.8]]), E('CORN_R', '1.7'), E('CORN_R', '1.7'), 'const', 1.0))
        phi, a, b = build_body(grid, bundles, k=0.4)
        write_part(grid, B, pid, phi, a, b, f'Aryepiglottic fold {"R" if lat < 0 else "L"}')
        print(f'     fold {2*R:.1f} mm thick from the apex {np.round(line[0]-[0,0,Z0],1)} to the epiglottis {np.round(line[-1]-[0,0,Z0],1)}; cuneiform tubercle at {np.round(ctop-[0,0,Z0],1)}, corniculate at {np.round(cc-[0,0,Z0],1)}')
# ---------------------------------------------------------------- epiglottic tubercle (60)
if 'tub' in which:
    ev = epi.vertices
    zt = VL[-1].vertices[:, 2].mean() + E('ET_Z', '9.0')
    band = ev[(np.abs(ev[:, 0] - CX) < 1.5) & (np.abs(ev[:, 2] - zt) < 1.0)]
    back = band[np.argmax(band[:, 1])]                                     # laryngeal (posterior) face of the petiole at the midline
    c = back + np.array([0, -0.6, 0])
    ax_, ay_, az_ = E('ET_W', '4.0'), E('ET_D', '2.2'), E('ET_H', '3.5')
    lo_mm = c - [ax_ + 1, ay_ + 1, az_ + 1]; hi_mm = c + [ax_ + 1, ay_ + 1, az_ + 1]
    a, b = grid.box(lo_mm, hi_mm, margin=0.3); xs, ys, zs = box_points(a, b)
    X, Y, Zg = np.meshgrid(xs, ys, zs, indexing='ij')
    q = np.sqrt(((X - c[0]) / ax_) ** 2 + ((Y - c[1]) / ay_) ** 2 + ((Zg - c[2]) / az_) ** 2)
    phi = ((q - 1.0) * min(ax_, ay_, az_)).astype(np.float32)
    write_part(grid, B, 60, phi, a, b, 'Epiglottic tubercle')
    print(f'     on the laryngeal face of the epiglottis at {np.round(back-[0,0,Z0],1)}, {2*ax_} wide x {2*az_} tall, protruding {ay_-0.6:.1f} mm')
# ---------------------------------------------------------------- interarytenoid mucosa (61): a layer on the front of the transverse arytenoid between the arytenoid bodies
if 'ia' in which:
    front = side_lookup(tra, 1, -1)                                        # most anterior y of the transverse arytenoid per (x, z)
    T = E('IA_T', '1.2')
    lo_mm = np.array([tra.bounds[0, 0], tra.bounds[0, 1] - T - 1, tra.bounds[0, 2]]); hi_mm = np.array([tra.bounds[1, 0], tra.bounds[1, 1], tra.bounds[1, 2]])
    a, b = grid.box(lo_mm, hi_mm, margin=0.3); xs, ys, zs = box_points(a, b)
    G = np.stack(np.meshgrid(xs, ys, zs, indexing='ij'), -1).reshape(-1, 3)
    yf = -front(G)                                                         # front face y
    occ = np.isfinite(yf) & (G[:, 1] < yf) & (G[:, 1] >= yf - T) & (np.abs(G[:, 0] - CX) < E('IA_HALFW', '4.5'))
    occ = occ.reshape(len(xs), len(ys), len(zs))
    write(61, occ, a, b, 'Interarytenoid mucosa', smooth=0.2)
