"""quick multi-view render of build parts: python mrender.py BUILD out.png 'ids' [prefix=part|final]"""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import numpy as np, trimesh, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from render import render
B, out, ids = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(',')]
prefix = sys.argv[4] if len(sys.argv) > 4 else 'part'
views = [(int(a), int(e), t) for a, e, t in (v.split(':') for v in (sys.argv[5] if len(sys.argv) > 5 else '180:15:behind,90:10:right side,0:-10:front,0:89:above').split(','))]
COL = {1: (0.94, 0.91, 0.84), 2: (0.55, 0.74, 0.9), 3: (0.95, 0.8, 0.32), 4: (0.85, 0.45, 0.5), 5: (0.75, 0.15, 0.15), 6: (0.98, 0.72, 0.62), 7: (0.94, 0.85, 0.45)}
from partsconfig import PARTS
grp = {p[0]: p[3] for p in PARTS}
Vs, Fs, C, off = [], [], [], 0
for pid in ids:
    f = f'{B}/{prefix}_{pid:02d}.ply'
    if not os.path.exists(f): print('missing', f); continue
    m = trimesh.load(f, process=False); Vs.append(m.vertices); Fs.append(m.faces + off); off += len(m.vertices)
    C += [COL[grp.get(pid, 5)]] * len(m.faces)
V = np.vstack(Vs); F = np.vstack(Fs); C = np.array(C); V = V - V.mean(0)
fig, axs = plt.subplots(1, len(views), figsize=(7 * len(views), 7))
for ax, (az, el, t) in zip(np.atleast_1d(axs), views):
    ax.imshow(render(V, F, az, el, size=800, colors=C)); ax.set_title(t); ax.axis('off')
plt.tight_layout(); plt.savefig(out, dpi=60); print('wrote', out)
