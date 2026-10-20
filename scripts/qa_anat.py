import sys, numpy as np, trimesh, shapely
from scipy import ndimage
from shapely.geometry import Polygon, Point, box as sbox
from shapely.ops import unary_union
from trimesh.ray.ray_pyembree import RayMeshIntersector
import os
B = os.environ.get('BUILD', '/tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad/build')
u = trimesh.load(f'{B}/final_union.ply'); part = lambda i: trimesh.load(f'{B}/final_{i:02d}.ply')
zc = u.bounds[0, 2]
print('overall size (mm): %.1f wide x %.1f deep x %.1f tall' % tuple(u.extents))
def sec(m, z):
    s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if s is None: return None
    p, _ = s.to_2D(to_2D=np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, -z], [0, 0, 0, 1]]))
    return unary_union(list(p.polygons_full))
def lumen(z, cx, cy):
    U = sec(u, z)
    holes = [Polygon(h) for g in getattr(U, 'geoms', [U]) for h in g.interiors]
    hs = [h for h in holes if h.contains(Point(cx, cy))]
    if not hs: return None
    h = hs[0]; x0, y0, x1, y1 = h.bounds
    return dict(area=h.area, w=x1 - x0, d=y1 - y0, mic=2 * shapely.maximum_inscribed_circle(h).length)
H = part(1); Th = part(2); Cr = part(3); E = part(10); VL = part(12)
cx = -0.6
for z, n in [(zc + 6, 'trachea (6 mm above base)'), (zc + 15, 'trachea (15 mm above base)')]:
    r = lumen(z, cx, -100.5); print(f'{n}: lumen {r["w"]:.1f} wide x {r["d"]:.1f} deep, area {r["area"]:.0f} mm2, index {r["w"]/r["d"]:.2f}')
best = None
for z in np.arange(Cr.bounds[0, 2] + 2, Cr.bounds[0, 2] + 8, 0.5):
    r = lumen(z, cx, -101.5)
    if r and (best is None or r['area'] < best[1]['area']): best = (z, r)
print(f'cricoid ring (narrowest enclosed level, z+{best[0]-zc:.1f}): lumen {best[1]["w"]:.1f} wide x {best[1]["d"]:.1f} deep, area {best[1]["area"]:.0f} mm2')
# glottis: empty region between the folds at vocal-ligament level
zs = VL.vertices[:, 2]; zg0, zg1 = zs.min(), zs.max()
res = []
for z in np.arange(zg0, zg1 + 0.01, 0.25):
    U = sec(u, z); win = sbox(-12, -120, 11, -86)
    air = win.difference(U)
    comps = [g for g in getattr(air, 'geoms', [air]) if g.contains(Point(cx, -104))]
    if comps:
        g = comps[0]; x0, y0, x1, y1 = g.bounds
        res.append((z, g.area, x1 - x0, y1 - y0, 2 * shapely.maximum_inscribed_circle(g).length))
if res:
    r = min(res, key=lambda t: t[1])
    print(f'rima glottidis (narrowest level, z+{r[0]-zc:.1f}): area {r[1]:.0f} mm2, length {r[3]:.1f} mm, max width {r[2]:.1f} mm, largest inscribed circle {r[4]:.1f} mm')
vl = VL.vertices; ax = np.linalg.svd(vl - vl.mean(0))[2][0]; pr = (vl - vl.mean(0)) @ ax
print(f'vocal ligament (R) length {np.ptp(pr):.1f} mm')
hv = H.vertices; print(f'hyoid greater-horn tip span {np.ptp(hv[:, 0]):.1f} mm')
body = hv[np.abs(hv[:, 0] - cx) < 6]; hz = body[:, 2].mean()
print(f'hyoid body centre to lower border of cricoid {hz - Cr.bounds[0, 2]:.1f} mm')
tv = Th.vertices; print(f'thyroid cartilage: superior-horn span {np.ptp(tv[:, 0]):.1f} mm, height (horn tip to horn tip) {np.ptp(tv[:, 2]):.1f} mm')
angs = []
for z in np.linspace(Th.bounds[0, 2] + 8, Th.bounds[0, 2] + 18, 5):
    s = Th.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1]).vertices
    a = []
    for sd in (1, -1):
        q = s[(sd * (s[:, 0] - cx) > 3) & (sd * (s[:, 0] - cx) < 14)]
        pts = []
        for bx in np.arange(3, 14, 1.0):
            bb = q[(sd * (q[:, 0] - cx) >= bx) & (sd * (q[:, 0] - cx) < bx + 1)]
            if len(bb): pts.append(bb[np.argmin(bb[:, 1])])
        pts = np.array(pts); k = np.polyfit(sd * (pts[:, 0] - cx), pts[:, 1], 1)[0]; a.append(np.degrees(np.arctan(1 / k)))
    angs.append(sum(a))
