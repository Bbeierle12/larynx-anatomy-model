"""v2 vs v3 (stage 1) summary sheet."""
import sys, os; sys.path.insert(0, 'scripts')
import numpy as np, trimesh, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from render import render
from partsconfig import PARTS
cols = {1: (0.94, 0.91, 0.84), 2: (0.55, 0.74, 0.9), 3: (0.95, 0.8, 0.32), 4: (0.85, 0.45, 0.5)}
grp = {p[0]: p[3] for p in PARTS}
def scene(B, ids=None):
    Vs, Fs, C, off = [], [], [], 0
    for pid in grp:
        f = f'{B}/final_{pid:02d}.ply'
        if (ids and pid not in ids) or not os.path.exists(f): continue
        m = trimesh.load(f, process=False); Vs.append(m.vertices); Fs.append(m.faces + off); off += len(m.vertices); C += [cols[grp[pid]]] * len(m.faces)
    V = np.vstack(Vs); return V - V.mean(0), np.vstack(Fs), np.array(C)
fig = plt.figure(figsize=(24, 15)); gs = fig.add_gridspec(2, 3)
FR = [1, 2, 3, 4, 5, 6, 7, 11, 33, 34, 35, 36, 37, 38, 39]
for k, (B, t) in enumerate([('build3', 'Version 2'), ('build5', 'Version 3, stage 1')]):
    V, F, C = scene(B, FR); ax = fig.add_subplot(gs[0, k]); ax.imshow(render(V, F, 150, 15, size=700, colors=C)); ax.axis('off')
    ax.set_title(f'{t}: framework from behind (soft tissue hidden)', fontsize=15)
    GL = [2, 3, 4, 5, 6, 7, 12, 13, 14, 15, 16, 24, 25, 28, 29, 30, 11, 33, 34, 37, 38, 39]
    V, F, C = scene(B, GL); ax = fig.add_subplot(gs[1, k]); ax.imshow(render(V, F, 0, 89, size=700, colors=C)); ax.axis('off')
    ax.set_title(f'{t}: glottis from above (anterior at bottom)', fontsize=15)
ax = fig.add_subplot(gs[0, 2]); ax.axis('off')
rows = [('Measure (1:1 mm)', 'v2', 'v3', 'Adult male reference'),
        ('Thyroid lamina, along the plate', '28–33', '33–36.5', '37.7 ± 3.4'),
        ('Cricoid width, ring / lamina top', '22.9 / 20', '24.8 / 22.8', 'lamina 27–31'),
        ('Cricoarytenoid facets apart', '9.6', '12.1', '11.8–12.6'),
        ('Subglottis, wide × deep', '14.9 × 15.6', '16.0 × 16.9', 'about 16 × 17.4'),
        ('Arytenoid, vocal process to apex', '9.4', '16.1', '16.2–17.5'),
        ('Glottal area', '139', '145–153', '126–141 (tidal / quiet)'),
        ('Glottis length / width', '21.8 / 10.3', '24.4 / 8.5', '22.1 ± 3.1 / 10 ± 6'),
        ('Vocal ligament', '16.0', '15.1', '13.8–18'),
        ('Lumen step at cricoid–trachea', '1–3 mm shelf', 'none', 'none'),
        ('Hyo-epiglottic ligament', 'cut web', '9 × 2.5 band', 'band'),
        ('Posterior cricoarytenoid ligs.', 'absent', 'present', 'present')]
tb = ax.table(cellText=[list(r) for r in rows[1:]], colLabels=list(rows[0]), loc='center', cellLoc='left', colWidths=[0.40, 0.17, 0.17, 0.30])
tb.auto_set_font_size(False); tb.set_fontsize(11.5); tb.scale(1.08, 2.0); ax.set_title('Key measurements', fontsize=15)
ax = fig.add_subplot(gs[1, 2])
for B, c, lab in [('build3', '#999999', 'v2'), ('build5', '#3070c0', 'v3')]:
    for pid in (1, 2, 3, 10, 22, 4):
        m = trimesh.load(f'{B}/final_{pid:02d}.ply', process=False)
        s = m.section(plane_origin=[-0.65 if pid != 4 else -5.5, 0, 0], plane_normal=[1, 0, 0])
        if s is None: continue
        for e in s.discrete: ax.plot(e[:, 1], e[:, 2] - 1359.0, color=c, lw=1.3, label=lab if pid == 3 else None)
h, l = ax.get_legend_handles_labels(); d = dict(zip(l, h)); ax.legend(d.values(), d.keys(), fontsize=12)
ax.set_aspect('equal'); ax.grid(alpha=.3); ax.set_xlabel('y (mm, anterior left)'); ax.set_ylabel('mm above tracheal cut')
ax.set_title('Sagittal outlines: hyoid, thyroid, cricoid, epiglottis, hyo-epiglottic band, right arytenoid', fontsize=13)
plt.tight_layout(); plt.savefig(sys.argv[1], dpi=60)
