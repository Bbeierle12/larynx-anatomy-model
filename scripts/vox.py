import sys, os, time, numpy as np, trimesh, igl
sys.path.insert(0, os.path.dirname(__file__))
from partsconfig import PARTS
B = os.environ['BUILD']
g = np.load(f'{B}/grid.npy'); lo = g[:3]; P = g[3]; shape = tuple(int(x) for x in g[4:7])
only = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else None
for pid, name, concepts, grp, pri, kind in PARTS:
    if (not concepts and kind != 'sculpt') or (only and pid not in only): continue
    if not os.path.exists(f'{B}/part_{pid:02d}.ply'): continue
    m = trimesh.load(f'{B}/part_{pid:02d}.ply', process=False)
    a = np.clip(np.floor((m.bounds[0] - 0.3 - lo) / P).astype(int), 0, None)
    b = np.minimum(np.ceil((m.bounds[1] + 0.3 - lo) / P).astype(int) + 1, shape)
    xs, ys, zs = [lo[i] + P * np.arange(a[i], b[i]) for i in range(3)]
    G = np.stack(np.meshgrid(xs, ys, zs, indexing='ij'), -1).reshape(-1, 3)
    V = np.ascontiguousarray(m.vertices, np.float64); F = np.ascontiguousarray(m.faces, np.int64)
    w = np.empty(len(G), np.float32); t = time.time()
    for k in range(0, len(G), 3_000_000):
        w[k:k + 3_000_000] = igl.fast_winding_number(V, F, np.ascontiguousarray(G[k:k + 3_000_000]))
    occ = (w > 0.5).reshape(len(xs), len(ys), len(zs))
    np.savez_compressed(f'{B}/occ_{pid:02d}.npz', occ=occ, a=a, b=b)
    print(f'{pid:2d} {name:32s} {occ.sum()*P**3:8.1f} mm3 ({time.time()-t:.0f}s)', flush=True)
