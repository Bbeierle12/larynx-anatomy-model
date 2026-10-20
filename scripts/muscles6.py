"""Stage 2: intrinsic muscles constructed as fibre bundles between attachment footprints on the v3 cartilages.
Run after deform (parts 1-39 in BUILD).  Writes occ/part for 40-47 (and rebuilds 24-27, 29, 30), then grid.npy."""
import sys, os, numpy as np, trimesh, igl
sys.path.insert(0, os.path.dirname(__file__))
from musclelib import *
B = os.environ['BUILD']; E = lambda k, d: float(os.environ.get(k, d))
grid = Grid(f'{B}/grid.npy'); Z0 = grid.z_cut; CX = -0.65
L = lambda i: trimesh.load(f'{B}/part_{i:02d}.ply', process=False)
thy, cri, aR, aL, pdR, pdL = L(2), L(3), L(4), L(5), L(38), L(39)
vlR, vlL, coR, coL = L(12), L(13), L(14), L(15)
which = sys.argv[1:] or ['pca', 'lca', 'ct', 'ta', 'ia', 'te', 'grid']
# airway exclusion: the enclosed lumen (flood fill inside cartilage + conus + ligaments + transverse arytenoid), dilated 0.3 mm
if os.environ.get('NO_LUMEN') != '1':
    _M, _a, _b, _areas, _ok = enclosed_lumen(grid, B, [2, 3, 4, 5, 38, 39, 12, 13, 14, 15, 16, 28], Z0 + 20, Z0 + 56, dilate=E('LUMEN_DILATE', '0.2'))
    LUMEN = (_M, _a, _b); print(f'airway exclusion: {_ok.sum()}/{len(_ok)} slices sealed, the rest take the nearest sealed slice', flush=True)
else: LUMEN = None
sd = {m: mesh_sdf_fn(m, sign=False) for m in ()}
def near_mesh(mesh, tol):
    f = mesh_sdf_fn(mesh, sign=False); return lambda p: f(p) < tol
ARY = {-1: aR, 1: aL}; PAD = {-1: pdR, 1: pdL}; CONUS = {-1: coR, 1: coL}; VL = {-1: vlR, 1: vlL}
def base_z(lat): return ARY[lat].bounds[0, 2]
# ------------------------------------------------------------------ posterior cricoarytenoid (40 R, 41 L)
if 'pca' in which:
    for pid, lat in ((40, -1), (41, 1)):
        zb = cri.bounds[0, 2]
        npad = near_mesh(PAD[lat], 1.2)
        o_pts, o_n = surface_points(cri, lambda p, n: (n[:, 1] > 0.55) & (lat * (p[:, 0] - CX) > E('PCA_MED', '3.2')) & (lat * (p[:, 0] - CX) < E('PCA_LAT', '9.5') - E('PCA_TAPER', '0.3') * np.maximum(p[:, 2] - zb - 4.0, 0)) & (p[:, 1] > -94.0)
                                    & (p[:, 2] > zb + E('PCA_LOW', '4.0')) & (p[:, 2] < Z0 + E('PCA_TOP', '40.5')) & ~npad(p), n=80000)
        a = ARY[lat]; bz = base_z(lat)
        i_pts, i_n = surface_points(a, lambda p, n: (p[:, 2] < bz + E('PCA_IZ', '3.0')) & (lat * (p[:, 0] - CX) > E('PCA_IX', '7.5')) & (p[:, 1] > -90.0) & (n[:, 1] > -0.3), n=40000)
        mp = i_pts.mean(0); drape_c = draper(cri); drape_p = draper(PAD[lat])
        # 2-D spread of origins: grid over (medial distance, height); pair with insertions by fibre angle
        med = -lat * (o_pts[:, 0] - mp[0]); hgt = o_pts[:, 2] - mp[2]
        ang_o = np.degrees(np.arctan2(-hgt, np.maximum(med, 0.1)))          # 0 = horizontal (medial), 90 = vertical (below)
        K = int(E('PCA_K', '70'))
        rng = np.random.default_rng(1)
        # farthest-point sampling for an even spread over the footprint
        sel = [rng.integers(len(o_pts))]; dmin = np.linalg.norm(o_pts - o_pts[sel[0]], axis=1)
        for _ in range(K - 1):
            j = int(np.argmax(dmin)); sel.append(j); dmin = np.minimum(dmin, np.linalg.norm(o_pts - o_pts[j], axis=1))
        O = o_pts[sel]; On = o_n[sel]; Oang = ang_o[sel]
        ikey = lat * (i_pts[:, 0] - CX)                                  # medial insertion first
        I_sorted = i_pts[np.argsort(ikey)]
        order = np.argsort(Oang)
        bundles = []
        r0, rb, ri = E('PCA_R0', '0.75'), E('PCA_RB', '1.35'), E('PCA_RI', '0.45')
        for rank, j in enumerate(order):
            q = rank / max(len(order) - 1, 1)
            ins = I_sorted[int(q * (len(I_sorted) - 1))]
            A = O[j] - On[j] * 0.5                      # start 0.5 mm inside the cartilage
            # insertion end: 0.6 mm inside the arytenoid along the direction from the muscle
            d = ins - A; d /= np.linalg.norm(d); Bp = ins + d * 0.6
            # fibre drapes over the lamina: interior points pushed outside the cricoid (and the facet pad) by the local radius
            prof = (lambda s, r0=r0, rb=rb, ri=ri: np.where(s < 0.4, r0 + (rb - r0) * np.sin(np.pi * s / 0.8), ri + (rb - ri) * np.cos(np.pi * (s - 0.4) / 1.2)))   # belly at 40 % of the way, tapering to a tendon-like insertion
            pts = chain_points(A, Bp, 12); sv = np.linspace(0, 1, 13)
            rr = prof(sv) + E('PCA_CLEAR', '0.1'); rr[0] = -1.0; rr[-1] = -1.0          # ends stay embedded
            pts = drape_c(pts, rr); pts = drape_p(pts, rr)
            bundles.append((pts, r0, rb, prof, 1.0))
        # keep the muscle behind the lamina / outside the cartilage is handled by priority; clip against the lumen is not needed (posterior)
        phi, a_, b_ = build_body(grid, bundles, k=E('PCA_SMOOTH', '0.4'))
        m, vol = write_part(grid, B, pid, phi, a_, b_, f'Posterior cricoarytenoid {"R" if lat < 0 else "L"}', clip=LUMEN)
        bk = m.vertices[:, 1].max(); print(f'     origin footprint {len(o_pts)} pts x {lat*(O[:,0]-CX).min():.1f}..{lat*(O[:,0]-CX).max():.1f} z {O[:,2].min()-Z0:.1f}..{O[:,2].max()-Z0:.1f}; insertion centre {np.round(mp-[0,0,Z0],1)}; back face y {bk:.1f} (lamina ridge -84.1)')

