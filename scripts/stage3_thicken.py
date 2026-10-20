"""Stage 3: enforce a printable minimum thickness (1.2 mm). Thin features grow outward by (0.6 mm - local half
thickness); where the other face is the enclosed airway the growth is one-sided so the airway is never narrowed."""
import sys, time, numpy as np, edt
from scipy import ndimage
sys.path.insert(0, '/tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad/scripts')
from partsconfig import PARTS
B = '/tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad/build'
g = np.load(f'{B}/grid.npy'); lo = g[:3]; P = g[3]; z_cut = g[7]
MIN_T = 1.2; R = MIN_T / 2; A = (P, P, P)
L0 = np.load(f'{B}/labels_raw.npy')
kcut = int(round((z_cut - lo[2]) / P))

# remove specks
U = L0 > 0
lab, n = ndimage.label(U, structure=np.ones((3, 3, 3)))
sizes = ndimage.sum(U, lab, range(1, n + 1))
for i in np.nonzero(sizes * P**3 < 1.0)[0]:
    L0[lab == i + 1] = 0
del lab
U = L0 > 0

# protected airway (enclosed lumen tracked from the trachea upward, small gaps sealed)
SEAL = 3; disk = ndimage.generate_binary_structure(2, 1)
prot = np.zeros(U.shape, bool); prev = None
for k in range(kcut, U.shape[2]):
    s = U[:, :, k]
    sd = ndimage.binary_dilation(s, structure=disk, iterations=SEAL)
    hole = ndimage.binary_fill_holes(sd) & ~sd
    hole = ndimage.binary_dilation(hole, structure=disk, iterations=SEAL) & ~s
    hl, hn = ndimage.label(hole)
    if hn == 0: break
    if prev is None: pick = int(np.argmax(ndimage.sum(hole, hl, range(1, hn + 1)))) + 1
    else:
        ov = np.bincount(hl[prev], minlength=hn + 1); ov[0] = 0
        if ov.max() == 0: break
        pick = int(np.argmax(ov))
    prot[:, :, k] = hl == pick; prev = prot[:, :, k]
print('protected airway z=%.1f..%.1f (%.0f mm3)' % (z_cut, lo[2] + k * P, prot.sum() * P**3))

def thin_of(U):
    d_in = edt.edt(U, anisotropy=A, black_border=True, parallel=2)
    core = d_in > R
    thin = U & ~(edt.edt(~core, anisotropy=A, black_border=False, parallel=2) <= R + 1e-6)
    thin[:, :, :kcut + 3] = False
    return thin, d_in

dprot = edt.edt(~prot, anisotropy=A, black_border=False, parallel=2)
edges = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.2]
thin0 = None
for pas in range(2):
    t = time.time()
    thin, d_in = thin_of(U)
    if thin0 is None:
        thin0 = thin.copy()
        zone = edt.edt(~thin0, anisotropy=A, black_border=False, parallel=2) <= 0.8   # later passes only touch original thin features
    else:
        thin &= zone
    h = ndimage.maximum_filter(d_in.astype(np.float32), size=9)
    surf = thin & (d_in <= 1.5 * P)
    del d_in
    gp = np.where(surf, np.clip(R - h, 0, R), 0).astype(np.float32); del h
    near = surf & (dprot <= MIN_T); gp[near] = np.minimum(2 * gp[near], MIN_T)
    add = np.zeros(U.shape, bool)
    for a, b in zip(edges[:-1], edges[1:]):
        seeds = surf & (gp > a) & (gp <= b)
        if seeds.any():
            add |= edt.edt(~seeds, anisotropy=A, black_border=False, parallel=2) <= b
    add &= ~U & ~prot; add[:, :, :kcut] = False
    U |= add
    print(f'pass {pas}: thin {thin.sum()*P**3:7.1f} mm3, added {add.sum()*P**3:6.1f} mm3 ({time.time()-t:.0f}s)')
    if add.sum() * P**3 < 5: break
thinF, _ = thin_of(U)

# labels: original voxels keep their label; added voxels take the nearest original label (chunked EDT)
L = L0.copy()
need = U & (L0 == 0)
CH, OV = 120, 16
for z0 in range(0, U.shape[2], CH):
    a, b = max(0, z0 - OV), min(U.shape[2], z0 + CH + OV)
    sub = L0[:, :, a:b]
    if not need[:, :, z0:min(U.shape[2], z0 + CH)].any(): continue
    _, ind = ndimage.distance_transform_edt(sub == 0, return_indices=True)
    near = sub[ind[0], ind[1], ind[2]]
    sl = slice(z0 - a, z0 - a + min(CH, U.shape[2] - z0))
    blk = L[:, :, z0:z0 + CH]; nb = need[:, :, z0:z0 + CH]
    blk[nb] = near[:, :, sl][nb]
    del ind, near
names = {p[0]: p[1] for p in PARTS}
tot0 = np.bincount(L0[L0 > 0], minlength=40); tot = np.bincount(L[L > 0], minlength=40)
th0 = np.bincount(L0[thin0], minlength=40); th = np.bincount(L[thinF], minlength=40)
print('part                            volume before -> after     thin(<1.2mm) before -> after')
for pid in range(1, 33):
    print(f'  {names[pid]:30s} {tot0[pid]*P**3:7.1f} -> {tot[pid]*P**3:7.1f}      {th0[pid]*P**3:6.1f} -> {th[pid]*P**3:6.1f}')
np.save(f'{B}/labels_thick.npy', L)
np.save(f'{B}/airway_protect.npy', prot)
np.save(f'{B}/thin_after.npy', thinF)
