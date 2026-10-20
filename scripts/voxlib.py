import numpy as np, trimesh
from scipy import ndimage

class Grid:
    def __init__(self, lo, hi, pitch):
        self.pitch = pitch
        self.lo = np.floor(np.asarray(lo) / pitch) * pitch
        self.shape = tuple(int(np.ceil((h - l) / pitch)) + 1 for l, h in zip(self.lo, hi))
    def idx(self, pts):
        return np.round((pts - self.lo) / self.pitch).astype(np.int64)
    def centers(self, sl):
        ax = [self.lo[i] + self.pitch * np.arange(sl[i].start, sl[i].stop) for i in range(3)]
        return ax
    def sub(self, lo, hi, margin):
        """slice of the grid covering [lo-margin, hi+margin]"""
        a = np.clip(np.floor((np.asarray(lo) - margin - self.lo) / self.pitch).astype(int), 0, None)
        b = np.minimum(np.ceil((np.asarray(hi) + margin - self.lo) / self.pitch).astype(int) + 1, self.shape)
        return tuple(slice(int(x), int(y)) for x, y in zip(a, b))

def surface_mask(mesh, grid, sl):
    """voxels that the surface passes through (barycentric lattice sampling, chunked)"""
    shp = tuple(s.stop - s.start for s in sl)
    m = np.zeros(shp, bool)
    off = np.array([s.start for s in sl])
    spacing = grid.pitch * 0.4
    T = mesh.vertices[mesh.faces]
    e = np.max(np.linalg.norm(T[:, [1, 2, 0]] - T, axis=2), axis=1)
    nseg = np.maximum(1, np.ceil(e / spacing).astype(int))
    for n in np.unique(nseg):
        tri = T[nseg == n]
        i, j = np.meshgrid(np.arange(n + 1), np.arange(n + 1), indexing='ij')
        keep = (i + j) <= n
        a = (i[keep] / n)[:, None]; b = (j[keep] / n)[:, None]
        w = np.hstack([1 - a - b, a, b])  # (k,3)
        step = max(1, int(2_000_000 // max(1, len(w))))
        for c in range(0, len(tri), step):
            pts = np.einsum('kj,tjd->tkd', w, tri[c:c + step]).reshape(-1, 3)
            ii = np.round((pts - grid.lo) / grid.pitch).astype(np.int64) - off
            ok = np.all((ii >= 0) & (ii < np.array(shp)), axis=1)
            ii = ii[ok]
            m[ii[:, 0], ii[:, 1], ii[:, 2]] = True
    return m

def solid_mask(mesh, grid, sl, mode='auto'):
    """returns (solid, surface, dist_mm) on sub-grid sl. solid via flood fill of exterior (sealed by surface)."""
    S = surface_mask(mesh, grid, sl)
    seal = ndimage.binary_dilation(S, iterations=1)
    free = ~seal
    lab, n = ndimage.label(free)
    border = set(np.unique(np.concatenate([lab[0].ravel(), lab[-1].ravel(), lab[:, 0].ravel(), lab[:, -1].ravel(), lab[:, :, 0].ravel(), lab[:, :, -1].ravel()]))) - {0}
    exterior = np.isin(lab, list(border))
    dist = ndimage.distance_transform_edt(~S) * grid.pitch
    interior = ~exterior & ~seal
    solid = interior | (dist <= 0.5 * grid.pitch * 1.01) | (seal & ~exterior & (dist <= grid.pitch))
    return solid, S, dist, interior.sum()

def refine_band_wn(mesh, grid, sl, solid, dist, band_mm=None):
    """re-decide voxels near the surface by fast winding number (closed or nearly closed meshes)"""
    import igl
    band_mm = band_mm or 1.6 * grid.pitch
    band = dist <= band_mm
    idx = np.argwhere(band)
    off = np.array([s.start for s in sl])
    P = grid.lo + (idx + off) * grid.pitch
    V = np.ascontiguousarray(mesh.vertices, dtype=np.float64); F = np.ascontiguousarray(mesh.faces, dtype=np.int64)
    w = np.empty(len(P))
    for c in range(0, len(P), 2_000_000):
        w[c:c + 2_000_000] = igl.fast_winding_number(V, F, np.ascontiguousarray(P[c:c + 2_000_000]))
    out = solid.copy()
    out[tuple(idx.T)] = np.abs(w) > 0.5
    return out

def opening_thin(solid, pitch, r_mm):
    """voxels of solid lying in features thinner than 2*r (not covered by opening with ball r)"""
    from scipy import ndimage
    inside = ndimage.distance_transform_edt(solid) * pitch
    core = inside > r_mm
    if not core.any():
        return solid.copy()
    back = ndimage.distance_transform_edt(~core) * pitch <= r_mm + 1e-6
    return solid & ~back
