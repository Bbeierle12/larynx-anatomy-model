import sys; sys.path.insert(0,'scripts'); from load import load; from render import render
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from shapely.ops import unary_union
from matplotlib.patches import Circle
m=load('extract/3D/Objects/object_2.model'); m.merge_vertices(); T=np.load('renders/thickness.npy')
zmin=m.bounds[0,2]; V=m.vertices-m.bounds.mean(0); F=m.faces
col=np.tile([0.92,0.90,0.86],(len(F),1)); col[T<1.2]=[0.98,0.85,0.3]; col[T<0.8]=[0.98,0.55,0.15]; col[T<0.4]=[0.85,0.1,0.1]
front=render(V,F,0,5,size=700,colors=col)
C=(m.vertices[F].mean(1)); zc=C[:,2]-zmin; k=(zc<64)&(zc>20)
below=render(V,F[k],0,-89,size=700,colors=col[k])
fig=plt.figure(figsize=(18,7.2))
ax1=fig.add_axes([0.0,0.04,0.30,0.86]); ax1.imshow(front); ax1.axis('off')
ax1.set_title('1  Wall thickness (front)\nred <0.4 mm · orange 0.4–0.8 · yellow 0.8–1.2',fontsize=11)
ax1.annotate('cricotracheal band\n0.1–0.4 mm',xy=(330,522),xytext=(440,640),fontsize=9,arrowprops=dict(arrowstyle='->'))
ax1.annotate('thyrohyoid membrane\n0.4–1.2 mm',xy=(250,190),xytext=(5,105),fontsize=9,arrowprops=dict(arrowstyle='->'))
# junction sections
axs=[fig.add_axes([0.31+i*0.12,0.30,0.115,0.55]) for i in range(3)]
for ax,zr in zip(axs,[22.0,26.5,30.5]):
    z=zmin+zr; s=m.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
    p,_=s.to_2D(to_2D=np.array([[1,0,0,0],[0,1,0,0],[0,0,1,-z],[0,0,0,1]]))
    U=unary_union(list(p.polygons_full)); O=U.buffer(-0.21).buffer(0.21)
    for g,c in [(U,'#d9534f'),(O,'#c9b79c')]:
        for poly in getattr(g,'geoms',[g]):
            if poly.is_empty: continue
            xs,ys=poly.exterior.xy; ax.fill(xs,ys,color=c,lw=0)
            for h in poly.interiors: xs,ys=h.xy; ax.fill(xs,ys,color='white',lw=0)
    ax.set_aspect('equal'); ax.set_xlim(-17,17); ax.set_ylim(-11,19); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(f'{zr:.1f} mm up',fontsize=10)
    ax.text(0,-10,'anterior',ha='center',fontsize=8)
fig.text(0.31,0.90,'2  Trachea–cricoid junction, horizontal slices',fontsize=11)
fig.text(0.31,0.22,'tan = printable with one 0.42 mm line or more\nred = thinner than one line (dropped by the\nclassic wall generator). From 24–29 mm up the\nfront wall never closes into a ring.',fontsize=9,va='top')
ax3=fig.add_axes([0.68,0.04,0.32,0.86]); ax3.imshow(below); ax3.axis('off')
ax3.set_title('3  Looking up through the cricoid at the glottis (anterior at top)\nlargest sphere that passes: 6.8 mm',fontsize=11)
# scale legend: draw circles for 6.8 mm and 7.5 ETT 10.2 mm OD using render scale
sc=(700*0.9)/max(np.ptp(V[:,0]),np.ptp(V[:,1]))
for d,lab,cx in [(6.8,'6.8 mm: largest\nthat passes',95),(10.2,'7.5 ETT\n10.2 mm OD',200)]:
    ax3.add_patch(Circle((cx,640),d/2*sc,fill=False,lw=2,ec='#1f5fbf'))
    ax3.text(cx,640+d/2*sc+28,lab,ha='center',fontsize=8,color='#1f5fbf')
plt.savefig('renders/review_figure.png',dpi=110)