def ang_about(p, cx=CX, cy=-97.0): return (np.degrees(np.arctan2(p[:, 1] - cy, p[:, 0] - cx)) + 360) % 360
def rim_z(mesh, nb=72):
    v = mesh.vertices; th = ang_about(v); bi = (th / (360 / nb)).astype(int) % nb
    zt = np.full(nb, -np.inf); np.maximum.at(zt, bi, v[:, 2]); return lambda p: zt[(ang_about(p) / (360 / nb)).astype(int) % nb]
def dir_push(mesh, direction):
    """push points that are inside `mesh` or within clearance of it along `direction` (unit vector or f(pts)->vectors) until clear"""
    f = mesh_sdf_fn(mesh, sign=True)
    def g(pts, clearance):
        pts = np.asarray(pts, float).copy(); cl = np.broadcast_to(np.asarray(clearance, float), (len(pts),))
        for _ in range(20):
            d = f(pts); bad = d < cl
            if not bad.any(): break
            dv = direction(pts[bad]) if callable(direction) else np.tile(np.asarray(direction, float), (bad.sum(), 1))
            pts[bad] += dv * np.maximum(cl[bad] - d[bad], 0.15)[:, None]
        return pts
    return g
def side_of(mesh, axis, sign, binw=0.5):
    """f(pts, clearance): push points along +sign*axis so they lie beyond the sheet `mesh` by >= clearance
    (lookup of the sheet's most extreme coordinate along the axis per bin of the other two coordinates)"""
    v, _ = trimesh.sample.sample_surface(mesh, 400000, seed=0); v = np.vstack([v, mesh.vertices])
    o = [i for i in range(3) if i != axis]
    lo0 = v[:, o].min(0) - 1; n = ((v[:, o].max(0) - lo0) / binw).astype(int) + 3
    X = np.full(tuple(n), -np.inf); ij = ((v[:, o] - lo0) / binw).astype(int)
    np.maximum.at(X, (ij[:, 0], ij[:, 1]), sign * v[:, axis])
    has = np.isfinite(X)
    from scipy import ndimage
    for _ in range(2):
        Xf = ndimage.maximum_filter(np.where(has, X, -np.inf), size=3); X = np.where(has, X, Xf); has = np.isfinite(X)
    def g(pts, clearance):
        pts = np.asarray(pts, float).copy(); cl = np.broadcast_to(np.asarray(clearance, float), (len(pts),))
        jj = ((pts[:, o] - lo0) / binw).astype(int)
        ok = (jj[:, 0] >= 0) & (jj[:, 0] < n[0]) & (jj[:, 1] >= 0) & (jj[:, 1] < n[1])
        xs = np.full(len(pts), -np.inf); xs[ok] = X[jj[ok, 0], jj[ok, 1]]
        need = np.isfinite(xs) & (cl > 0) & (sign * pts[:, axis] < xs + cl)
        pts[need, axis] = sign * (xs[need] + cl[need])
        return pts
    return g
