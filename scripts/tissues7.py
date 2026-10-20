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
which = sys.argv[1:] or ['cover', 'false', 'quad', 'ae', 'tub', 'ia', 'vest', 'plug']
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
def medial_edge(lat, mesh=None):
    """x of the medial edge of a mesh (default: the vocal ligament) as a function of y (lookup), and its mean z"""
    vl = VL[lat] if mesh is None else mesh; v = vl.vertices
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
        zl = zlig(np.clip(G[:, 1], y0, y1))
        near &= (G[:, 1] >= y0 - 1.0) & (G[:, 1] <= y1 + 1.5) & (G[:, 2] >= zl - E('COVER_DOWN', '6.0')) & (G[:, 2] <= zl + E('COVER_TOP', '3.0'))   # top cap: nothing above the ventricle floor
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
def fold_ref(lat):
    """the free edge of the covered true fold: x(y) of the medial edge of the cover part, with the ligament's z(y)"""
    cov = L(50 if lat < 0 else 51)
    xc, _, yc0, yc1 = medial_edge(lat, cov); xl, zlig, y0, y1 = medial_edge(lat)
    return xc, zlig, y0, y1
def ary_insertion(lat, z):
    """anterolateral face of the arytenoid at height z: the most anterior arytenoid vertex on the lateral half, within 2 mm of z"""
    av = ARY[lat].vertices; s_ = av[(np.abs(av[:, 2] - z) < 2.0) & (lat * (av[:, 0] - CX) > 2.0)]
    if len(s_) == 0: s_ = av[np.abs(av[:, 2] - z) < 2.0]
    return s_[np.argmin(s_[:, 1])]
def lig_line(lat, n=14):
    """centreline of the vestibular ligament: inside the false fold, LIG_OFF lateral of the covered true-fold edge, LIG_Z above the ligament level, thyroid angle -> anterolateral arytenoid"""
    xedge, zlig, y0, y1 = fold_ref(lat); OFF = E('FF_OFF', '2.4'); ZLO = E('FF_ZLO', '5.6')
    yA = y0 - 1.5; ins = ary_insertion(lat, zlig(y1) + ZLO + E('LIG_Z', '1.8'))
    pts = np.array([[xedge(np.clip(y, y0, y1)) + lat * (OFF + E('LIG_OFF', '2.2')), y, zlig(np.clip(y, y0, y1)) + ZLO + E('LIG_Z', '1.8')] for y in np.linspace(yA - 0.3, ins[1], n)])
    tp = thy_inner_point(pts[0, 1], pts[0, 2], lat)
    if tp is not None: pts[0] = tp + np.array([lat * (-0.5), 0.3, 0])
    pts[-1] = ins + np.array([lat * 0.3, -0.3, 0])                 # just in front of the arytenoid face (the cord ends in it after the CSG)
    return pts, ins
