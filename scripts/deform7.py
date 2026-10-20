"""Version 5 framework = version 3 stage 1 + lateral widening (thyroid x SXT about the midline; cricoid outer wall radially, lumen kept).
1. Whole laryngeal framework below the hyoid deepened front-to-back by G about the laryngeal prominence (the source
   thyroid is ~12-15 % shallow against adult-male norms); the hyoid is unchanged and hyoid-attached membranes blend.
2. Cricoid placed between the thyroid's lower edge (3 mm set-back) and posterior border (0.5 mm behind), widened SX,
   lamina lengthened, arch dropped (as v2/v3).  Thyroid inferior horns re-seated on the facets (slight overlap so the
   print fuses the joint).
3. Arytenoids scaled about their facets (SA), rocked ALPHA about the facet axis (AX_AZ from sagittal); facet pads fill
   the lamina shoulder under the enlarged bases.
4. Soft tissue blended; median cricothyroid ligament follows the conus rule.  Hyo-epiglottic band, posterior
   cricoarytenoid ligaments as in deform4.  Reads src_XX.ply, writes part_XX.ply + grid.npy."""
import sys, os, numpy as np, trimesh, igl, shapely
from scipy import ndimage
sys.path.insert(0, os.path.dirname(__file__))
from partsconfig import PARTS
B = os.environ['BUILD']
E = lambda k, d: float(os.environ.get(k, d))
G = E('G', '1.12'); G_HORN = E('G_HORN', '1.08')
SX = E('SX', '1.30'); SX_RING = E('SX_RING', '1.08')      # transverse widening: SX_RING at the ring, SX at the lamina top (facets)
SA = np.array([E('SA_X', '1.25'), E('SA_Y', '1.55'), E('SA_Z', '1.9')])
ARCH_SETBACK = E('ARCH_SETBACK', '2.5'); LAMINA_BEHIND = E('LAMINA_BEHIND', '1.0')
SXT = E('SXT', '1.10')                                  # thyroid lateral scale about the midline
PET_LIFT = E('PET_LIFT', '5.0'); TIP_LIFT = E('TIP_LIFT', '5.0')   # v6: raise the petiole (and the tip less) so the thyro-epiglottic ligament attaches above the vestibular ligaments
CR_W = E('CR_W', '0.10'); CR_R0 = E('CR_R0', '8.8'); CR_R1 = E('CR_R1', '11.2')   # cricoid outer wall: lateral widening ramping from r=CR_R0 (none) to CR_R1 (full)
BASE0 = 1366.05
CX, CY = -0.65, -100.6
Z_NEW = BASE0 + E('Z_NEW', '15.0')
ARCH_DROP = 6.0
Z_VL = BASE0 + 38.5; Z_THY_LOW = BASE0 + 30.2; Z_ARCH_TOP = BASE0 + 27.5
Z_APEX, Z_EP = BASE0 + 44.9, BASE0 + 62.0
Y_ANT = -112.0
P = 0.1
src = lambda i: trimesh.load(f'{B}/src_{i:02d}.ply', process=False)
def ang(x, y): return (np.degrees(np.arctan2(y - CY, x - CX)) + 360) % 360
def cosw(d, a, b): return np.where(d <= a, 1.0, np.where(d >= b, 0.0, 0.5 * (1 + np.cos(np.pi * (d - a) / (b - a)))))
def adist(th, c): return np.abs(((th - c + 180) % 360) - 180)
def arch_w(th): return cosw(adist(th, 270), E('ARCH_A0', '20'), E('ARCH_A1', '100'))
def smooth01(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)

# ---------------- global AP deepening about the laryngeal prominence ----------------
thy = src(2); hy = src(1); cr = src(3)
Y0 = thy.vertices[:, 1].min()
Z_TT = BASE0 + 55.7     # thyroid upper border at the membrane
Z_HL = hy.vertices[:, 2].min() + 1.0
def g_ap(p, w=None):
    d = np.zeros_like(p); d[:, 1] = (p[:, 1] - Y0) * (G - 1) * (1.0 if w is None else w); return d
def w_hyoid(p):     # 1 at the thyroid upper border, 0 at the hyoid lower border (for hyoid-attached membranes)
    return 1 - smooth01((p[:, 2] - Z_TT) / (Z_HL - Z_TT))
