"""Version-2 corrections: (1) cricoid lamina extended down, arch lowered, ring deepened AP; (2) arytenoids abducted
to the respiratory position with attached soft tissue blended.  Reads src_XX.ply, writes part_XX.ply + grid.npy."""
import sys, os, json, numpy as np, trimesh, igl, edt, pymeshlab
from scipy import ndimage
from skimage import measure
sys.path.insert(0, os.path.dirname(__file__))
from partsconfig import PARTS
B = os.environ['BUILD']
PHI = float(os.environ.get('PHI', '35'))       # abduction rotation (deg) per arytenoid
F_AP = float(os.environ.get('F_AP', '1.2'))    # AP deepening of the cricoid ring
BASE0 = 1366.05                                 # old base (z) for reference
CX, CY = -0.65, -100.6
Z_NEW = BASE0 + 16.0          # new inferior border of the cricoid
ARCH_DROP = 6.0               # arch moved down (mm)
Z_JOINT = BASE0 + 24.8        # cricothyroid joints: lateral cricoid above this is kept
Z_VL = BASE0 + 38.5           # vocal-fold level
Z_THY_LOW = BASE0 + 30.2      # thyroid lower border at the midline
Z_ARCH_TOP = BASE0 + 27.5
Z_APEX, Z_EP = BASE0 + 44.9, BASE0 + 62.0
Y_ANT, Y_VP = -112.0, -99.4
P = 0.1
src = lambda i: trimesh.load(f'{B}/src_{i:02d}.ply', process=False)

def ang(x, y): return (np.degrees(np.arctan2(y - CY, x - CX)) + 360) % 360
def arch_w(th):
    d = np.abs(((th - 270 + 180) % 360) - 180)
    return np.where(d <= 35, 1.0, np.where(d >= 75, 0.0, 0.5 * (1 + np.cos(np.pi * (d - 35) / 40))))
def d_cricoid(p):
    th = ang(p[:, 0], p[:, 1])
    return np.c_[np.zeros(len(p)), (p[:, 1] - CY) * (F_AP - 1), -ARCH_DROP * arch_w(th)]

# ---------------- cricoid: voxel reshape ----------------
cr = src(3)
lo = np.floor((cr.bounds[0] - [3, 4, 12]) / P) * P; hi = cr.bounds[1] + [3, 4, 2]
shape = tuple(int(np.ceil((h - l) / P)) + 1 for l, h in zip(lo, hi))
xs, ys, zs = [lo[i] + P * np.arange(shape[i]) for i in range(3)]
G = np.stack(np.meshgrid(xs, ys, zs, indexing='ij'), -1).reshape(-1, 3)
w = np.empty(len(G), np.float32)
V = np.ascontiguousarray(cr.vertices, np.float64); Fc = np.ascontiguousarray(cr.faces, np.int64)
for k in range(0, len(G), 3_000_000): w[k:k + 3_000_000] = igl.fast_winding_number(V, Fc, np.ascontiguousarray(G[k:k + 3_000_000]))
C = (w > 0.5).reshape(shape); del G, w
X, Y = np.meshgrid(xs, ys, indexing='ij'); TH = ang(X, Y); A = arch_w(TH)
ks = np.round(ARCH_DROP * A / P).astype(int)                     # shift down by ks voxels
K = np.arange(shape[2])[None, None, :] + ks[:, :, None]
valid = K < shape[2]
C1 = np.where(valid, np.take_along_axis(C, np.clip(K, 0, shape[2] - 1), axis=2), False)
# extrusion of the wall profile down to the new inferior border
has = C1.any(2); kbot = np.where(has, np.argmax(C1, axis=2), 10**6)
NB = 72; tb = (TH / (360 / NB)).astype(int) % NB
zlo_bin = np.full(NB, 10**6); np.minimum.at(zlo_bin, tb[has], kbot[has])
near_bottom = has & (kbot <= zlo_bin[tb] + int(2.5 / P))
solid_above = np.take_along_axis(C1, np.clip(kbot + int(1.0 / P), 0, shape[2] - 1)[:, :, None], axis=2)[:, :, 0]
ext = near_bottom & solid_above
knew = int(round((Z_NEW - lo[2]) / P))
kk = np.arange(shape[2])[None, None, :]
C2 = C1 | (ext[:, :, None] & (kk >= knew) & (kk <= kbot[:, :, None]))
# AP deepening about the ring centre
jj = np.arange(shape[1]); ysrc = CY + (ys - CY) / F_AP
jsrc = np.round((ysrc - lo[1]) / P).astype(int); okj = (jsrc >= 0) & (jsrc < shape[1])
C3 = np.zeros_like(C2); C3[:, okj, :] = C2[:, jsrc[okj], :]
# surface
pad = 3; m = np.pad(C3, pad)
sdf = (edt.edt(~m, anisotropy=(P, P, P), black_border=False) - edt.edt(m, anisotropy=(P, P, P), black_border=True)).astype(np.float32)
sdf[m] += P / 2; sdf[~m] -= P / 2
sdf = ndimage.gaussian_filter(sdf, 1.5)
v, f, _, _ = measure.marching_cubes(sdf, 0.0, spacing=(P, P, P)); v += lo - pad * P
print('MC verts', len(v), 'nonfinite', (~np.isfinite(v)).sum(), 'z range', v[:,2].min()-BASE0, v[:,2].max()-BASE0, 'sdf finite', np.isfinite(sdf).all())
ms = pymeshlab.MeshSet(); ms.add_mesh(pymeshlab.Mesh(np.ascontiguousarray(v, np.float64), np.ascontiguousarray(f[:, ::-1], np.int32)))
ms.meshing_decimation_quadric_edge_collapse(targetfacenum=120000, qualitythr=0.4, preserveboundary=True, preservenormal=True, preservetopology=True, optimalplacement=True, planarquadric=True)
ms.meshing_remove_unreferenced_vertices()
mm = ms.current_mesh()
print('after decimation z range', mm.vertex_matrix()[:,2].min()-BASE0); crn = trimesh.Trimesh(mm.vertex_matrix(), mm.face_matrix(), process=True)
if crn.volume < 0: crn.invert()
crn.export(f'{B}/part_03.ply')
print(f'cricoid: volume {cr.volume:.0f} -> {crn.volume:.0f} mm3; z {cr.bounds[0,2]-BASE0:.1f}..{cr.bounds[1,2]-BASE0:.1f} -> {crn.bounds[0,2]-BASE0:.1f}..{crn.bounds[1,2]-BASE0:.1f}; AP extent {np.ptp(cr.vertices[:,1]):.1f} -> {np.ptp(crn.vertices[:,1]):.1f}')

