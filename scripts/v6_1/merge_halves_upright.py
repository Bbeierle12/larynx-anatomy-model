"""Both 2x halves of one version, standing upright (anatomical z up, base cut on the bed) side by side
on a bed of size BED (mm), as one 3MF. Usage: python merge_halves_upright.py halfR.3mf halfL.3mf out.3mf BED"""
import re, sys, zipfile, uuid
import numpy as np

fr, fl, out, BED = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
GAP = 12.0

def load(path):
    z = zipfile.ZipFile(path)
    return (z, z.read('3D/3dmodel.model').decode(), z.read('3D/Objects/object_1.model'), z.read('Metadata/model_settings.config').decode())

def verts(obj):
    return np.array(re.findall(rb'x="([-\d.]+)" y="([-\d.]+)" z="([-\d.]+)"', obj), dtype=float)

def hyoid_axis(obj, ms):
    """The anatomical 'up' in this half's frame: the hyoid lies at the top of the model, the trachea at the bottom,
    so up = direction from the trachea rings' centroid to the hyoid's centroid, snapped to an axis."""
    names = dict(re.findall(r'<part id="(\d+)" subtype="normal_part">\s*<metadata key="name" value="([^"]*)"', ms))
    inv = {v: k for k, v in names.items()}
    def part_v(name):
        pid = inv[name].encode()
        m = re.search(rb'<object id="%s"[^>]*>(.*?)</object>' % pid, obj, re.S)
        return verts(m.group(1))
    d = part_v('Hyoid bone').mean(0) - part_v('Trachea - cartilage rings').mean(0)
    ax = int(np.argmax(np.abs(d))); sgn = int(np.sign(d[ax]))
    assert ax != 2, 'expected the cut face on z'
    return ax, sgn

def rot_up(ax, sgn):
    """Rotation matrix (column-vector convention) taking the unit vector sgn*e_ax to +z, keeping z -> the other in-plane axis."""
    up = np.zeros(3); up[ax] = sgn
    # choose: new z = up; new y = old z (the cut face normal); new x = y cross z
    z = up; y = np.array([0, 0, 1.0]); x = np.cross(y, z)
    R = np.vstack([x, y, z])           # rows: new axes in old coords -> p_new = R @ p_old
    assert abs(np.linalg.det(R) - 1) < 1e-9
    return R

zr, topr, objr, msr = load(fr)
zl, topl, objl, msl = load(fl)
OFF = 1000
objl2 = re.sub(rb'<object id="(\d+)"', lambda m: b'<object id="%d"' % (int(m.group(1)) + OFF), objl)
msl2 = re.sub(r'<part id="(\d+)"', lambda m: '<part id="%d"' % (int(m.group(1)) + OFF), msl)
compl = re.findall(r'<component [^>]*/>', topl)
compl2 = [re.sub(r'objectid="(\d+)"', lambda m: 'objectid="%d"' % (int(m.group(1)) + OFF), c) for c in compl]
compl2 = [re.sub(r'p:UUID="[^"]*"', lambda m: 'p:UUID="%s"' % uuid.uuid4(), c) for c in compl2]

placements = []
for tag, obj, ms in (('R', objr, msr), ('L', objl, msl)):
    ax, sgn = hyoid_axis(obj, ms)
    R = rot_up(ax, sgn)
    v = verts(obj) @ R.T                       # rotated vertices
    lo, hi = v.min(0), v.max(0)
    ext = hi - lo
    placements.append((tag, R, lo, hi, ext))
    print(f'{tag}: up = {"xyz"[ax]}{"+" if sgn > 0 else "-"}, upright extents {np.round(ext, 1)} (x y z)')
total_x = sum(p[4][0] for p in placements) + GAP
assert total_x < BED - 20 and max(p[4][1] for p in placements) < BED - 20
x0 = (BED - total_x) / 2
tfs = []
for tag, R, lo, hi, ext in placements:
    cx = x0 + ext[0] / 2; x0 += ext[0] + GAP
    cy = BED / 2
    t = np.array([cx, cy, 0.0]) - (lo + hi) / 2 + np.array([0, 0, (hi[2] - lo[2]) / 2])   # lo/hi are already rotated: centre in x,y; bottom on z=0
    # 3MF transform: row-vector convention p' = p*M + t, so M = R^T written row-major
    M = R.T
    tfs.append('%s %.6f %.6f %.6f' % (' '.join('%.6f' % x for x in M.flatten()), t[0], t[1], t[2]))
    print(f'   {tag} at x {cx:.1f}, y {cy:.1f}, bottom on the bed; top at z {ext[2]:.1f}')
tr, tl = tfs

res_l = ('  <object id="1001" p:UUID="%s" type="model">\n   <components>\n' % uuid.uuid4() + '\n'.join('    ' + c for c in compl2) + '\n   </components>\n  </object>\n')
top = topr.replace(' </resources>', res_l + ' </resources>')
top = re.sub(r'<item objectid="1000" [^>]*/>',
             '<item objectid="1000" p:UUID="%s" transform="%s" printable="1"/>\n  <item objectid="1001" p:UUID="%s" transform="%s" printable="1"/>' % (uuid.uuid4(), tr, uuid.uuid4(), tl), top)
top = top.replace('v6.2<', 'v6.2, both 2x halves upright on one P1S plate<')
objm = objr.replace(b' </resources>', objl2[objl2.index(b'<object id='):objl2.rindex(b'</object>') + 9] + b'\n </resources>')
obj_r = re.search(r'  <object id="1000".*?  </object>\n', msr, re.S).group(0)
obj_l = re.search(r'  <object id="1000".*?  </object>\n', msl2, re.S).group(0).replace('<object id="1000"', '<object id="1001"', 1)
ms = msr.replace(obj_r, obj_r + obj_l)
ms = ms.replace('      <metadata key="identify_id" value="300"/>\n    </model_instance>',
                '      <metadata key="identify_id" value="300"/>\n    </model_instance>\n    <model_instance>\n'
                '      <metadata key="object_id" value="1001"/>\n      <metadata key="instance_id" value="0"/>\n'
                '      <metadata key="identify_id" value="301"/>\n    </model_instance>', 1)
assert ms.count('<model_instance>') == 2 and ms.count('<object id="100') == 2
zout = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED)
for info in zr.infolist():
    data = zr.read(info.filename)
    if info.filename == '3D/3dmodel.model': data = top.encode()
    elif info.filename == '3D/Objects/object_1.model': data = objm
    elif info.filename == 'Metadata/model_settings.config': data = ms.encode()
    zout.writestr(info, data)
zout.close()
print('wrote', out)
