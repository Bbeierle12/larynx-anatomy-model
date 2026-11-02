"""Sculpted tongue base with vallecula, built in the frame of a whole-model 3MF from its own parts.

Same anatomy rules as v6's block (tissues8_v6a.py, 'tongue' section): floor on the hyo-epiglottic
ligament, bottom overlapping the hyoid, vallecula pockets VW wide and VD deep in front of the
epiglottis's lingual face, a median glossoepiglottic fold, lateral folds beyond LAT_X, the
pharyngo-epiglottic fold back to the piriform fossa's anterior wall, a flat cut 1 mm above the
epiglottis tip.  What is new: the box is gone.  The front follows the hyoid body as a convex
parabola and leans forward with height; the vertical edges are rounded (2-D opening per slice,
so the top cut stays flat and sharp); and the vallecula's anterior wall carries two paramedian
lingual-tonsil mounds either side of the median fold (Sung 2013: lingual tonsil 3.6 mm midline,
4.9 mm paramedian on MRI).

Usage: python build_tongue.py <v6 whole.3mf> <scale> <out.npz>
"""
import sys, numpy as np, trimesh
from scipy import ndimage
from skimage import measure
from parts import read_parts, one

path, S, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
P = 0.2 * S                      # voxel pitch (mm): 0.2 at 1:1, 0.4 at 2x (same voxel count)
CX = -0.65 * S                   # the model's midline (tissues8: CX = -0.65)
mm = lambda v: v * S             # a life-size millimetre value in this file's units

parts = read_parts(path)
hy, epi = one(parts, 'Hyoid bone'), one(parts, 'Epiglottis')
HE = one(parts, 'Hyo-epiglottic ligament')
old = one(parts, 'Tongue base and vallecula (with glossoepiglottic folds)')

# --- landmarks (as in tissues8_v6a)
hb = hy.vertices[np.abs(hy.vertices[:, 0] - CX) < mm(6)]            # hyoid body, near the midline
z_hy_top, y_hy_front, y_hy_back = hb[:, 2].max(), hb[:, 1].min(), hb[:, 1].max()
z_floor = HE.vertices[:, 2].max() - mm(0.3)                           # vallecula floor on the ligament
z_top = epi.vertices[:, 2].max() + mm(1.0)                            # flat cut level, 1 mm above the tip
HW, VW, VD, SEPT, LAT_X = mm(15.0), mm(6.0), mm(12.0), mm(0.8), mm(9.5)
TONSIL = mm(2.0)                 # how far the paramedian mounds bulge into the vallecula (gap 6 -> 4 mm; flank slope about 35 deg)
FLOOR_T = mm(2.5)                # floor thickness beside the ligament
print(f'hyoid top z {z_hy_top:.1f}, front y {y_hy_front:.1f}, back y {y_hy_back:.1f}; floor z {z_floor:.1f}; top z {z_top:.1f}')

# lingual (anterior) face of the epiglottis: min y per (x, z) bin, with a little dilation at the margins
def face_lookup(mesh, binw):
    v, _ = trimesh.sample.sample_surface(mesh, 400000, seed=0)
    v = np.vstack([v, mesh.vertices])
    lo0 = v[:, [0, 2]].min(0) - 1
    n = ((v[:, [0, 2]].max(0) - lo0) / binw).astype(int) + 3
    X = np.full(tuple(n), np.inf)
    ij = ((v[:, [0, 2]] - lo0) / binw).astype(int)
    np.minimum.at(X, (ij[:, 0], ij[:, 1]), v[:, 1])
    has = np.isfinite(X)
    for _ in range(2):
        Xf = ndimage.minimum_filter(np.where(has, X, np.inf), size=3)
        X = np.where(has, X, Xf)
        has = np.isfinite(X)
    def f(pts):
        jj = ((pts[:, [0, 2]] - lo0) / binw).astype(int)
        ok = (jj[:, 0] >= 0) & (jj[:, 0] < n[0]) & (jj[:, 1] >= 0) & (jj[:, 1] < n[1])
        o = np.full(len(pts), np.nan)
        o[ok] = X[jj[ok, 0], jj[ok, 1]]
        o[~np.isfinite(o)] = np.nan
        return o
    return f
ep_front = face_lookup(epi, mm(0.3))

# --- voxel domain
lo = np.array([CX - HW - mm(3), y_hy_front - mm(7), min(z_hy_top, z_floor) - mm(5)])
hi = np.array([CX + HW + mm(3), epi.vertices[:, 1].max() + mm(2), z_top + mm(1)])
n = np.ceil((hi - lo) / P).astype(int) + 1
xs, ys, zs = [lo[i] + P * np.arange(n[i]) for i in range(3)]
G = np.stack(np.meshgrid(xs, ys, zs, indexing='ij'), -1).reshape(-1, 3)
X, Y, Z = G[:, 0] - CX, G[:, 1], G[:, 2]

