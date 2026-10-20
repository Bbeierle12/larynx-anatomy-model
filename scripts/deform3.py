"""Version-2 corrections (mesh-warp revision): (1) cricoid lamina extended down, arch lowered, ring deepened AP; (2) arytenoids abducted
to the respiratory position with attached soft tissue blended.  Reads src_XX.ply, writes part_XX.ply + grid.npy."""
import sys, os, json, numpy as np, trimesh, igl, edt, pymeshlab
from scipy import ndimage
from skimage import measure
sys.path.insert(0, os.path.dirname(__file__))
from partsconfig import PARTS
B = os.environ['BUILD']
F_AP = float(os.environ.get('F_AP', '1.2'))    # AP deepening of the cricoid ring
BASE0 = 1366.05                                 # old base (z) for reference
CX, CY = -0.65, -100.6
Z_NEW = BASE0 + float(os.environ.get('Z_NEW', '15.0'))   # new inferior border of the cricoid
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
    A0, A1 = float(os.environ.get('ARCH_A0', '20')), float(os.environ.get('ARCH_A1', '100'))   # full drop within A0 deg of anterior, none beyond A1
    return np.where(d <= A0, 1.0, np.where(d >= A1, 0.0, 0.5 * (1 + np.cos(np.pi * (d - A0) / (A1 - A0)))))
def d_cricoid(p):
    th = ang(p[:, 0], p[:, 1])
    return np.c_[np.zeros(len(p)), (p[:, 1] - CY) * (F_AP - 1), -ARCH_DROP * arch_w(th)]

# ---------------- cricoid: smooth mesh warp ----------------
# Lower border to Z_NEW all round; arch top dropped ARCH_DROP; lamina top, arytenoid facets and the
# cricothyroid facets unchanged; the stretch happens in a band above the rounded lower edge.
def cosw(d, a, b): return np.where(d <= a, 1.0, np.where(d >= b, 0.0, 0.5 * (1 + np.cos(np.pi * (d - a) / (b - a)))))
def adist(th, c): return np.abs(((th - c + 180) % 360) - 180)
cr = src(3)
thy = src(2).vertices
facet_angles = []
for sd in (-1, 1):
    q = thy[sd * (thy[:, 0] - CX) > 5]; tip = q[np.argmin(q[:, 2])]; facet_angles.append(float(ang(tip[0:1], tip[1:2])[0]))
NB = 72; tv = ang(cr.vertices[:, 0], cr.vertices[:, 1]); bi = (tv / (360 / NB)).astype(int) % NB
zb_bin = np.full(NB, np.inf); np.minimum.at(zb_bin, bi, cr.vertices[:, 2])
zb_bin = ndimage.gaussian_filter1d(zb_bin, 1.5, mode='wrap'); centers = (np.arange(NB) + 0.5) * 360 / NB
v, f = trimesh.remesh.subdivide_to_size(cr.vertices, cr.faces, max_edge=0.25, max_iter=20)
th = ang(v[:, 0], v[:, 1]); zb = np.interp(th, centers, zb_bin, period=360)
A = arch_w(th); Pw = cosw(adist(th, 90), 20, 45)
FW0, FW1 = float(os.environ.get('FW0', '6')), float(os.environ.get('FW1', '16'))
Fw = np.maximum(cosw(adist(th, facet_angles[0]), FW0, FW1), cosw(adist(th, facet_angles[1]), FW0, FW1))
HF, HL = float(os.environ.get('HF', '1.5')), float(os.environ.get('HL', '5.0'))
h = HF * Fw + (1 - Fw) * (HL + (7.0 - HL) * Pw + 1.0 * A)
mrg = 0.3 * Fw + (1 - Fw) * (0.8 + 2.2 * Pw)
t = np.clip((v[:, 2] - (zb + mrg)) / h, 0, 1); g = 1 - t * t * (3 - 2 * t)
dz_top = -ARCH_DROP * A; dz_bot = Z_NEW - zb
v2 = v.copy(); v2[:, 2] = v[:, 2] + dz_top + (dz_bot - dz_top) * g
v2[:, 1] = CY + (v[:, 1] - CY) * F_AP
crn = trimesh.Trimesh(v2, f, process=False)
assert crn.is_watertight
crn.export(f'{B}/part_03.ply')
print(f'cricoid: facet angles {facet_angles[0]:.0f}/{facet_angles[1]:.0f}; volume {cr.volume:.0f} -> {crn.volume:.0f} mm3; z {cr.bounds[0,2]-BASE0:.1f}..{cr.bounds[1,2]-BASE0:.1f} -> {crn.bounds[0,2]-BASE0:.1f}..{crn.bounds[1,2]-BASE0:.1f}')