# thyroid: full G on the laminae, G_HORN at the superior horn tips
tv = thy.vertices
wt = 1 - smooth01((tv[:, 2] - (BASE0 + 55.0)) / 9.0) * (1 - (G_HORN - 1) / (G - 1))
def lat_thy(p, w=None):
    d = np.zeros_like(p); d[:, 0] = (p[:, 0] - CX) * (SXT - 1) * (1.0 if w is None else w); return d
thy_v = tv + g_ap(tv, wt) + lat_thy(tv)
thy_low = thy_v[np.abs(tv[:, 0] - CX) < 1.5]; thy_low = thy_low[thy_low[:, 2] < thy_low[:, 2].min() + 1.5][:, 1].min()
thy_post = thy_v[(np.abs(tv[:, 0] - CX) > 6) & (tv[:, 2] > BASE0 + 33) & (tv[:, 2] < BASE0 + 43)][:, 1].max()
print(f'global AP x{G}: thyroid prominence {Y0:.1f} fixed; lower edge y {thy_low:.1f}; posterior border y {thy_post:.1f}')

# ---------------- cricoid: placed between the thyroid lower edge and posterior border ----------------
cv = cr.vertices
y_front, y_back = cv[:, 1].min(), cv[:, 1].max()
T_front, T_back = thy_low + ARCH_SETBACK, thy_post + LAMINA_BEHIND
def y_cric(y): return T_front + (y - y_front) / (y_back - y_front) * (T_back - T_front)
CYn = y_cric(CY)
facet_angles = []; horn_tips = []
for sd in (-1, 1):
    q = tv[sd * (tv[:, 0] - CX) > 5]; tip = q[np.argmin(q[:, 2])]
    facet_angles.append(float(ang(tip[0:1], tip[1:2])[0])); horn_tips.append(tip)
NB = 72; tva = ang(cv[:, 0], cv[:, 1]); bi = (tva / (360 / NB)).astype(int) % NB
zb_bin = np.full(NB, np.inf); np.minimum.at(zb_bin, bi, cv[:, 2])
zb_bin = ndimage.gaussian_filter1d(zb_bin, 1.5, mode='wrap'); centers = (np.arange(NB) + 0.5) * 360 / NB
FW0, FW1 = E('FW0', '6'), E('FW1', '16'); HF, HL = E('HF', '1.5'), E('HL', '5.0')
def warp_cricoid(v, stretch=True):
    th = ang(v[:, 0], v[:, 1]); A = arch_w(th)
    sx = SX_RING + (SX - SX_RING) * smooth01((v[:, 2] - Z_ARCH_TOP) / (BASE0 + 38.0 - Z_ARCH_TOP))
    rr = np.hypot(v[:, 0] - CX, v[:, 1] - CY); wr = CR_W * smooth01((rr - CR_R0) / (CR_R1 - CR_R0))
    out = np.c_[(v[:, 0] - CX) * (sx - 1) + (v[:, 0] - CX) * sx * wr, y_cric(v[:, 1]) - v[:, 1], -ARCH_DROP * A]
    if stretch:
        zb = np.interp(th, centers, zb_bin, period=360); Pw = cosw(adist(th, 90), 20, 45)
        Fw = np.maximum(cosw(adist(th, facet_angles[0]), FW0, FW1), cosw(adist(th, facet_angles[1]), FW0, FW1))
        h = HF * Fw + (1 - Fw) * (HL + (7.0 - HL) * Pw + 1.0 * A); mrg = 0.3 * Fw + (1 - Fw) * (0.8 + 2.2 * Pw)
        g = 1 - smooth01((v[:, 2] - (zb + mrg)) / h)
        out[:, 2] = -ARCH_DROP * A + (Z_NEW - zb + ARCH_DROP * A) * g
    return out
v, f = trimesh.remesh.subdivide_to_size(cv, cr.faces, max_edge=0.25, max_iter=20)
crn = trimesh.Trimesh(v + warp_cricoid(v), f, process=False); assert crn.is_watertight
crn.export(f'{B}/part_03.ply')
print(f'thyroid lateral x{SXT}; cricoid outer wall +{CR_W*100:.0f}% beyond r {CR_R0}-{CR_R1}')
print(f'cricoid: y {y_front:.1f}..{y_back:.1f} -> {T_front:.1f}..{T_back:.1f} (AP {T_back-T_front:.1f}); width {np.ptp(cv[:,0]):.1f} -> {np.ptp(crn.vertices[:,0]):.1f}; z -> {crn.bounds[0,2]-BASE0:.1f}..{crn.bounds[1,2]-BASE0:.1f}; volume {cr.volume:.0f} -> {crn.volume:.0f}')

