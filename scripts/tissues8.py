"""Stage 3b: tongue base + vallecula (67), pre-epiglottic fat (68), paraglottic fat (69/70) from the enclosed voids,
laryngeal saccules carved from the fold tissues, anterior commissure tendon (71), joint capsules (72-75).
Runs after tissues7.py in BUILD.  Sections: tongue fat saccule tendon capsule."""
import sys, os, numpy as np, trimesh, igl, edt
from scipy import ndimage
sys.path.insert(0, os.path.dirname(__file__))
from musclelib import *
from partsconfig import PARTS
B = os.environ['BUILD']; E = lambda k, d: float(os.environ.get(k, d))
grid = Grid(f'{B}/grid.npy'); Z0 = grid.z_cut; CX = -0.65; P = grid.P
G_ = np.load(f'{B}/grid.npy'); LO = G_[:3]; NG = G_[4:7].astype(int)
L = lambda i: trimesh.load(f'{B}/part_{i:02d}.ply', process=False)
which = sys.argv[1:] or ['tongue', 'fat', 'saccule', 'vline', 'tendon', 'capsule']
hy, thy, cr, epi = L(1), L(2), L(3), L(10)
ARY = {-1: L(4), 1: L(5)}; VL = {-1: L(12), 1: L(13)}; HE = L(22)
def occ_to_phi(occ):
    return np.where(occ, -edt.edt(occ, anisotropy=(P,)*3, black_border=True), edt.edt(~occ, anisotropy=(P,)*3, black_border=False)).astype(np.float32)
def box_points(a, b):
    return [LO[i] + P * np.arange(a[i], b[i]) for i in range(3)]
def side_lookup(mesh, axis, sign, binw=0.3):
    """per bin of the other two coords: most extreme sign*coord of the mesh surface (NaN where none)"""
    v, _ = trimesh.sample.sample_surface(mesh, 600000, seed=0); v = np.vstack([v, mesh.vertices])
    o = [i for i in range(3) if i != axis]; lo0 = v[:, o].min(0) - 1; n = ((v[:, o].max(0) - lo0) / binw).astype(int) + 3
    X = np.full(tuple(n), -np.inf); ij = ((v[:, o] - lo0) / binw).astype(int); np.maximum.at(X, (ij[:, 0], ij[:, 1]), sign * v[:, axis])
    has = np.isfinite(X)
    for _ in range(2):
        Xf = ndimage.maximum_filter(np.where(has, X, -np.inf), size=3); X = np.where(has, X, Xf); has = np.isfinite(X)
    def f(pts):
        jj = ((pts[:, o] - lo0) / binw).astype(int); ok = (jj[:, 0] >= 0) & (jj[:, 0] < n[0]) & (jj[:, 1] >= 0) & (jj[:, 1] < n[1])
        out = np.full(len(pts), np.nan); out[ok] = X[jj[ok, 0], jj[ok, 1]]; out[~np.isfinite(out)] = np.nan; return out
    return f
def write(pid, occ, a, b, name, smooth=0.25):
    phi = occ_to_phi(occ)
    if smooth > 0: phi = ndimage.gaussian_filter(phi, smooth / P, mode='nearest')
    return write_part(grid, B, pid, phi, a, b, name)
def load_occ(pid):
    d = np.load(f'{B}/occ_{pid:02d}.npz'); return d['occ'], d['a'], d['b']
def all_occ(skip=()):
    occ = np.zeros(tuple(NG), bool)
    for pid, *_ in PARTS:
        f = f'{B}/occ_{pid:02d}.npz'
        if pid in skip or not os.path.exists(f): continue
        o, a, b = load_occ(pid); occ[a[0]:b[0], a[1]:b[1], a[2]:b[2]] |= o
    return occ
def medial_edge(lat, mesh):
    v = mesh.vertices; ys = np.arange(v[:, 1].min(), v[:, 1].max() + 0.01, 0.5); xe, ze = [], []
    for y in ys:
        s = v[np.abs(v[:, 1] - y) < 0.6]
        if len(s) == 0: xe.append(np.nan); ze.append(np.nan); continue
        k = np.argmax(-lat * s[:, 0]); xe.append(s[k, 0]); ze.append(s[:, 2].mean())
    xe = np.array(xe); ze = np.array(ze); ok = np.isfinite(xe)
    return lambda y: np.interp(y, ys[ok], xe[ok]), lambda y: np.interp(y, ys[ok], ze[ok]), ys[ok].min(), ys[ok].max()