if 'false' in which:
    for lat, pid, pidl, pidw in ((-1, 52, 54, 62), (1, 53, 55, 63)):
        thy_half = thy.slice_plane([CX, 0, 0], [lat, 0, 0], cap=True); thy_inner = side_lookup(thy_half, 0, -lat)      # most medial x of this lamina per (y, z)
        xedge, zlig, y0, y1 = fold_ref(lat)
        OFF = E('FF_OFF', '2.4'); ZLO = E('FF_ZLO', '5.6'); ZHI = E('FF_ZHI', '10.2')      # false-fold free edge: OFF mm lateral of the covered true-fold edge; underside at z0+ZLO, top at z0+ZHI
        zc = 0.5 * (ZLO + ZHI); rz = 0.5 * (ZHI - ZLO)
        yA = y0 - 1.5; ins = ary_insertion(lat, zlig(y1) + zc); yP = ins[1]
        bundles = []
        r1 = 2.0
        for off, zoff, r in ((OFF + r1, zc, r1), (OFF + 3.8, zc - 0.2, 2.2), (OFF + 5.8, zc - 0.4, 2.4), (OFF + 7.6, zc - 0.5, 2.3)):
            pts = []
            for y in np.linspace(yA, yP, 14):
                yc = np.clip(y, y0, y1); pts.append([xedge(yc) + lat * off, y, zlig(yc) + zoff])
            pts = np.array(pts)
            tp = thy_inner_point(pts[0, 1], pts[0, 2], lat)
            if tp is not None and lat * (tp[0] - CX) < lat * (pts[0, 0] - CX) + 0.5: pts[0, 0] = tp[0] + lat * 0.3   # do not start lateral of the lamina
            pts[-1] = ins + (pts[-1] - ins) * 0.1 + np.array([lat * 0.5, 0, 0])                                        # onto the anterolateral arytenoid
            bundles.append((pts, r, r, 'const', 1.0))
        phi, a, b = build_body(grid, bundles, k=0.5)
        xs, ys, zs = box_points(a, b)
        # nothing lateral of the thyroid's inner surface (the fold ends on the lamina)
        G = np.stack(np.meshgrid(xs, ys, zs, indexing='ij'), -1).reshape(-1, 3)
        xin = thy_inner(G); outside = np.isfinite(xin) & (-lat * G[:, 0] < xin + 0.3)      # xin is max(-lat*x): the lamina inner surface
        phi = np.where(outside.reshape(phi.shape), np.maximum(phi, 0.01), phi).astype(np.float32)
        phi = ndimage.gaussian_filter(phi, 0.3 / P, mode='nearest')
        write_part(grid, B, pid, phi, a, b, f'Vestibular fold {"R" if lat < 0 else "L"}')
        # vestibular ligament: a cord inside the lower part of the fold, from the thyroid angle to the arytenoid
        pts, _ = lig_line(lat)
        phi, a, b = build_body(grid, [(pts, 0.55, 0.55, 'const', 1.0)], k=0.2)
        write_part(grid, B, pidl, phi, a, b, f'Vestibular ligament {"R" if lat < 0 else "L"}')
        print(f'     false fold edge {OFF} mm lateral of the covered true-fold edge, z0+{ZLO}..+{ZHI}; from y {yA:.1f} (thyroid) to the arytenoid at {np.round(ins-[0,0,Z0],1)}')
        # ventricle lateral wall: mucosa closing the paraglottic slot between the fold cover (floor) and the false fold (roof),
        # VENT_D lateral of the covered true-fold edge at the roof, sloping laterally toward the floor (VENT_SLOPE mm per mm)
        VD = E('VENT_D', '4.5'); VS = E('VENT_SLOPE', '0.5'); zfloor = E('VENT_FLOOR', '0.0'); zroof = ZLO + 1.5
        lo_mm = np.array([min(xedge(np.clip(y, y0, y1)) for y in ys) if lat < 0 else CX, yA, zlig(y0) + zfloor - 1]); hi_mm = np.array([CX if lat < 0 else max(xedge(np.clip(y, y0, y1)) for y in ys), yP + 1, zlig(y1) + zroof + 1])
        lo_mm[0] = thy.bounds[0, 0] if lat < 0 else lo_mm[0]; hi_mm[0] = thy.bounds[1, 0] if lat > 0 else hi_mm[0]
        a, b = grid.box(lo_mm, hi_mm, margin=0.3); xs, ys, zs = box_points(a, b)
        G = np.stack(np.meshgrid(xs, ys, zs, indexing='ij'), -1).reshape(-1, 3)
        yc = np.clip(G[:, 1], y0, y1); ex = xedge(yc); zl = zlig(yc)
        xmed = ex + lat * (VD + np.maximum(0.0, (zl + ZLO) - G[:, 2]) * VS)                 # medial face of the wall at this height
        xin = thy_inner(G); xlam = -lat * xin                                                 # inner surface of the lamina at (y, z)
        lim = xlam - lat * E('VENT_MIN_T', '1.5')                                             # the wall is at least this thick against the lamina
        xmed = np.where(np.isfinite(xlam), CX + lat * np.minimum(lat * (xmed - CX), lat * (lim - CX)), xmed)
        occ = (lat * (G[:, 0] - xmed) >= 0) & (lat * (G[:, 0] - ex) >= 1.0) & (G[:, 2] >= zl + zfloor) & (G[:, 2] <= zl + zroof) & (G[:, 1] >= yA) & (G[:, 1] <= yP)   # never within 1 mm of the fold edge
        occ &= ~(np.isfinite(xin) & (-lat * G[:, 0] < xin - 0.3))                           # 0.3 mm into the lamina: no seam against it
        VT = E('VENT_T', '0.8')                                                              # v6: the wall is a mucosal lining only; the paraglottic space lateral of it is left for the fat fill
        if VT > 0:
            lining = lat * (G[:, 0] - xmed) < VT
            # keep the lining joined to the lamina at its ends (front and back 1 mm) and along the roof and floor (0.5 mm) so the paraglottic pocket is closed on all sides
            rim = (G[:, 1] < yA + 1.0) | (G[:, 1] > yP - 1.0) | (G[:, 2] < zl + zfloor + 0.5) | (G[:, 2] > zl + zroof - 0.5)
            occ &= (lining | rim)
        occ = occ.reshape(len(xs), len(ys), len(zs))
        write(pidw, occ, a, b, f'Ventricle lateral wall {"R" if lat < 0 else "L"}', smooth=0.3)
        print(f'     ventricle wall {VD} mm lateral of the fold edge at the roof, slope {VS}, floor z0+{zfloor} to roof z0+{zroof}' + (f'; lining {VT} mm, paraglottic pocket left for fat' if VT > 0 else ''))

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
        lower, _ = lig_line(lat, 16)                                      # the vestibular ligament line
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
        # the membrane attaches along the epiglottis's lateral margin: nothing medial of the margin (minus QM_EMB) at the epiglottis's levels
        ev = epi.vertices; zb = np.arange(ev[:, 2].min(), ev[:, 2].max() + 0.5, 0.5); wz = []
        for z_ in zb:
            sl = ev[np.abs(ev[:, 2] - z_) < 0.6]; wz.append((lat * (sl[:, 0] - CX)).max() if len(sl) else np.nan)
        wz = np.array(wz); ok = np.isfinite(wz); wz = np.interp(zb, zb[ok], wz[ok])
        Gz = np.clip(G[:, 2], zb[0], zb[-1]); wmar = np.interp(Gz, zb, wz)
        medial_of_margin = (G[:, 2] >= ev[:, 2].min() + 0.5) & (lat * (G[:, 0] - CX) < wmar - E('QM_EMB', '1.0'))
        phi = np.where(medial_of_margin.reshape(phi.shape), np.maximum(phi, 0.01), phi).astype(np.float32)
        write_part(grid, B, pid, phi, a, b, f'Quadrangular membrane {"R" if lat < 0 else "L"}')
        # the thyro-epiglottic muscle lies lateral to the membrane: trim its voxels medial of the sheet
        tpid = 48 if lat < 0 else 49; src = f'{B}/srcTE_{tpid:02d}.npz'
        if not os.path.exists(src): os.rename(f'{B}/occ_{tpid:02d}.npz', src)
        dd = np.load(src); to, ta, tb = dd['occ'], dd['a'], dd['b']
        txs, tys, tzs = box_points(ta, tb); TG = np.stack(np.meshgrid(txs, tys, tzs, indexing='ij'), -1).reshape(-1, 3)
        xsheet = side_lookup(sheet, 0, lat, binw=0.3)(TG)                   # x of the sheet per (y, z); NaN beyond its edges
        medial = np.isfinite(xsheet) & (lat * TG[:, 0] - xsheet < TH / 2 + 0.05)  # xsheet is lat*x of the sheet; the muscle starts at the sheet's lateral face
        # below the membrane's lower edge (inside the false fold) trim to the lateral side of the vestibular ligament line
        oy = np.argsort(lower[:, 1]); xl = np.interp(TG[:, 1], lower[oy, 1], lower[oy, 0])
        below = ~np.isfinite(xsheet) & (TG[:, 1] >= lower[:, 1].min() - 0.5) & (TG[:, 1] <= lower[:, 1].max() + 0.5) & (TG[:, 2] < lower[:, 2].max() + 1.0)
        medial |= below & (lat * (TG[:, 0] - xl) < 0.0)
        to2 = to & ~medial.reshape(to.shape)
        lab, n = ndimage.label(to2)
        if n > 1:
            sizes = np.bincount(lab.ravel()); sizes[0] = 0; to2 = lab == sizes.argmax()
        tphi = ndimage.gaussian_filter(occ_to_phi(to2), 0.2 / P, mode='nearest')
        write_part(grid, B, tpid, tphi, ta, tb, f'Thyro-epiglottic part {"R" if lat < 0 else "L"} (trimmed lateral of the membrane)')
        print(f'     thyro-epiglottic muscle trimmed: {to.sum()*P**3:.0f} -> {to2.sum()*P**3:.0f} mm3')
        print(f'     from the vestibular ligament line up to the aryepiglottic line (apex {np.round(upper[-1]-[0,0,Z0],1)} .. epiglottis margin {np.round(upper[0]-[0,0,Z0],1)}), {TH} mm')
