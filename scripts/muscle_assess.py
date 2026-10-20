"""Load the stage-2 muscles from BodyParts3D, rotate into the model frame, and measure them against the SOURCE framework (build5/src_*)."""
import sys, os, json, numpy as np, trimesh, igl
S = '/tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad'
B5 = f'{S}/build5'; OUT = f'{S}/build6'
R = np.load(f'{B5}/rotation.npy')
inv = json.load(open(f'{S}/bp4/parts/inventory.json'))
def load_clean(e, keep_all=False):
    m = trimesh.load(f'{S}/bp4/parts/{e}.obj', force='mesh'); m.merge_vertices()
    bodies = [b for b in m.split(only_watertight=False) if abs(b.volume) > 0.01]
    big = max(bodies, key=lambda b: abs(b.volume)); c = big.bounds.mean(0)
    if not keep_all: bodies = [b for b in bodies if np.linalg.norm(b.bounds.mean(0) - c) < 40]
    return trimesh.util.concatenate(bodies), bodies
def smooth(m, iters_sub=2, taubin=10):
    try: v, f = trimesh.remesh.subdivide_loop(m.vertices, m.faces, iterations=iters_sub)
    except ValueError:
        v, f = m.vertices, m.faces
        for _ in range(iters_sub): v, f = trimesh.remesh.subdivide(v, f)
    s = trimesh.Trimesh(v, f, process=False); trimesh.smoothing.filter_taubin(s, lamb=0.5, nu=0.53, iterations=taubin); return s
MUS = {'PCA R': 'FJ2800', 'PCA L': 'FJ2782', 'LCA R': 'FJ2796', 'LCA L': 'FJ2778',
       'CT straight R': 'FJ2801', 'CT straight L': 'FJ2783', 'CT oblique R': 'FJ2799', 'CT oblique L': 'FJ2781',
       'TA R a': 'FJ2802', 'TA R b': 'FJ2803', 'TA L a': 'FJ2784', 'TA L b': 'FJ2785', 'vocalis R': 'FJ2806', 'vocalis L': 'FJ2788',
       'transverse ary': 'FJ2809', 'oblique ary R': 'FJ2798', 'oblique ary L': 'FJ2780', 'aryepiglotticus R': 'FJ2791', 'aryepiglotticus L': 'FJ2774'}
src = lambda i: trimesh.load(f'{B5}/src_{i:02d}.ply', process=False)
thy, cri, aR, aL, epi = src(2), src(3), src(4), src(5), src(10)
BASE0 = 1359.0
def near(m, pts, tol=1.0):
    d2, _, _ = igl.point_mesh_squared_distance(np.ascontiguousarray(pts, np.float64), np.ascontiguousarray(m.vertices, np.float64), np.ascontiguousarray(m.faces, np.int64)); return np.sqrt(d2) < tol
os.makedirs(OUT, exist_ok=True)
for name, e in MUS.items():
    raw, bodies = load_clean(e, keep_all=True)
    big = max(bodies, key=lambda b: abs(b.volume)); c = big.bounds.mean(0)
    far = [b for b in bodies if np.linalg.norm(b.bounds.mean(0) - c) >= 40]
    m = trimesh.util.concatenate([b for b in bodies if np.linalg.norm(b.bounds.mean(0) - c) < 40])
    m.apply_transform(R); raw_vol = m.volume
    s = smooth(m); s.apply_transform(R)
    v = s.vertices; lo, hi = s.bounds
    # attachment fractions: vertices within 1 mm of each cartilage
    fr = {k: near(mm, v).mean() * 100 for k, mm in [('thy', thy), ('cri', cri), ('aryR', aR), ('aryL', aL), ('epi', epi)]}
    print(f'{name:18s} {e} raw vol {raw_vol:7.1f} smooth {s.volume:7.1f} mm3  far bodies {len(far)}  x {lo[0]:6.1f}..{hi[0]:6.1f}  y {lo[1]:7.1f}..{hi[1]:7.1f}  z {lo[2]-BASE0:5.1f}..{hi[2]-BASE0:5.1f}  near%: ' + ' '.join(f'{k} {fr[k]:4.0f}' for k in fr))
    s.export(f'{OUT}/mus_{e}.ply')