# ---------------------------------------------------------------- tongue base and vallecula (67)
if 'tongue' in which:
    ep_front = side_lookup(epi, 1, -1, binw=0.3)                    # returns -y of the lingual (anterior) face per (x, z)
    hv = hy.vertices; hb = hv[np.abs(hv[:, 0] - CX) < 6]
    z_hy_top = hb[:, 2].max(); y_hy_front = hb[:, 1].min(); y_hy_back = hb[:, 1].max()
    z_floor = HE.vertices[:, 2].max() - E('VAL_FLOOR_DROP', '0.3')      # vallecula floor: on the hyo-epiglottic ligament
    z_top = min(epi.vertices[:, 2].max() + E('TONGUE_ABOVE_TIP', '1.0'), LO[2] + (NG[2] - 4) * P)     # flat cut level with the epiglottis tip (grid top)
    HW = E('TONGUE_HW', '15.0'); VW = E('VAL_W', '6.0'); VD = E('VAL_DEPTH', '12.0'); SEPT = E('MED_FOLD_HW', '0.8'); LAT_X = E('LAT_FOLD_X', '9.5')
    lo_mm = np.array([CX - HW, y_hy_front - E('TONGUE_FRONT', '4.0'), min(z_hy_top, z_floor) - 3.5]); hi_mm = np.array([CX + HW, epi.vertices[:, 1].max() + 1, z_top])
    a, b = grid.box(lo_mm, hi_mm, margin=0.3); xs, ys, zs = box_points(a, b)
    G = np.stack(np.meshgrid(xs, ys, zs, indexing='ij'), -1).reshape(-1, 3)
    yf = -ep_front(G)                                                  # anterior face y of the epiglottis at (x, z); NaN beyond its margins
    inside = (np.abs(G[:, 0] - CX) <= HW) & (G[:, 1] >= lo_mm[1]) & (G[:, 2] <= z_top)
    # bottom: on the hyoid in front of the hyoid's back face, on the ligament (vallecula floor) behind it
    bottom = np.where(G[:, 1] <= y_hy_back, z_hy_top - 3.0, z_floor - E('VAL_FLOOR_T', '2.5'))      # overlaps the hyoid and the ligament (they win); the floor is 2.5 mm thick beside the ligament
    inside &= G[:, 2] >= bottom
    # back face: the vallecula pocket in front of the epiglottis, VW wide, from the floor up VD; lateral folds where |x| > LAT_X; median fold septum
    dz = G[:, 2] - z_floor; pocket_w = np.where(dz < 0, 0.0, np.minimum(VW, VW * np.clip(dz / 2.0, 0, 1)))
    pocket_w = np.where(dz > VD, VW, pocket_w)
    lateral = np.abs(G[:, 0] - CX) > LAT_X; septum = np.abs(G[:, 0] - CX) < SEPT
    pocket_w = np.where(lateral | septum, 0.0, pocket_w)
    yback = np.where(np.isfinite(yf), yf - pocket_w, np.nan)
    def y_ant(z):                                                      # the piriform fossa's anterior wall (same table as tissues9)
        zz = np.array([47.0, 50.0, 54.0, 60.0, 66.0, 72.0, 80.0]); yy = np.array([-90.0, -93.0, -96.0, -98.0, -99.0, -100.0, -101.0]) + E('SIN_YOFF', '0.0')
        return np.interp(z, zz, yy)
    inside &= np.where(np.isfinite(yback), G[:, 1] <= yback, G[:, 1] <= y_ant(G[:, 2] - Z0))        # beyond the epiglottis margins: the pharyngo-epiglottic fold, back to the fossa's front wall
    occ = inside.reshape(len(xs), len(ys), len(zs))
    lab, n = ndimage.label(occ)
    if n > 1:
        sizes = np.bincount(lab.ravel()); sizes[0] = 0; occ = lab == sizes.argmax()
    write(67, occ, a, b, 'Tongue base and vallecula', smooth=0.3)
    print(f'     tongue base x ±{HW}, front y {lo_mm[1]:.1f}, floor z {z_floor-Z0:.1f} (hyoid top {z_hy_top-Z0:.1f}), top z {z_top-Z0:.1f}; vallecula {VW} mm wide, {VD} deep')

