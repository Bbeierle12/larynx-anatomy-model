"""Stage 3c (part 2): the hypopharynx behind the larynx.
oesoph:  the upper oesophagus (82) as a collapsed muscular tube behind the trachea, from the base cut up to the cricoid's
         lower border, with a slit lumen that opens upward into the postcricoid lumen.
pharynx: the hypopharyngeal mucosa (83): a MUC_T lining on every bare surface facing the pharyngeal lumen behind the larynx
         (postcricoid surface, inner face of the constrictors, backs of the arytenoids), found by a bounded flood fill of the air.
Runs after the constrictors (80/81) are voxelised and after tissues8/9.  Sections: oesoph pharynx."""
import sys, os, numpy as np, trimesh, edt
from scipy import ndimage
sys.path.insert(0, os.path.dirname(__file__))
from musclelib import *
from partsconfig import PARTS
B = os.environ['BUILD']; E = lambda k, d: float(os.environ.get(k, d))
grid = Grid(f'{B}/grid.npy'); Z0 = grid.z_cut; CX = -0.65; P = grid.P
G_ = np.load(f'{B}/grid.npy'); LO = G_[:3]; NG = G_[4:7].astype(int)
L = lambda i: trimesh.load(f'{B}/part_{i:02d}.ply', process=False)
which = sys.argv[1:] or ['oesoph', 'pharynx']
def occ_to_phi(occ):
    return np.where(occ, -edt.edt(occ, anisotropy=(P,)*3, black_border=True), edt.edt(~occ, anisotropy=(P,)*3, black_border=False)).astype(np.float32)
def box_points(a, b):
    return [LO[i] + P * np.arange(a[i], b[i]) for i in range(3)]
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

if 'oesoph' in which:
    tr = L(11); cr = L(3); tv = tr.vertices
    y_back = np.percentile(tv[(tv[:, 2] < Z0 + 15) & (np.abs(tv[:, 0] - CX) < 6)][:, 1], 99)       # back of the trachea at the base
    W, D = E('OES_W', '20.0'), E('OES_D', '9.0'); LW, LD = E('OES_LW', '12.0'), E('OES_LD', '1.4')
    cy = y_back + D / 2 + E('OES_GAP', '-0.5'); ztop = cr.bounds[0, 2] + E('OES_OVER', '3.0')
    lo_mm = np.array([CX - W / 2 - 1, cy - D / 2 - 1, Z0 - 1]); hi_mm = np.array([CX + W / 2 + 1, cy + D / 2 + 1, ztop + 1])
    a, b = grid.box(lo_mm, hi_mm, margin=0.3); xs, ys, zs = box_points(a, b)
    X, Y, Zg = np.meshgrid(xs, ys, zs, indexing='ij')
    outer = ((X - CX) / (W / 2)) ** 2 + ((Y - cy) / (D / 2)) ** 2 <= 1.0
    lumen = ((X - CX) / (LW / 2)) ** 2 + ((Y - cy) / (LD / 2)) ** 2 <= 1.0
    occ = outer & ~lumen & (Zg >= Z0 - 0.5) & (Zg <= ztop)
    write(82, occ, a, b, 'Oesophagus (upper end)', smooth=0.3)
    print(f'     oesophagus {W} x {D} mm behind the trachea (centre y {cy:.1f}), lumen slit {LW} x {LD}, z 0..{ztop-Z0:.1f}')

