"""Merge two single-object Bambu 3MFs (half R, half L) into one 3MF with two objects, placed side by side
on a bed of size BED (mm). Usage: python merge_halves.py halfR.3mf halfL.3mf out.3mf BED"""
import re, sys, zipfile, uuid
import numpy as np

fr, fl, out, BED = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
GAP = 6.0  # mm between the two halves

def load(path):
    z = zipfile.ZipFile(path)
    return (z, z.read('3D/3dmodel.model').decode(), z.read('3D/Objects/object_1.model'),
            z.read('Metadata/model_settings.config').decode())

def bbox_xy(obj):
    v = np.array(re.findall(rb'x="([-\d.]+)" y="([-\d.]+)" z="([-\d.]+)"', obj), dtype=float)
    return v.min(0), v.max(0)

zr, topr, objr, msr = load(fr)
zl, topl, objl, msl = load(fl)
OFF = 1000  # id offset for the left half's parts

# --- left half: renumber part/object ids by OFF
objl2 = re.sub(rb'<object id="(\d+)"', lambda m: b'<object id="%d"' % (int(m.group(1)) + OFF), objl)
msl2 = re.sub(r'<part id="(\d+)"', lambda m: '<part id="%d"' % (int(m.group(1)) + OFF), msl)
compl = re.findall(r'<component [^>]*/>', topl)
compl2 = [re.sub(r'objectid="(\d+)"', lambda m: 'objectid="%d"' % (int(m.group(1)) + OFF), c) for c in compl]
compl2 = [re.sub(r'p:UUID="[^"]*"', lambda m: 'p:UUID="%s"' % uuid.uuid4(), c) for c in compl2]

# --- placement: each half's own vertex bbox (in its object frame); the build transform centres it on the bed
(lo_r, hi_r), (lo_l, hi_l) = bbox_xy(objr), bbox_xy(objl)
ext_r, ext_l = hi_r - lo_r, hi_l - lo_l
A = 0 if ext_r[0] + ext_l[0] < ext_r[1] + ext_l[1] else 1   # stack along the shorter footprint axis
wr, wl = ext_r[A], ext_l[A]
total = wr + wl + GAP
assert total < BED - 10, f'two halves need {total:.1f} mm of a {BED:.0f} mm bed'
assert max(ext_r[1-A], ext_l[1-A]) < BED - 10
cr = (BED - total) / 2 + wr / 2
cl = cr + wr / 2 + GAP + wl / 2
def tf(lo, hi, ca):   # translation that puts the bbox centre at (ca on axis A, BED/2 on the other) and the bottom on z=0
    c = (lo + hi) / 2
    target = [BED / 2, BED / 2]; target[A] = ca
    return '1 0 0 0 1 0 0 0 1 %.4f %.4f %.4f' % (target[0] - c[0], target[1] - c[1], -lo[2])
tr, tl = tf(lo_r, hi_r, cr), tf(lo_l, hi_l, cl)
print('right footprint %.1f x %.1f, left %.1f x %.1f, total depth %.1f of %.0f' % (
    hi_r[0]-lo_r[0], wr, hi_l[0]-lo_l[0], wl, total, BED))

# --- 3dmodel.model: add object 1001 with the left half's components, two build items
res_l = ('  <object id="1001" p:UUID="%s" type="model">\n   <components>\n' % uuid.uuid4()
         + '\n'.join('    ' + c for c in compl2) + '\n   </components>\n  </object>\n')
top = topr.replace(' </resources>', res_l + ' </resources>')
top = re.sub(r'<item objectid="1000" [^>]*/>',
             '<item objectid="1000" p:UUID="%s" transform="%s" printable="1"/>\n'
             '  <item objectid="1001" p:UUID="%s" transform="%s" printable="1"/>' % (uuid.uuid4(), tr, uuid.uuid4(), tl), top)
top = top.replace('v6.1<', 'v6.1, both 2x halves on one P1S plate<')

# --- object_1.model: append the left half's objects before </resources>
objm = objr.replace(b' </resources>', objl2[objl2.index(b'<object id='):objl2.rindex(b'</object>') + 9] + b'\n </resources>')

# --- model_settings.config: both <object> blocks; plate lists both instances
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
print('wrote', out, 'R at', tr.split()[-3:], 'L at', tl.split()[-3:])