# ---------------------------------------------------------------- fat (68 pre-epiglottic, 69/70 paraglottic): the enclosed voids
if 'fat' in which:
    occ = all_occ(skip=(68, 69, 70))
    k0 = int(np.floor((Z0 - LO[2]) / P)); occ[:, :, :k0] = True                       # below the cut counts as solid
    for sp in (76, 77):                                                                 # the piriform fossa lumina (with their lining's width) count as walls
        f = f'{B}/sinus_{sp:02d}.npz'
        if os.path.exists(f):
            d = np.load(f); a_, b_ = d['a'], d['b']; Sd = d['Sd'] if 'Sd' in d.files else ndimage.binary_dilation(d['S'], iterations=int(round(E('MUC_T', '0.8') / P)))
            occ[a_[0]:b_[0], a_[1]:b_[1], a_[2]:b_[2]] |= Sd
    air = ~occ; D = edt.edt(air, anisotropy=(P, P, P), black_border=False)
    def enclosed_core(seed_mm):
        sv = tuple(((np.array(seed_mm) + [0, 0, Z0] - LO) / P).astype(int))
        if occ[sv]: print('     seed is solid', seed_mm); return None, None
        for r in np.arange(0.3, 1.55, 0.1):
            lab, n = ndimage.label(D >= r); s_ = lab[sv]
            if s_ == 0: del lab; return None, r
            c = lab == s_; del lab
            touches = c[0].any() or c[-1].any() or c[:, 0].any() or c[:, -1].any() or c[:, :, -1].any() or c[:, :, k0].any()
            if not touches: return c, r
            del c
        return None, None
    mir = lambda x: -x + 2 * CX
    pR = (E('FAT_PARA_X', '-9'), E('FAT_PARA_Y', '-102'), E('FAT_PARA_Z', '41'))               # lower paraglottic space (lateral of the conus, under the fold)
    vR = (E('FAT_PV_X', '-10.5'), E('FAT_PV_Y', '-101'), E('FAT_PV_Z', '51'))                  # paraglottic space at ventricle level (lateral of the ventricle lining, medial of the lamina)
    seeds = {'pre': [(CX, E('FAT_PRE_Y', '-112'), E('FAT_PRE_Z', '62'))], 'R': [pR, vR], 'L': [(mir(pR[0]),) + pR[1:], (mir(vR[0]),) + vR[1:]]}
    cores = {}
    for k, sds in seeds.items():
        for sd in sds:
            c, r = enclosed_core(sd)
            if c is None: print(f'     fat {k} seed {np.round(sd, 1)}: no enclosed core (r {r})'); continue
            filled = ndimage.binary_dilation(c, iterations=int(round((r + 0.1) / P))) & air
            print(f'     fat {k} seed {np.round(sd, 1)}: enclosed at air width {2*r:.1f} mm; core {c.sum()*P**3:.0f} -> filled {filled.sum()*P**3:.0f} mm3')
            cores[k] = (cores[k] | filled) if k in cores else filled
    del D                                                                                # memory: the distance field is no longer needed
    # split a shared space: pre-epiglottic = above the thyroid angle and near the midline, paraglottic by side
    X, Y, Zg = np.meshgrid(LO[0] + P * np.arange(NG[0]), LO[1] + P * np.arange(NG[1]), LO[2] + P * np.arange(NG[2]), indexing='ij', sparse=True)
    allfat = np.zeros_like(occ)
    for k in cores: allfat |= cores[k]
    ep_front = epi.vertices[:, 1].min()
    is_pre = allfat & (Zg - Z0 > E('FAT_PRE_ZMIN', '52')) & (Y < ep_front + 14.0) & (np.abs(X - CX) < 12.0)
    pre = is_pre; para = {-1: allfat & ~is_pre & (X < CX), 1: allfat & ~is_pre & (X >= CX)}
    def save(pid, m, name):
        if not m.any(): print(f'     {pid} {name}: nothing'); return
        idx = np.argwhere(m); a = np.maximum(idx.min(0) - 3, 0); b = np.minimum(idx.max(0) + 4, NG); del idx
        sub = m[a[0]:b[0], a[1]:b[1], a[2]:b[2]].copy()
        lab, n = ndimage.label(sub)
        if n > 1:
            sizes = np.bincount(lab.ravel()); sizes[0] = 0; keep = sizes >= E('FAT_MIN', '30') / P ** 3; keep[0] = False; sub = keep[lab]
        del lab
        write(pid, sub, a, b, name, smooth=0.15)
    save(68, pre, 'Pre-epiglottic fat'); save(69, para[-1], 'Paraglottic fat R'); save(70, para[1], 'Paraglottic fat L')

