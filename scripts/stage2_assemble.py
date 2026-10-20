"""Stage 2: stamp parts into a label grid, hollow the trachea, seat it under the cricoid."""
import sys, json, time, numpy as np, edt
from scipy import ndimage
sys.path.insert(0, '/tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad/scripts')
from partsconfig import PARTS
B = '/tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad/build'
g = np.load(f'{B}/grid.npy'); lo = g[:3]; P = g[3]; shape = tuple(int(x) for x in g[4:7]); z_cut = g[7]
WALL = 2.0          # tracheal wall thickness, mm (CT normal 1-3 mm)
ENV = 2.5           # half-window (mm) along z used to fill ring grooves before offsetting the lumen
def occ(pid):
    d = np.load(f'{B}/occ_{pid:02d}.npz'); a, b = d['a'], d['b']
    return d['occ'], tuple(slice(int(x), int(y)) for x, y in zip(a, b))

# ---- trachea: hollow with a smooth lumen (rings stay on the outside) ----
T, ts = occ(11)
env = ndimage.maximum_filter1d(T, size=int(2 * ENV / P) + 1, axis=2)
inside2d = edt.edt(env, anisotropy=(P, P, 1e6), black_border=False, parallel=2)
lumen = inside2d > WALL
Tw = T & ~lumen
print('trachea wall volume %.0f mm3, lumen voxels %d' % (Tw.sum() * P**3, lumen.sum()))

# ---- seat trachea under the cricoid: remove trachea above the cricoid's inferior border ----
C, cs = occ(3)
full = np.zeros(shape, bool); full[cs] = C
Cf = full[ts]   # cricoid in trachea sub-box
zidx = np.arange(Cf.shape[2])
has = Cf.any(2)
zlow = np.where(has, np.argmax(Cf, axis=2), 10**6).astype(float)   # lowest cricoid voxel per column
foot = ndimage.binary_fill_holes(ndimage.binary_dilation(has, iterations=int(1.5 / P)))
# columns inside the ring (no cricoid voxels) take the inferior-border height of the nearest cricoid column
_, (ii, jj) = ndimage.distance_transform_edt(~has, return_indices=True)
zb = np.where(foot, zlow[ii, jj], 10**6)
keep = zidx[None, None, :] <= (zb[:, :, None] + int(0.6 / P))      # 0.6 mm overlap = cricotracheal ligament seam
removed = (Tw & ~keep).sum()
Tw &= keep
lumen &= zidx[None, None, :] <= zb[:, :, None]
print('trachea voxels removed inside/above the cricoid: %.0f mm3' % (removed * P**3))
np.savez_compressed(f'{B}/trachea_lumen.npz', lumen=lumen, s=np.array([[s.start, s.stop] for s in ts]))

# ---- stamp labels by priority (low first, high overwrites) ----
L = np.zeros(shape, np.uint8)
for pid, name, concepts, grp, pri, kind in sorted(PARTS, key=lambda p: p[4]):
    if pid == 11:
        o, s = Tw, ts
    else:
        o, s = occ(pid)
    sub = L[s]; sub[o] = pid
# airway lumen of the trachea must stay empty
sub = L[ts]; sub[lumen] = 0
L[:, :, :int(round((z_cut - lo[2]) / P))] = 0
np.save(f'{B}/labels_raw.npy', L)
for pid, name, *_ in PARTS:
    print(f'{pid:2d} {name:30s} {np.count_nonzero(L == pid) * P**3:8.1f} mm3')
