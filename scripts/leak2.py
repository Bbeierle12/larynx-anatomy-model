"""Bottleneck of the leak from an interior space: python leak2.py BUILD x y z(rel)"""
import sys, os, numpy as np, edt
from scipy import ndimage
sys.path.insert(0, os.path.dirname(__file__))
from partsconfig import PARTS
B = sys.argv[1]; seed_mm = np.array([float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])])
g = np.load(f'{B}/grid.npy'); LO = g[:3]; P = g[3]; NG = g[4:7].astype(int); Z0 = g[7]; seed_mm[2] += Z0
occ = np.zeros(tuple(NG), bool)
for pid, *_ in PARTS:
    f = f'{B}/occ_{pid:02d}.npz'
    if not os.path.exists(f): continue
    d = np.load(f); o, a, b = d['occ'], d['a'], d['b']; occ[a[0]:b[0], a[1]:b[1], a[2]:b[2]] |= o
k0 = int(np.floor((Z0 - LO[2]) / P)); occ[:, :, :k0] = True
sv = tuple(((seed_mm - LO) / P).astype(int))
D = edt.edt(~occ, anisotropy=(P, P, P), black_border=False)      # distance of air voxels to the nearest solid
def comp_at(r):
    air = D >= r; lab, n = ndimage.label(air); s = lab[sv]
    if s == 0: return None, None
    c = lab == s
    t = c[0].any() or c[-1].any() or c[:, 0].any() or c[:, -1].any() or c[:, :, -1].any() or c[:, :, k0].any()
    return c, t
rs = np.arange(0.3, 2.01, 0.1); prev = None
for r in rs:
    c, t = comp_at(r)
    if c is None: print(f'r {r:.1f}: seed swallowed'); break
    print(f'r {r:.1f}: component {c.sum()*P**3:.0f} mm3, touches outside {t}')
    if not t:
        cprev, _ = comp_at(r - 0.1)
        neck = cprev & (D < r + 0.05) & ~c
        # keep only neck voxels adjacent to the enclosed component (within 0.3 mm) AND adjacent to the outside remainder
        near_in = ndimage.binary_dilation(c, iterations=3) & neck
        rest = cprev & ~c & ~near_in
        near_out = ndimage.binary_dilation(rest, iterations=3) & near_in
        lab2, n2 = ndimage.label(near_out)
        sizes = ndimage.sum(near_out, lab2, index=np.arange(1, n2 + 1))
        print(f'  leak channels narrower than {2*r:.1f} mm (candidates, largest first):')
        for i in np.argsort(-sizes)[:10]:
            idx = np.argwhere(lab2 == i + 1); mn = LO + idx.min(0) * P; mx = LO + idx.max(0) * P; cc = LO + idx.mean(0) * P
            print(f'  {sizes[i]*P**3:6.1f} mm3  x {mn[0]:6.1f}..{mx[0]:6.1f}  y {mn[1]:7.1f}..{mx[1]:7.1f}  z {mn[2]-Z0:5.1f}..{mx[2]-Z0:5.1f}  centre ({cc[0]:.1f}, {cc[1]:.1f}, {cc[2]-Z0:.1f})')
        break
