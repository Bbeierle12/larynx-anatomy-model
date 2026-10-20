"""Stage 3c: knock off sub-0.5 mm bumps created by the thickening (opening of the added material only)."""
import numpy as np, edt
B = '/tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad/build'
g = np.load(f'{B}/grid.npy'); P = g[3]; A = (P, P, P)
L = np.load(f'{B}/labels_clean.npy'); L0 = np.load(f'{B}/labels_raw.npy')
U = L > 0; U0 = L0 > 0
r = 0.25
core = edt.edt(U, anisotropy=A, black_border=True, parallel=2) > r
opened = edt.edt(~core, anisotropy=A, black_border=False, parallel=2) <= r + 1e-6
keep = U0 | (opened & U)
removed = U & ~keep
L[removed] = 0
print('removed %.1f mm3 of bumps; added material kept %.1f mm3' % (removed.sum() * P**3, ((L > 0) & ~U0).sum() * P**3))
np.save(f'{B}/labels_final.npy', L)
