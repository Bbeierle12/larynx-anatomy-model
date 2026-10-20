"""Landmarks on the v3 (build5) framework needed to place the stage-2 muscles. z printed relative to the tracheal cut (1359.0)."""
import numpy as np, trimesh, igl, sys
B = '/tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad/build5'
Z0 = 1359.0; CX = -0.65
L = lambda i: trimesh.load(f'{B}/part_{i:02d}.ply', process=False)
thy, cri, aR, aL = L(2), L(3), L(4), L(5)
vlR, vlL, coR, coL, mcl = L(12), L(13), L(14), L(15), L(16)
taR, taL, tra, obR, obL, aeR, aeL, pdR, pdL = L(24), L(25), L(28), L(29), L(30), L(31), L(32), L(38), L(39)
def bb(m, name):
    lo, hi = m.bounds; print(f'{name:28s} x {lo[0]:6.1f}..{hi[0]:6.1f}  y {lo[1]:7.1f}..{hi[1]:7.1f}  z {lo[2]-Z0:5.1f}..{hi[2]-Z0:5.1f}  vol {m.volume:7.1f}')
for m, n in [(thy,'thyroid'),(cri,'cricoid'),(aR,'arytenoid R'),(aL,'arytenoid L'),(vlR,'vocal lig R'),(coR,'conus R'),(mcl,'median CT lig'),(taR,'TA R'),(tra,'transverse ary'),(obR,'oblique ary R'),(aeR,'aryepiglotticus R'),(pdR,'facet pad R')]: bb(m, n)
print('\n-- cricoid: posterior-face profile (max y) and lamina extent per z slice --')
cv = cri.vertices
for z in np.arange(23, 45, 2.0):
    s = cv[np.abs(cv[:, 2] - Z0 - z) < 0.5]
    if not len(s): continue
    back = s[s[:, 1] > s[:, 1].max() - 2.5]      # posterior face
    row = []
    for x in np.arange(-13, 13.1, 2.0):
        q = s[np.abs(s[:, 0] - x) < 1.0]
        row.append(f'{q[:,1].max():6.1f}' if len(q) else '   -- ')
    print(f'z {z:4.1f}: x-range {s[:,0].min():6.1f}..{s[:,0].max():6.1f}  ymax@x=-13..13: ' + ' '.join(row))
print('\n-- cricoid: upper border (max z) per angle sector (0 = +x, 270 = anterior) and outer radius --')
th = (np.degrees(np.arctan2(cv[:, 1] + 97.0, cv[:, 0] - CX)) + 360) % 360
for a in range(0, 360, 15):
    q = cv[np.abs(((th - a + 180) % 360) - 180) < 7.5]
    r = np.hypot(q[:, 0] - CX, q[:, 1] + 97.0)
    print(f'ang {a:3d}: zmax {q[:,2].max()-Z0:5.1f} zmin {q[:,2].min()-Z0:5.1f} r {r.min():5.1f}..{r.max():5.1f}')
print('\n-- arytenoids --')
for a, n, lat in ((aR, 'R', -1), (aL, 'L', 1)):
    v = a.vertices; base = v[v[:, 2] < v[:, 2].min() + 2.5]
    mp = v[np.argmax(lat * (v[:, 0] - CX) + 1.0 * (v[:, 1]) - 0.3 * (v[:, 2] - v[:, 2].min()))]
    vp = v[np.argmin(v[:, 1])]; apex = v[np.argmax(v[:, 2])]
    print(f'{n}: base z {v[:,2].min()-Z0:.1f}  apex {np.round(apex-[0,0,Z0],1)}  VP {np.round(vp-[0,0,Z0],1)}  MP(cand) {np.round(mp-[0,0,Z0],1)}  x-range {v[:,0].min():.1f}..{v[:,0].max():.1f}  y-range {v[:,1].min():.1f}..{v[:,1].max():.1f}')
    for z in np.arange(0, 17, 2.0):
        s = v[np.abs(v[:, 2] - v[:, 2].min() - z) < 0.5]
        if len(s): print(f'   +{z:4.1f}: x {s[:,0].min():6.1f}..{s[:,0].max():6.1f}  y {s[:,1].min():7.1f}..{s[:,1].max():7.1f}')
print('\n-- thyroid: inferior border (min z) per x; posterior border; inner surface at the angle --')
tv = thy.vertices
for x in np.arange(-18, 18.1, 2.0):
    q = tv[np.abs(tv[:, 0] - x) < 1.0]
    if not len(q): continue
    low = q[np.argmin(q[:, 2])]
    print(f'x {x:5.1f}: lowest z {low[2]-Z0:5.1f} at y {low[1]:7.1f};  y-range {q[:,1].min():7.1f}..{q[:,1].max():7.1f}; z-range {q[:,2].min()-Z0:5.1f}..{q[:,2].max()-Z0:5.1f}')
print('\n-- thyroid inner surface at the angle (min y face) per z: ymin at |x-CX|<1.5, and lamina inner-face y at x=+-6, +-10 --')
for z in np.arange(30, 56, 2.0):
    s = tv[np.abs(tv[:, 2] - Z0 - z) < 0.5]
    if not len(s): continue
    mid = s[np.abs(s[:, 0] - CX) < 1.5]
    out = f'z {z:4.1f}: angle y {mid[:,1].min():7.1f}..{mid[:,1].max():7.1f}' if len(mid) else f'z {z:4.1f}: angle --'
    for x in (-6, 6, -10, 10, -14, 14):
        q = s[np.abs(s[:, 0] - x) < 0.7]
        out += f' | x{x:+d}: y {q[:,1].min():6.1f}..{q[:,1].max():6.1f}' if len(q) else f' | x{x:+d}: --'
    print(out)
print('\n-- vocal ligament R: anterior and posterior ends; conus lateral extent per z --')
v = vlR.vertices; print('VL R ant', np.round(v[np.argmin(v[:,1])]-[0,0,Z0],1), 'post', np.round(v[np.argmax(v[:,1])]-[0,0,Z0],1))
v = vlL.vertices; print('VL L ant', np.round(v[np.argmin(v[:,1])]-[0,0,Z0],1), 'post', np.round(v[np.argmax(v[:,1])]-[0,0,Z0],1))
cvR = coR.vertices
for z in np.arange(26, 48, 2.0):
    s = cvR[np.abs(cvR[:, 2] - Z0 - z) < 0.5]
    if len(s): print(f'conus R z {z:4.1f}: x {s[:,0].min():6.1f}..{s[:,0].max():6.1f}  y {s[:,1].min():7.1f}..{s[:,1].max():7.1f}')
print('\n-- TA R per z (current strip) --')
v = taR.vertices
for z in np.arange(40, 72, 3.0):
    s = v[np.abs(v[:, 2] - Z0 - z) < 0.5]
    if len(s): print(f'TA R z {z:4.1f}: x {s[:,0].min():6.1f}..{s[:,0].max():6.1f}  y {s[:,1].min():7.1f}..{s[:,1].max():7.1f}')
