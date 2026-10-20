import sys; sys.path.insert(0,sys.argv[2]); from load import load
import numpy as np, shapely
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
m=load(sys.argv[1]); m.merge_vertices(); zmin=m.bounds[0,2]
print('shapely',shapely.__version__)
rows=[]
for zr in np.arange(1,66,0.5):
    z=zmin+zr
    s=m.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
    if s is None: continue
    p,_=s.to_2D(to_2D=np.array([[1,0,0,0],[0,1,0,0],[0,0,1,-z],[0,0,0,1]]))
    polys=p.polygons_full
    holes=[Polygon(h) for poly in polys for h in poly.interiors]
    # pick hole with largest area containing near-centerline
    cand=[h for h in holes if h.area>5]
    if not cand: rows.append((zr,None,None,None,None)); continue
    h=max(cand,key=lambda h:h.area)
    mic=shapely.maximum_inscribed_circle(h)
    r=mic.length
    b=h.bounds
    rows.append((zr,h.area,2*r,b[2]-b[0],b[3]-b[1]))
for r in rows:
    if r[1] is None: print(f'z={r[0]:5.1f}  no enclosed lumen')
    else: print(f'z={r[0]:5.1f}  lumen area {r[1]:6.1f} mm2  max circle dia {r[2]:5.1f}  width {r[3]:5.1f}  AP {r[4]:5.1f}')
