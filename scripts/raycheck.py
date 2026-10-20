import sys; sys.path.insert(0,sys.argv[2]); from load import load
import numpy as np
from trimesh.ray.ray_pyembree import RayMeshIntersector
m=load(sys.argv[1]); m.merge_vertices(); zmin=m.bounds[0,2]
ri=RayMeshIntersector(m)
xs=np.arange(-10,10.01,0.5); ys=np.arange(-10,16.01,0.5)
X,Y=np.meshgrid(xs,ys); O=np.c_[X.ravel(),Y.ravel(),np.full(X.size,zmin+30)]
D=np.tile([0,0,1.0],(len(O),1))
loc,ir,it=ri.intersects_location(O,D,multiple_hits=False)
hz=np.full(len(O),np.nan); hz[ir]=loc[:,2]-zmin
H=hz.reshape(X.shape)
# print a character map: '.' = passes beyond z=65, digits = hit height band
import string
print('rays cast upward from z=30 (trachea/cricoid level); rows = y from -10 (anterior, top) to +16 (posterior)')
print('legend: . = clear to z>=65  c = hit <36 (cricoid)  m = 36-50  P = 50-54  g = 54-65')
for j in range(H.shape[0]):
    row=''
    for i in range(H.shape[1]):
        h=H[j,i]
        row+= '.' if (np.isnan(h) or h>=65) else ('c' if h<36 else 'm' if h<50 else 'P' if h<54 else 'g')
    print(f'{ys[j]:6.1f} {row}')
