"""Flatten Bambu system presets (resolve 'inherits') into standalone JSON the CLI can load without the vendor tree."""
import json
R = r'C:\Program Files\Bambu Studio\resources\profiles\BBL'
def flat(kind, name):
    d = json.load(open(f'{R}\\{kind}\\{name}.json', encoding='utf-8'))
    base = flat(kind, d['inherits']) if d.get('inherits') else {}
    base.update({k: v for k, v in d.items() if k != 'inherits'})
    return base
def dump(d, path):
    d = {k: v for k, v in d.items() if k not in ('inherits', 'instantiation', 'setting_id')}
    d['from'] = 'User'
    json.dump(d, open(path, 'w', encoding='utf-8'), indent=2)
    print(path, len(d), 'keys; name =', d.get('name'))
dump(flat('machine', 'Bambu Lab P1S 0.4 nozzle'), 'p1s_machine_flat.json')
dump(flat('filament', 'Bambu PLA Basic @BBL P1S 0.4 nozzle'), 'p1s_pla_basic_flat.json')
proc = flat('process', '0.20mm Standard @BBL X1C')
ov = json.load(open('p1s_process_larynx.json', encoding='utf-8'))
proc.update({k: v for k, v in ov.items() if k != 'inherits'})
dump(proc, 'p1s_process_flat.json')
m = json.load(open('p1s_machine_flat.json'))
print('printable_area', m.get('printable_area'), 'height', m.get('printable_height'), 'start gcode starts:', m.get('machine_start_gcode', '')[:60].replace('\n', ' | '))
