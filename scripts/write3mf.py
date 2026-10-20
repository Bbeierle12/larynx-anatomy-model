"""Minimal Bambu Studio-compatible multi-part 3MF writer (one object made of named parts)."""
import zipfile, uuid, json, io, numpy as np

CT = '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
 <Default Extension="png" ContentType="image/png"/>
 <Default Extension="gcode" ContentType="text/x.gcode"/>
</Types>'''
RELS = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
 <Relationship Target="/Metadata/plate_1.png" Id="rel-2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/thumbnail"/>
</Relationships>'''
MODEL_RELS = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Target="/3D/Objects/object_1.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>'''
NS = 'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p"'

def _mesh_xml(oid, V, F):
    out = io.StringIO()
    out.write(f'  <object id="{oid}" p:UUID="{uuid.uuid4()}" type="model">\n   <mesh>\n    <vertices>\n')
    for x, y, z in V:
        out.write(f'     <vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>\n')
    out.write('    </vertices>\n    <triangles>\n')
    for a, b, c in F:
        out.write(f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>\n')
    out.write('    </triangles>\n   </mesh>\n  </object>\n')
    return out.getvalue()

def write(path, objects, project_settings=None, metadata=None, thumbnail_png=None, bed_center=(90, 90)):
    """objects: list of dicts {name, parts:[{name, V, F, extruder}], offset:(x,y)} ; meshes in object-local mm coords"""
    meta = metadata or {}
    z = zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED)
    z.writestr('[Content_Types].xml', CT)
    z.writestr('_rels/.rels', RELS)
    z.writestr('3D/_rels/3dmodel.model.rels', MODEL_RELS)
    # sub-model with all part meshes
    sub = io.StringIO()
    sub.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" {NS}>\n <metadata name="BambuStudio:3mfVersion">1</metadata>\n <resources>\n')
    comp_xml, settings_xml, build_xml, plate_inst, assemble = [], [], [], [], []
    mesh_id = 1
    obj_id_base = 1000
    for oi, obj in enumerate(objects):
        allV = np.vstack([p['V'] for p in obj['parts']])
        zmin = allV[:, 2].min()
        comps = []
        sett = [f'  <object id="{obj_id_base+oi}">', f'    <metadata key="name" value="{obj["name"]}"/>', f'    <metadata key="extruder" value="{obj.get("extruder",1)}"/>']
        for p in obj['parts']:
            sub.write(_mesh_xml(mesh_id, p['V'], p['F']))
            comps.append(f'    <component p:path="/3D/Objects/object_1.model" objectid="{mesh_id}" p:UUID="{uuid.uuid4()}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>')
            sett += [f'    <part id="{mesh_id}" subtype="normal_part">', f'      <metadata key="name" value="{p["name"]}"/>',
                     '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>', f'      <metadata key="extruder" value="{p.get("extruder",1)}"/>',
                     f'      <mesh_stat face_count="{len(p["F"])}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>', '    </part>']
            mesh_id += 1
        sett.append('  </object>')
        settings_xml += sett
        comp_xml.append(f'  <object id="{obj_id_base+oi}" p:UUID="{uuid.uuid4()}" type="model">\n   <components>\n' + '\n'.join(comps) + '\n   </components>\n  </object>')
        ox, oy = obj.get('offset', (0, 0))
        build_xml.append(f'  <item objectid="{obj_id_base+oi}" p:UUID="{uuid.uuid4()}" transform="1 0 0 0 1 0 0 0 1 {bed_center[0]+ox:.4f} {bed_center[1]+oy:.4f} {-zmin:.4f}" printable="1"/>')
        plate_inst.append(f'    <model_instance>\n      <metadata key="object_id" value="{obj_id_base+oi}"/>\n      <metadata key="instance_id" value="0"/>\n      <metadata key="identify_id" value="{300+oi}"/>\n    </model_instance>')
        assemble.append(f'   <assemble_item object_id="{obj_id_base+oi}" instance_id="0" transform="1 0 0 0 1 0 0 0 1 {ox:.4f} {oy:.4f} {-zmin:.4f}" offset="0 0 0" />')
    sub.write(' </resources>\n <build/>\n</model>\n')
    z.writestr('3D/Objects/object_1.model', sub.getvalue())
    md = '\n'.join(f' <metadata name="{k}">{v}</metadata>' for k, v in meta.items())
    main = (f'<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" {NS}>\n <metadata name="Application">BambuStudio-02.08.02.61</metadata>\n <metadata name="BambuStudio:3mfVersion">1</metadata>\n{md}\n'
            f' <resources>\n' + '\n'.join(comp_xml) + '\n </resources>\n <build p:UUID="' + str(uuid.uuid4()) + '">\n' + '\n'.join(build_xml) + '\n </build>\n</model>\n')
    z.writestr('3D/3dmodel.model', main)
    cfg = ('<?xml version="1.0" encoding="UTF-8"?>\n<config>\n' + '\n'.join(settings_xml) +
           '\n  <plate>\n    <metadata key="plater_id" value="1"/>\n    <metadata key="plater_name" value=""/>\n    <metadata key="locked" value="false"/>\n'
           '    <metadata key="thumbnail_file" value="Metadata/plate_1.png"/>\n' + '\n'.join(plate_inst) + '\n  </plate>\n  <assemble>\n' + '\n'.join(assemble) + '\n  </assemble>\n</config>\n')
    z.writestr('Metadata/model_settings.config', cfg)
    if project_settings is not None:
        z.writestr('Metadata/project_settings.config', json.dumps(project_settings, indent=4))
    if thumbnail_png is not None:
        z.writestr('Metadata/plate_1.png', thumbnail_png)
    z.close()