# ---------------------------------------------------------------- saccules: a blind pouch from the front of each ventricle up between the false fold and the lamina
if 'saccule' in which:
    for lat in (-1, 1):
        cov = L(50 if lat < 0 else 51); xedge, zc_, yc0, yc1 = medial_edge(lat, cov)
        vl = VL[lat].vertices; zlig = vl[:, 2].mean(); y0 = vl[:, 1].min()
        OFF = E('FF_OFF', '2.4')
        yS = y0 + E('SAC_Y', '6.0'); x0 = xedge(yS) + lat * (OFF + E('SAC_X', '3.4'))      # lateral of the vestibular ligament / membrane line, where the lamina leaves room
        S0 = np.array([x0, yS, zlig + E('SAC_Z0', '3.2')]); S1 = S0 + np.array([lat * E('SAC_DX', '0.2'), E('SAC_DY', '0.5'), E('SAC_H', '8.0')])
        r0, r1 = E('SAC_R0', '1.6'), E('SAC_R1', '0.9')
        n_ = 24; pts = S0 + (S1 - S0) * np.linspace(0, 1, n_)[:, None]; rr = r0 + (r1 - r0) * np.linspace(0, 1, n_)
        lo_mm = pts.min(0) - r0 - 0.5; hi_mm = pts.max(0) + r0 + 0.5
        for pid in (52, 53, 62, 63, 68, 69, 70, 64, 65):                 # medial of the thyro-epiglottic muscle, which is not carved
            f = f'{B}/occ_{pid:02d}.npz'
            if not os.path.exists(f): continue
            o, a, b = load_occ(pid); xs, ys, zs = box_points(a, b)
            G = np.stack(np.meshgrid(xs, ys, zs, indexing='ij'), -1).reshape(-1, 3)
            d = np.full(len(G), np.inf)
            for q, r in zip(pts, rr): d = np.minimum(d, np.linalg.norm(G - q, axis=1) - r)
            cut = (d <= 0).reshape(o.shape)
            if cut.sum() == 0: continue
            o2 = o & ~cut
            if o2.sum() == o.sum(): continue
            phi = ndimage.gaussian_filter(occ_to_phi(o2), 0.15 / P, mode='nearest')
            nm = [p[1] for p in PARTS if p[0] == pid][0]
            write_part(grid, B, pid, phi, a, b, nm + ' (saccule carved)')
            print(f'     saccule {"R" if lat < 0 else "L"} carved {cut.sum()*P**3:.1f} mm3 out of part {pid}')
        print(f'     saccule {"R" if lat < 0 else "L"}: from {np.round(S0-[0,0,Z0],1)} up to {np.round(S1-[0,0,Z0],1)}, r {r0}->{r1}')

