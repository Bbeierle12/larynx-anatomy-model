"""Reshape the BodyParts3D trachea so its outer outline continues the cricoid's inferior ring, then re-voxelize."""
import numpy as np, trimesh, igl
from scipy import ndimage
import os
B = os.environ.get('BUILD', '/tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad/build')
g = np.load(f'{B}/grid.npy'); lo = g[:3]; P = g[3]; shape = tuple(int(x) for x in g[4:7])
d = np.load(f'{B}/occ_03.npz'); C, ca = d['occ'], d['a']
# cricoid outer outline at its lowest complete-ring level
best = None
for k in range(C.shape[2]):
    s = C[:, :, k]
    if not s.any(): continue
    hole = ndimage.binary_fill_holes(s) & ~s
    if hole.sum() * P * P > 100:
        best = k; break
best = min(best + int(round(2.0 / P)), C.shape[2] - 1)   # 2 mm above the rounded lower edge: full outer outline
s = C[:, :, best]
MATCH = os.environ.get('MATCH', 'outer')      # 'outer': trachea outer follows the cricoid outer; 'lumen': trachea lumen follows the cricoid lumen
if MATCH == 'lumen':
    hole = ndimage.binary_fill_holes(s) & ~s
    xs = np.nonzero(hole.any(1))[0]; ys = np.nonzero(hole.any(0))[0]
    WALL = 2.0; CLEAR = float(os.environ.get('LUMEN_STEP', '0.3'))
    cw = (xs.max() - xs.min()) * P + 2 * (WALL + CLEAR); cd = (ys.max() - ys.min()) * P + 2 * (WALL + CLEAR)
else:
    xs = np.nonzero(s.any(1))[0]; ys = np.nonzero(s.any(0))[0]
    cw = (xs.max() - xs.min()) * P; cd = (ys.max() - ys.min()) * P
cx = lo[0] + (ca[0] + (xs.min() + xs.max()) / 2) * P; cy = lo[1] + (ca[1] + (ys.min() + ys.max()) / 2) * P
zc = lo[2] + (ca[2] + best) * P
m = trimesh.load(f'{B}/part_11.ply')
sec = m.section(plane_origin=[0, 0, zc - 3], plane_normal=[0, 0, 1]).vertices
tw = np.ptp(sec[:, 0]); td = np.ptp(sec[:, 1]); tx = (sec[:, 0].min() + sec[:, 0].max()) / 2; ty = (sec[:, 1].min() + sec[:, 1].max()) / 2
sx = np.clip(cw / tw, 0.9, 1.3); sy = np.clip(cd / td, 0.9, 1.6)
print(f'cricoid ring at z={zc:.1f} ({MATCH} match): target trachea outer {cw:.1f} x {cd:.1f}, centre ({cx:.1f},{cy:.1f}); trachea 3 mm below: {tw:.1f} x {td:.1f}, centre ({tx:.1f},{ty:.1f})')
print(f'scale trachea x {sx:.3f}, y {sy:.3f}; shift to cricoid centre by ({cx-tx:.2f},{cy-ty:.2f})')
M = np.eye(4); M[0, 0] = sx; M[1, 1] = sy
M[0, 3] = tx - sx * tx + (cx - tx); M[1, 3] = ty - sy * ty + (cy - ty)
m.apply_transform(M); m.export(f'{B}/part_11.ply')
a = np.clip(np.floor((m.bounds[0] - 0.3 - lo) / P).astype(int), 0, None)
b = np.minimum(np.ceil((m.bounds[1] + 0.3 - lo) / P).astype(int) + 1, shape)
xs_, ys_, zs_ = [lo[i] + P * np.arange(a[i], b[i]) for i in range(3)]
G = np.stack(np.meshgrid(xs_, ys_, zs_, indexing='ij'), -1).reshape(-1, 3)
V = np.ascontiguousarray(m.vertices, np.float64); F = np.ascontiguousarray(m.faces, np.int64)
w = np.empty(len(G), np.float32)
for k in range(0, len(G), 3_000_000):
    w[k:k + 3_000_000] = igl.fast_winding_number(V, F, np.ascontiguousarray(G[k:k + 3_000_000]))
occ = (w > 0.5).reshape(len(xs_), len(ys_), len(zs_))
np.savez_compressed(f'{B}/occ_11.npz', occ=occ, a=a, b=b)
np.save(f'{B}/trachea_scale.npy', np.array([sx, sy, cx - tx, cy - ty]))
print('trachea solid %.0f mm3' % (occ.sum() * P**3))