# ---------------- thyroid: inferior horns re-seated on the moved facets ----------------
crV = np.ascontiguousarray(cv, np.float64); crF = np.ascontiguousarray(cr.faces, np.int64)
crnV = np.ascontiguousarray(crn.vertices, np.float64); crnF = np.ascontiguousarray(crn.faces, np.int64)
OVERLAP = E('JOINT_OVERLAP', '0.2')
disp = g_ap(tv, wt) + lat_thy(tv)
for sd, tip in zip((-1, 1), horn_tips):
    d0, _, cp = igl.point_mesh_squared_distance(np.ascontiguousarray(tip[None, :]), crV, crF)
    cp0 = np.asarray(cp).reshape(3); dfac = warp_cricoid(cp0[None, :])[0]
    tipg = tip + g_ap(tip[None, :], wt[np.argmin(np.linalg.norm(tv - tip, axis=1))])[0] + lat_thy(tip[None, :])[0]
    extra = (tip + dfac) - tipg
    for _ in range(4):
        tip2 = tipg + extra
        d1, _, cp1 = igl.point_mesh_squared_distance(np.ascontiguousarray(tip2[None, :]), crnV, crnF)
        cp1 = np.asarray(cp1).reshape(3); nrm = tip2 - cp1; nrm /= np.linalg.norm(nrm) + 1e-9
        extra = extra + nrm * ((np.sqrt(d0[0]) - OVERLAP) - np.sqrt(d1[0]))
    side = (sd * (tv[:, 0] - CX) > 2) & (tv[:, 1] > -103)
    w = 1 - smooth01((tv[:, 2] - (tip[2] + 2.0)) / 10.0)
    disp[side] += (w[side])[:, None] * extra
    print(f'thyroid inferior horn ({"R" if sd < 0 else "L"}): extra move {np.round(extra, 2)} (joint {np.sqrt(d0[0]):.2f} -> {np.sqrt(d1[0]):.2f} mm)')
thn = trimesh.Trimesh(tv + disp, thy.faces, process=False); thn.export(f'{B}/part_02.ply')

# ---------------- arytenoids ----------------
ALPHA = E('ALPHA', '9'); AX_EL = E('AX_EL', '35'); AX_AZ = E('AX_AZ', '30'); AX_R = E('AX_R', '3.0')
samp = cr.sample(150000)
def facet_patch(a):
    d2, _, _ = igl.point_mesh_squared_distance(np.ascontiguousarray(samp), np.ascontiguousarray(a.vertices, np.float64), np.ascontiguousarray(a.faces, np.int64))
    p = samp[np.sqrt(d2) < 1.0]; c = p.mean(0); n = np.linalg.svd(p - c, full_matrices=False)[2][2]
    return c, n * np.sign(n[2])
T = trimesh.transformations.translation_matrix
def ary_transform(pid, lat):
    a = src(pid); c, n = facet_patch(a)
    t = warp_cricoid(c[None, :])[0]; c2 = c + t
    S = np.eye(4); S[0, 0], S[1, 1], S[2, 2] = SA
    Msc = T(c2) @ S @ T(-c2) @ T(t)
    el, az = np.radians(AX_EL), np.radians(AX_AZ)
    d = np.array([lat * np.cos(el) * np.sin(az), -np.cos(el) * np.cos(az), -np.sin(el)])
    pt = c2 - AX_R * n
    vs = a.vertices[np.argmin(a.vertices[:, 1])]
    best = None
    for s in (1, -1):
        M = trimesh.transformations.rotation_matrix(np.radians(s * ALPHA), d, point=pt) @ Msc
        vp2 = M[:3, :3] @ vs + M[:3, 3]
        if best is None or lat * vp2[0] > lat * best[1][0]: best = (M, vp2)
    apex = a.vertices[np.argmax(a.vertices[:, 2])]; apex2 = best[0][:3, :3] @ apex + best[0][:3, 3]
    print(f'arytenoid {pid}: facet {np.round(c - [0,0,BASE0], 1)} -> {np.round(c2 - [0,0,BASE0], 1)}; VP {np.round(vs - [0,0,BASE0], 1)} -> {np.round(best[1] - [0,0,BASE0], 1)}; apex z {apex[2]-BASE0:.1f} -> {apex2[2]-BASE0:.1f}')
    return best[0], a.vertices.mean(0), vs, best[1], c2