# ---------------------------------------------------------------- ventricle and saccule lining top-up (62/63): after the saccule is cut, the air of the ventricle's
# lateral recess and of the saccule faces bare fat (and, where the recess reaches the lamina, bare cartilage).  The saccule is a mucosal pouch, so the
# VL_T of fat next to that air becomes ventricle mucosa (converted, not added: the pouch keeps its lumen), and VL_T of mucosa is laid on the bare lamina.
if 'vline' in which:
    T = E('VL_T', '0.8'); k0 = int(np.floor((Z0 - LO[2]) / P))
    occ = all_occ(); occ[:, :, :k0] = True
    lo_mm = np.array([thy.bounds[0, 0], E('VL_YMIN', '-115'), Z0 + E('VL_Z0', '46.0')]); hi_mm = np.array([thy.bounds[1, 0], E('VL_YMAX', '-86'), Z0 + E('VL_Z1', '62')])
    a, b = grid.box(lo_mm, hi_mm, margin=0.3); sl = tuple(slice(a[i], b[i]) for i in range(3))
    air = ~occ[sl]; del occ
    for sp in (76, 77):                                                                 # the fossae are lined already
        f = f'{B}/sinus_{sp:02d}.npz'
        if os.path.exists(f):
            d = np.load(f); a_, b_ = d['a'], d['b']; Sd = d['Sd'] if 'Sd' in d.files else d['S']
            full = np.zeros(tuple(NG), bool); full[a_[0]:b_[0], a_[1]:b_[1], a_[2]:b_[2]] = Sd; air &= ~full[sl]; del full
    def sub(pid):
        o, a2, b2 = load_occ(pid); out = np.zeros(air.shape, bool)
        lo_ = np.maximum(a, a2); hi_ = np.minimum(b, b2)
        if np.all(hi_ > lo_): out[lo_[0]-a[0]:hi_[0]-a[0], lo_[1]-a[1]:hi_[1]-a[1], lo_[2]-a[2]:hi_[2]-a[2]] = o[lo_[0]-a2[0]:hi_[0]-a2[0], lo_[1]-a2[1]:hi_[1]-a2[1], lo_[2]-a2[2]:hi_[2]-a2[2]]
        return out
    lam = sub(2); fat = sub(68) | sub(69) | sub(70)
    lab, n = ndimage.label(air)
    for lat, pidw, pidf in ((-1, 62, 69), (1, 63, 70)):
        sv = tuple(((np.array([CX + lat * E('VL_SEED_X', '6.0'), E('VL_SEED_Y', '-104'), Z0 + E('VL_SEED_Z', '50')]) - LO) / P).astype(int) - a)
        if not air[sv]: print(f'     vline {pidw}: seed is not air'); continue
        comp = lab == lab[sv]                                                           # the airway, ventricle and saccule on this side (not the fossa, not the outside)
        comp &= (lat * (LO[0] + P * (a[0] + np.arange(air.shape[0])) - CX) > 0)[:, None, None]
        Dair = edt.edt(~comp, anisotropy=(P, P, P), black_border=False)
        conv = fat & (Dair <= T + 0.05)                                                  # fat facing the air -> mucosa
        Dlam = edt.edt(~lam, anisotropy=(P, P, P), black_border=False)
        onlam = comp & (Dlam <= T + 0.05)                                                # air against bare lamina -> mucosa (into the air)
        new = conv | onlam
        ow, aw, bw = load_occ(pidw)
        full = np.zeros(tuple(NG), bool); full[aw[0]:bw[0], aw[1]:bw[1], aw[2]:bw[2]] = ow; full[sl] |= new
        idx = np.argwhere(full); a3 = np.maximum(idx.min(0) - 3, 0); b3 = np.minimum(idx.max(0) + 4, NG); del idx
        nm = [q[1] for q in PARTS if q[0] == pidw][0]
        write(pidw, full[a3[0]:b3[0], a3[1]:b3[1], a3[2]:b3[2]], a3, b3, nm + ' (saccule and recess lined)', smooth=0.2); del full
        for pf in (68, 69, 70):                                                         # take the converted voxels out of the fat
            of, af, bf = load_occ(pf); ff = np.zeros(tuple(NG), bool); ff[af[0]:bf[0], af[1]:bf[1], af[2]:bf[2]] = of
            before = ff.sum(); ff[sl] &= ~conv
            if ff.sum() < before:
                nmf = [q[1] for q in PARTS if q[0] == pf][0]
                write(pf, ff[af[0]:bf[0], af[1]:bf[1], af[2]:bf[2]], af, bf, nmf, smooth=0.15)
            del ff
        print(f'     vline {pidw}: {conv.sum()*P**3:.0f} mm3 of fat converted to mucosa around the saccule and recess, {onlam.sum()*P**3:.0f} mm3 laid on the bare lamina')
        del Dair, Dlam, comp