# --- back face: the vallecula in front of the epiglottis, with the lingual-tonsil mounds
yf = ep_front(G)
dz = Z - z_floor
pocket = np.where(dz < 0, 0.0, np.minimum(VW, VW * np.clip(dz / mm(2.0), 0, 1)))
pocket = np.where(dz > VD, VW, pocket)
# paramedian mounds: Gaussian in x about +/-5 mm, raised cosine in z over floor+3 .. floor+11
mound = np.exp(-((np.abs(X) - mm(5.0)) / mm(3.0)) ** 2) * (0.5 - 0.5 * np.cos(np.pi * np.clip((dz - mm(3)) / mm(8), 0, 1) * 2)) * (dz < mm(11))
pocket = pocket - TONSIL * mound
pocket = np.where((np.abs(X) > LAT_X) | (np.abs(X) < SEPT), 0.0, np.maximum(pocket, 0.0))
yback = np.where(np.isfinite(yf), yf - pocket, np.nan)
# beyond the epiglottis margins the old block ran back to the piriform fossa's anterior wall; take that
# boundary from the old block itself (max y of its surface per (x, z) bin) so the frame offset does not matter
def back_lookup(mesh, binw):
    v, _ = trimesh.sample.sample_surface(mesh, 400000, seed=1)
    v = np.vstack([v, mesh.vertices])
    lo0 = v[:, [0, 2]].min(0) - 1
    nn = ((v[:, [0, 2]].max(0) - lo0) / binw).astype(int) + 3
    Xb = np.full(tuple(nn), -np.inf)
    ij = ((v[:, [0, 2]] - lo0) / binw).astype(int)
    np.maximum.at(Xb, (ij[:, 0], ij[:, 1]), v[:, 1])
    has = np.isfinite(Xb)
    for _ in range(3):
        Xf = ndimage.maximum_filter(np.where(has, Xb, -np.inf), size=3)
        Xb = np.where(has, Xb, Xf)
        has = np.isfinite(Xb)
    def f(pts):
        jj = ((pts[:, [0, 2]] - lo0) / binw).astype(int)
        ok = (jj[:, 0] >= 0) & (jj[:, 0] < nn[0]) & (jj[:, 1] >= 0) & (jj[:, 1] < nn[1])
        o = np.full(len(pts), np.nan)
        o[ok] = Xb[jj[ok, 0], jj[ok, 1]]
        o[~np.isfinite(o)] = np.nan
        return o
    return f
old_back = back_lookup(old, mm(0.5))(G)
behind_ok = np.where(np.isfinite(yback), Y <= yback, Y <= np.where(np.isfinite(old_back), old_back, -np.inf))

# --- bottom: overlapping the hyoid in front of its back face, the floor beside the ligament behind it
bottom = np.where(Y <= y_hy_back, z_hy_top - mm(3.0), z_floor - FLOOR_T)

# --- front and sides: a forward-leaning parabola instead of a flat face, |x| within HW at the floor widening 1 mm at the top
lean = mm(0.25) * np.clip((Z - z_hy_top) / S, 0, None) / 1.0       # 0.25 mm forward per mm of height
y_front = (y_hy_front - mm(1.0)) - lean + mm(9.0) * (X / HW) ** 2    # convex forward at the midline, 9 mm further back at the sides
hw = HW + mm(1.0) * np.clip((Z - z_floor) / (z_top - z_floor), 0, 1)
inside = (np.abs(X) <= hw) & (Y >= y_front) & (Z <= z_top) & (Z >= bottom) & behind_ok
occ = inside.reshape(n[0], n[1], n[2])

# --- round the vertical edges: 2-D opening per z slice with a disk, keeping the vallecula side untouched
r = int(round(mm(4.0) / P))
yy, xx = np.ogrid[-r:r + 1, -r:r + 1]
disk = (xx ** 2 + yy ** 2) <= r * r
protect_y = (np.nanmin(np.where(np.isfinite(yback), yback, np.nan)) - mm(5.0))   # everything behind this line is vallecula/fold detail
jcut = int(np.clip((protect_y - lo[1]) / P, 0, n[1]))
for k in range(n[2]):
    sl = occ[:, :, k]
    if not sl.any():
        continue
    opened = ndimage.binary_opening(sl, structure=disk)
    sl2 = sl.copy()
    sl2[:, :jcut] = opened[:, :jcut]
    occ[:, :, k] = sl2
lab, nl = ndimage.label(occ)
if nl > 1:
    sizes = np.bincount(lab.ravel()); sizes[0] = 0
    occ = lab == sizes.argmax()

# --- signed distance, light smoothing, marching cubes
import edt
phi = np.where(occ, -edt.edt(occ, anisotropy=(P,) * 3, black_border=True), edt.edt(~occ, anisotropy=(P,) * 3, black_border=False)).astype(np.float32)
phi = ndimage.gaussian_filter(phi, mm(0.3) / P, mode='nearest')
phi[np.abs(phi) < 1e-4] = 1e-4                       # keep the isosurface off the grid nodes (no degenerate triangles)
verts, faces, _, _ = measure.marching_cubes(phi, level=0.0, spacing=(P, P, P), allow_degenerate=False)
verts = verts + lo
m = trimesh.Trimesh(verts, faces, process=True)
m.fix_normals()
print('marching cubes: watertight', m.is_watertight, len(m.faces), 'faces')
def clean(mesh):
    # weld at the precision the 3MF will carry (5 decimals), so what we check is what is stored
    mesh = trimesh.Trimesh(np.round(mesh.vertices, 5), mesh.faces, process=True)
    mesh.merge_vertices(); mesh.fix_normals()
    # reload-stable check: every edge on exactly two faces after merging coincident vertices
    _, cnt = np.unique(mesh.edges_sorted, axis=0, return_counts=True)
    return mesh, bool(mesh.is_watertight and (cnt == 2).all())
chosen = None
for target in (80000, 90000, 100000, 120000):
    if len(m.faces) <= target: break
    m2, ok = clean(m.simplify_quadric_decimation(face_count=target))
    if ok:
        chosen = m2; break
if chosen is None:
    chosen, ok = clean(m); assert ok, 'raw marching-cubes mesh not clean'
m = chosen
print(f'tongue: {len(m.vertices)} verts, {len(m.faces)} faces, watertight={m.is_watertight}, volume {m.volume / S**3:.0f} mm3 at 1:1 (old block {old.volume / S**3:.0f})')
print('bbox', np.round(m.bounds, 1))
np.savez(out, v=np.round(m.vertices, 5), f=m.faces)   # float64; a PLY would round to float32 and pinch vertices
