"""Rewrite a 3MF's embedded project settings for the P1S: machine and filament keys come from the flattened Bambu
system presets (p1s_machine_flat.json, p1s_pla_basic_flat.json); the process keys are the project's own, plus the
overrides in p1s_process_larynx.json. Usage: python apply_p1s.py in.3mf out.3mf"""
import json, sys, zipfile
src, dst = sys.argv[1], sys.argv[2]
META = {'name', 'type', 'from', 'inherits', 'instantiation', 'setting_id', 'compatible_printers', 'compatible_printers_condition'}
mach = json.load(open('p1s_machine_flat.json', encoding='utf-8'))
fila = json.load(open('p1s_pla_basic_flat.json', encoding='utf-8'))
ov = json.load(open('p1s_process_larynx.json', encoding='utf-8'))
zin = zipfile.ZipFile(src)
pj = json.loads(zin.read('Metadata/project_settings.config'))
old = dict(pj)
for d in (mach, fila):
    for k, v in d.items():
        if k not in META:
            pj[k] = v
for k, v in ov.items():
    if k not in META:
        pj[k] = v
pj['printer_settings_id'] = mach['name']
pj['printer_model'] = mach['printer_model']
pj['filament_settings_id'] = [fila['name']]
pj['print_settings_id'] = '0.20mm Standard @BBL X1C'
pj['print_compatible_printers'] = [mach['name']]
pj['curr_bed_type'] = 'Textured PEI Plate'
changed = sorted(k for k in pj if str(pj[k]) != str(old.get(k)))
print(len(changed), 'keys changed; e.g.', [k for k in changed if k in ('printable_area', 'printable_height', 'machine_start_gcode', 'machine_max_speed_x', 'nozzle_temperature', 'retraction_length', 'elefant_foot_compensation', 'enable_prime_tower', 'fan_cooling_layer_time', 'bed_exclude_area', 'thumbnails')])
zout = zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED)
for info in zin.infolist():
    data = zin.read(info.filename)
    if info.filename == 'Metadata/project_settings.config':
        data = json.dumps(pj, indent=4, ensure_ascii=False).encode('utf-8')
    zout.writestr(info, data)
zout.close()
print('wrote', dst)
