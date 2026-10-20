import sys; sys.path.insert(0,'scripts'); from load import load
import numpy as np
from shapely.ops import unary_union
m=load('extract/3D/Objects/object_2.model'); m.merge_vertices(); zmin=m.bounds[0,2]; H=m.extents[2]
lost_total=0; area_total=0; rows=[]
for zr in np.arange(0.1,H,0.2):
    z=zmin+zr
    s=m.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
    if s is None: continue
    p,_=s.to_2D(to_2D=np.array([[1,0,0,0],[0,1,0,0],[0,0,1,-z],[0,0,0,1]]))
    U=unary_union(list(p.polygons_full))
    O=U.buffer(-0.21).buffer(0.21)   # morphological opening by ~one 0.42 mm line
    lost=U.area-O.area; lost_total+=lost; area_total+=U.area
    ncomp=len(getattr(O,'geoms',[O])) if not O.is_empty else 0
    rows.append((zr,U.area,lost,ncomp))
print(f'overall: {lost_total/area_total*100:.1f}% of sliced cross-section area is narrower than one 0.42 mm line')
for lo,hi,n in [(0,23.5,'trachea'),(23.5,29.5,'cricotracheal junction'),(29.5,40,'cricoid'),(40,62,'glottis/conus'),(62,72,'thyroid upper'),(72,95,'thyrohyoid membrane'),(95,121,'hyoid+epiglottis')]:
    r=[x for x in rows if lo<=x[0]<hi]
    a=sum(x[1] for x in r); l=sum(x[2] for x in r)
    worst=max(r,key=lambda x:x[2]/max(x[1],1e-9))
    print(f'{n:24s} z{lo:>5}-{hi:<5}: {l/a*100:5.1f}% of area too thin; worst layer z={worst[0]:.1f} loses {worst[2]/worst[1]*100:.0f}%')