print(f'thyroid angle (outer laminae, 5 levels): {np.median(angs):.0f} deg (range {min(angs):.0f}-{max(angs):.0f})')
ev = E.vertices; ax = np.linalg.svd(ev - ev.mean(0))[2][0]; print(f'epiglottis length (tip to petiole) {np.ptp((ev - ev.mean(0)) @ ax):.1f} mm')
# largest sphere from trachea base up through the glottis (voxel EDT inside a box around the airway)
P = 0.1; xs = np.arange(cx - 11, cx + 11, P); ys = np.arange(-116, -87, P); zz = np.arange(zc + 0.5, zg1 + 6, P)
X, Y = np.meshgrid(xs, ys, indexing='ij'); O = np.c_[X.ravel(), Y.ravel(), np.full(X.size, zc - 1)]
ri = RayMeshIntersector(u); loc, ir, it = ri.intersects_location(O, np.tile([0, 0, 1.0], (len(O), 1)), multiple_hits=True)
solid = np.zeros((len(xs), len(ys), len(zz)), bool)
order = np.lexsort((loc[:, 2], ir)); ir = ir[order]; hz_ = loc[order, 2]
st = np.r_[0, np.flatnonzero(np.diff(ir)) + 1]; en = np.r_[st[1:], len(ir)]
for s_, e_ in zip(st, en):
    i, j = np.unravel_index(ir[s_], X.shape); h = np.unique(np.round(hz_[s_:e_], 5))
    if len(h) % 2: h = h[:-1]
    for a_, b_ in zip(h[0::2], h[1::2]): solid[i, j, (zz >= a_) & (zz <= b_)] = True
air = ~solid; air[0] = air[-1] = False; air[:, 0] = air[:, -1] = False
edt = ndimage.distance_transform_edt(air) * P
lo_, hi_ = 0.0, 10.0
for _ in range(22):
    mid = (lo_ + hi_) / 2; lab, n = ndimage.label(edt >= mid)
    ok = len((set(np.unique(lab[:, :, 0])) - {0}) & (set(np.unique(lab[:, :, -1])) - {0})) > 0
    lo_, hi_ = (mid, hi_) if ok else (lo_, mid)
print(f'largest sphere that passes from the tracheal base up through the glottis: {2*lo_:.1f} mm')
# cricoid detail
zb_ = u.bounds[0, 2]
for x in [cx, cx - 3, cx + 3, cx - 6, cx + 6]:
    s = Cr.section(plane_origin=[x, 0, 0], plane_normal=[1, 0, 0]); v = s.vertices
    post = v[v[:, 1] > -98]; ant = v[v[:, 1] < -104]
    print(f'cricoid x={x-cx:+.0f}: lamina height {np.ptp(post[:,2]):.1f} (z {post[:,2].min()-zb_:.1f}-{post[:,2].max()-zb_:.1f})' + (f', arch height {np.ptp(ant[:,2]):.1f}' if len(ant) else ''))
Tv = Th.vertices; mid = Tv[np.abs(Tv[:, 0] - cx) < 1.5]; tl = mid[mid[:, 1] < -108][:, 2].min()
av = Cr.vertices; am = av[(np.abs(av[:, 0] - cx) < 1.5) & (av[:, 1] < -104)][:, 2].max()
print(f'cricothyroid gap at midline (vertical): {tl - am:.1f} mm')
# subglottic lumen across the cricoid ring (all enclosed levels)
best = []
for z in np.arange(Cr.bounds[0, 2] + 1, Cr.bounds[0, 2] + 10, 0.5):
    r = lumen(z, cx, -101.0)
    if r: best.append((z - zb_, r['w'], r['d'], r['area']))
if best:
    a = min(best, key=lambda t: t[3]); print(f'subglottis (cricoid ring) narrowest: z+{a[0]:.1f} {a[1]:.1f} W x {a[2]:.1f} D, area {a[3]:.0f}; median depth {np.median([b[2] for b in best]):.1f}, width {np.median([b[1] for b in best]):.1f}')
vl2 = trimesh.load(f'{B}/final_13.ply'); vv = vl2.vertices; ax2 = np.linalg.svd(vv - vv.mean(0))[2][0]; print(f'vocal ligament (L) length {np.ptp((vv - vv.mean(0)) @ ax2):.1f} mm')
