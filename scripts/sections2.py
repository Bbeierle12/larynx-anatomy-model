import sys; sys.path.insert(0,sys.argv[3]); from load import load
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
m=load(sys.argv[1]); m.merge_vertices(); zmin=m.bounds[0,2]
levels=[float(x) for x in sys.argv[4].split(',')]
n=len(levels); cols=5; rows=(n+cols-1)//cols
fig,axs=plt.subplots(rows,cols,figsize=(4*cols,4*rows))
for ax,zr in zip(axs.flat,levels):
    z=zmin+zr
    s=m.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
    for ent in s.entities:
        pts=s.vertices[ent.points]; ax.plot(pts[:,0],pts[:,1],'k-',lw=0.7)
    p,_=s.to_2D(to_2D=np.array([[1,0,0,0],[0,1,0,0],[0,0,1,-z],[0,0,0,1]]))
    for poly in p.polygons_full:
        xs,ys=poly.exterior.xy; ax.fill(xs,ys,color='#c9b79c',alpha=0.7)
        for h in poly.interiors:
            xs,ys=h.xy; ax.fill(xs,ys,color='white')
    ax.set_title(f'z={zr}'); ax.set_aspect('equal'); ax.set_xlim(*[float(v) for v in sys.argv[5].split(',')]); ax.set_ylim(*[float(v) for v in sys.argv[6].split(',')]); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig(sys.argv[2],dpi=70)
