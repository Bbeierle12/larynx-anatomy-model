"""Add mesh parts to a Bambu 3MF (v6.1 -> v6.2): one npz mesh per object.
Usage: python add_part.py <in.3mf> <out.3mf> <object_id>=<mesh.npz> [<object_id>=<mesh.npz> ...]
The part is named "Tongue base and vallecula (sculpted, with glossoepiglottic folds)" on extruder 6 in
the 7-colour files (1 otherwise), and the title/description are moved from v6.1 to v6.2."""
import os, re, sys, uuid, zipfile
import numpy as np, trimesh

src, dst = sys.argv[1], sys.argv[2]
adds = [a.split('=', 1) for a in sys.argv[3:]]
NAME = 'Tongue base and vallecula (sculpted, with glossoepiglottic folds)'
multi = '7colour' in os.path.basename(src)
extruder = '6' if multi else '1'

zin = zipfile.ZipFile(src)
top = zin.read('3D/3dmodel.model').decode()
obj = zin.read('3D/Objects/object_1.model')
ms = zin.read('Metadata/model_settings.config').decode()

ids = [int(i) for i in re.findall(rb'<object id="(\d+)"', obj)]
next_id = max(ids) + 1
for object_id, ply in adds:
    _d = np.load(ply); m = trimesh.Trimesh(np.round(_d['v'], 5), _d['f'], process=True); m.merge_vertices()
    _, _cnt = np.unique(m.edges_sorted, axis=0, return_counts=True)
    assert m.is_watertight and (_cnt == 2).all(), ply
    pid = next_id; next_id += 1
    # 1. mesh object
    vs = '\n'.join(f'     <vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>' for x, y, z in m.vertices)
    ts = '\n'.join(f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in m.faces)
    block = (f'  <object id="{pid}" p:UUID="{uuid.uuid4()}" type="model">\n   <mesh>\n    <vertices>\n{vs}\n    </vertices>\n'
             f'    <triangles>\n{ts}\n    </triangles>\n   </mesh>\n  </object>\n')
    obj = obj.replace(b' </resources>', block.encode() + b' </resources>', 1)
    # 2. component in the right assembly object
    comp = f'    <component p:path="/3D/Objects/object_1.model" objectid="{pid}" p:UUID="{uuid.uuid4()}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n   </components>'
    pat = re.compile(r'(<object id="%s" [^>]*>\s*<components>.*?)   </components>' % object_id, re.S)
    top, n = pat.subn(lambda mo: mo.group(1) + comp, top, count=1)
    assert n == 1, ('component', object_id)
    # 3. part block in model_settings, at the end of that object's part list
    part = (f'    <part id="{pid}" subtype="normal_part">\n      <metadata key="name" value="{NAME}"/>\n'
            f'      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n      <metadata key="extruder" value="{extruder}"/>\n'
            f'      <mesh_stat face_count="{len(m.faces)}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>\n    </part>\n  </object>')
    pat = re.compile(r'(  <object id="%s">.*?)  </object>' % object_id, re.S)
    ms, n = pat.subn(lambda mo: mo.group(1) + part, ms, count=1)
    assert n == 1, ('part', object_id)
    print(f'{os.path.basename(dst)}: added part {pid} ({len(m.faces)} faces, {m.volume:.0f} mm3) to object {object_id}, extruder {extruder}')

top = top.replace('v6.1<', 'v6.2<')
top = top.replace('no tongue base (v6.1: the tongue block is removed; the pre-epiglottic fat is exposed above).',
                  'sculpted tongue base with vallecula (v6.2: the flat block of v6 replaced by a convex base of tongue with paramedian lingual-tonsil mounds, a median and two lateral glossoepiglottic folds, and a forward-leaning front; cut flat 1 mm above the epiglottis tip).')
assert 'v6.2' in top and 'sculpted tongue base' in top
zout = zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED)
for info in zin.infolist():
    data = zin.read(info.filename)
    if info.filename == '3D/3dmodel.model': data = top.encode()
    elif info.filename == '3D/Objects/object_1.model': data = obj
    elif info.filename == 'Metadata/model_settings.config': data = ms.encode()
    zout.writestr(info, data)
zout.close()