if 'pharynx' in which:
    # the hypopharynx is collapsed in the source: the constrictors lie directly on the back of the larynx.  The mucosa is modelled as the
    # MUC_T interface band between the constrictors' inner surface and the laryngeal structures they touch (carved out of the constrictors),
    # plus any air gap under 2*MUC_T between them.  Where the constrictor does not touch anything (the open inlet above, the oesophagus below) nothing is added.
    T = E('MUC_T', '0.8'); k0 = int(np.floor((Z0 - LO[2]) / P))
    # work inside the constrictors' box (plus 2 mm) to keep memory down
    boxes = [load_occ(pid)[1:] for pid in (80, 81)]
    A0 = np.maximum(np.min([bb[0] for bb in boxes], 0) - int(2 / P), 0); B0 = np.minimum(np.max([bb[1] for bb in boxes], 0) + int(2 / P), NG)
    sh = tuple(B0 - A0)
    def crop(full): return full[A0[0]:B0[0], A0[1]:B0[1], A0[2]:B0[2]]
    con = np.zeros(sh, bool)
    for pid in (80, 81):
        o, a, b = load_occ(pid); con[a[0]-A0[0]:b[0]-A0[0], a[1]-A0[1]:b[1]-A0[1], a[2]-A0[2]:b[2]-A0[2]] |= o
    # only the structures that face the pharyngeal lumen count: not the laminae, membranes, hyoid, cricothyroid muscles, lateral walls, fossa linings or the oesophagus
    PH_FACING = (3, 4, 5, 6, 7, 8, 9, 10, 28, 29, 30, 31, 32, 38, 39, 40, 41, 42, 43, 56, 57, 58, 59, 61, 64, 65)
    larf = np.zeros(tuple(NG), bool)
    for pid in PH_FACING:
        f = f'{B}/occ_{pid:02d}.npz'
        if not os.path.exists(f): continue
        o, a, b = load_occ(pid); larf[a[0]:b[0], a[1]:b[1], a[2]:b[2]] |= o
    for pid in (11, 82):                                                             # at the inlet the lining continues over the back of the cricotracheal junction onto the oesophagus's upper rim
        f = f'{B}/occ_{pid:02d}.npz'
        if not os.path.exists(f): continue
        o, a, b = load_occ(pid); zz = LO[2] + P * np.arange(a[2], b[2]); keep = (zz >= Z0 + E('PH_INLET_Z', '24.0'))
        larf[a[0]:b[0], a[1]:b[1], a[2]:b[2]] |= o & keep[None, None, :]
    lar = crop(larf).copy(); del larf
    anyf = all_occ(skip=(80, 81, 83)); anyf[:, :, :k0] = True; anyp = crop(anyf).copy(); del anyf
    Dc = edt.edt(~con, anisotropy=(P, P, P), black_border=False); Dl = edt.edt(~lar, anisotropy=(P, P, P), black_border=False)
    REACH = E('PH_REACH', '2.5')                                                       # the laryngeal surface is lined wherever the constrictor lies within this distance of it
    band = (Dc <= REACH) & (Dl <= T + 0.05) & ~anyp & ~con                            # a T layer on the larynx's posterior surface, in the air between it and the constrictor
    inner = con & ~anyp & (Dl <= T + 0.05)                                            # the constrictor's own inner layer where it touches the larynx (outside the larynx only: the warp lets the constrictor sink ~0.5 mm into it)
    lining = band | inner
    lab2, n2 = ndimage.label(lining)
    if n2 > 1:
        sizes = np.bincount(lab2.ravel()); sizes[0] = 0; keep = sizes >= 20 / P ** 3; keep[0] = False; lining = keep[lab2]
    print(f'     hypopharyngeal mucosa: {lining.sum()*P**3:.0f} mm3 interface band ({band.sum()*P**3:.0f} in gaps, {inner.sum()*P**3:.0f} from the constrictors)')
    for pid in (80, 81):                                                               # carve the band out of the constrictors
        o, a, b = load_occ(pid); sub = lining[a[0]-A0[0]:b[0]-A0[0], a[1]-A0[1]:b[1]-A0[1], a[2]-A0[2]:b[2]-A0[2]]
        o2 = o & ~sub
        labc, nc = ndimage.label(o2)                                                   # islands cut off by the carve (internal slivers) go to the mucosa
        if nc > 1:
            sizes = np.bincount(labc.ravel()); main = np.argmax(sizes[1:]) + 1; isl = o2 & (labc != main)
            print(f'     constrictor {pid}: {nc-1} island(s) {isl.sum()*P**3:.0f} mm3 moved to the mucosa')
            o2 &= ~isl; lining[a[0]-A0[0]:b[0]-A0[0], a[1]-A0[1]:b[1]-A0[1], a[2]-A0[2]:b[2]-A0[2]] |= isl
        del labc
        phi = ndimage.gaussian_filter(occ_to_phi(o2), 0.15 / P, mode='nearest')
        nm = [q[1] for q in PARTS if q[0] == pid][0]
        write_part(grid, B, pid, phi, a, b, nm + ' (mucosa carved)')
    idx = np.argwhere(lining); a = np.maximum(idx.min(0) - 3, 0) ; b = np.minimum(idx.max(0) + 4, np.array(sh))
    write(83, lining[a[0]:b[0], a[1]:b[1], a[2]:b[2]], a + A0, b + A0, 'Hypopharyngeal mucosa', smooth=0.2)
