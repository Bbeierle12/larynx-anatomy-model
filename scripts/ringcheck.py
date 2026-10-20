import sys; sys.path.insert(0,sys.argv[2]); from load import load
import numpy as np
from shapely.ops import unary_union
m=load(sys.argv[1]); m.merge_vertices(); zmin=m.bounds[0,2]
print('z    | min wall where tracheal/cricoid ring still forms a closed loop after erosion')
for zr in np.arange(20,32.01,0.5):
    z=zmin+zr
    s=m.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
    p,_=s.to_2D(to_2D=np.array([[1,0,0,0],[0,1,0,0],[0,0,1,-z],[0,0,0,1]]))
    U=unary_union(list(p.polygons_full))
    geoms=list(U.geoms) if hasattr(U,'geoms') else [U]
    ring=[g for g in geoms if len(g.interiors)>0 and max(__import__('shapely').geometry.Polygon(h).area for h in g.interiors)>100]
    if not ring: print(f'{zr:5.1f} | ring NOT closed at this level (wall has a gap)'); continue
    g=max(ring,key=lambda g:g.area)
    ok=None
    for t in [0.2,0.3,0.4,0.6,0.8,1.0,1.2,1.6]:
        e=g.buffer(-t/2)
        es=list(e.geoms) if hasattr(e,'geoms') else [e]
        closed=any(len(x.interiors)>0 and max(__import__('shapely').geometry.Polygon(h).area for h in x.interiors)>100 for x in es if not x.is_empty)
        if not closed: ok=t; break
    print(f'{zr:5.1f} | ring breaks when eroded to {ok} mm min wall -> thinnest point < {ok} mm' if ok else f'{zr:5.1f} | ring >= 1.6 mm everywhere')
