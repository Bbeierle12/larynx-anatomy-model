import sys, os; sys.path.insert(0, 'scripts')
import numpy as np, trimesh, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from render import render
from partsconfig import PARTS
cols = {1: (0.94, 0.91, 0.84), 2: (0.55, 0.74, 0.9), 3: (0.95, 0.8, 0.32), 4: (0.85, 0.45, 0.5)}
grp = {p[0]: p[3] for p in PARTS}
GLOTTIS = [2, 3, 4, 5, 6, 7, 12, 13, 14, 15, 16, 24, 25, 28, 29, 30, 11, 33, 34]
def scene(B, ids=None, ctr=None):
    Vs, Fs, C, off = [], [], [], 0
    for pid in grp:
        f = f'{B}/final_{pid:02d}.ply'
        if (ids and pid not in ids) or not os.path.exists(f): continue
        m = trimesh.load(f, process=False); Vs.append(m.vertices); Fs.append(m.faces + off); off += len(m.vertices); C += [cols[grp[pid]]] * len(m.faces)
    V = np.vstack(Vs); return V - (ctr if ctr is not None else V.mean(0)), np.vstack(Fs), np.array(C)
def crop(im, V, F, az, el):  # same scale for v1/v2 by padding? keep as is
    return im
fig = plt.figure(figsize=(24, 15))
gs = fig.add_gridspec(2, 3)
# glottis from above, with everything above the vocal folds hidden (thyroid kept for orientation)
for k, (B, t) in enumerate([('build', 'Version 1: source glottis (semi-closed)'), ('build3', 'Version 2: quiet-breathing position')]):
    V, F, C = scene(B, GLOTTIS)
    zc = trimesh.load(f'{B}/final_union.ply', process=False).bounds[0, 2]
    # keep only faces below the top of the arytenoids + 1 mm, to look down on the folds
    za = trimesh.load(f'{B}/final_04.ply', process=False).bounds[1, 2] + 1.0
    Vw = V + V.mean(0) * 0
    ax = fig.add_subplot(gs[0, k])
    im = render(V, F, 0, 89, size=700, colors=C)
    ax.imshow(im); ax.set_title(t + '\nviewed from above, supraglottic parts hidden; anterior at bottom', fontsize=15); ax.axis('off')
# posterior-oblique whole model, same scale
Vb, Fb, Cb = scene('build'); V3, F3, C3 = scene('build3')
for k, (V, F, C, t) in enumerate([(Vb, Fb, Cb, 'Version 1'), (V3, F3, C3, 'Version 2')]):
    ax = fig.add_subplot(gs[1, k]); im = render(V, F, 150, 15, size=700, colors=C)
    ax.imshow(im); ax.set_title(t + ': posterior-oblique view (patient right side)', fontsize=15); ax.axis('off')
ax = fig.add_subplot(gs[0, 2]); ax.axis('off')
rows = [('Measure', 'v1', 'v2', 'Adult male reference'),
        ('Glottal area (mm²)', '73', '139', '140.7 ± 8.6, quiet breathing'),
        ('Largest circle in glottis (mm)', '4.6', '9.4', 'scope 5.8 mm'),
        ('Largest sphere through airway (mm)', '5.3', '8.8', ''),
        ('Glottis length (mm)', '19.1', '21.8', '22.1 ± 3.1'),
        ('Cricoid lamina height (mm)', '12.2', '21.4', '21.5 ± 2.0 to 24.5 ± 2.8'),
        ('Cricothyroid gap (mm)', '2.6', '8.7', '7.9 ± 2.2 (CT)'),
        ('Subglottis depth × width (mm)', '12.0 × 15.0', '15.6 × 14.9', 'depth 17.4 ± 2.3'),
        ('Trachea lumen width × depth (mm)', '18.4 × 13.3', '18.5 × 18.1', 'ratio ≈ 1'),
        ('Hyoid to cricoid lower border (mm)', '42.4', '49.5', '53.5 ± 6.1 (MRI)')]
tb = ax.table(cellText=[list(r) for r in rows[1:]], colLabels=list(rows[0]), loc='center', cellLoc='left', colWidths=[0.40, 0.14, 0.14, 0.34])
tb.auto_set_font_size(False); tb.set_fontsize(12); tb.scale(1.08, 2.2)
ax.set_title('Key measurements', fontsize=15)
# mid-sagittal sections
ax = fig.add_subplot(gs[1, 2])
for B, c, lab, dx in [('build', '#999999', 'v1', 0), ('build3', '#3070c0', 'v2', 0)]:
    zc = 1366.05 - 22.2   # same anatomical reference for both: v2 tracheal cut level
    for pid in (2, 3, 4, 5):
        m = trimesh.load(f'{B}/final_{pid:02d}.ply', process=False)
        s = m.section(plane_origin=[-0.65 if pid in (2, 3) else (-4.5 if pid == 4 else 3.5), 0, 0], plane_normal=[1, 0, 0])
        if s is None or pid in (4, 5): continue
        for e in s.discrete: ax.plot(e[:, 1], e[:, 2] - zc, color=c, lw=1.6, label=lab if pid == 3 else None)
h, l = ax.get_legend_handles_labels(); d = dict(zip(l, h)); ax.legend(d.values(), d.keys(), fontsize=13)
ax.set_aspect('equal'); ax.grid(alpha=.3); ax.set_xlabel('y (mm, anterior left)'); ax.set_ylabel('mm (same body coordinates in both)')
ax.set_title('Mid-sagittal outline: thyroid (unchanged) and cricoid', fontsize=15)
plt.tight_layout(); plt.savefig(sys.argv[1], dpi=60)
