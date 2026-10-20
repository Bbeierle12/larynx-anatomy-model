"""Union surface from the saved min-field (run in a fresh process to keep memory low)."""
import sys, os, json, numpy as np, trimesh, pymeshlab
from skimage import measure
from scipy import ndimage
B = os.environ['BUILD']
g = np.load(f'{B}/grid.npy'); lo = g[:3]; P = g[3]; z_cut = g[7]; BIG = 50.0
H = np.load(f'{B}/union_sdf_min.npy', mmap_mode='r')
k0 = max(int(np.floor((z_cut - lo[2]) / P)) - 2, 0)
Hs = np.ascontiguousarray(H[:, :, k0:]); del H
CLOSE = float(os.environ.get('UNION_CLOSE', '0.25'))      # mm: hairline cracks between abutting parts narrower than 2*CLOSE are closed (they are seams, not anatomy)
if CLOSE > 0:
    import edt
    occ = Hs <= 0; n_ = int(round(CLOSE / P))
    closed = ndimage.binary_closing(occ, iterations=n_, border_value=0)
    added = closed & ~occ; del occ, closed
    if added.any():
        # a smooth field for the added slivers: distance from the (dilated) union, negative inside the closed solid
        phi_c = np.where(Hs <= 0, Hs, np.where(added, -0.5 * P, Hs)).astype(np.float32)
        print('union: closed %.1f mm3 of hairline cracks (<= %.2f mm wide)' % (added.sum() * P ** 3, 2 * CLOSE))
        Hs = phi_c; del phi_c
    del added
ph = np.pad(Hs, 1, constant_values=BIG); del Hs
v, f, _, _ = measure.marching_cubes(ph, 0.0, spacing=(P, P, P)); del ph
v += lo + (np.array([0, 0, k0]) - 1) * P
ms = pymeshlab.MeshSet(); ms.add_mesh(pymeshlab.Mesh(np.ascontiguousarray(v, np.float64), np.ascontiguousarray(f, np.int32))); del v, f
ms.meshing_decimation_quadric_edge_collapse(targetfacenum=max(int(ms.current_mesh().face_number() * 0.12), 500), qualitythr=0.4,
    preserveboundary=True, preservenormal=True, preservetopology=True, optimalplacement=True, planarquadric=True)
ms.meshing_remove_duplicate_vertices(); ms.meshing_remove_unreferenced_vertices()
try: ms.meshing_repair_non_manifold_edges(); ms.meshing_remove_unreferenced_vertices()
except Exception as e_: print('non-manifold repair skipped:', e_)
mm = ms.current_mesh(); m = trimesh.Trimesh(mm.vertex_matrix(), mm.face_matrix(), process=True)
if m.volume < 0: m.invert()
allb = m.split(only_watertight=False)
cav = [x for x in allb if x.volume < 0 and abs(x.volume) < 30.0]        # small closed cavities between parts (e.g. inside a fold): filled
if cav: print('filled %d closed cavities, %.1f mm3 in all' % (len(cav), sum(abs(x.volume) for x in cav)))
bodies = [x for x in allb if abs(x.volume) >= 2.0 and x not in cav]; m = trimesh.util.concatenate(bodies)
m.update_faces(m.nondegenerate_faces()); m.merge_vertices(); m.remove_unreferenced_vertices()
bodies = [x for x in m.split(only_watertight=False) if abs(x.volume) >= 2.0]; m = trimesh.util.concatenate(bodies)
near = m.vertices[:, 2] < z_cut + 0.5 * P; m.vertices[near, 2] = np.maximum(m.vertices[near, 2], z_cut)
m.export(f'{B}/final_union.ply')
print('union: faces', len(m.faces), 'watertight', m.is_watertight, 'vol %.0f' % m.volume, 'bodies', len(m.split(only_watertight=False)), 'bounds', np.round(m.bounds, 1).tolist())
st = {}
for fn in sorted(os.listdir(B)):
    if fn.startswith('final_') and fn.endswith('.ply') and fn != 'final_union.ply':
        q = trimesh.load(f'{B}/{fn}', process=False); st[int(fn[6:8])] = dict(faces=len(q.faces), watertight=bool(q.is_watertight), volume=float(q.volume))
json.dump(st, open(f'{B}/final_stats.json', 'w'), indent=1)
