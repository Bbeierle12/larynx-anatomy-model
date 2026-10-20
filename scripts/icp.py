import sys; sys.path.insert(0,sys.argv[1]); from load import load
import numpy as np, trimesh
from trimesh.registration import icp
M=load(sys.argv[2]); M.merge_vertices(); zmin=M.bounds[0,2]
T=M.copy(); T.vertices[:,2]-=zmin   # model with z from 0
def fit(path,name,init_scale,anchor_model,anchor_fn):
    S=trimesh.load(path)
    P=S.sample(4000,return_index=False)
    a_src=anchor_fn(S.vertices)
    best=None
    for s0 in [init_scale*0.85,init_scale,init_scale*1.15]:
        A=np.eye(4); A[:3,:3]*=s0; A[:3,3]=anchor_model-s0*a_src
        mat,tr,cost=icp(P,T,initial=A,threshold=1e-6,max_iterations=200,reflection=False,scale=True)
        sc=np.cbrt(np.linalg.det(mat[:3,:3]))
        d=trimesh.proximity.closest_point(T,tr)[1]
        if best is None or np.median(d)<best[2]: best=(sc,cost,np.median(d),np.percentile(d,90))
    print(f'{name}: best-fit uniform scale vs BodyParts3D original = {best[0]:.3f}  (median residual {best[2]:.2f} mm, p90 {best[3]:.2f} mm)')
bp='bp3d/repo/assets/BodyParts3D_data/stl/'
# thyroid: anchor = most anterior point (laryngeal prominence)
ant=lambda V: V[np.argmin(V[:,1])]
fit(bp+'FMA55099.stl','thyroid cartilage',1.45,np.array([-0.1,-24.1,65.3]),ant)
# hyoid: anchor = most anterior point of hyoid in model near z 95-108
H=T.vertices[(T.vertices[:,2]>92)&(T.vertices[:,2]<110)]; ha=H[np.argmin(H[:,1])]
fit(bp+'FMA52749.stl','hyoid bone',1.45,ha,ant)
# trachea: anchor = top-anterior; use top centroid of trachea
def top_ant(V):
    top=V[V[:,2]>V[:,2].max()-8]; return np.array([top[:,0].mean(),top[:,1].min(),top[:,2].max()])
TT=T.vertices[T.vertices[:,2]<26]; ta=np.array([TT[:,0].mean(),TT[:,1].min(),26.0])
fit(bp+'FMA7394.stl','trachea (top 25 mm)',1.2,ta,top_ant)
