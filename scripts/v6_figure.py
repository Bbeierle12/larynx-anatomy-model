"""Stage-3 (v6) figure: inlet from above, coronal sections through the folds, mid-sagittal, and a cut-away."""
import sys, os; sys.path.insert(0, 'scripts')
import numpy as np, trimesh, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from render import render
from partsconfig import PARTS
B = sys.argv[1]; out = sys.argv[2]; Z0 = 1359.0
cols = {1: (0.94, 0.91, 0.84), 2: (0.55, 0.74, 0.9), 3: (0.95, 0.8, 0.32), 4: (0.85, 0.45, 0.5), 5: (0.72, 0.2, 0.2), 6: (0.98, 0.72, 0.62), 7: (0.94, 0.85, 0.45)}
grp = {p[0]: p[3] for p in PARTS}
def scene(ids, cut=None):
    Vs, Fs, C, off = [], [], [], 0
    for pid in ids:
        f = f'{B}/final_{pid:02d}.ply'
        if not os.path.exists(f): continue
        m = trimesh.load(f, process=False)
        if cut is not None:
            m = m.slice_plane(cut[0], cut[1], cap=True)
            if m.is_empty: continue
        Vs.append(m.vertices); Fs.append(m.faces + off); off += len(m.vertices); C += [cols[grp[pid]]] * len(m.faces)
    V = np.vstack(Vs); return V - V.mean(0), np.vstack(Fs), np.array(C)
ALL = [p[0] for p in PARTS]
fig, axs = plt.subplots(2, 4, figsize=(32, 16))
V, F, C = scene([i for i in ALL if i not in (1, 17, 18, 19, 20, 21, 22)]); axs[0, 0].imshow(render(V, F, 0, 89, size=800, colors=C)); axs[0, 0].set_title('Laryngeal inlet from above: epiglottis, aryepiglottic folds with tubercles, false folds, glottis', fontsize=13)
V, F, C = scene([i for i in ALL if i not in (1, 17, 18, 19, 20, 21, 22)], cut=([-0.65, 0, 0], [1, 0, 0])); axs[0, 1].imshow(render(V, F, 270, 0, size=800, colors=C)); axs[0, 1].set_title('Mid-sagittal cut, seen from the left: epiglottis, tubercle, false and true folds, interarytenoid mucosa', fontsize=13)
V, F, C = scene([i for i in ALL if i not in (1, 17, 18, 19, 20, 21, 22)], cut=([0, -103.0, 0], [0, 1, 0])); axs[0, 2].imshow(render(V, F, 0, 0, size=800, colors=C)); axs[0, 2].set_title('Coronal cut at mid-fold (y = -103), seen from the front', fontsize=13)
V, F, C = scene([i for i in ALL if i not in (1, 17, 18, 19, 20, 21, 22)]); axs[0, 3].imshow(render(V, F, 160, 30, size=800, colors=C)); axs[0, 3].set_title('From behind and above', fontsize=13)
for ax in axs[0]: ax.axis('off')
COLS = {2: '#5b9bd5', 3: '#5b9bd5', 4: '#2060a0', 5: '#2060a0', 38: '#5b9bd5', 39: '#5b9bd5', 10: '#c0a000', 12: '#d08020', 13: '#d08020', 14: '#d0a040', 15: '#d0a040', 16: '#d0a040', 54: '#d08020', 55: '#d08020', 56: '#d0a040', 57: '#d0a040'}
def sect(ax, ids, org, nrm, ix, iy, title, xlim=None, ylim=None):
    for pid in ids:
        f = f'{B}/final_{pid:02d}.ply'
        if not os.path.exists(f): continue
        m = trimesh.load(f, process=False); s = m.section(plane_origin=org, plane_normal=nrm)
        if s is None: continue
        c = COLS.get(pid, '#b22222' if grp[pid] == 5 else ('#8030a0' if grp[pid] == 6 else '#999999'))
        for e in s.discrete: ax.plot(e[:, ix], e[:, iy] - (Z0 if iy == 2 else 0), color=c, lw=1.3)
    ax.set_aspect('equal'); ax.grid(alpha=.3); ax.set_title(title, fontsize=13)
    if xlim: ax.set_xlim(*xlim)
    if ylim: ax.set_ylim(*ylim)
SEC = [i for i in ALL if i not in (1, 17, 18, 19, 20, 21, 22, 11, 33, 34, 37)]
sect(axs[1, 0], SEC, [0, -106.0, 0], [0, 1, 0], 0, 2, 'Coronal y = -106: true fold (cover purple, muscle red, ligament orange), ventricle, false fold, tubercle', (-16, 16), (36, 66))
sect(axs[1, 1], SEC, [0, -100.0, 0], [0, 1, 0], 0, 2, 'Coronal y = -100', (-16, 16), (36, 66))
sect(axs[1, 2], SEC, [0, 0, Z0 + 47.0], [0, 0, 1], 0, 1, 'Axial at the glottis (z = 47): folds with cover', (-18, 18), (-118, -80))
sect(axs[1, 3], SEC, [0, 0, Z0 + 54.0], [0, 0, 1], 0, 1, 'Axial at the false folds (z = 54): vestibule, epiglottic tubercle, quadrangular membranes', (-18, 18), (-118, -80))
plt.tight_layout(); plt.savefig(out, dpi=55); print('wrote', out)
