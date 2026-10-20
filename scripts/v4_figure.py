"""Stage-2 (v4) figure: muscles on the framework, with the thyroid removed where it hides them, plus sections."""
import sys, os; sys.path.insert(0, 'scripts')
import numpy as np, trimesh, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from render import render
from partsconfig import PARTS
B = sys.argv[1]; out = sys.argv[2]; Z0 = 1359.0
cols = {1: (0.94, 0.91, 0.84), 2: (0.55, 0.74, 0.9), 3: (0.95, 0.8, 0.32), 4: (0.85, 0.45, 0.5), 5: (0.72, 0.2, 0.2)}
grp = {p[0]: p[3] for p in PARTS}; names = {p[0]: p[1] for p in PARTS}
def scene(ids, ctr=None, hide_side=None):
    Vs, Fs, C, off = [], [], [], 0
    for pid in ids:
        f = f'{B}/final_{pid:02d}.ply'
        if not os.path.exists(f): continue
        m = trimesh.load(f, process=False)
        if hide_side is not None and pid == 2:     # remove one thyroid lamina to look into the paraglottic space
            m = m.slice_plane([-0.65 + hide_side * 1.0, 0, 0], [-hide_side, 0, 0], cap=True)
        Vs.append(m.vertices); Fs.append(m.faces + off); off += len(m.vertices); C += [cols[grp[pid]]] * len(m.faces)
    V = np.vstack(Vs); return V - (ctr if ctr is not None else V.mean(0)), np.vstack(Fs), np.array(C)
ALL = [p[0] for p in PARTS]
NOHY = [i for i in ALL if i not in (1, 17, 18, 19, 20, 21, 22, 10, 23, 48, 49, 31, 32)]
fig, axs = plt.subplots(2, 4, figsize=(32, 16))
V, F, C = scene([i for i in ALL if i not in (1, 17, 18, 19, 20, 21, 22)]); axs[0, 0].imshow(render(V, F, 180, 12, size=800, colors=C)); axs[0, 0].set_title('From behind: posterior cricoarytenoids, interarytenoids, aryepiglottic', fontsize=14)
V, F, C = scene([i for i in ALL if i not in (1, 17, 18, 19, 20, 21, 22)]); axs[0, 1].imshow(render(V, F, 0, -8, size=800, colors=C)); axs[0, 1].set_title('From the front: cricothyroid (straight and oblique parts)', fontsize=14)
V, F, C = scene([i for i in ALL if i not in (1, 17, 18, 19, 20, 21, 22)]); axs[0, 2].imshow(render(V, F, 90, 5, size=800, colors=C)); axs[0, 2].set_title('Right side', fontsize=14)
V, F, C = scene(NOHY, hide_side=-1); axs[0, 3].imshow(render(V, F, 90, 5, size=800, colors=C)); axs[0, 3].set_title('Right side, right thyroid lamina removed: thyroarytenoid, lateral cricoarytenoid', fontsize=14)
V, F, C = scene([i for i in ALL if i not in (1, 17, 18, 19, 20, 21, 22, 10, 23, 48, 49, 31, 32, 6, 7, 8, 9)]); axs[1, 0].imshow(render(V, F, 0, 89, size=800, colors=C)); axs[1, 0].set_title('From above (anterior at the bottom): vocalis and thyroarytenoid beside the ligaments', fontsize=14)
for ax in axs[0, :].tolist() + [axs[1, 0]]: ax.axis('off')
COLS = {2: '#5b9bd5', 3: '#5b9bd5', 4: '#2060a0', 5: '#2060a0', 38: '#5b9bd5', 39: '#5b9bd5', 12: '#d08020', 13: '#d08020', 14: '#d0a040', 15: '#d0a040', 16: '#d0a040'}
def sect(ax, ids, org, nrm, ix, iy, title, xlim=None, ylim=None):
    for pid in ids:
        f = f'{B}/final_{pid:02d}.ply'
        if not os.path.exists(f): continue
        m = trimesh.load(f, process=False); s = m.section(plane_origin=org, plane_normal=nrm)
        if s is None: continue
        c = COLS.get(pid, '#b22222' if grp[pid] == 5 else '#999999')
        for e in s.discrete: ax.plot(e[:, ix], e[:, iy] - (Z0 if iy == 2 else 0), color=c, lw=1.3)
    ax.set_aspect('equal'); ax.grid(alpha=.3); ax.set_title(title, fontsize=13)
    if xlim: ax.set_xlim(*xlim)
    if ylim: ax.set_ylim(*ylim)
SEC = [2, 3, 4, 5, 12, 13, 14, 15, 16, 24, 25, 26, 27, 28, 29, 30, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49]
sect(axs[1, 1], SEC, [0, -103.0, 0], [0, 1, 0], 0, 2, 'Coronal, mid-fold (y = -103): TA (red) with vocalis beside the ligament (orange), conus (yellow)', (-18, 18), (20, 66))
sect(axs[1, 2], SEC, [0, 0, Z0 + 47.0], [0, 0, 1], 0, 1, 'Axial at the vocal ligament (z = 47): folds, TA, LCA, arytenoids', (-18, 18), (-116, -80))
sect(axs[1, 3], SEC, [0, 0, Z0 + 32.0], [0, 0, 1], 0, 1, 'Axial through the cricoid (z = 32): PCA behind the lamina, CT in front of the arch', (-18, 18), (-116, -80))
plt.tight_layout(); plt.savefig(out, dpi=55); print('wrote', out)
