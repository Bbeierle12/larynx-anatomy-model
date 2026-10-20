"""Stage-2 muscle QA on the final (CSG-trimmed) parts: volume, attachment contact, thickness, airway clearance."""
import os, sys, numpy as np, trimesh, igl
sys.path.insert(0, os.path.dirname(__file__))
from partsconfig import PARTS
B = os.environ.get('BUILD', 'build6'); Z0 = 1359.0
L = lambda i: trimesh.load(f'{B}/final_{i:02d}.ply', process=False)
def dfn(mesh):
    V = np.ascontiguousarray(mesh.vertices, np.float64); F = np.ascontiguousarray(mesh.faces, np.int64)
    return lambda p: np.sqrt(igl.point_mesh_squared_distance(np.ascontiguousarray(p, np.float64), V, F)[0])
cart = {k: dfn(L(k)) for k in (2, 3, 4, 5, 38, 39)}
MUS = {40: ('PCA R', (3, 38), (4,)), 41: ('PCA L', (3, 39), (5,)), 42: ('LCA R', (3,), (4,)), 43: ('LCA L', (3,), (5,)),
       44: ('CT straight R', (3,), (2,)), 45: ('CT straight L', (3,), (2,)), 46: ('CT oblique R', (3,), (2,)), 47: ('CT oblique L', (3,), (2,)),
       24: ('TA R', (2,), (4,)), 25: ('TA L', (2,), (5,)), 26: ('Vocalis R', (2,), (4,)), 27: ('Vocalis L', (2,), (5,)),
       28: ('Transverse arytenoid', (4,), (5,)), 29: ('Oblique arytenoid R', (4, 5), (4, 5)), 30: ('Oblique arytenoid L', (4, 5), (4, 5)),
       48: ('Thyro-epiglottic R', (2,), (10,)), 49: ('Thyro-epiglottic L', (2,), (10,))}
cart[10] = dfn(L(10))
print(f'{"muscle":22s} {"vol mm3":>8s} {"bodies":>6s}  contact(origin) contact(insertion)  min thickness (p5 / median)')
for pid, (name, org, ins) in MUS.items():
    f = f'{B}/final_{pid:02d}.ply'
    if not os.path.exists(f): print(name, 'MISSING'); continue
    m = L(pid); pts, fid = trimesh.sample.sample_surface(m, 40000, seed=0)
    do = np.min([cart[k](pts) for k in org], axis=0); di = np.min([cart[k](pts) for k in ins], axis=0)
    co = (do < 0.25).mean() * 100; ci = (di < 0.25).mean() * 100
    # thickness: ray-cast inward from surface points
    nrm = m.face_normals[fid]
    try:
        from trimesh.ray.ray_pyembree import RayMeshIntersector
        ray = RayMeshIntersector(m)
    except Exception:
        ray = m.ray
    loc, idr, _ = ray.intersects_location(pts - nrm * 0.01, -nrm, multiple_hits=False)
    th = np.full(len(pts), np.nan); th[idr] = np.linalg.norm(loc - pts[idr], axis=1)
    th = th[np.isfinite(th)]
    print(f'{name:22s} {m.volume:8.1f} {len(m.split(only_watertight=False)):6d}  {co:6.1f}% of surface  {ci:6.1f}% of surface   {np.percentile(th,5):.2f} / {np.median(th):.2f} mm')