# ---------------- arytenoids: rocking about the cricoarytenoid facet axis ----------------
# The main abduction motion is rocking about the long axis of the cricoid facet, which runs
# anterolaterally and downward; the vocal process moves laterally and upward.  ALPHA = rocking angle.
ALPHA = float(os.environ.get('ALPHA', '29'))
AX_EL = float(os.environ.get('AX_EL', '35'))      # facet axis: degrees below horizontal
AX_AZ = float(os.environ.get('AX_AZ', '45'))      # facet axis: degrees from the sagittal plane
AX_R = float(os.environ.get('AX_R', '3.0'))       # facet radius of curvature (axis depth below the contact)
crs = src(3); samp = crs.sample(150000)
def facet_patch(a):
    d2, _, _ = igl.point_mesh_squared_distance(np.ascontiguousarray(samp), np.ascontiguousarray(a.vertices, np.float64), np.ascontiguousarray(a.faces, np.int64))
    p = samp[np.sqrt(d2) < 1.0]; c = p.mean(0); n = np.linalg.svd(p - c, full_matrices=False)[2][2]
    return c, n * np.sign(n[2])
def ary_transform(pid, lat):
    a = src(pid)
    c, n = facet_patch(a)
    t = np.array([0, (c[1] - CY) * (F_AP - 1), 0])             # follow the AP deepening of the ring
    el, az = np.radians(AX_EL), np.radians(AX_AZ)
    d = np.array([lat * np.cos(el) * np.sin(az), -np.cos(el) * np.cos(az), -np.sin(el)])
    pt = c + t - AX_R * n
    vp = a.vertices[np.argmin(a.vertices[:, 1])] + t          # vocal process tip
    best = None
    for s in (1, -1):
        M = trimesh.transformations.rotation_matrix(np.radians(s * ALPHA), d, point=pt) @ trimesh.transformations.translation_matrix(t)
        mv = (M[:3, :3] @ (vp - t)) + M[:3, 3] - vp
        if best is None or lat * mv[0] > lat * best[1][0]: best = (M, mv)
    print(f'arytenoid {pid}: facet at {np.round(c - [0, 0, BASE0], 1)}, vocal process moves {np.round(best[1], 1)} mm')
    vs = a.vertices[np.argmin(a.vertices[:, 1])]
    D = (best[0][:3, :3] @ vs) + best[0][:3, 3] - vs                 # total displacement of the vocal process tip
    return best[0], a.vertices.mean(0), vs, D
MR, cR, VPR, DR = ary_transform(4, -1)     # right arytenoid (x < CX): lateral is -x
ML, cL, VPL, DL = ary_transform(5, +1)
def apply(M, p): return (M[:3, :3] @ p.T).T + M[:3, 3]
def d_side(p):
    dR = apply(MR, p) - p; dL = apply(ML, p) - p
    return np.where((p[:, 0] < CX)[:, None], dR, dL)
def d_fold(p, zfade=False):
    # Fold tissue between the anterior commissure (fixed) and the vocal process: displacement grows
    # linearly from 0 to the vocal-process displacement, so the free edge stays a straight line.
    # In the last 20 % next to the vocal process it blends into the arytenoid's rigid motion.
    right = (p[:, 0] < CX)
    vpy = np.where(right, VPR[1], VPL[1]); D = np.where(right[:, None], DR, DL)
    t = (p[:, 1] - Y_ANT) / (vpy - Y_ANT)
    tl = np.clip(t, 0, 1)[:, None]
    u = np.clip((t - 0.8) / 0.2, 0, 1); s = (u * u * (3 - 2 * u))[:, None]
    d = (1 - s) * tl * D + s * d_side(p)
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
    if pid == 11: p = p - [0, 0, float(os.environ.get('TRACHEA_DZ', '1.2'))]   # ring phase: keep an annular gap under the cricoid
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
