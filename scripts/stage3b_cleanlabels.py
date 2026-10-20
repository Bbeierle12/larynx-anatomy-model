"""Stage 3b: remove small label islands (reassign to surrounding part) so each anatomical part is one clean piece."""
import sys, numpy as np
from scipy import ndimage
sys.path.insert(0, '/tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad/scripts')
from partsconfig import PARTS
B = '/tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad/build'
g = np.load(f'{B}/grid.npy'); P = g[3]
L = np.load(f'{B}/labels_thick.npy')
U = L > 0
MIN_ISLAND = 0.8   # mm3
st = np.ones((3, 3, 3))
for rnd in range(3):
    S = np.zeros(L.shape, bool); nisl = 0
    for pid, name, *_ in PARTS:
        idx = np.argwhere(L == pid)
        if len(idx) == 0: continue
        a = np.maximum(idx.min(0) - 1, 0); b = idx.max(0) + 2
        sub = L[a[0]:b[0], a[1]:b[1], a[2]:b[2]] == pid
        lab, n = ndimage.label(sub, structure=st)
        if n <= 1: continue
        sizes = ndimage.sum(sub, lab, range(1, n + 1))
        keep = np.argmax(sizes) + 1
        small = (lab != keep) & (lab > 0) & (np.isin(lab, np.nonzero(sizes * P**3 < MIN_ISLAND)[0] + 1) | (lab != keep))
        # keep genuinely separate large pieces (e.g. a part legitimately in two pieces)
        big_other = np.isin(lab, np.nonzero(sizes * P**3 >= MIN_ISLAND)[0] + 1) & (lab != keep)
        small &= ~big_other
        if small.any():
            S[a[0]:b[0], a[1]:b[1], a[2]:b[2]] |= small; nisl += int(small.sum())
    if nisl == 0: break
    L[S] = 0
    # reassign island voxels to the nearest remaining label (chunked)
    CH, OV = 120, 16
    for z0 in range(0, L.shape[2], CH):
        if not S[:, :, z0:z0 + CH].any(): continue
        a_, b_ = max(0, z0 - OV), min(L.shape[2], z0 + CH + OV)
        sub = L[:, :, a_:b_]
        _, ind = ndimage.distance_transform_edt(sub == 0, return_indices=True)
        near = sub[ind[0], ind[1], ind[2]]
        sl = slice(z0 - a_, z0 - a_ + min(CH, L.shape[2] - z0))
        blk = L[:, :, z0:z0 + CH]; nb = S[:, :, z0:z0 + CH]
        blk[nb] = near[:, :, sl][nb]
        del ind, near
    print(f'round {rnd}: reassigned {nisl*P**3:.1f} mm3 of island voxels')
assert ((L > 0) == U).all()
np.save(f'{B}/labels_clean.npy', L)
