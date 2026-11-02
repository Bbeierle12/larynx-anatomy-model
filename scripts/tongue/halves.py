"""Find the rigid transform from a whole-model 3MF frame to a half's frame (via an unclipped part on that
side), find the sagittal cut plane, and clip + transform the new tongue into the half.
Usage: python halves.py <v6 whole.3mf> <v6 halves.3mf> <side R|L> <tongue_whole.npz> <out.npz>"""
import sys, itertools, numpy as np, trimesh
from trimesh import registration
from parts import read_parts

whole_path, half_path, side, tongue_path, out = sys.argv[1:6]
W, H = read_parts(whole_path), read_parts(half_path)
ary = f'Arytenoid cartilage {side}'
aw = W[ary][0][1]
ah = H[ary][0][1]
assert len(aw.vertices) == len(ah.vertices), (len(aw.vertices), len(ah.vertices))

# candidate initial rotations: the 24 axis-aligned ones; ICP from each, keep the best
best = None
for perm in itertools.permutations(range(3)):
    for signs in itertools.product([1, -1], repeat=3):
        R = np.zeros((3, 3))
        for i, p in enumerate(perm):
            R[i, p] = signs[i]
        if np.linalg.det(R) < 0:
            continue
        T0 = np.eye(4); T0[:3, :3] = R
        T0[:3, 3] = ah.vertices.mean(0) - R @ aw.vertices.mean(0)
        try:
            T, transformed, cost = registration.icp(aw.vertices, ah.vertices, initial=T0, max_iterations=40, scale=False)
        except Exception:
            continue
        if best is None or cost < best[1]:
            best = (T, cost)
T, cost = best
print(f'{side}: icp cost {cost:.4f}')
# verify on the corniculate (also unclipped, small, asymmetric)
cw = W[f'Corniculate cartilage {side}'][0][1]; ch = H[f'Corniculate cartilage {side}'][0][1]
pts = trimesh.transform_points(cw.vertices, T)
d = ch.nearest.on_surface(pts)[1]
print(f'   corniculate check: max distance {d.max():.3f} mm, mean {d.mean():.3f}')
assert d.max() < 0.15, 'transform not exact'

# the cut plane, in the whole frame: the clipped hyoid's flat face
hyh = H['Hyoid bone'][0][1]
Tinv = np.linalg.inv(T)
hv = trimesh.transform_points(hyh.vertices, Tinv)
xcut = hv[:, 0].max() if side == 'R' else hv[:, 0].min()
print(f'   half hyoid x range in whole frame: {hv[:,0].min():.2f} .. {hv[:,0].max():.2f}')
flat = np.abs(hv[:, 0] - xcut) < 0.05
print(f'   cut plane x = {xcut:.3f} ({flat.sum()} hyoid vertices on it)')

_d = np.load(tongue_path); tongue = trimesh.Trimesh(_d['v'], _d['f'], process=False)
normal = np.array([-1.0, 0, 0]) if hv[:, 0].mean() < xcut else np.array([1.0, 0, 0])   # keep the side the half's hyoid is on
import manifold3d as m3
man = m3.Manifold(m3.Mesh(tongue.vertices.astype(np.float32), tongue.faces.astype(np.uint32)))
lo, hi = tongue.bounds[0] - 5, tongue.bounds[1] + 5
if normal[0] < 0: hi[0] = xcut        # keep x <= xcut
else: lo[0] = xcut                    # keep x >= xcut
box = m3.Manifold.cube(hi - lo).translate(lo)
cut = man ^ box
mm_ = cut.to_mesh()
half_t = trimesh.Trimesh(np.asarray(mm_.vert_properties)[:, :3], np.asarray(mm_.tri_verts), process=True); half_t.fix_normals()
print(f'   tongue half: {len(half_t.faces)} faces, watertight {half_t.is_watertight}, volume {half_t.volume:.0f} (whole {tongue.volume:.0f})')
half_t.apply_transform(T)
np.savez(out, v=np.round(half_t.vertices, 5), f=half_t.faces)
np.save(out + '.T.npy', T)
