"""Stage-1 (v3) comparison figure: v2 vs v3 framework and glottis."""
import sys, os; sys.path.insert(0, 'scripts')
import numpy as np, trimesh, shapely, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from shapely.geometry import Point, box as sbox
from shapely.ops import unary_union
from render import render
from partsconfig import PARTS
cols = {1: (0.94, 0.91, 0.84), 2: (0.55, 0.74, 0.9), 3: (0.95, 0.8, 0.32), 4: (0.85, 0.45, 0.5)}
grp = {p[0]: p[3] for p in PARTS}
BA, BB = sys.argv[1], sys.argv[2]; out = sys.argv[3]
def scene(B, ids=None, ctr=None):
    Vs, Fs, C, off = [], [], [], 0
    for pid in grp:
        f = f'{B}/final_{pid:02d}.ply'
        if (ids and pid not in ids) or not os.path.exists(f): continue
        m = trimesh.load(f, process=False); Vs.append(m.vertices); Fs.append(m.faces + off); off += len(m.vertices); C += [cols[grp[pid]]] * len(m.faces)
    V = np.vstack(Vs); return V - (ctr if ctr is not None else V.mean(0)), np.vstack(Fs), np.array(C)
fig, axs = plt.subplots(2, 4, figsize=(30, 15))
FR = [2, 3, 4, 5, 6, 7, 11, 33, 34, 35, 36, 37]
for k, (B, t) in enumerate([(BA, 'v2'), (BB, 'v3 (stage 1)')]):
    V, F, C = scene(B, FR)
    axs[0, k].imshow(render(V, F, 180, 15, size=700, colors=C)); axs[0, k].set_title(f'{t}: framework from behind', fontsize=15); axs[0, k].axis('off')
    GL = [2, 3, 4, 5, 6, 7, 12, 13, 14, 15, 16, 24, 25, 28, 29, 30, 11, 33, 34, 37]
    V, F, C = scene(B, GL)
    axs[1, k].imshow(render(V, F, 0, 89, size=700, colors=C)); axs[1, k].set_title(f'{t}: glottis from above (anterior at bottom)', fontsize=15); axs[1, k].axis('off')
# mid-sagittal and junction sections
for k, (B, t, c) in enumerate([(BA, 'v2', '#999999'), (BB, 'v3', '#3070c0')]):
    ax = axs[0, 2]
    for pid in (2, 3, 1, 10, 22):
        m = trimesh.load(f'{B}/final_{pid:02d}.ply', process=False)
        s = m.section(plane_origin=[-0.65, 0, 0], plane_normal=[1, 0, 0])
        if s is None: continue
        for e in s.discrete: ax.plot(e[:, 1], e[:, 2] - 1359.0, color=c, lw=1.4, label=t if pid == 3 else None)
    ax = axs[0, 3]
    for pid in (3, 4, 2):
        m = trimesh.load(f'{B}/final_{pid:02d}.ply', process=False)
        s = m.section(plane_origin=[0, -92.0 if B == BB else -94.0, 0], plane_normal=[0, 1, 0])
        if s is None: continue
        for e in s.discrete: ax.plot(e[:, 0], e[:, 2] - 1359.0, color=c, lw=1.4, label=t if pid == 3 else None)
for ax, t in [(axs[0, 2], 'Mid-sagittal: hyoid, thyroid, cricoid, epiglottis, hyo-epiglottic lig.'), (axs[0, 3], 'Coronal through the cricoarytenoid facets: cricoid, arytenoid, thyroid horns')]:
    h, l = ax.get_legend_handles_labels(); d = dict(zip(l, h)); ax.legend(d.values(), d.keys(), fontsize=12)
    ax.set_aspect('equal'); ax.grid(alpha=.3); ax.set_title(t, fontsize=13); ax.set_ylabel('mm above tracheal cut')
# cricotracheal junction: union sections
for k, B in enumerate([BA, BB]):
    ax = axs[1, 2 + k]
    for pid, c in [(3, '#5b9bd5'), (11, '#5b9bd5'), (34, '#d05060'), (37, '#d05060'), (33, '#d05060')]:
        f = f'{B}/final_{pid:02d}.ply'
        if not os.path.exists(f): continue
        m = trimesh.load(f, process=False)
        s = m.section(plane_origin=[-0.65, 0, 0], plane_normal=[1, 0, 0])
        if s is None: continue
        for e in s.discrete: ax.plot(e[:, 1], e[:, 2] - 1359.0, color=c, lw=1.2)
    ax.set_xlim(-116, -84); ax.set_ylim(5, 32); ax.set_aspect('equal'); ax.grid(alpha=.3)
    ax.set_title(('v2' if k == 0 else 'v3') + ': cricotracheal junction, mid-sagittal (blue cartilage, red ligament)', fontsize=13)
plt.tight_layout(); plt.savefig(out, dpi=55)
