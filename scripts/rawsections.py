import sys; sys.path.insert(0,'scripts')
import numpy as np, trimesh, json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from partsconfig import PARTS
inv=json.load(open('bp4/parts/inventory.json'))
cols={1:'#bbb39f',2:'#5b9bd5',3:'#e0b020',4:'#d05060'}
meshes=[]
for pid,name,concepts,grp,pri,kind in PARTS:
    for e in inv[concepts[0]][:2] if 'thyro-arytenoid' in concepts[0] else inv[concepts[0]][:1]:
        m=trimesh.load(f'bp4/parts/{e}.obj',force='mesh'); m.merge_vertices(); meshes.append((name,grp,m))
levels=[float(x) for x in sys.argv[2].split(',')]
mode=sys.argv[3] if len(sys.argv)>3 else 'z'
n=len(levels); cols_n=4; rows=(n+cols_n-1)//cols_n
fig,axs=plt.subplots(rows,cols_n,figsize=(5*cols_n,5*rows))
for ax,lv in zip(np.ravel(axs),levels):
    for name,grp,m in meshes:
        if mode=='z': s=m.section(plane_origin=[0,0,lv],plane_normal=[0,0,1]); a,b=0,1
        elif mode=='x': s=m.section(plane_origin=[lv,0,0],plane_normal=[1,0,0]); a,b=1,2
        else: s=m.section(plane_origin=[0,lv,0],plane_normal=[0,1,0]); a,b=0,2
        if s is None: continue
        for ent in s.entities:
            pts=s.vertices[ent.points]; ax.fill(pts[:,a],pts[:,b],color=cols[grp],alpha=0.6,lw=0.5,ec='k')
    ax.set_aspect('equal'); ax.set_title(f'{mode}={lv}'); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig(sys.argv[1],dpi=55)
