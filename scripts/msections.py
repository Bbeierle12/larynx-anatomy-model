"""axial / coronal / sagittal section plots: python msections.py BUILD out.png 'ids' 'axis:val,axis:val,...' [prefix]"""
import sys, numpy as np, trimesh, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
B, out, ids, cuts = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(',')], sys.argv[4].split(',')
prefix = sys.argv[5] if len(sys.argv) > 5 else 'part'
Z0 = 1359.0
COL = {2:'#5b9bd5',3:'#5b9bd5',4:'#2060a0',5:'#2060a0',38:'#5b9bd5',39:'#5b9bd5',12:'#d08020',13:'#d08020',14:'#d0a040',15:'#d0a040',16:'#d0a040',1:'#999999',10:'#c0a000',24:'#e09090',25:'#e09090',26:'#e09090',27:'#e09090',50:'#c03030',51:'#c03030',52:'#8030a0',53:'#8030a0',54:'#d08020',55:'#d08020',56:'#d0a040',57:'#d0a040',58:'#8030a0',59:'#8030a0',60:'#8030a0',61:'#8030a0',62:'#8030a0',63:'#8030a0',64:'#c03030',65:'#c03030',66:'#8030a0',67:'#8030a0',68:'#c0a020',69:'#c0a020',70:'#c0a020',71:'#d08020',72:'#d08020',73:'#d08020',74:'#d08020',75:'#d08020',76:'#8030a0',77:'#8030a0',78:'#8030a0',79:'#8030a0',80:'#e09090',81:'#e09090',82:'#e09090',83:'#8030a0',28:'#e09090',31:'#e09090',32:'#e09090',48:'#e09090',49:'#e09090'}
ms = {i: trimesh.load(f'{B}/{prefix}_{i:02d}.ply', process=False) for i in ids}
fig, axs = plt.subplots(1, len(cuts), figsize=(7 * len(cuts), 7))
for ax, cut in zip(np.atleast_1d(axs), cuts):
    axn, val = cut.split(':'); val = float(val)
    if axn == 'z': org, nrm, ix, iy, lab = [0, 0, Z0 + val], [0, 0, 1], 0, 1, ('x', 'y')
    elif axn == 'y': org, nrm, ix, iy, lab = [0, val, 0], [0, 1, 0], 0, 2, ('x', 'z')
    else: org, nrm, ix, iy, lab = [val, 0, 0], [1, 0, 0], 1, 2, ('y', 'z')
    for i, m in ms.items():
        s = m.section(plane_origin=org, plane_normal=nrm)
        if s is None: continue
        for e in s.discrete:
            yy = e[:, iy] - (Z0 if iy == 2 else 0)
            ax.plot(e[:, ix], yy, color=COL.get(i, '#c03030'), lw=1.3)
    ax.set_aspect('equal'); ax.grid(alpha=.3); ax.set_title(f'{axn} = {val}'); ax.set_xlabel(lab[0]); ax.set_ylabel(lab[1])
plt.tight_layout(); plt.savefig(out, dpi=55); print('wrote', out)
