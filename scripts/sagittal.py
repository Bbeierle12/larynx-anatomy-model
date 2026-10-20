import sys; sys.path.insert(0,sys.argv[3]); from load import load
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
m=load(sys.argv[1]); m.merge_vertices(); zmin=m.bounds[0,2]
def plot(ax,origin,normal,proj,title):
    s=m.section(plane_origin=origin,plane_normal=normal)
    for ent in s.entities:
        pts=s.vertices[ent.points]
        ax.plot(pts[:,proj[0]],pts[:,proj[1]]-zmin,'k-',lw=0.6)
    ax.set_aspect('equal'); ax.set_title(title); ax.grid(alpha=0.3)
fig,axs=plt.subplots(1,4,figsize=(24,9))
plot(axs[0],[0,0,0],[1,0,0],(1,2),'mid-sagittal x=0 (anterior = left, -y)')
plot(axs[1],[3,0,0],[1,0,0],(1,2),'parasagittal x=3')
plot(axs[2],[0,3,0],[0,1,0],(0,2),'coronal y=3')
plot(axs[3],[0,10,0],[0,1,0],(0,2),'coronal y=10')
plt.tight_layout(); plt.savefig(sys.argv[2],dpi=55)
