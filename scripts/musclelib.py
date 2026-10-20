"""Muscle construction: fibre bundles (capsule chains with a radius profile) merged by a smooth minimum into one body,
rasterised on the build grid (0.1 mm) and written as occ_XX.npz (vox.py format) + part_XX.ply (marching cubes)."""
import os, numpy as np, trimesh, igl
from skimage import measure
BIG = 50.0
def smin(a, b, k):
    h = np.maximum(k - np.abs(a - b), 0.0) / k
    return np.minimum(a, b) - h * h * k * 0.25
def seg_sdf(G, A, Bp, r0, r1, rprof='sin', pw=1.0):
    """distance from points G to segment A-B minus the radius profile r(s) (r0 at both ends, r1 at the belly)"""
    d = Bp - A; L2 = d @ d
    s = np.clip(((G - A) @ d) / L2, 0, 1)
    dist = np.linalg.norm(G - (A + s[:, None] * d), axis=1)
    if rprof == 'sin': r = r0 + (r1 - r0) * np.sin(np.pi * s) ** pw
    elif rprof == 'lin': r = r0 + (r1 - r0) * s                      # grows toward B
    elif rprof == 'const': r = np.full_like(s, r1)
    elif callable(rprof): r = rprof(s)
    return dist - r
def chain_sdf(G, pts, r0, r1, rprof='sin', pw=1.0):
    """polyline through pts, radius profile over the whole chain length"""
    pts = np.asarray(pts, float); seglen = np.linalg.norm(np.diff(pts, axis=0), axis=1); Ltot = seglen.sum(); cum = np.r_[0, np.cumsum(seglen)]
    best = np.full(len(G), BIG)
    for i in range(len(pts) - 1):
        A, Bp = pts[i], pts[i + 1]; d = Bp - A
        s = np.clip(((G - A) @ d) / (d @ d), 0, 1)
        dist = np.linalg.norm(G - (A + s[:, None] * d), axis=1)
        sg = (cum[i] + s * seglen[i]) / Ltot
        if rprof == 'sin': r = r0 + (r1 - r0) * np.sin(np.pi * sg) ** pw
        elif rprof == 'lin': r = r0 + (r1 - r0) * sg
        elif callable(rprof): r = rprof(sg)
        else: r = np.full_like(sg, r1)
        best = np.minimum(best, dist - r)
    return best
class Grid:
    def __init__(self, gridfile):
        g = np.load(gridfile); self.lo = g[:3]; self.P = g[3]; self.shape = tuple(int(x) for x in g[4:7]); self.z_cut = g[7]
    def box(self, lo_mm, hi_mm, margin=1.0):
        a = np.maximum(np.floor((lo_mm - margin - self.lo) / self.P).astype(int), 0)
        b = np.minimum(np.ceil((hi_mm + margin - self.lo) / self.P).astype(int) + 1, self.shape)
        return a, b
    def points(self, a, b):
        xs, ys, zs = [self.lo[i] + self.P * np.arange(a[i], b[i]) for i in range(3)]
        return np.stack(np.meshgrid(xs, ys, zs, indexing='ij'), -1).reshape(-1, 3), (len(xs), len(ys), len(zs))