MR, cR, VPR, VPR2, FR = ary_transform(4, -1)
ML, cL, VPL, VPL2, FL = ary_transform(5, +1)
def apply(M, p): return (M[:3, :3] @ p.T).T + M[:3, 3]
def D_side(p):
    dR = apply(MR, p) - p; dL = apply(ML, p) - p
    return np.where((p[:, 0] < CX)[:, None], dR, dL)
def D_fold(p, zfade=False):
    """total displacement for fold tissue: global AP everywhere, plus a linear share of the vocal process's extra motion"""
    right = (p[:, 0] < CX)
    vpy = np.where(right, VPR[1], VPL[1])
    Ev = np.where(right[:, None], (VPR2 - VPR) - g_ap(VPR[None, :])[0], (VPL2 - VPL) - g_ap(VPL[None, :])[0])
    t = (p[:, 1] - Y_ANT) / (vpy - Y_ANT); tl = np.clip(t, 0, 1)[:, None]
    s = smooth01((t - 0.8) / 0.2)[:, None]
    d = (1 - s) * (g_ap(p) + tl * Ev) + s * D_side(p)
    if zfade:
        fz = np.clip((Z_EP - p[:, 2]) / (Z_EP - (Z_VL + 6)), 0, 1)[:, None]
        d = g_ap(p) + fz * (d - g_ap(p))
    return d
def D_cric_soft(p): return warp_cricoid(p, stretch=False)
def zhi_cricoid(th):
    b = (ang(cv[:, 0], cv[:, 1]) / 5).astype(int) % 72
    zh = np.full(72, -1e9); np.maximum.at(zh, b, cv[:, 2]); return zh[(th / 5).astype(int) % 72]

_ep = src(10).vertices; _ep = _ep + g_ap(_ep); Z_PET, Z_TIP = _ep[:, 2].min(), _ep[:, 2].max()
def lift(z): return PET_LIFT + (TIP_LIFT - PET_LIFT) * smooth01((z - Z_PET) / (Z_TIP - Z_PET))
print(f'epiglottis petiole lifted {PET_LIFT} mm (tip {TIP_LIFT}): petiole bottom {Z_PET-BASE0:.1f} -> {Z_PET-BASE0+PET_LIFT:.1f}, tip {Z_TIP-BASE0:.1f} -> {Z_TIP-BASE0+TIP_LIFT:.1f}')
for pid, name, concepts, grp, pri, kind in PARTS:
    if not concepts or pid in (1, 2, 3, 22): continue
    m = src(pid); p = m.vertices.copy()
    if pid in (4, 6):   p = apply(MR, p)
    elif pid in (5, 7): p = apply(ML, p)
    elif pid in (12, 13, 26, 27): p = p + D_fold(p)
    elif pid in (24, 25):
        wl = np.clip((np.abs(p[:, 0] - CX) - 3.0) / 6.0, 0, 1)
        p = p + D_fold(p, zfade=True) + lat_thy(p, wl)
    elif pid in (14, 15, 16):                                   # conus and median cricothyroid ligament: cricoid below, fold above
        th = ang(p[:, 0], p[:, 1]); zh = zhi_cricoid(th)
        wc = np.clip((Z_VL - p[:, 2]) / np.maximum(Z_VL - zh, 1.0), 0, 1)[:, None]
        if pid == 16: wc = np.clip((Z_THY_LOW - p[:, 2]) / (Z_THY_LOW - Z_ARCH_TOP), 0, 1)[:, None]
        p = p + wc * D_cric_soft(p) + (1 - wc) * (D_fold(p) if pid != 16 else g_ap(p))
    elif pid in (28, 29, 30):
        wl = np.clip((p[:, 0] - cR[0]) / (cL[0] - cR[0]), 0, 1)[:, None]
        p = p + (1 - wl) * (apply(MR, p) - p) + wl * (apply(ML, p) - p)
    elif pid in (31, 32, 8, 9):
        wa = np.clip((Z_EP - p[:, 2]) / (Z_EP - Z_APEX), 0, 1)[:, None]
        wl = np.clip((np.abs(p[:, 0] - CX) - 3.0) / 6.0, 0, 1) * 0.5
        p = p + wa * D_side(p) + (1 - wa) * g_ap(p) + lat_thy(p, wl)
        p[:, 2] += (1 - wa[:, 0]) * lift(p[:, 2])                                  # epiglottis-side ends follow the lifted margin
    elif pid in (17, 18, 19, 20, 21): p = p + g_ap(p, w_hyoid(p)) + lat_thy(p, w_hyoid(p))          # hyoid-attached membranes and ligaments
    elif pid == 11: p = p + g_ap(p); p[:, 1] = y_cric(p[:, 1]); p = p - [0, 0, E('TRACHEA_DZ', '2.2')]
    elif pid in (80, 81):                                                       # inferior constrictors: follow the widened laminae, the cricoid warp below the lamina
        wc = np.clip((BASE0 + E('CON_ZC', '38.0') - p[:, 2]) / 10.0, 0, 1)[:, None]
        p = p + wc * D_cric_soft(p) + (1 - wc) * (g_ap(p, w_hyoid(p)) + lat_thy(p, w_hyoid(p)))
    else:
        p = p + g_ap(p)                                                         # epiglottis, thyro-epiglottic ligament
        if pid in (10, 23): p[:, 2] += lift(p[:, 2])
        if pid == 23:                                                           # seat the thyroid end on the inner angle: forward and a little higher at the front
            t = (p[:, 1] - p[:, 1].min()) / max(p[:, 1].max() - p[:, 1].min(), 1e-6)
            p[:, 1] -= E('TEL_FWD', '2.3') * (1 - t); p[:, 2] += E('TEL_UP', '2.0') * (1 - t)
    trimesh.Trimesh(p, m.faces, process=False).export(f'{B}/part_{pid:02d}.ply')
