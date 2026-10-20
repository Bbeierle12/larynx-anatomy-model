"""Enclosed voids of a build: voxels in no part and not reachable from the exterior/airway.  python voids.py BUILD"""
import sys, os, numpy as np
from scipy import ndimage
sys.path.insert(0, os.path.dirname(__file__))
from musclelib import Grid
from partsconfig import PARTS
B = sys.argv[1]; grid = Grid(f'{B}/grid.npy'); P = grid.P; Z0 = grid.z_cut
shape = tuple(grid.shape) if hasattr(grid, 'shape') else None
occ_all = None
for pid, *_ in PARTS:
    f = f'{B}/occ_{pid:02d}.npz'
    if not os.path.exists(f): continue
    d = np.load(f); o, a, b = d['occ'], d['a'], d['b']
    if occ_all is None:
        g = np.load(f'{B}/grid.npy'); n = g[4:7].astype(int); occ_all = np.zeros(tuple(n), bool); lo = g[:3]
    occ_all[a[0]:b[0], a[1]:b[1], a[2]:b[2]] |= o
k0 = int(np.floor((Z0 - lo[2]) / P))
occ_all[:, :, :k0] = False
air = ~occ_all
lab, n = ndimage.label(air)
edge = np.unique(np.concatenate([lab[0].ravel(), lab[-1].ravel(), lab[:, 0].ravel(), lab[:, -1].ravel(), lab[:, :, 0].ravel(), lab[:, :, -1].ravel(), lab[:, :, k0].ravel()]))
sizes = ndimage.sum(air, lab, index=np.arange(1, n + 1)) * P ** 3
print('exterior components:', len(edge), 'total air components', n)
voids = [(i + 1, s) for i, s in enumerate(sizes) if (i + 1) not in edge and s > 5]
voids.sort(key=lambda t: -t[1])
for i, s in voids[:15]:
    idx = np.argwhere(lab == i); mn = lo + idx.min(0) * P; mx = lo + idx.max(0) * P
    c = lo + idx.mean(0) * P
    print(f'void {i}: {s:7.0f} mm3  x {mn[0]:6.1f}..{mx[0]:6.1f}  y {mn[1]:7.1f}..{mx[1]:7.1f}  z {mn[2]-Z0:5.1f}..{mx[2]-Z0:5.1f}  centre ({c[0]:.1f}, {c[1]:.1f}, {c[2]-Z0:.1f})')
np.save(f'{B}/voids_lab.npy', lab.astype(np.int32)); np.save(f'{B}/voids_ids.npy', np.array([i for i, _ in voids]))
