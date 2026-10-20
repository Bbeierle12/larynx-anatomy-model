import sys; sys.path.insert(0,'scripts'); from load import load
import numpy as np, trimesh
from trimesh.registration import icp
from scipy.spatial import cKDTree
M=load('extract/3D/Objects/object_2.model'); M.merge_vertices(); zmin=M.bounds[0,2]
T=M.copy(); T.vertices[:,2]-=zmin
TP=T.sample(200000)
def check(fma,name,anchor_dst,anchor_fn,roi_fn):
    S=trimesh.load(f'bp3d/repo/assets/BodyParts3D_data/stl/{fma}.stl'); P=S.sample(6000); a=anchor_fn(S.vertices)
    roi=TP[roi_fn(TP)]
    for s0 in [1.0,1.2,1.35,1.45,1.55]:
        Q=(P-a)*s0+anchor_dst
        mat,tr,cost=icp(Q,T,max_iterations=150,scale=False)
        d1=trimesh.proximity.closest_point(T,tr)[1]
        d2=cKDTree(tr).query(roi)[0]
        print(f'{name} scale {s0}: src->model median {np.median(d1):.2f}, model ROI->src median {np.median(d2):.2f}, sym {0.5*(np.median(d1)+np.median(d2)):.2f}')
ant=lambda V: V[np.argmin(V[:,1])]
# thyroid ROI: model points with y<5 (anterior half) and z 40-72 outer laminae region |x|>3
check('FMA55099','thyroid',np.array([-0.1,-24.1,65.3]),ant,lambda p:(p[:,2]>45)&(p[:,2]<68)&(p[:,1]<0)&(np.abs(p[:,0])>6)&(p[:,1]< -0.6*np.abs(p[:,0])+8))
H=T.vertices[(T.vertices[:,2]>92)&(T.vertices[:,2]<110)]; ha=H[np.argmin(H[:,1])]
check('FMA52749','hyoid',ha,ant,lambda p:(p[:,2]>95)&(p[:,1]< -12))