if 'ae' in which:
    for lat, pid in ((-1, 58), (1, 59)):
        line = ae_line(lat, 18)
        R = E('AE_R', '2.2')
        bundles = [(line, R, R, 'const', 1.0)]
        # cuneiform tubercle: a bulge over the upper end of the cuneiform cartilage; corniculate tubercle over the corniculate
        cu = CU[lat].vertices; ctop = cu[np.argmax(cu[:, 2])]; cc = CORN[lat].vertices.mean(0)
        bundles.append((np.array([ctop + [0, 0.6, -1.0], ctop + [0, 0.8, 1.0]]), E('CUN_R', '2.7'), E('CUN_R', '2.7'), 'const', 1.0))
        bundles.append((np.array([cc + [0, 0.6, -0.8], cc + [0, 0.8, 0.8]]), E('CORN_R', '2.4'), E('CORN_R', '2.4'), 'const', 1.0))
        phi, a, b = build_body(grid, bundles, k=0.4)
        write_part(grid, B, pid, phi, a, b, f'Aryepiglottic fold {"R" if lat < 0 else "L"}')
        print(f'     fold {2*R:.1f} mm thick from the apex {np.round(line[0]-[0,0,Z0],1)} to the epiglottis {np.round(line[-1]-[0,0,Z0],1)}; cuneiform tubercle at {np.round(ctop-[0,0,Z0],1)}, corniculate at {np.round(cc-[0,0,Z0],1)}')
