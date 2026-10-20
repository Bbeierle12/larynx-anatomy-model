"""Load BodyParts3D 4.0 parts, clean, smooth, rotate (trachea vertical). Writes src_XX.ply (trachea uncut)."""
import sys, os, json, numpy as np, trimesh
sys.path.insert(0, os.path.dirname(__file__))
from partsconfig import PARTS
S = '/tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad'
OUT = os.environ['BUILD']; os.makedirs(OUT, exist_ok=True)
inv = json.load(open(f'{S}/bp4/parts/inventory.json'))
def load_clean(e):
    m = trimesh.load(f'{S}/bp4/parts/{e}.obj', force='mesh'); m.merge_vertices()
    bodies = [b for b in m.split(only_watertight=False) if abs(b.volume) > 0.01]
    big = max(bodies, key=lambda b: abs(b.volume)); c = big.bounds.mean(0)
    bodies = [b for b in bodies if np.linalg.norm(b.bounds.mean(0) - c) < 40]
    return trimesh.util.concatenate(bodies)
def smooth(m, iters_sub=2, taubin=10):
    try:
        v, f = trimesh.remesh.subdivide_loop(m.vertices, m.faces, iterations=iters_sub)
    except ValueError:
        v, f = m.vertices, m.faces
        for _ in range(iters_sub): v, f = trimesh.remesh.subdivide(v, f)
    s = trimesh.Trimesh(v, f, process=False)
    trimesh.smoothing.filter_taubin(s, lamb=0.5, nu=0.53, iterations=taubin)
    return s
T = load_clean(inv['trachea'][0])
seg = T.vertices[T.vertices[:, 2] > 1355]; c0 = seg.mean(0)
_, _, vt = np.linalg.svd(seg - c0); ax = vt[0] * np.sign(vt[0][2])
R = trimesh.transformations.rotation_matrix(np.arctan2(ax[1], ax[2]), [1, 0, 0], point=c0)
np.save(f'{OUT}/rotation.npy', R)
for pid, name, concepts, grp, pri, kind in PARTS:
    if not concepts: continue
    els = inv[concepts[0]]
    if concepts[0] in ('hyoid bone', 'cricoid cartilage'): els = els[:1]
    ms = []
    for e in els:
        m = load_clean(e); s = smooth(m)
        if (s.volume - m.volume) / m.volume < -0.15: s = smooth(m, 1, 0)
        s.apply_transform(R); ms.append(s)
    m = trimesh.util.concatenate(ms) if len(ms) > 1 else ms[0]
    m.export(f'{OUT}/src_{pid:02d}.ply')
    print(pid, name, len(m.faces))