# ---------------------------------------------------------------- anterior commissure tendon (71): the vocal ligaments' insertion into the thyroid angle
if 'tendon' in which:
    vR, vL = VL[-1].vertices, VL[1].vertices
    aR = vR[np.argmin(vR[:, 1])]; aL = vL[np.argmin(vL[:, 1])]; A = (aR + aL) / 2; A[0] = CX
    tv = thy.vertices; s_ = tv[(np.abs(tv[:, 0] - CX) < 1.0) & (np.abs(tv[:, 2] - A[2]) < 2.0)]
    y_in = s_[:, 1].max() if len(s_) else A[1] - 2.0                        # inner surface of the angle at the midline
    pts = np.array([[CX, y_in - E('ACT_IN', '1.5'), A[2]], [CX, y_in, A[2]], [CX, A[1] + E('ACT_BACK', '-0.2'), A[2]]])
    phi, a, b = build_body(grid, [(pts, E('ACT_R0', '0.5'), E('ACT_R1', '0.8'), 'const', 1.0)], k=0.2)
    write_part(grid, B, 71, phi, a, b, 'Anterior commissure tendon')
    print(f'     tendon from the thyroid angle (y {y_in:.1f}) back to the ligament ends at {np.round(A-[0,0,Z0],1)}')

# ---------------------------------------------------------------- joint capsules (72/73 cricoarytenoid, 74/75 cricothyroid): a thin sleeve over each joint
if 'capsule' in which:
    T = E('CAP_T', '0.8')
    def sleeve(pid, side_a, side_b, centre, R, name, reach=2.0):
        """capsule: a T-thick skin on either joint partner, only where the other partner is within `reach` (the joint line), inside radius R of the joint centre"""
        A = trimesh.util.concatenate(side_a); Bm = trimesh.util.concatenate(side_b); core = trimesh.util.concatenate([A, Bm])
        lo_mm = centre - R - T - 0.5; hi_mm = centre + R + T + 0.5
        a, b = grid.box(lo_mm, hi_mm, margin=0.3); xs, ys, zs = box_points(a, b)
        G = np.stack(np.meshgrid(xs, ys, zs, indexing='ij'), -1).reshape(-1, 3)
        def dist_to(m):
            d2, _, _ = igl.point_mesh_squared_distance(G, np.ascontiguousarray(m.vertices, np.float64), np.ascontiguousarray(m.faces, np.int64)); return np.sqrt(d2)
        da, db = dist_to(A), dist_to(Bm)
        inside = igl.fast_winding_number(np.ascontiguousarray(core.vertices, np.float64), np.ascontiguousarray(core.faces, np.int64), np.ascontiguousarray(G)) > 0.5
        occ = (((da <= T + 0.05) & (db <= reach)) | ((db <= T + 0.05) & (da <= reach))) & ~inside & (np.linalg.norm(G - centre, axis=1) <= R)
        occ = occ.reshape(len(xs), len(ys), len(zs))
        write(pid, occ, a, b, name, smooth=0.12)
    for lat, pid, fp in ((-1, 72, 38), (1, 73, 39)):
        pad = L(fp); c = pad.vertices.mean(0); c[2] = pad.vertices[:, 2].max() + E('CA_ZUP', '0.5')     # centred on the joint surface, not the pad
        sleeve(pid, [ARY[lat]], [pad, cr], c, E('CA_R', '4.5'), f'Cricoarytenoid joint capsule {"R" if lat < 0 else "L"}')
        print(f'     cricoarytenoid capsule {"R" if lat < 0 else "L"} about {np.round(c-[0,0,Z0],1)}')
    tv = thy.vertices
    for lat, pid in ((-1, 74), (1, 75)):
        s_ = tv[lat * (tv[:, 0] - CX) > 8.0]; tip = s_[np.argmin(s_[:, 2])]
        sleeve(pid, [thy], [cr], tip, E('CT_R', '4.0'), f'Cricothyroid joint capsule {"R" if lat < 0 else "L"}')
        print(f'     cricothyroid capsule {"R" if lat < 0 else "L"} about the horn tip {np.round(tip-[0,0,Z0],1)}')
