import sys; sys.path.insert(0,'scripts')
import numpy as np, trimesh, json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from partsconfig import PARTS
inv=json.load(open('bp4/parts/inventory.json'))
cols={1:'#bbb39f',2:'#5b9bd5',3:'#e0b020',4:'#d05060'}
meshes=[]
for pid,name,concepts,grp,pri,kind in PARTS:
    for e in (inv[concepts[0]][:2] if 'thyro-arytenoid' in concepts[0] else inv[concepts[0]][:1]):
        m=trimesh.load(f'bp4/parts/{e}.obj',force='mesh'); m.merge_vertices(); meshes.append((name,grp,m))
specs=[('x',-0.4,(1,2),(-130,-88),(1378,1444)),('x',-4,(1,2),(-130,-88),(1378,1444)),('y',-104,(0,2),(-21,21),(1378,1444)),('y',-99,(0,2),(-21,21),(1378,1444))]
fig,axs=plt.subplots(1,4,figsize=(26,10))
for ax,(mode,lv,(a,b),xl,yl) in zip(axs,specs):
    n=[0,0,0]; n['xyz'.index(mode)]=1; o=[0,0,0]; o['xyz'.index(mode)]=lv
    for name,grp,m in meshes:
        s=m.section(plane_origin=o,plane_normal=n)
        if s is None: continue
        for ent in s.entities:
            pts=s.vertices[ent.points]; ax.fill(pts[:,a],pts[:,b],color=cols[grp],alpha=0.65,lw=0.4,ec='k')
    ax.set_aspect('equal'); ax.set_xlim(*xl); ax.set_ylim(*yl); ax.grid(alpha=0.3); ax.set_title(f'{mode}={lv}')
plt.tight_layout(); plt.savefig(sys.argv[1],dpi=50)
