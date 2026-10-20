import sys; sys.path.insert(0,sys.argv[2]); from load import load
import numpy as np, trimesh
from trimesh.ray.ray_pyembree import RayMeshIntersector
m=load(sys.argv[1]); m.merge_vertices()
ri=RayMeshIntersector(m)
C=m.triangles_center; N=m.face_normals
def cone(n,ang=np.radians(15),k=6):
    # build k directions around -n
    a=np.where(np.abs(n[:,0:1])<0.9,np.array([[1,0,0]]),np.array([[0,1,0]]))
    u=np.cross(n,a); u/=np.linalg.norm(u,axis=1,keepdims=True); v=np.cross(n,u)
    dirs=[-n]
    for i in range(k):
        t=2*np.pi*i/k; d=-n*np.cos(ang)+np.sin(ang)*(np.cos(t)*u+np.sin(t)*v); dirs.append(d)
    return dirs
res=[]
for d in cone(N):
    o=C+d*1e-4
    loc,idx_ray,idx_tri=ri.intersects_location(o,d,multiple_hits=False)
    dist=np.full(len(C),np.nan)
    dist[idx_ray]=np.linalg.norm(loc-o[idx_ray],axis=1)
    res.append(dist)
R=np.array(res); T=np.nanmedian(R,axis=0)
np.save(sys.argv[3],T)
A=m.area_faces; tot=A.sum()
for thr in [0.2,0.4,0.6,0.8,1.0,1.5,2.0]:
    sel=T<thr; print(f'< {thr} mm: {A[sel].sum()/tot*100:.1f}% of surface, {sel.sum()} faces')
print('median thickness',np.nanmedian(T))
zmin=m.bounds[0,2]
z=C[:,2]-zmin
bins=[0,27,40,62,72,95,110,121]
for lo,hi in zip(bins[:-1],bins[1:]):
    s=(z>=lo)&(z<hi)
    thin=s&(T<0.8)
    print(f'z {lo}-{hi}: faces {s.sum()}, area<0.8mm {A[thin].sum():.0f} of {A[s].sum():.0f} mm2 ({A[thin].sum()/A[s].sum()*100:.0f}%)')