def build_body(grid, bundles, k=0.4, clip=None, margin=1.5, coarse=2):
    """bundles: list of (pts, r0, r1, rprof, pw).  clip: optional f(G) -> sdf of an exclusion region (muscle removed where <0).
    Evaluated per bundle on its own sub-box at coarse*P, then upsampled to the grid.  Returns (phi, a, b) on the grid box."""
    from scipy import ndimage
    allp = np.vstack([np.asarray(bd[0]) for bd in bundles]); rmax = max(bd[2] for bd in bundles)
    a, b = grid.box(allp.min(0), allp.max(0), margin=rmax + margin)
    a = (a // coarse) * coarse; b = a + ((b - a + coarse - 1) // coarse) * coarse
    Pc = grid.P * coarse; shp = tuple((b - a) // coarse)
    xs, ys, zs = [(grid.lo[i] + grid.P * a[i] + Pc * np.arange(shp[i])).astype(np.float32) for i in range(3)]
    phi = np.full(shp, BIG, np.float32)
    for pts, r0, r1, rprof, pw in bundles:
        pts = np.asarray(pts, np.float32); ext = r1 + k + Pc
        ia = np.maximum(np.floor((pts.min(0) - ext - (grid.lo + grid.P * a)) / Pc).astype(int), 0)
        ib = np.minimum(np.ceil((pts.max(0) + ext - (grid.lo + grid.P * a)) / Pc).astype(int) + 1, shp)
        G = np.stack(np.meshgrid(xs[ia[0]:ib[0]], ys[ia[1]:ib[1]], zs[ia[2]:ib[2]], indexing='ij'), -1).reshape(-1, 3)
        sub = (slice(ia[0], ib[0]), slice(ia[1], ib[1]), slice(ia[2], ib[2]))
        phi[sub] = np.minimum(phi[sub], chain_sdf(G, pts, r0, r1, rprof, pw).reshape(ib - ia).astype(np.float32))
    if clip is not None:
        G = np.stack(np.meshgrid(xs, ys, zs, indexing='ij'), -1).reshape(-1, 3)
        phi = np.maximum(phi, -clip(G).reshape(shp).astype(np.float32))
    if coarse > 1:   # fine sample j <-> coarse coordinate j/coarse: zoom to (coarse*N - coarse + 1) samples, then edge-pad
        N = np.array(shp); M = coarse * (N - 1) + 1
        phi = ndimage.zoom(phi, M / N, order=1, mode='nearest', grid_mode=False)
        phi = np.pad(phi, [(0, int(b[i] - a[i] - phi.shape[i])) for i in range(3)], mode='edge')
    b = np.minimum(b, np.array(grid.shape)); phi = phi[:b[0]-a[0], :b[1]-a[1], :b[2]-a[2]]      # never beyond the grid
    if k > 0: phi = ndimage.gaussian_filter(phi, k / grid.P, mode='nearest')      # k = smoothing radius (mm): rounds the creases between bundles without inflating them
    return phi.astype(np.float32), a, b
def mesh_sdf_fn(mesh, sign=True):
    V = np.ascontiguousarray(mesh.vertices, np.float64); F = np.ascontiguousarray(mesh.faces, np.int64)
    def f(G):
        d2, _, _ = igl.point_mesh_squared_distance(np.ascontiguousarray(G, np.float64), V, F); d = np.sqrt(d2)
        if sign:
            w = igl.fast_winding_number(V, F, np.ascontiguousarray(G, np.float64)); d = np.where(w > 0.5, -d, d)
        return d
    return f
def write_part(grid, B, pid, phi, a, b, name='', decim=0.15, clip=None):
    occ = phi <= 0
    if clip is not None:      # (mask, ma, mb): remove voxels inside the mask (e.g. the airway lumen)
        M, ma, mb = clip
        oa = np.maximum(a, ma); ob = np.minimum(b, mb)
        if np.all(ob > oa):
            sub = M[oa[0]-ma[0]:ob[0]-ma[0], oa[1]-ma[1]:ob[1]-ma[1], oa[2]-ma[2]:ob[2]-ma[2]]
            occ[oa[0]-a[0]:ob[0]-a[0], oa[1]-a[1]:ob[1]-a[1], oa[2]-a[2]:ob[2]-a[2]] &= ~sub
            phi = np.where(occ, np.minimum(phi, -0.01), np.maximum(phi, 0.01)).astype(np.float32)
    np.savez_compressed(f'{B}/occ_{pid:02d}.npz', occ=occ, a=a, b=b)
    ph = np.pad(phi, 1, constant_values=BIG)
    v, f, _, _ = measure.marching_cubes(ph, 0.0, spacing=(grid.P,) * 3)
    v += grid.lo + (np.array(a) - 1) * grid.P
    m = trimesh.Trimesh(v, f, process=True)
    if m.volume < 0: m.invert()
    m = m.simplify_quadric_decimation(face_count=max(int(len(m.faces) * decim), 2000)) if len(m.faces) > 20000 else m
    m.export(f'{B}/part_{pid:02d}.ply')
    vol = occ.sum() * grid.P ** 3
    lo_, hi_ = m.bounds
    print(f'{pid:2d} {name:36s} {vol:7.1f} mm3  x {lo_[0]:6.1f}..{hi_[0]:6.1f}  y {lo_[1]:7.1f}..{hi_[1]:7.1f}  z {lo_[2]-grid.z_cut:5.1f}..{hi_[2]-grid.z_cut:5.1f}  bodies {len(m.split(only_watertight=False))}', flush=True)
    return m, vol
def surface_points(mesh, pred, n=60000, seed=0):
    """evenly sampled surface points (with normals) satisfying pred(points, normals)"""
    pts, fid = trimesh.sample.sample_surface_even(mesh, n, seed=seed)
    nrm = mesh.face_normals[fid]
    keep = pred(pts, nrm); return pts[keep], nrm[keep]
def pick(points, order_key, K):
    """K points spread evenly along a sort key (quantiles)"""
    o = np.argsort(order_key); q = np.linspace(0, 1, K); idx = o[np.clip((q * (len(o) - 1)).round().astype(int), 0, len(o) - 1)]
    return points[idx]
def draper(mesh):
    """returns f(points, clearance) that pushes points outside the mesh to at least `clearance` from its surface"""
    V = np.ascontiguousarray(mesh.vertices, np.float64); F = np.ascontiguousarray(mesh.faces, np.int64)
    def f(pts, clearance):
        pts = np.asarray(pts, np.float64).copy()
        d2, _, cp = igl.point_mesh_squared_distance(np.ascontiguousarray(pts), V, F); cp = np.asarray(cp).reshape(-1, 3)
        w = igl.fast_winding_number(V, F, np.ascontiguousarray(pts)); inside = w > 0.5
        d = np.sqrt(d2) * np.where(inside, -1, 1)
        out = pts - cp; nrm = np.linalg.norm(out, axis=1, keepdims=True) + 1e-9; out = out / nrm * np.where(inside, -1, 1)[:, None]
        cl = np.broadcast_to(np.asarray(clearance, float), (len(pts),))
        move = d < cl
        pts[move] = cp[move] + out[move] * cl[move][:, None]
        return pts
    return f
def puller(mesh, extra=0.3):
    """returns f(points, radius) that pulls points lying further than radius+extra from the mesh in to that distance (toward the nearest surface point); endpoints (radius < 0) untouched"""
    V = np.ascontiguousarray(mesh.vertices, np.float64); F = np.ascontiguousarray(mesh.faces, np.int64)
    def f(pts, radius):
        pts = np.asarray(pts, np.float64).copy(); rr = np.broadcast_to(np.asarray(radius, float), (len(pts),))
        d2, _, cp = igl.point_mesh_squared_distance(np.ascontiguousarray(pts), V, F); cp = np.asarray(cp).reshape(-1, 3); d = np.sqrt(d2)
        w = igl.fast_winding_number(V, F, np.ascontiguousarray(pts)); inside = w > 0.5
        want = rr + extra; move = (~inside) & (d > want) & (rr >= 0)
        out = pts - cp; out /= (np.linalg.norm(out, axis=1, keepdims=True) + 1e-9)
        pts[move] = cp[move] + out[move] * want[move][:, None]
        return pts
    return f
def chain_points(A, Bp, n, bow=None):
    """n+1 points from A to B (optionally bowed by vector `bow` at the middle, sin profile)"""
    s = np.linspace(0, 1, n + 1)[:, None]; pts = A + (Bp - A) * s
    if bow is not None: pts = pts + np.sin(np.pi * s) * np.asarray(bow)[None, :]
    return pts
def enclosed_lumen(grid, B, wall_ids, z0, z1, axis_xy=(-0.65, -101.0), max_area=350.0, dilate=0.3):
    """per axial slice, the airway region enclosed by the wall parts (flood fill from the airway axis); slices whose fill
    leaks (area > max_area) take the mask of the nearest clean slice.  Returns (mask, a, b) on the grid (bool)."""
    from scipy import ndimage
    k0 = int((z0 - grid.lo[2]) / grid.P); k1 = int((z1 - grid.lo[2]) / grid.P) + 1
    a = np.array([0, 0, k0]); b = np.array([grid.shape[0], grid.shape[1], k1])
    W = np.zeros((grid.shape[0], grid.shape[1], k1 - k0), bool)
    for pid in wall_ids:
        f = f'{B}/occ_{pid:02d}.npz'
        if not os.path.exists(f): continue
        d = np.load(f); o, oa, ob = d['occ'], d['a'], d['b']
        za, zb = max(oa[2], k0), min(ob[2], k1)
        if zb <= za: continue
        W[oa[0]:ob[0], oa[1]:ob[1], za - k0:zb - k0] |= o[:, :, za - oa[2]:zb - oa[2]]
    ix = int(round((axis_xy[0] - grid.lo[0]) / grid.P)); iy = int(round((axis_xy[1] - grid.lo[1]) / grid.P))
    M = np.zeros_like(W); areas = np.zeros(W.shape[2]); ok = np.zeros(W.shape[2], bool)
    for k in range(W.shape[2]):
        lab, n = ndimage.label(~W[:, :, k])
        l = lab[ix, iy]
        if l == 0: continue
        m = lab == l; A = m.sum() * grid.P ** 2
        areas[k] = A
        if A <= max_area: M[:, :, k] = m; ok[k] = True
    # leaked slices: copy the nearest clean slice
    good = np.nonzero(ok)[0]
    for k in range(W.shape[2]):
        if not ok[k] and len(good): M[:, :, k] = M[:, :, good[np.argmin(np.abs(good - k))]]
    if dilate > 0: M = ndimage.binary_dilation(M, iterations=int(round(dilate / grid.P)))
    return M, a, b, areas, ok