def lateral_of(mesh, lat, binw=0.5): return side_of(mesh, 0, lat, binw)
def fps(pts, K, seed=1):
    rng = np.random.default_rng(seed); sel = [rng.integers(len(pts))]; dmin = np.linalg.norm(pts - pts[sel[0]], axis=1)
    for _ in range(K - 1):
        j = int(np.argmax(dmin)); sel.append(j); dmin = np.minimum(dmin, np.linalg.norm(pts - pts[j], axis=1))
    return np.array(sel)
# ------------------------------------------------------------------ lateral cricoarytenoid (42 R, 43 L)
if 'lca' in which:
    rz = rim_z(cri)
    for pid, lat in ((42, -1), (43, 1)):
        a = ARY[lat]; bz = base_z(lat)
        A0, A1 = E('LCA_A0', '190'), E('LCA_A1', '212')       # angular sector of the arch rim (0 = +x; 270 = anterior); mirrored for the left
        def sect(p):
            th = ang_about(p); th = th if lat < 0 else (540 - th) % 360
            return (th > A0) & (th < A1)
        # origin: the top of the arch's upper border (rim) in the sector
        o_pts, o_n = surface_points(cri, lambda p, n: sect(p) & (p[:, 2] > rz(p) - E('LCA_RIM', '1.2')) & (n[:, 2] > 0.45), n=120000)
        i_pts, i_n = surface_points(a, lambda p, n: (p[:, 2] < bz + E('LCA_IZ', '4.0')) & (lat * (p[:, 0] - CX) > E('LCA_IX', '6.0')) & (p[:, 1] > -95.0) & (p[:, 1] < -87.5) & ((n[:, 1] < -0.2) | (n[:, 2] < -0.3) | (lat * n[:, 0] > 0.5)), n=40000)
        K = int(E('LCA_K', '20')); sel = fps(o_pts, K)
        O, On = o_pts[sel], o_n[sel]
        okey = ang_about(O); okey = okey if lat < 0 else (540 - okey) % 360         # anterior origins (large angle) -> medial/inferior insertion
        ikey = -(lat * (i_pts[:, 0] - CX)) + 0.5 * (i_pts[:, 2] - bz)
        I_sorted = i_pts[np.argsort(ikey)]; order = np.argsort(-okey)
        drape_c = dir_push(cri, np.array([0, 0, 1.0]))      # out of the cricoid upward (never into the lumen)
        drape_thy = dir_push(thy, np.array([-lat * 1.0, 0, 0])); co = CONUS[lat]      # out of the lamina toward the midline
        push_co = lateral_of(co, lat)
        r0, rb, ri = E('LCA_R0', '0.6'), E('LCA_RB', '1.4'), E('LCA_RI', '0.6')
        bundles = []
        for rank, j in enumerate(order):
            q = rank / max(len(order) - 1, 1); ins = I_sorted[int(q * (len(I_sorted) - 1))]
            A = O[j] - On[j] * 0.5; d = ins - A; d /= np.linalg.norm(d); Bp = ins + d * 0.6
            prof = (lambda s, r0=r0, rb=rb, ri=ri: np.where(s < 0.5, r0 + (rb - r0) * np.sin(np.pi * s), ri + (rb - ri) * np.sin(np.pi * s)))
            # via point: stay low (just above the rim) until behind the conus, then rise to the muscular process
            V = np.array([0.5 * (A[0] + Bp[0]), E('LCA_YV', '-91.5'), A[2] + E('LCA_RISE', '1.5')])
            pts = np.vstack([chain_points(A, V, 7)[:-1], chain_points(V, Bp, 5)]); sv = np.linspace(0, 1, len(pts))
            rr = prof(sv) + 0.1; rr[0] = rr[-1] = -1.0
            pts = drape_c(pts, rr)
            for _ in range(3): pts = push_co(pts, rr); pts = drape_thy(pts, rr)
            pts[1:-1, 2] = np.maximum(pts[1:-1, 2], rz(pts[1:-1]) + rr[1:-1] * 0.9)   # never below the rim
            bundles.append((pts, r0, rb, prof, 1.0))
        phi, a_, b_ = build_body(grid, bundles, k=E('LCA_SMOOTH', '0.4'))
        m, vol = write_part(grid, B, pid, phi, a_, b_, f'Lateral cricoarytenoid {"R" if lat < 0 else "L"}', clip=LUMEN)
        print(f'     origin {len(o_pts)} pts: x {O[:,0].min():.1f}..{O[:,0].max():.1f} y {O[:,1].min():.1f}..{O[:,1].max():.1f} z {O[:,2].min()-Z0:.1f}..{O[:,2].max()-Z0:.1f}; insertion centre {np.round(i_pts.mean(0)-[0,0,Z0],1)} ({len(i_pts)} pts); fibre length {np.mean([np.sum(np.linalg.norm(np.diff(b[0],axis=0),axis=1)) for b in bundles]):.1f} mm')