# ---------------- arytenoid rigid transforms ----------------
def ary_transform(pid, sign):
    a = src(pid).vertices
    base = a[a[:, 2] < a[:, 2].min() + 1.5].mean(0)
    t = np.array([0, (base[1] - CY) * (F_AP - 1), 0])
    c = base + t
    Rz = trimesh.transformations.rotation_matrix(np.radians(sign * PHI), [0, 0, 1], point=c)
    M = Rz @ trimesh.transformations.translation_matrix(t)
    return M, a.mean(0)
MR, cR = ary_transform(4, -1)     # right (x<CX): clockwise swings the vocal process laterally
ML, cL = ary_transform(5, +1)
def apply(M, p): return (M[:3, :3] @ p.T).T + M[:3, 3]
def d_side(p):
    dR = apply(MR, p) - p; dL = apply(ML, p) - p
    return np.where((p[:, 0] < CX)[:, None], dR, dL)
def w_fold(p):
    t = np.clip((p[:, 1] - Y_ANT) / (Y_VP - Y_ANT), 0, 1); return t * t * (3 - 2 * t)
def d_fold(p, zfade=False):
    d = w_fold(p)[:, None] * d_side(p)
    if zfade: d *= np.clip((Z_EP - p[:, 2]) / (Z_EP - (Z_VL + 6)), 0, 1)[:, None]
    return d
def zhi_cricoid(th):
    # original cricoid upper border per angle
    Vc = src(3).vertices; tv = ang(Vc[:, 0], Vc[:, 1]); b = (tv / 5).astype(int) % 72
    zh = np.full(72, -1e9); np.maximum.at(zh, b, Vc[:, 2])
    return zh[(th / 5).astype(int) % 72]

out = {}
for pid, name, concepts, grp, pri, kind in PARTS:
    if not concepts or pid == 3: continue
    m = src(pid); p = m.vertices.copy()
    if pid in (4, 6):   p = apply(MR, p)                     # right arytenoid + corniculate (rigid)
    elif pid in (5, 7): p = apply(ML, p)
    elif pid in (12, 13, 26, 27): p = p + d_fold(p)          # vocal ligament, vocalis
    elif pid in (24, 25): p = p + d_fold(p, zfade=True)      # thyro-arytenoid (both parts)
    elif pid in (14, 15):                                     # conus: cricoid below, fold above
        th = ang(p[:, 0], p[:, 1]); zh = zhi_cricoid(th)
        wc = np.clip((Z_VL - p[:, 2]) / np.maximum(Z_VL - zh, 1.0), 0, 1)[:, None]
        p = p + wc * d_cricoid(p) + (1 - wc) * d_fold(p)
    elif pid == 16:                                           # median cricothyroid ligament: arch below, thyroid above
        wc = np.clip((Z_THY_LOW - p[:, 2]) / (Z_THY_LOW - Z_ARCH_TOP), 0, 1)[:, None]
        p = p + wc * d_cricoid(p)
    elif pid in (28, 29, 30):                                 # interarytenoid muscles stretch between the arytenoids
        wl = np.clip((p[:, 0] - cR[0]) / (cL[0] - cR[0]), 0, 1)[:, None]
        p = p + (1 - wl) * (apply(MR, p) - p) + wl * (apply(ML, p) - p)
    elif pid in (31, 32, 8, 9):                               # aryepiglottic folds + cuneiforms
        wa = np.clip((Z_EP - p[:, 2]) / (Z_EP - Z_APEX), 0, 1)[:, None]
        p = p + wa * d_side(p)
    m = trimesh.Trimesh(p, m.faces, process=False)
    out[pid] = m
    m.export(f'{B}/part_{pid:02d}.ply')
# grid: trachea kept 22 mm below the new cricoid
z_cut = crn.bounds[0, 2] - 22.0
T = trimesh.load(f'{B}/part_11.ply', process=False)
T = T.slice_plane([0, 0, z_cut - 4], [0, 0, 1], cap=True); T.export(f'{B}/part_11.ply')
allb = [trimesh.load(f'{B}/part_{i:02d}.ply', process=False).bounds for i in [p[0] for p in PARTS if p[2]]]
lo_g = np.min([b[0] for b in allb], 0) - 2.0; hi_g = np.max([b[1] for b in allb], 0) + 2.0
lo_g[2] = z_cut - 4; lo_g = np.floor(lo_g / P) * P
shape_g = tuple(int(np.ceil((h - l) / P)) + 1 for l, h in zip(lo_g, hi_g))
np.save(f'{B}/grid.npy', np.array([*lo_g, P, *shape_g, z_cut]))
print('new z_cut %.2f (old base %.2f); grid %s' % (z_cut, BASE0, shape_g))
