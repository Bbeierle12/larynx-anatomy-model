"""v6 -> v6.1: drop the 'Tongue base and vallecula' part and relabel as an adult male larynx.
Usage: python make_v6_1.py <in.3mf> <out.3mf>
Bambu 3MFs hold every part as its own <object> in 3D/Objects/object_1.model, referenced by a
<component objectid> in 3D/3dmodel.model and a <part id> block in Metadata/model_settings.config,
all with the same id. The slicer unions the parts at slice time, so no mesh boolean is needed.
"""
import re, sys, zipfile

src, dst = sys.argv[1], sys.argv[2]
PART = "Tongue base and vallecula"
scale = "2x scale" if "_2x_" in src else "life size"

zin = zipfile.ZipFile(src)
ms = zin.read("Metadata/model_settings.config").decode()
top = zin.read("3D/3dmodel.model").decode()
obj = zin.read("3D/Objects/object_1.model")

ids = [m.group(1) for m in re.finditer(
    r'<part id="(\d+)" subtype="normal_part">\s*<metadata key="name" value="([^"]*)"', ms)
    if m.group(2).startswith(PART)]
if not ids:
    sys.exit(src + ": no tongue part found")
for pid in ids:
    ms, n = re.subn(r'\s*<part id="%s" subtype="normal_part">.*?</part>' % pid, "", ms, 1, flags=re.S); assert n == 1
    top, n = re.subn(r'\s*<component [^>]*objectid="%s" [^>]*/>' % pid, "", top, 1); assert n == 1
    obj, n = re.compile(rb'\s*<object id="%s" [^>]*>.*?</object>' % pid.encode(), re.S).subn(b"", obj, 1); assert n == 1

# relabel
ms = ms.replace('value="Larynx (life size)"', 'value="Adult male larynx (%s)"' % scale)
ms = ms.replace('value="Right half (patient right)"', 'value="Adult male larynx, right half (%s)"' % scale)
ms = ms.replace('value="Left half (patient left)"', 'value="Adult male larynx, left half (%s)"' % scale)
top = re.sub(r'(name="Title">)[^<]*', r'\1Adult male larynx and upper trachea (BodyParts3D 4.0 rebuild), v6.1', top)
top = re.sub(r'(name="Description">)Life-size laryngeal skeleton',
             r'\1ADULT MALE larynx: the source is one adult male dataset (BodyParts3D 4.0) and every corrected '
             r'dimension was steered to published adult-male norms (thyroid angle 81 deg, male-typical). '
             r'Life-size laryngeal skeleton', top)
top = top.replace("tongue base with vallecula.",
                  "no tongue base (v6.1: the tongue block is removed; the pre-epiglottic fat is exposed above).")
top = top.replace("Print halves to see inside;", "Printed at %s. Print halves to see inside;" % scale)
assert "Adult male" in ms and "ADULT MALE" in top

zout = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
for info in zin.infolist():
    data = zin.read(info.filename)
    if info.filename == "Metadata/model_settings.config": data = ms.encode()
    elif info.filename == "3D/3dmodel.model": data = top.encode()
    elif info.filename == "3D/Objects/object_1.model": data = obj
    zout.writestr(info, data)
zout.close()
print(dst, "removed part id(s)", ids)