hy.export(f'{B}/part_01.ply')

# ---------------- facet pads: fill the lamina shoulder under the enlarged arytenoid bases ----------------
for pid, M, apid, lat in ((38, MR, 4, -1), (39, ML, 5, 1)):
    a = apply(M, src(apid).vertices)
    base = a[a[:, 2] < a[:, 2].min() + 2.0]
    hull = trimesh.convex.convex_hull(np.vstack([base, base - [0, 0, E('PAD_DEPTH', '4.0')]]))
    # keep only what lies over cartilage: clip at the lamina's inner face (fitted near the facet, 1 mm below the base)
    zs_ = base[:, 2].min() - 1.0
    sec = crn.section(plane_origin=[0, 0, zs_], plane_normal=[0, 0, 1]).vertices
    fx = base[:, 0].mean()
    near = sec[np.abs(sec[:, 0] - fx) < 4.0]
    inner = []
    for xb in np.arange(near[:, 0].min(), near[:, 0].max(), 0.5):
        q = near[(near[:, 0] >= xb) & (near[:, 0] < xb + 0.5)]
        if len(q) and np.ptp(q[:, 1]) > 1.0: inner.append([xb + 0.25, q[:, 1].min()])     # inner (anterior) face of the lamina
    inner = np.array(inner); k_, c_ = np.polyfit(inner[:, 0], inner[:, 1], 1)
    n_ = np.array([-k_, 1.0, 0.0]); n_ /= np.linalg.norm(n_)                                   # points posteriorly
    hull = hull.slice_plane(np.array([fx, k_ * fx + c_ + E('PAD_IN', '0.5'), zs_]), n_, cap=True)
    hull.export(f'{B}/part_{pid:02d}.ply')
    print(f'facet pad {pid}: {hull.volume:.0f} mm3, clipped at the lamina inner face y = {k_:.2f} x + {c_:.1f}')

