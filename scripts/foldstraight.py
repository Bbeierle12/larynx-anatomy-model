import sys, numpy as np, trimesh
B=sys.argv[1]; pre=sys.argv[2] if len(sys.argv)>2 else 'part'
for pid in (12,13):
    v=trimesh.load(f'{B}/{pre}_{pid:02d}.ply',process=False).vertices
    c=v.mean(0); ax=np.linalg.svd(v-c)[2][0]; s=(v-c)@ax
    # centreline: mean of vertices in 20 slabs along the ligament
    edges=np.linspace(s.min(),s.max(),21); cl=np.array([v[(s>=a)&(s<b)].mean(0) for a,b in zip(edges[:-1],edges[1:])])
    a,b=cl[1],cl[-2]; u=(b-a)/np.linalg.norm(b-a)
    dev=cl-a-np.outer((cl-a)@u,u)
    lat=np.abs(dev[:,0]).max(); vert=np.abs(dev[:,2]).max()
    print(f'{B} vocal ligament {pid}: max centreline deviation from straight: lateral {lat:.2f} mm, vertical {vert:.2f} mm')