# ---------------------------------------------------------------- epiglottic tubercle (60)
if 'tub' in which:
    back = side_lookup(epi, 1, 1, binw=0.3)                                 # most posterior y of the epiglottis per (x, z): its laryngeal face
    zt = max(VL[-1].vertices[:, 2].mean() + E('ET_Z', '10.5'), epi.vertices[:, 2].min() + 1.5)   # on the lower petiole, at false-fold level
    yb = back(np.array([[CX, 0.0, zt]]))[0]
    if not np.isfinite(yb): yb = back(np.array([[CX, 0.0, epi.vertices[:, 2].min() + 2.5]]))[0]
    c = np.array([CX, yb - 0.3, zt])
    ax_, ay_, az_ = E('ET_W', '4.0'), E('ET_D', '2.5'), E('ET_H', '3.5')
    lo_mm = c - [ax_ + 1, ay_ + 1, az_ + 1]; hi_mm = c + [ax_ + 1, ay_ + 1, az_ + 1]
    a, b = grid.box(lo_mm, hi_mm, margin=0.3); xs, ys, zs = box_points(a, b)
    X, Y, Zg = np.meshgrid(xs, ys, zs, indexing='ij')
    q = np.sqrt(((X - c[0]) / ax_) ** 2 + ((Y - c[1]) / ay_) ** 2 + ((Zg - c[2]) / az_) ** 2)
    phi = ((q - 1.0) * min(ax_, ay_, az_)).astype(np.float32)
    G = np.stack([X.ravel(), Y.ravel(), Zg.ravel()], 1); yface = back(G)
    front = np.isfinite(yface) & (G[:, 1] < yface - 0.3)                     # nothing in front of the laryngeal face (lingual side)
    phi = np.where(front.reshape(phi.shape), np.maximum(phi, 0.01), phi).astype(np.float32)
    phi = ndimage.gaussian_filter(phi, 0.2 / P, mode='nearest')
    write_part(grid, B, 60, phi, a, b, 'Epiglottic tubercle')
    print(f'     half-ellipsoid on the laryngeal face of the petiole at {np.round(c-[0,0,Z0],1)}, {2*ax_} wide x {2*az_} tall, protruding {ay_-0.3:.1f} mm')
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