# ---------------- hyo-epiglottic ligament (band) ----------------
hyv = hy.vertices; ep = trimesh.load(f'{B}/part_10.ply', process=False).vertices
hb = hyv[np.abs(hyv[:, 0] - CX) < 5]
sel = hb[(hb[:, 2] > hb[:, 2].max() - 3.5) & (hb[:, 2] < hb[:, 2].max() - 1.5)]
A = sel[sel[:, 1] > np.percentile(sel[:, 1], 70)].mean(0)
em = ep[np.abs(ep[:, 0] - CX) < 4]; band = em[np.abs(em[:, 2] - (A[2] - E('HE_DROP', '2.0'))) < 1.5]
Bp = band[band[:, 1] < np.percentile(band[:, 1], 30)].mean(0)
u = (Bp - A); L = np.linalg.norm(u); u /= L
A0 = A - E('HE_IN_HY', '0.8') * u; B0_ = Bp + 1.5 * u
W, TH = E('HE_W', '9.0'), E('HE_T', '2.5')
poly = shapely.geometry.box(-(W / 2 - TH / 2), 0, (W / 2 - TH / 2), 0).buffer(TH / 2)
band_m = trimesh.creation.extrude_polygon(poly, np.linalg.norm(B0_ - A0))
ez = u; ex = np.array([1.0, 0, 0]); ey = np.cross(ez, ex); ey /= np.linalg.norm(ey); ex = np.cross(ey, ez)
R = np.eye(4); R[:3, 0], R[:3, 1], R[:3, 2] = ex, ey, ez; R[:3, 3] = A0
band_m.apply_transform(R)
epm = trimesh.load(f'{B}/part_10.ply', process=False); pts = []
for dz in np.arange(-4, 5, 1.0):
    sec = epm.section(plane_origin=[0, 0, Bp[2] + dz], plane_normal=[0, 0, 1])
    if sec is None: continue
    vv = sec.vertices; mm_ = vv[np.abs(vv[:, 0] - CX) < 1.0]
    if len(mm_): pts.append([mm_[:, 1].min(), Bp[2] + dz])
pts = np.array(pts); k_, c_ = np.polyfit(pts[:, 1], pts[:, 0], 1)
n_ = np.array([0.0, -1.0, k_]); n_ /= np.linalg.norm(n_)
band_m = band_m.slice_plane(np.array([CX, k_ * Bp[2] + c_ + E('HE_IN_EP', '0.4'), Bp[2]]), n_, cap=True)
band_m.export(f'{B}/part_22.ply')
print(f'hyo-epiglottic ligament: hyoid {np.round(A - [0,0,BASE0],1)} -> epiglottis {np.round(Bp - [0,0,BASE0],1)}, length {L:.1f} mm')

# ---------------- posterior cricoarytenoid ligaments ----------------
for pid, M, lat, Fc in ((35, MR, -1, FR), (36, ML, 1, FL)):
    a = apply(M, src(4 if pid == 35 else 5).vertices)
    base = a[a[:, 2] < a[:, 2].min() + 2.5]
    pa = base[np.argmax(base[:, 1] - 0.5 * lat * (base[:, 0] - CX))]
    target = Fc + np.array([-lat * 2.0, 2.5, 0.5])
    _, _, cp = igl.point_mesh_squared_distance(np.ascontiguousarray(target[None, :]), crnV, crnF); pc = np.asarray(cp).reshape(3)
    seg = pc - pa; Ls = np.linalg.norm(seg)
    cap = trimesh.creation.capsule(height=Ls + 1.0, radius=E('PCL_R', '0.8'))
    zax = seg / Ls; xax = np.cross([0, 1, 0], zax); xax /= np.linalg.norm(xax); yax = np.cross(zax, xax)
    Rm = np.eye(4); Rm[:3, 0], Rm[:3, 1], Rm[:3, 2] = xax, yax, zax; Rm[:3, 3] = (pa + pc) / 2
    cap.apply_transform(Rm); cap.export(f'{B}/part_{pid:02d}.ply')

# ---------------- grid ----------------
z_cut = crn.bounds[0, 2] - 22.0
Tm = trimesh.load(f'{B}/part_11.ply', process=False); Tm = Tm.slice_plane([0, 0, z_cut - 4], [0, 0, 1], cap=True); Tm.export(f'{B}/part_11.ply')
ids = [p[0] for p in PARTS if p[2] and os.path.exists(f'{B}/part_{p[0]:02d}.ply')]      # v6: source parts only, so the grid never depends on what has been built before
allb = [trimesh.load(f'{B}/part_{i:02d}.ply', process=False).bounds for i in ids]
lo_g = np.min([b[0] for b in allb], 0) - 2.0; hi_g = np.max([b[1] for b in allb], 0) + 2.0
lo_g[2] = z_cut - 4; lo_g = np.floor(lo_g / P) * P
shape_g = tuple(int(np.ceil((h - l) / P)) + 1 for l, h in zip(lo_g, hi_g))
np.save(f'{B}/grid.npy', np.array([*lo_g, P, *shape_g, z_cut]))
print('z_cut %.2f; grid %s' % (z_cut, shape_g))
