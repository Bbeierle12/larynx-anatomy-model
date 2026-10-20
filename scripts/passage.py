import sys; sys.path.insert(0,sys.argv[2]); from load import load
import numpy as np
from scipy import ndimage
from trimesh.ray.ray_pyembree import RayMeshIntersector
m=load(sys.argv[1]); m.merge_vertices(); zmin=m.bounds[0,2]
ri=RayMeshIntersector(m)
p=0.2
xs=np.arange(-12,12+1e-9,p); ys=np.arange(-11,16+1e-9,p); zs=np.arange(1,70+1e-9,p)
X,Y=np.meshgrid(xs,ys,indexing='ij')
O=np.c_[X.ravel(),Y.ravel(),np.full(X.size,zmin-5)]; D=np.tile([0,0,1.0],(len(O),1))
loc,ir,it=ri.intersects_location(O,D,multiple_hits=True)
solid=np.zeros((len(xs),len(ys),len(zs)),bool)
order=np.lexsort((loc[:,2],ir))
ir=ir[order]; hz=loc[order,2]-zmin
starts=np.r_[0,np.flatnonzero(np.diff(ir))+1]; ends=np.r_[starts[1:],len(ir)]
odd=0
for s,e in zip(starts,ends):
    k=ir[s]; i,j=np.unravel_index(k,X.shape); h=np.unique(np.round(hz[s:e],5))
    if len(h)%2: odd+=1; h=h[:-1]
    for a,b in zip(h[0::2],h[1::2]):
        solid[i,j,(zs>=a)&(zs<=b)]=True
print('odd-hit columns',odd)
air=~solid
# treat box sides as walls
air[0,:,:]=air[-1,:,:]=False; air[:,0,:]=air[:,-1,:]=False
edt=ndimage.distance_transform_edt(air)*p
def passes(r):
    lab,n=ndimage.label(edt>=r)
    bot=set(np.unique(lab[:,:,0]))-{0}; top=set(np.unique(lab[:,:,-1]))-{0}
    return len(bot&top)>0
lo,hi=0.0,10.0
for _ in range(25):
    mid=(lo+hi)/2
    if passes(mid): lo=mid
    else: hi=mid
print(f'largest sphere that can pass trachea->above glottis: diameter {2*lo:.2f} mm')
# where is the bottleneck: per-z max edt within the passing component at r slightly below lo
lab,n=ndimage.label(edt>=lo*0.98)
bot=set(np.unique(lab[:,:,0]))-{0}; top=set(np.unique(lab[:,:,-1]))-{0}; comp=list(bot&top)[0]
mask=lab==comp
per_z=[(zs[k], (edt[:,:,k]*mask[:,:,k]).max()) for k in range(len(zs))]
bz=min(per_z,key=lambda t:t[1]); print(f'bottleneck at z={bz[0]:.1f} mm from base, local max radius {bz[1]:.2f}')
# also report per-z free radius (any air in box)
for k in range(0,len(zs),10):
    print(f'z={zs[k]:5.1f} max free circle dia in box {2*edt[:,:,k].max():5.1f}')
