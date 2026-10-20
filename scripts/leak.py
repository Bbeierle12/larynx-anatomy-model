"""Where does an interior space leak to the outside?  python leak.py BUILD x y z(rel) [ids to skip]"""
import sys, os, numpy as np
from scipy import ndimage
sys.path.insert(0, os.path.dirname(__file__))
from partsconfig import PARTS
B = sys.argv[1]; seed_mm = np.array([float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])])
skip = [int(x) for x in sys.argv[5:]]
g = np.load(f'{B}/grid.npy'); LO = g[:3]; P = g[3]; NG = g[4:7].astype(int); Z0 = g[7]; seed_mm[2] += Z0
occ = np.zeros(tuple(NG), bool)
for pid, *_ in PARTS:
    f = f'{B}/occ_{pid:02d}.npz'
    if pid in skip or not os.path.exists(f): continue
    d = np.load(f); o, a, b = d['occ'], d['a'], d['b']; occ[a[0]:b[0], a[1]:b[1], a[2]:b[2]] |= o
k0 = int(np.floor((Z0 - LO[2]) / P)); occ[:, :, :k0] = True
sv = tuple(((seed_mm - LO) / P).astype(int))
print('seed voxel solid?', occ[sv])
def enclosed(solid):
    air = ~solid; lab, n = ndimage.label(air)
    s = lab[sv]
    if s == 0: return None, None
    comp = lab == s
    touches = comp[0].any() or comp[-1].any() or comp[:, 0].any() or comp[:, -1].any() or comp[:, :, -1].any() or comp[:, :, k0].any()
    return comp, touches
comp0, t0 = enclosed(occ)
print('undilated: component %.0f mm3, touches outside: %s' % (comp0.sum() * P**3, t0))
prev = comp0
for r in (0.5, 1.0, 1.5, 2.0, 3.0, 4.0):
    n_ = int(round(r / P)); solid = ndimage.binary_dilation(occ, iterations=n_)
    comp, t = enclosed(solid)
    if comp is None: print(f'dilate {r}: seed swallowed'); break
    print(f'dilate {r} mm: component {comp.sum()*P**3:.0f} mm3, touches outside: {t}')
    if not t:
        # neck: voxels of the undilated component that are outside the enclosed one but within 2*r of it
        near = ndimage.binary_dilation(comp, iterations=2 * n_) & comp0 & ~comp
        lab2, n2 = ndimage.label(near)
        sizes = ndimage.sum(near, lab2, index=np.arange(1, n2 + 1))
        for i in np.argsort(-sizes)[:6]:
            idx = np.argwhere(lab2 == i + 1); mn = LO + idx.min(0) * P; mx = LO + idx.max(0) * P; c = LO + idx.mean(0) * P
            print(f'  neck {sizes[i]*P**3:6.1f} mm3  x {mn[0]:6.1f}..{mx[0]:6.1f}  y {mn[1]:7.1f}..{mx[1]:7.1f}  z {mn[2]-Z0:5.1f}..{mx[2]-Z0:5.1f}  centre ({c[0]:.1f}, {c[1]:.1f}, {c[2]-Z0:.1f})')
        break
