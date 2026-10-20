"""Stage 1: load BodyParts3D 4.0 parts, clean, smooth, rotate (trachea vertical), voxelize each part (FWN) on a shared 0.1 mm grid."""
import sys, json, time, numpy as np, trimesh, igl
sys.path.insert(0, '/tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad/scripts')
from partsconfig import PARTS
B = '/tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad'
OUT = f'{B}/build'
PITCH = 0.1
TRACHEA_BELOW_CRICOID = 22.0   # mm of trachea kept below the lowest point of the cricoid
inv = json.load(open(f'{B}/bp4/parts/inventory.json'))

def load_clean(e):
    m = trimesh.load(f'{B}/bp4/parts/{e}.obj', force='mesh'); m.merge_vertices()
    bodies = [b for b in m.split(only_watertight=False) if abs(b.volume) > 0.01]
    return trimesh.util.concatenate(bodies)

def smooth(m, iters_sub=2, taubin=10):
    try:
        v, f = trimesh.remesh.subdivide_loop(m.vertices, m.faces, iterations=iters_sub) if iters_sub else (m.vertices, m.faces)
    except ValueError:   # non-manifold source mesh: midpoint subdivision + Taubin only
        v, f = m.vertices, m.faces
        for _ in range(iters_sub):
            v, f = trimesh.remesh.subdivide(v, f)
    s = trimesh.Trimesh(v, f, process=False)
    trimesh.smoothing.filter_taubin(s, lamb=0.5, nu=0.53, iterations=taubin)
    return s

# rotation: make upper trachea axis vertical
T = load_clean(inv['trachea'][0])
seg = T.vertices[T.vertices[:, 2] > 1355]; c0 = seg.mean(0)
_, _, vt = np.linalg.svd(seg - c0); ax = vt[0] * np.sign(vt[0][2])
theta = np.arctan2(ax[1], ax[2])          # rotate about x by +theta maps ax to +z  (y' = y cos - z sin ...)
R = trimesh.transformations.rotation_matrix(theta, [1, 0, 0], point=c0)
print('trachea tilt removed: %.2f deg about x' % np.degrees(theta))

meshes = {}
for pid, name, concepts, grp, pri, kind in PARTS:
    els = inv[concepts[0]]
    if concepts[0] in ('hyoid bone', 'cricoid cartilage'): els = els[:1]   # duplicated elements
    parts = []
    for e in els:
        m = load_clean(e)
        s = smooth(m)
        dv = (s.volume - m.volume) / m.volume
        if dv < -0.15:   # thin structure collapsing under subdivision: use lighter smoothing
            s = smooth(m, iters_sub=1, taubin=0)
            dv = (s.volume - m.volume) / m.volume
        s.apply_transform(R)
        parts.append(s)
        print(f'{pid:2d} {name:30s} {e} vol {m.volume:8.1f} -> {s.volume:8.1f} ({dv*100:+.1f}%)')
    meshes[pid] = trimesh.util.concatenate(parts) if len(parts) > 1 else parts[0]

cr = meshes[3]
z_cut = cr.bounds[0, 2] - TRACHEA_BELOW_CRICOID
print('cricoid lowest z', round(cr.bounds[0, 2], 2), 'trachea cut z', round(z_cut, 2))
# keep trachea slightly longer than the cut for hollowing (no cap at the base)
meshes[11] = meshes[11].slice_plane([0, 0, z_cut - 4], [0, 0, 1], cap=True)

lo = np.min([m.bounds[0] for m in meshes.values()], axis=0) - 2.0
hi = np.max([m.bounds[1] for m in meshes.values()], axis=0) + 2.0
lo[2] = z_cut - 4
lo = np.floor(lo / PITCH) * PITCH
shape = tuple(int(np.ceil((h - l) / PITCH)) + 1 for l, h in zip(lo, hi))
print('grid', shape, 'voxels %.1fM' % (np.prod(shape) / 1e6))
np.save(f'{OUT}/grid.npy', np.array([*lo, PITCH, *shape, z_cut]))
for pid, m in meshes.items():
    m.export(f'{OUT}/part_{pid:02d}.ply')
    a = np.clip(np.floor((m.bounds[0] - 0.3 - lo) / PITCH).astype(int), 0, None)
    b = np.minimum(np.ceil((m.bounds[1] + 0.3 - lo) / PITCH).astype(int) + 1, shape)
    xs, ys, zs = [lo[i] + PITCH * np.arange(a[i], b[i]) for i in range(3)]
    G = np.stack(np.meshgrid(xs, ys, zs, indexing='ij'), -1).reshape(-1, 3)
    V = np.ascontiguousarray(m.vertices, np.float64); F = np.ascontiguousarray(m.faces, np.int64)
    w = np.empty(len(G), np.float32)
    t = time.time()
    for k in range(0, len(G), 3_000_000):
        w[k:k + 3_000_000] = igl.fast_winding_number(V, F, np.ascontiguousarray(G[k:k + 3_000_000]))
    occ = (w > 0.5).reshape(len(xs), len(ys), len(zs))
    np.savez_compressed(f'{OUT}/occ_{pid:02d}.npz', occ=occ, a=a, b=b)
    print(f'   voxelized {pid:2d} {occ.sum()*PITCH**3:8.1f} mm3 vs mesh {m.volume:8.1f}  ({time.time()-t:.0f}s)')