# ---------------------------------------------------------------- vestibular mucosa (64 R, 65 L): MUC_T lining on the airway side of the quadrangular membrane and the arytenoid above the vocal process
if 'vest' in which:
    for lat, pid in ((-1, 64), (1, 65)):
        qm = L(56 if lat < 0 else 57); xedge, zlig, y0, y1 = medial_edge(lat)
        core = trimesh.util.concatenate([qm, ARY[lat], CORN[lat]])
        T = E('MUC_T', '0.8')
        ZMIN = zlig(y1) + E('MUC_ZMIN', '2.0')                                               # above the vocal-process level (the fold cover owns the glottis)
        lo_mm = core.bounds[0] - T - 1; hi_mm = core.bounds[1] + T + 1; lo_mm[2] = max(lo_mm[2], ZMIN - 0.5)
        a, b = grid.box(lo_mm, hi_mm, margin=0.3); xs, ys, zs = box_points(a, b)
        G = np.stack(np.meshgrid(xs, ys, zs, indexing='ij'), -1).reshape(-1, 3)
        Vc = np.ascontiguousarray(core.vertices, np.float64); Fc = np.ascontiguousarray(core.faces, np.int64)
        d2, _, _ = igl.point_mesh_squared_distance(G, Vc, Fc); dist = np.sqrt(d2)
        inside = igl.fast_winding_number(Vc, Fc, np.ascontiguousarray(G)) > 0.5
        near = (dist <= T + 0.05) & ~inside & (G[:, 2] >= ZMIN) & (lat * (G[:, 0] - CX) > -0.5)
        cand = np.nonzero(near)[0]; Gc = G[cand]
        axis = np.array([CX, E('AXIS_Y', '-101.0')])
        K = 14; ts = (np.arange(1, K + 1) / (K + 1))[None, :, None]
        seg = Gc[:, None, :].repeat(K, 1); seg[:, :, 0] = Gc[:, None, 0] + (axis[0] - Gc[:, None, 0]) * ts[:, :, 0]; seg[:, :, 1] = Gc[:, None, 1] + (axis[1] - Gc[:, None, 1]) * ts[:, :, 0]
        segf = np.ascontiguousarray(seg.reshape(-1, 3))
        blocked = igl.fast_winding_number(Vc, Fc, segf) > 0.5
        for blk in (thy, epi):
            blocked |= igl.fast_winding_number(np.ascontiguousarray(blk.vertices, np.float64), np.ascontiguousarray(blk.faces, np.int64), segf) > 0.5
        blocked = blocked.reshape(len(cand), K).any(1)
        near[cand[blocked]] = False
        occ = near.reshape(len(xs), len(ys), len(zs))
        lab, n = ndimage.label(occ)
        if n > 1:
            sizes = np.bincount(lab.ravel()); sizes[0] = 0; occ = lab == sizes.argmax()
        write(pid, occ, a, b, f'Vestibular mucosa {"R" if lat < 0 else "L"}', smooth=0.2)

# ---------------------------------------------------------------- anterior vestibule wall (66): fills the slot at the thyroid angle between the ventricle walls / false folds,
# the thyro-epiglottic ligament and the laryngeal face of the petiole, so the vestibule does not open into the pre-epiglottic space
if 'plug' in which:
    back = side_lookup(epi, 1, 1, binw=0.3)
    xl_, zlig, y0, y1 = medial_edge(-1); zb = zlig(y0)
    lo_mm = np.array([CX - E('PLUG_HW', '5.0'), E('PLUG_YMIN', '-118.5'), zb + E('PLUG_Z0', '3.7')]); hi_mm = np.array([CX + E('PLUG_HW', '5.0'), E('PLUG_YMAX', '-109.0'), zb + E('PLUG_Z1', '12.2')])
    a, b = grid.box(lo_mm, hi_mm, margin=0.3); xs, ys, zs = box_points(a, b)
    G = np.stack(np.meshgrid(xs, ys, zs, indexing='ij'), -1).reshape(-1, 3)
    yface = back(G)
    occ = (G[:, 0] >= lo_mm[0]) & (G[:, 0] <= hi_mm[0]) & (G[:, 1] >= lo_mm[1]) & (G[:, 1] <= hi_mm[1]) & (G[:, 2] >= lo_mm[2]) & (G[:, 2] <= hi_mm[2])
    occ &= ~(np.isfinite(yface) & (G[:, 1] > yface - 0.3))                  # nothing behind the laryngeal face of the epiglottis
    occ &= ~((np.abs(G[:, 0] - CX) > E('PLUG_HW2', '2.0')) & (G[:, 1] < E('PLUG_Y2', '-113.0')))   # no slivers beside the thyroid notch
    occ = occ.reshape(len(xs), len(ys), len(zs))
    write(66, occ, a, b, 'Anterior vestibule wall', smooth=0.2)
    print(f'     plug x {lo_mm[0]:.1f}..{hi_mm[0]:.1f}, y {lo_mm[1]:.1f}..{hi_mm[1]:.1f}, z {lo_mm[2]-Z0:.1f}..{hi_mm[2]-Z0:.1f}, bounded behind by the epiglottis face')
