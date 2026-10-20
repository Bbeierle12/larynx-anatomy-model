"""Stage 4: per-part surfaces (marching cubes on lightly smoothed masks), decimated, plus the union surface."""
import sys, time, numpy as np, trimesh, pymeshlab, edt
from scipy import ndimage
from skimage import measure
sys.path.insert(0, '/tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad/scripts')
from partsconfig import PARTS
B = '/tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad/build'
g = np.load(f'{B}/grid.npy'); lo = g[:3]; P = g[3]; z_cut = g[7]
L = np.load(f'{B}/labels_final.npy')
kcut = int(round((z_cut - lo[2]) / P))
TOL = 0.02   # mm, max geometric deviation allowed in decimation

def surface(mask, off, sigma=1.2):
    """signed-distance based surface: removes voxel staircase without moving the surface"""
    pad = 4
    m = np.pad(mask, pad)
    din = edt.edt(m, anisotropy=(P, P, P), black_border=True, parallel=2)
    dout = edt.edt(~m, anisotropy=(P, P, P), black_border=False, parallel=2)
    sdf = (dout - din).astype(np.float32)
    sdf[m] += P / 2; sdf[~m] -= P / 2          # place the zero level on the voxel boundary
    sdf = ndimage.gaussian_filter(sdf, sigma)
    v, f, _, _ = measure.marching_cubes(sdf, 0.0, spacing=(P, P, P))
    v += lo + (np.array(off) - pad) * P
    return v, f

def decimate(v, f, target_ratio=0.07):
    ms = pymeshlab.MeshSet(); ms.add_mesh(pymeshlab.Mesh(v, f))
    ms.apply_coord_taubin_smoothing(lambda_=0.5, mu=-0.53, stepsmoothnum=6)
    n = int(len(f) * target_ratio)
    ms.meshing_decimation_quadric_edge_collapse(targetfacenum=max(n, 500), qualitythr=0.4, preserveboundary=True,
                                                preservenormal=True, preservetopology=True, optimalplacement=True, planarquadric=True)
    ms.meshing_remove_duplicate_vertices(); ms.meshing_remove_unreferenced_vertices()
    m = ms.current_mesh()
    return m.vertex_matrix(), m.face_matrix()

out = {}
for pid, name, concepts, grp, pri, kind in PARTS:
    t = time.time()
    idx = np.argwhere(L == pid)
    a = idx.min(0); b = idx.max(0) + 1
    mask = L[a[0]:b[0], a[1]:b[1], a[2]:b[2]] == pid
    v, f = surface(mask, a)
    v2, f2 = decimate(v, f)
    mesh = trimesh.Trimesh(v2, f2, process=True)
    if mesh.volume < 0: mesh.invert()
    # base: snap vertices within half a voxel of the cut plane onto it (flat bottom)
    near = mesh.vertices[:, 2] < z_cut + 0.5 * P
    mesh.vertices[near, 2] = np.maximum(mesh.vertices[near, 2], z_cut)
    dev = trimesh.proximity.closest_point(trimesh.Trimesh(v2, f2), v[::50])[1]
    mesh.export(f'{B}/mesh_{pid:02d}.ply')
    out[pid] = mesh
    print(f'{pid:2d} {name:30s} faces {len(f):7d} -> {len(mesh.faces):6d}  watertight {mesh.is_watertight}  dev max {dev.max():.3f} p99 {np.percentile(dev,99):.3f}  vol {mesh.volume:8.1f} mm3  ({time.time()-t:.0f}s)')
# union surface for analysis
U = L > 0
U[:, :, :kcut] = False
v, f = surface(U, (0, 0, 0))
v2, f2 = decimate(v, f, 0.12)
um = trimesh.Trimesh(v2, f2, process=True)
if um.volume < 0: um.invert()
near = um.vertices[:, 2] < z_cut + 0.5 * P
um.vertices[near, 2] = np.maximum(um.vertices[near, 2], z_cut)
um.export(f'{B}/mesh_union.ply')
print('union faces', len(um.faces), 'watertight', um.is_watertight, 'volume %.0f' % um.volume, 'bounds', np.round(um.bounds, 1).tolist())