# ------------------------------------------------------------------ cricothyroid: straight (44 R, 45 L) and oblique (46 R, 47 L) parts
if 'ct' in which:
    rz = rim_z(cri); zlow = cri.bounds[0, 2]
    def radial(p):
        v = np.c_[p[:, 0] - CX, p[:, 1] + 97.0, np.zeros(len(p))]; return v / (np.linalg.norm(v, axis=1, keepdims=True) + 1e-9)
    drape_c = dir_push(cri, radial); drape_t = draper(thy)      # muscle stays outside the ring: pushed radially outward, never into the lumen
    bed = puller(trimesh.util.concatenate([cri, coR, coL, L(16)]), extra=E('CT_BED_GAP', '0.3'))   # v6: the muscle lies on the cricothyroid membrane / conus and the arch, no gap under it
    tv = thy.vertices
    def thy_border_z(x):    # lower border of the thyroid at a given x (min z of vertices within 0.6 mm)
        q = tv[np.abs(tv[:, 0] - x) < 0.6]; return q[:, 2].min() if len(q) else np.nan
    for part, lat, pid in (('recta', -1, 44), ('recta', 1, 45), ('obliqua', -1, 46), ('obliqua', 1, 47)):
        d0, d1 = (E('CT_R_D0', '24'), E('CT_R_D1', '38')) if part == 'recta' else (E('CT_O_D0', '36'), E('CT_O_D1', '58'))
        def delta(p):          # angle from the anterior midline, positive toward this side
            th = ang_about(p); return (270 - th) * (1 if lat < 0 else -1)
        o_pts, o_n = surface_points(cri, lambda p, n: (delta(p) > d0) & (delta(p) < d1) & (p[:, 2] > zlow + E('CT_ZLOW', '1.5')) & (p[:, 2] < rz(p) - 0.5) & (p[:, 2] < Z0 + (E('CT_R_ZTOP', '40') if part == 'recta' else E('CT_O_ZTOP', '31')))
                                    & ((n[:, 1] * (p[:, 1] + 97) + n[:, 0] * (p[:, 0] - CX)) > 0.3 * np.hypot(p[:, 0] - CX, p[:, 1] + 97)), n=150000)   # outward-facing external surface
        if part == 'recta':
            x0, x1 = E('CT_R_X0', '4.5'), E('CT_R_X1', '9.0')
            i_pts, i_n = surface_points(thy, lambda p, n: (lat * (p[:, 0] - CX) > x0) & (lat * (p[:, 0] - CX) < x1) & (p[:, 1] < -99.0)
                                        & (p[:, 2] < np.array([thy_border_z(x) for x in p[:, 0]]) + E('CT_R_UP', '2.0')) & ((n[:, 2] < -0.6) | (n[:, 1] < -0.3)) & (p[:, 1] < -102.0), n=150000)
        else:
            x0, x1 = E('CT_O_X0', '9.0'), E('CT_O_X1', '13.5')
            i_pts, i_n = surface_points(thy, lambda p, n: (lat * (p[:, 0] - CX) > x0) & (lat * (p[:, 0] - CX) < x1) & (p[:, 1] > E('CT_O_YMIN', '-106.0')) & (p[:, 1] < E('CT_O_YMAX', '-86.5'))
                                        & (p[:, 2] < Z0 + E('CT_O_ZMAX', '40.5')) & (p[:, 2] > Z0 + 30.5) & ((n[:, 1] < -0.4) | (n[:, 2] < -0.6)), n=150000)     # v6: fans onto the lower border of the lamina (downward-facing) as well as the anterior border of the inferior horn
        K = int(E('CT_K', '30')); sel = fps(o_pts, K); O, On = o_pts[sel], o_n[sel]
        # pair by lateral position (delta) so the fibres stay parallel: medial origins -> medial insertions
        okey = delta(O); ikey = lat * (i_pts[:, 0] - CX) if part == 'recta' else (lat * (i_pts[:, 0] - CX) + 0.8 * (i_pts[:, 1] + 97))
        I_sorted = i_pts[np.argsort(ikey)]; order = np.argsort(okey)
        r0, rb, ri = E('CT_R0', '0.9'), E('CT_RB', '1.6'), E('CT_RI', '0.7')
        if part == 'obliqua': rb = E('CT_O_RB', '1.3')                        # v6: the fanned oblique part is wider, so thinner
        bundles = []
        for rank, j in enumerate(order):
            q = rank / max(len(order) - 1, 1); ins = I_sorted[int(q * (len(I_sorted) - 1))]
            A = O[j] - On[j] * 0.5; d = ins - A; d /= np.linalg.norm(d); Bp = ins + d * 0.6
            prof = (lambda s, r0=r0, rb=rb, ri=ri: np.where(s < 0.5, r0 + (rb - r0) * np.sin(np.pi * s), ri + (rb - ri) * np.sin(np.pi * s)))
            pts = chain_points(A, Bp, 10); sv = np.linspace(0, 1, 11); rr = prof(sv) + 0.1; rr[0] = rr[-1] = -1.0
            pts = drape_c(pts, rr); pts = drape_t(pts, rr)
            if os.environ.get('CT_BED', '1') == '1': pts = bed(pts, rr); pts = drape_c(pts, rr); pts = drape_t(pts, rr)
            bundles.append((pts, r0, rb, prof, 1.0))
        phi, a_, b_ = build_body(grid, bundles, k=E('CT_SMOOTH', '0.4'))
        if part == 'obliqua':      # end flush with the anterior border of the inferior horn: clip at the plane fitted to that border (CT_O_IN mm inside it), horn region only
            c0 = i_pts.mean(0); nrm = np.linalg.svd(i_pts - c0, full_matrices=False)[2][2]
            if nrm[1] > 0: nrm = -nrm                                    # normal points anteriorly (away from the horn)
            xs_ = grid.lo[0] + grid.P * np.arange(a_[0], b_[0]); ys_ = grid.lo[1] + grid.P * np.arange(a_[1], b_[1]); zs_ = grid.lo[2] + grid.P * np.arange(a_[2], b_[2])
            Gx, Gy, Gz = np.meshgrid(xs_, ys_, zs_, indexing='ij')
            sdist = (Gx - c0[0]) * nrm[0] + (Gy - c0[1]) * nrm[1] + (Gz - c0[2]) * nrm[2]        # >0 in front of the border plane
            horn = (lat * (Gx - CX) > E('CT_O_XHORN', '8.0'))
            phi = np.where(horn, np.maximum(phi, (-(sdist + E('CT_O_IN', '0.7'))).astype(np.float32)), phi).astype(np.float32)
            del Gx, Gy, Gz, sdist
        name = f'Cricothyroid - {"straight" if part == "recta" else "oblique"} part {"R" if lat < 0 else "L"}'
        m, vol = write_part(grid, B, pid, phi, a_, b_, name, clip=LUMEN)
        print(f'     origin {len(o_pts)} pts x {O[:,0].min():.1f}..{O[:,0].max():.1f} z {O[:,2].min()-Z0:.1f}..{O[:,2].max()-Z0:.1f}; insertion {len(i_pts)} pts x {i_pts[:,0].min():.1f}..{i_pts[:,0].max():.1f} y {i_pts[:,1].min():.1f}..{i_pts[:,1].max():.1f} z {i_pts[:,2].min()-Z0:.1f}..{i_pts[:,2].max()-Z0:.1f}; fibre length {np.mean([np.sum(np.linalg.norm(np.diff(b[0],axis=0),axis=1)) for b in bundles]):.1f} mm')

