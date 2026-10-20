import sys, os, numpy as np, trimesh, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0,'scripts'); from partsconfig import PARTS
cols={1:'#d8cfb8',2:'#5b9bd5',3:'#e0b020',4:'#d05060'}
ms=[]
for pid,name,c,grp,*_ in PARTS:
    f=f"{os.environ.get('BUILD','build')}/final_{pid:02d}.ply"
    if os.path.exists(f): ms.append((name,grp,trimesh.load(f,process=False)))
zmin=min(m.bounds[0,2] for *_,m in ms)
ZV=float(os.environ.get('ZV','38.5')); ZC=float(os.environ.get('ZC','25.6')); XP=float(os.environ.get('XP','-4.0'))
specs=[('x',-0.65,'mid-sagittal (anterior left)'),('x',XP,f'parasagittal {-0.65-XP:.1f} mm right of midline'),('y',-104.0,'coronal through the glottis'),('y',-98.0,'coronal through the arytenoids'),
       ('z',zmin+ZV,'axial at vocal folds'),('z',zmin+ZC,'axial at cricoid ring'),('z',zmin+8,'axial trachea'),('z',zmin+ZV+17.5,'axial supraglottis')]
fig,axs=plt.subplots(2,4,figsize=(28,16))
for ax,(a,v,t) in zip(axs.ravel(),specs):
    n=[0,0,0]; i='xyz'.index(a); n[i]=1; o=[0,0,0]; o[i]=v
    oth=[j for j in range(3) if j!=i]
    for name,grp,m in ms:
        s=m.section(plane_origin=o,plane_normal=n)
        if s is None: continue
        T=np.eye(4); T=T[[oth[0],oth[1],i,3]]; T[2,3]=-v
        try:
            pp,_=s.to_2D(to_2D=T)
            for poly in pp.polygons_full:
                xs,ys=poly.exterior.xy; ys=np.array(ys)-(zmin if oth[1]==2 else 0); ax.fill(xs,ys,color=cols[grp],ec='k',lw=0.3)
                for h in poly.interiors:
                    xs,ys=h.xy; ys=np.array(ys)-(zmin if oth[1]==2 else 0); ax.fill(xs,ys,color='white',ec='k',lw=0.3)
        except Exception as ex:
            for e in s.entities:
                p=s.vertices[e.points]; ax.plot(p[:,oth[0]],p[:,oth[1]]-(zmin if oth[1]==2 else 0),color=cols[grp],lw=0.8)
    ax.set_aspect('equal'); ax.set_title(t,fontsize=14); ax.grid(alpha=0.3)
    ax.set_xlabel('xyz'[oth[0]]+' (mm)'); ax.set_ylabel(('z above base' if oth[1]==2 else 'xyz'[oth[1]])+' (mm)')
plt.tight_layout(); plt.savefig(sys.argv[1] if len(sys.argv)>1 else 'renders/review_sections.png',dpi=55)
