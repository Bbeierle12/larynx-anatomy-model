import sys, os, numpy as np, trimesh, shapely
from shapely.geometry import Point, box
from shapely.ops import unary_union
sys.path.insert(0,'scripts'); from partsconfig import PARTS
B=sys.argv[1]; BASE0=1366.05
ms=[trimesh.load(f'{B}/part_{p[0]:02d}.ply',process=False) for p in PARTS if p[2] and p[0] not in (11,)]
best=None
for z in np.arange(BASE0+36.5, BASE0+42.5, 0.25):
    polys=[]
    for m in ms:
        if m.bounds[0,2]>z or m.bounds[1,2]<z: continue
        s=m.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
        if s is None: continue
        try:
            p,_=s.to_2D(to_2D=np.array([[1,0,0,0],[0,1,0,0],[0,0,1,-z],[0,0,0,1]])); polys+=list(p.polygons_full)
        except Exception: pass
    U=unary_union(polys)
    air=box(-12,-120,11,-86).difference(U)
    comps=[g for g in getattr(air,'geoms',[air]) if g.contains(Point(-0.65,-104))]
    if not comps: continue
    g=comps[0]; r=shapely.maximum_inscribed_circle(g).length*2; x0,y0,x1,y1=g.bounds
    # only count it as glottis if enclosed (doesn't touch the window edge)
    enclosed = not g.intersects(box(-12,-120,11,-86).exterior.buffer(0.05))
    if enclosed and (best is None or g.area<best[1]): best=(z-BASE0,g.area,r,x1-x0,y1-y0)
print('narrowest enclosed glottic level: z+%.2f area %.0f mm2, inscribed circle %.1f mm, width %.1f, length %.1f'%best if best else 'no enclosed level found')