# ------------------------------------------------------------------ thyroarytenoid body (24 R, 25 L), vocalis (26 R, 27 L), thyroepiglotticus (48 R, 49 L)
if 'ta' in which:
    for lat, pid_ta, pid_vo, pid_te in ((-1, 24, 26, 48), (1, 25, 27, 49)):
        drape_t = dir_push(thy, lambda p: np.where((p[:, 1] < E('TA_YFRONT', '-106.0'))[:, None], np.array([[0, 1.0, 0]]), np.array([[-lat * 1.0, 0, 0]])))      # out of the lamina: backward at the angle, medially along the lamina
        a = ARY[lat]; bz = base_z(lat); vl = VL[lat]; co = CONUS[lat]
        zvl = vl.vertices[np.argmin(vl.vertices[:, 1])][2]                      # anterior commissure level
        # keep the upper sheet of the warped source TA as the thyroepiglottic part
        import shutil
        if not os.path.exists(f'{B}/srcTA_{pid_ta}.ply'): shutil.copy(f'{B}/part_{pid_ta:02d}.ply', f'{B}/srcTA_{pid_ta}.ply')   # the source-warped TA (both sheets), saved before it is replaced
        old = trimesh.load(f'{B}/srcTA_{pid_ta}.ply', process=False); bodies = old.split(only_watertight=False); upper = max(bodies, key=lambda b: b.bounds[1, 2])
        upper.export(f'{B}/part_{pid_te:02d}.ply'); print(f'{pid_te:2d} Thyro-epiglottic part of TA {"R" if lat < 0 else "L"}: kept upper sheet, {upper.volume:.0f} mm3, z {upper.bounds[0,2]-Z0:.1f}..{upper.bounds[1,2]-Z0:.1f}')
        # origin: inner surface of the thyroid angle
        o_pts, o_n = surface_points(thy, lambda p, n: (lat * (p[:, 0] - CX) > E('TA_OX0', '1.5')) & (lat * (p[:, 0] - CX) < E('TA_OX1', '7.0')) & (p[:, 1] < -104.0) & (n[:, 1] > 0.3)
                                    & (p[:, 2] > zvl - E('TA_OZ0', '4.5')) & (p[:, 2] < zvl + E('TA_OZ1', '0.8')), n=200000)
        # insertion: lateral / anterior surface of the arytenoid body, vocal process and muscular process
        npad = near_mesh(PAD[lat], 1.0)
        i_pts, i_n = surface_points(a, lambda p, n: (lat * (p[:, 0] - CX) > 2.5) & (p[:, 1] < -88.0) & (p[:, 2] > bz + E('TA_IZ0', '1.0')) & (p[:, 2] < bz + E('TA_IZ', '4.3')) & ((lat * n[:, 0] > 0.3) | (n[:, 1] < -0.3)) & ~npad(p), n=60000)
        K = int(E('TA_K', '90')); sel = fps(o_pts, K); O, On = o_pts[sel], o_n[sel]
        # pair by (height, lateral offset) rank so fibres run front to back without crossing
        okey = (O[:, 2] - zvl) + E('TA_PAIR_W', '0.8') * lat * (O[:, 0] - CX)
        ikey = (i_pts[:, 2] - bz - 2.0) + E('TA_PAIR_W', '0.8') * lat * (i_pts[:, 0] - CX)
        I_sorted = i_pts[np.argsort(ikey)]; order = np.argsort(okey)
        # a vertical wall above the vocal ligament keeps the muscle lateral to the fold's medial edge above the ligament level too
        wall = trimesh.util.concatenate([trimesh.Trimesh(vl.vertices + [0, 0, dz], vl.faces, process=False) for dz in np.arange(1.2, 9.0, 0.4)])
        push_co = lateral_of(co, lat); push_vl = lateral_of(vl, lat); push_wall = lateral_of(wall, lat)
        r0, rb, ri = E('TA_R0', '0.8'), E('TA_RB', '1.25'), E('TA_RI', '0.8')
        bundles, voc = [], []
        for rank, j in enumerate(order):
            q = rank / max(len(order) - 1, 1); ins = I_sorted[int(q * (len(I_sorted) - 1))]
            A = O[j] - On[j] * 0.5; d = ins - A; d /= np.linalg.norm(d); Bp = ins + d * 0.6
            prof = (lambda s, r0=r0, rb=rb, ri=ri: np.where(s < 0.5, r0 + (rb - r0) * np.sin(np.pi * s), ri + (rb - ri) * np.sin(np.pi * s)))
            pts = chain_points(A, Bp, 14); sv = np.linspace(0, 1, 15); rr = prof(sv) + 0.15; rr[0] = rr[-1] = -1.0
            for _ in range(3):
                pts = push_co(pts, rr); pts = push_vl(pts, rr); pts = push_wall(pts, rr + E('TA_WALL', '0.8')); pts = drape_t(pts, rr)
            bundles.append((pts, r0, rb, prof, 1.0))
        # one muscle body, then split by relative position between the medial sheets (conus + vocal ligament) and the thyroid lamina:
        # vocalis = medial TA_VOC_FRAC of the local width, TA = the rest (one smooth parasagittal interface)
        phi, a_, b_ = build_body(grid, bundles, k=E('TA_SMOOTH', '0.45'))
        sheets = trimesh.util.concatenate([co, vl, wall])
        c2 = 2; shp = phi.shape
        xs, ys, zs = [(grid.lo[i] + grid.P * (a_[i] + c2 * np.arange((shp[i] + c2 - 1) // c2))) for i in range(3)]
        G = np.stack(np.meshgrid(xs, ys, zs, indexing='ij'), -1).reshape(-1, 3)
        def dist_to(mesh):
            d2, _, _ = igl.point_mesh_squared_distance(G, np.ascontiguousarray(mesh.vertices, np.float64), np.ascontiguousarray(mesh.faces, np.int64))
            return np.sqrt(d2).reshape(len(xs), len(ys), len(zs)).astype(np.float32)
        dm, dl = dist_to(sheets), dist_to(thy)
        rel = dm / (dm + dl + 1e-6)
        from scipy import ndimage
        relf = ndimage.zoom(rel, [shp[i] / rel.shape[i] for i in range(3)], order=1, mode='nearest')[:shp[0], :shp[1], :shp[2]]
        FR = E('TA_VOC_FRAC', '0.35'); W_ = E('TA_SPLIT_W', '1.0')            # split surface at rel = FR, as a signed field in ~mm
        dmf = ndimage.zoom(dm, [shp[i] / dm.shape[i] for i in range(3)], order=1, mode='nearest')[:shp[0], :shp[1], :shp[2]]
        split = np.minimum((relf - FR) * (dm.mean() + dl.mean()) * W_, dmf - E('TA_VOC_MIN', '1.2')).astype(np.float32)   # vocalis: medial fraction, never thinner than TA_VOC_MIN
        phi_vo = np.maximum(phi, split); phi_ta = np.maximum(phi, -split)
        # opening: slivers thinner than ~1 mm go to the other compartment; then keep each part's main body only
        r = int(round(E('TA_OPEN', '0.5') / grid.P)); ball = np.zeros((2 * r + 1,) * 3, bool); ii = np.indices(ball.shape) - r; ball[(ii ** 2).sum(0) <= r * r] = True
        occ_all = phi <= 0
        o_ta = ndimage.binary_opening(phi_ta <= 0, structure=ball); o_vo = ndimage.binary_opening(phi_vo <= 0, structure=ball)
        lab, nl = ndimage.label(o_ta); 
        if nl > 1: o_ta = lab == (np.bincount(lab.ravel())[1:].argmax() + 1)
        o_vo = o_vo & ~o_ta
        lab, nl = ndimage.label(o_vo)
        if nl > 1: o_vo = lab == (np.bincount(lab.ravel())[1:].argmax() + 1)
        o_ta = o_ta | (occ_all & ~o_vo & ndimage.binary_dilation(o_ta, iterations=3))      # leftovers near the TA join it
        o_vo = o_vo | (occ_all & ~o_ta)                                                    # the rest joins the vocalis
        phi_ta = np.where(o_ta, np.minimum(phi, -0.01), np.maximum(phi, 0.01)).astype(np.float32)
        phi_vo = np.where(o_vo, np.minimum(phi, -0.01), np.maximum(phi, 0.01)).astype(np.float32)
        phi_ta = ndimage.gaussian_filter(phi_ta, 1.5); phi_vo = ndimage.gaussian_filter(phi_vo, 1.5)      # soften the voxel steps of the split surface
        m, vol = write_part(grid, B, pid_ta, phi_ta, a_, b_, f'Thyro-arytenoid {"R" if lat < 0 else "L"}', clip=LUMEN)
        print(f'     origin {len(o_pts)} pts z {O[:,2].min()-Z0:.1f}..{O[:,2].max()-Z0:.1f} x {O[:,0].min():.1f}..{O[:,0].max():.1f}; insertion {len(i_pts)} pts z {i_pts[:,2].min()-Z0:.1f}..{i_pts[:,2].max()-Z0:.1f}; fibre length {np.mean([np.sum(np.linalg.norm(np.diff(b[0],axis=0),axis=1)) for b in bundles]):.1f} mm; vocalis = medial {FR:.0%} of the width between the conus/ligament and the lamina')
        write_part(grid, B, pid_vo, phi_vo, a_, b_, f'Vocalis {"R" if lat < 0 else "L"}', clip=LUMEN)

# ------------------------------------------------------------------ thyro-epiglottic part (48/49): bridge its anterior edge onto the thyroid lamina
if 'te' in which:
    for lat, pid_te in ((-1, 48), (1, 49)):
        sheet = L(pid_te); sv_ = sheet.vertices
        V = np.ascontiguousarray(thy.vertices, np.float64); F = np.ascontiguousarray(thy.faces, np.int64)
        bundles = []
        for z in np.arange(sv_[:, 2].min() + 0.5, sv_[:, 2].min() + E('TE_H', '12.0'), 1.2):
            band = sv_[np.abs(sv_[:, 2] - z) < 0.6]
            if len(band) < 3: continue
            edge = band[np.argmin(band[:, 1])]                                   # anterior edge of the sheet at this level
            d2, _, cp = igl.point_mesh_squared_distance(np.ascontiguousarray(edge[None, :]), V, F); cp = np.asarray(cp).reshape(3)
            if np.sqrt(d2[0]) > E('TE_MAXGAP', '4.0'): continue
            d = cp - edge; d /= np.linalg.norm(d) + 1e-9
            A = edge + d * (-0.4); Bp = cp + d * 0.5                             # from 0.4 mm inside the sheet to 0.5 mm inside the cartilage
            bundles.append((chain_points(A, Bp, 4), E('TE_R', '0.6'), E('TE_R', '0.6'), 'const', 1.0))
        if not bundles: print(pid_te, 'no bridge fibres'); continue
        phi, a_, b_ = build_body(grid, bundles, k=0.3, margin=1.0)
        bm, _ = write_part(grid, B, 99, phi, a_, b_, 'TE bridge (temp)')
        os.remove(f'{B}/occ_99.npz'); os.remove(f'{B}/part_99.ply')
        merged = trimesh.util.concatenate([sheet, bm]); merged.export(f'{B}/part_{pid_te:02d}.ply')
        if os.path.exists(f'{B}/occ_{pid_te:02d}.npz'): os.remove(f'{B}/occ_{pid_te:02d}.npz')     # vox.py rasterises the merged mesh
        print(f'{pid_te:2d} thyro-epiglottic part {"R" if lat < 0 else "L"}: {len(bundles)} bridge fibres to the thyroid lamina added to the source sheet ({sheet.volume:.0f} + {bm.volume:.0f} mm3)')

# ------------------------------------------------------------------ grid: enlarge to hold every part (origin fixed)
if 'grid' in which:
    from partsconfig import PARTS
    g = np.load(f'{B}/grid.npy'); lo0 = g[:3]; P = g[3]; z_cut = g[7]
    ids = [p[0] for p in PARTS if (p[2] or p[5] == 'sculpt') and os.path.exists(f'{B}/part_{p[0]:02d}.ply')]
    allb = np.array([trimesh.load(f'{B}/part_{i:02d}.ply', process=False).bounds for i in ids])
    lo_g = np.floor((allb[:, 0].min(0) - 2.0) / P) * P; hi_g = allb[:, 1].max(0) + 2.0
    lo_g[2] = z_cut - 4
    assert np.all(lo_g >= lo0 - 1e-6), f'grid origin would move: {lo_g} vs {lo0}'
    shape_g = tuple(int(np.ceil((h - l) / P)) + 1 for l, h in zip(lo0, hi_g))
    np.save(f'{B}/grid.npy', np.array([*lo0, P, *shape_g, z_cut]))
    print('grid: origin kept', np.round(lo0, 2), 'shape', tuple(int(x) for x in g[4:7]), '->', shape_g)

# ------------------------------------------------------------------ oblique arytenoids (29 R: from the right muscular process to the left apex; 30 L mirrored)
if 'ia' in which:
    tra = L(28)
    push_back = side_of(tra, 1, +1)          # stays behind (posterior to) the transverse arytenoid
    for pid, lat in ((29, -1), (30, 1)):
        a_from, a_to = ARY[lat], ARY[-lat]; bz = base_z(lat)
        o_pts, o_n = surface_points(a_from, lambda p, n: (p[:, 2] < bz + 3.5) & (lat * (p[:, 0] - CX) > 5.5) & (p[:, 1] > -91.0) & (n[:, 1] > -0.2), n=40000)
        apex = a_to.vertices[np.argmax(a_to.vertices[:, 2])]
        i_pts, i_n = surface_points(a_to, lambda p, n: (p[:, 2] > apex[2] - E('OA_APEX', '4.0')) & (n[:, 1] > -0.2) & (-lat * (p[:, 0] - CX) > 1.0), n=40000)
        ae = L(31 if lat > 0 else 32); aev = ae.vertices; ae_low = aev[aev[:, 2] < aev[:, 2].min() + 2.5]      # lower end of the opposite aryepiglotticus: continuity
        i_pts = np.vstack([i_pts, ae_low])
        K = int(E('OA_K', '3')); sel = fps(o_pts, K); O, On = o_pts[sel], o_n[sel]
        okey = O[:, 2] + 0.5 * lat * (O[:, 0] - CX); ikey = i_pts[:, 2] + 0.5 * (-lat) * (i_pts[:, 0] - CX)
        I_sorted = i_pts[np.argsort(ikey)]; order = np.argsort(okey)
        r0, rb = E('OA_R0', '0.8'), E('OA_RB', '1.1'); bundles = []
        for rank, j in enumerate(order):
            q = rank / max(len(order) - 1, 1); ins = I_sorted[int(q * (len(I_sorted) - 1))]
            A = O[j] - On[j] * 0.5; d = ins - A; d /= np.linalg.norm(d); Bp = ins + d * 0.6
            prof = (lambda s, r0=r0, rb=rb: r0 + (rb - r0) * np.sin(np.pi * s))
            pts = chain_points(A, Bp, 12); sv = np.linspace(0, 1, 13); rr = prof(sv) + 0.1; rr[0] = rr[-1] = -1.0
            pts = push_back(pts, rr)
            if lat > 0: pts = push_back_R(pts, rr)      # the left oblique crosses superficial (posterior) to the right one
            bundles.append((pts, r0, rb, prof, 1.0))
        phi, a_, b_ = build_body(grid, bundles, k=E('OA_SMOOTH', '0.5'))
        m, vol = write_part(grid, B, pid, phi, a_, b_, f'Oblique arytenoid {"R" if lat < 0 else "L"}', clip=LUMEN)
        if lat < 0: push_back_R = side_of(m, 1, +1)
        print(f'     from MP {np.round(O.mean(0)-[0,0,Z0],1)} to apex {np.round(apex-[0,0,Z0],1)}; fibre length {np.mean([np.sum(np.linalg.norm(np.diff(b[0],axis=0),axis=1)) for b in bundles]):.1f} mm')
