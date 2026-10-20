import sys; sys.path.insert(0,sys.argv[3]); from load import load
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
m=load(sys.argv[1]); m.merge_vertices()
zmin,zmax=m.bounds[:,2]
levels=np.linspace(zmin+2,zmax-2,20)
fig,axs=plt.subplots(4,5,figsize=(20,16))
for ax,z in zip(axs.flat,levels):
    s=m.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
    if s is not None:
        p,_=s.to_2D(to_2D=np.array([[1,0,0,0],[0,1,0,0],[0,0,1,-z],[0,0,0,1]]))
        try:
            for poly in p.polygons_full:
                xs,ys=poly.exterior.xy; ax.fill(xs,ys,color='#c9b79c',ec='k',lw=0.5)
                for h in poly.interiors:
                    xs,ys=h.xy; ax.fill(xs,ys,color='white',ec='k',lw=0.5)
        except Exception as e: print(z,e)
        area=p.area
    else: area=0
    ax.set_title(f'z={z-zmin:.1f} mm from bottom  area={area:.0f}'); ax.set_aspect('equal'); ax.set_xlim(-33,33); ax.set_ylim(-26,26); ax.axhline(0,lw=0.3); ax.axvline(0,lw=0.3)
    ax.text(-31,-24,'anterior (-y)',fontsize=7)
plt.tight_layout(); plt.savefig(sys.argv[2],dpi=60)
