import sys, numpy as np, trimesh
from shapely.ops import unary_union
from shapely.geometry import Polygon
from trimesh.ray.ray_pyembree import RayMeshIntersector
m = trimesh.load(sys.argv[1]); zmin = m.bounds[0, 2]
# --- ray thickness (same method as the original review) ---
ri = RayMeshIntersector(m); C = m.triangles_center; N = m.face_normals
def cone(n, ang=np.radians(15), k=6):
    a = np.where(np.abs(n[:, 0:1]) < 0.9, np.array([[1, 0, 0]]), np.array([[0, 1, 0]]))
    u = np.cross(n, a); u /= np.linalg.norm(u, axis=1, keepdims=True); v = np.cross(n, u)
    ds = [-n] + [-n * np.cos(ang) + np.sin(ang) * (np.cos(2*np.pi*i/k) * u + np.sin(2*np.pi*i/k) * v) for i in range(k)]
    return ds
R = []
for d in cone(N):
    o = C + d * 1e-4
    loc, ir, it = ri.intersects_location(o, d, multiple_hits=False)
    dist = np.full(len(C), np.nan); dist[ir] = np.linalg.norm(loc - o[ir], axis=1); R.append(dist)
T = np.nanmedian(np.array(R), axis=0); A = m.area_faces
np.save(sys.argv[2], T)
for thr in [0.4, 0.8, 1.2]:
    print(f'surface thinner than {thr} mm: {A[T < thr].sum() / A.sum() * 100:.1f}%')
# --- slice simulation: 0.2 mm layers, 0.42 mm line ---
lost_tot = area_tot = 0; worst = (0, 0); broken_layers = 0
for z in np.arange(zmin + 0.1, m.bounds[1, 2], 0.2):
    s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if s is None: continue
    p, _ = s.to_2D(to_2D=np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, -z], [0, 0, 0, 1]]))
    U = unary_union(list(p.polygons_full)); O = U.buffer(-0.21).buffer(0.21)
    lost = U.area - O.area; lost_tot += lost; area_tot += U.area
    if U.area > 0 and lost / U.area > worst[1]: worst = (z - zmin, lost / U.area)
print(f'slice sim: {lost_tot / area_tot * 100:.2f}% of all layer area narrower than one 0.42 mm line; worst layer {worst[0]:.1f} mm up loses {worst[1]*100:.1f}%')
# tracheal / cricoid ring closure through the junction
from shapely.geometry import box as sbox
bad = []
for z in np.arange(zmin + 0.1, zmin + 30, 0.2):
    s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    p, _ = s.to_2D(to_2D=np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, -z], [0, 0, 0, 1]]))
    O = unary_union(list(p.polygons_full)).buffer(-0.21).buffer(0.21)
    gs = getattr(O, 'geoms', [O])
    if not any(len(g.interiors) and max(Polygon(h).area for h in g.interiors) > 50 for g in gs if not g.is_empty): bad.append(round(z - zmin, 1))
print('layers 0-30 mm where the printed airway ring would not close:', bad if bad else 'none')
