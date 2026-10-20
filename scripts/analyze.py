import sys; sys.path.insert(0, sys.argv[2])
from load import load
import numpy as np, trimesh
m=load(sys.argv[1])
print('verts',len(m.vertices),'faces',len(m.faces))
print('bounds',m.bounds, 'extents',m.extents)
m2=m.copy(); m2.merge_vertices()
print('after merge verts',len(m2.vertices))
print('watertight',m2.is_watertight,'winding consistent',m2.is_winding_consistent,'volume ok',m2.is_volume)
print('euler',m2.euler_number)
print('volume',m2.volume,'area',m2.area)
cc=m2.split(only_watertight=False)
print('components',len(cc))
for i,c in enumerate(sorted(cc,key=lambda c:-len(c.faces))):
    print(i,len(c.faces),'wt',c.is_watertight,'vol',round(c.volume,1),'ext',np.round(c.extents,1),'center',np.round(c.bounds.mean(0),1))
# degenerate
a=m2.area_faces; print('zero-area faces',(a<1e-8).sum(), 'min area',a.min())
# edges
from collections import Counter
e=m2.edges_sorted; u,cnt=np.unique(e,axis=0,return_counts=True)
print('edge use counts',Counter(cnt.tolist()))
