"""Stage-3 QA on the union: airway at every level from the trachea to the inlet, false-fold gap, ventricle presence, mucosa parts."""
import os, sys, json, numpy as np, trimesh, shapely
from shapely.geometry import Polygon, Point, box as sbox
from shapely.ops import unary_union
sys.path.insert(0, os.path.dirname(__file__)); from partsconfig import PARTS
B = os.environ.get('BUILD', 'build7'); Z0 = 1359.0; CX = -0.65
u = trimesh.load(f'{B}/final_union.ply', process=False)
def sec(z):
    s = u.section(plane_origin=[0, 0, Z0 + z], plane_normal=[0, 0, 1])
    if s is None: return None
    p, _ = s.to_2D(to_2D=np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, -(Z0 + z)], [0, 0, 0, 1]])); return unary_union(list(p.polygons_full))
def air(z, cy, win=sbox(-14, -118, 13, -84)):
    U = sec(z)
    if U is None: return None
    A = win.difference(U); comps = [g for g in getattr(A, 'geoms', [A]) if g.contains(Point(CX, cy))]
    if not comps: return None
    g = comps[0]; x0, y0, x1, y1 = g.bounds
    return dict(area=g.area, w=x1 - x0, d=y1 - y0, mic=2 * shapely.maximum_inscribed_circle(g).length, g=g)
print('airway profile (area / width / inscribed circle) by level:')
for z, cy, lab in [(24, -97, 'subglottis'), (40, -100, 'infraglottic'), (44, -102, 'below the folds'), (46.8, -104, 'rima (ligament level)'), (48.5, -104, 'fold upper surface'), (50.5, -104, 'ventricle level'), (53.5, -104, 'false folds'), (56, -104, 'above the false folds'), (60, -100, 'vestibule'), (66, -97, 'inlet')]:
    r = air(z, cy)
    if r: print(f'  z+{z:5.1f} {lab:24s} area {r["area"]:6.0f} mm2  width {r["w"]:5.1f}  circle {r["mic"]:4.1f}')
    else: print(f'  z+{z:5.1f} {lab:24s} no enclosed air at the probe point')
# narrowest glottis with the cover
best = None
for z in np.arange(45.0, 49.5, 0.25):
    r = air(z, -104)
    if r and (best is None or r['area'] < best[1]['area']): best = (z, r)
if best: print(f'glottis narrowest at z+{best[0]:.2f}: area {best[1]["area"]:.0f} mm2, width {best[1]["w"]:.1f}, length {best[1]["d"]:.1f}, inscribed circle {best[1]["mic"]:.1f}')
# ventricle: coronal section at mid-fold, air pocket lateral to the vestibule between z0+2 and z0+6
for y in (-106, -103, -100):
    s = u.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
    p, _ = s.to_2D(to_2D=np.array([[1, 0, 0, 0], [0, 0, 1, -Z0], [0, 1, 0, -y], [0, 0, 0, 1]])); U = unary_union(list(p.polygons_full))
    win = sbox(-16, 38, 15, 62); A = win.difference(U)
    comps = [g for g in getattr(A, 'geoms', [A])]
    # the airway component containing the midline at z 50
    mid = [g for g in comps if g.contains(Point(CX, 50))]
    if mid:
        g = mid[0]; x0, z0_, x1, z1 = g.bounds
        # lateral extent of air at ventricle height vs at the fold top
        wv = g.intersection(sbox(-16, 50, 15, 52)).bounds; wf = g.intersection(sbox(-16, 47.5, 15, 48.5)).bounds
        print(f'coronal y {y}: airway lateral reach at z 50-52 (ventricle): x {wv[0]:.1f}..{wv[2]:.1f}; at z 47.5-48.5 (fold level): x {wf[0]:.1f}..{wf[2]:.1f}')
st = json.load(open(f'{B}/final_stats.json')); grp = {p[0]: p[3] for p in PARTS}; nm = {p[0]: p[1] for p in PARTS}
print('stage-3 parts (final volumes, bodies):')
for k, v in st.items():
    if int(k) >= 50:
        m = trimesh.load(f'{B}/final_{int(k):02d}.ply', process=False)
        print(f'  {int(k):2d} {nm[int(k)]:58s} {v["volume"]:7.1f} mm3  bodies {len(m.split(only_watertight=False))}')
