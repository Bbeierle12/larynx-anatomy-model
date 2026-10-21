"""Build the v6 README (from the v5 README + the v6 section) and fill the slice results into it and the v6 notes. Input: out8/slice.json."""
import json, sys, re, os
S = '/tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad'
res = json.load(open(f'{S}/out8/slice.json')) if os.path.exists(f'{S}/out8/slice.json') else {}
def fmt(n):
    r = res.get(n)
    if not r: return 'not sliced yet'
    if r.get('exit') != 0: return f'did not slice (exit {r.get("exit")})'
    s = int(r['secs']); h, m = divmod(s // 60, 60); t = f'{h} h {m:02d} min'
    g = r['grams']; ch = r.get('changes', 0)
    return f'{t}, {g:.0f} g' + (f', {ch} colour changes (mostly purge)' if ch else '')
K2 = ('2x_whole_1colour', '2x_halfR_1colour', '2x_halfL_1colour', '2x_whole_7colour', '2x_halfR_7colour', '2x_halfL_7colour')
K1 = ('lifesize_whole_1colour', 'lifesize_halves_1colour', 'lifesize_whole_7colour', 'lifesize_halves_7colour')
names = {k: f'Larynx_v6_{k}.3mf' for k in K2 + K1}
qa = {}
for line in open(f'{S}/build8/pipeline8m.log'):
    if line.startswith('rima glottidis'): qa['rima'] = re.search(r'area (\d+) mm2', line).group(1); qa['circle'] = re.search(r'circle ([\d.]+)', line).group(1)
    if line.startswith('largest sphere'): qa['sphere'] = re.search(r': ([\d.]+) mm', line).group(1)
sec = open(f'{S}/out8/readme_v6_section.txt').read()
f2 = '\n'.join(f'{names[k]:38s} {fmt(k)}' for k in K2)
f2 = f2.replace(f'{names["2x_halfL_1colour"]:38s} {fmt("2x_halfL_1colour")}', f'{names["2x_halfL_1colour"]:38s} {fmt("2x_halfL_1colour")}\n  Pins: 1.75 mm filament cut to 16 mm (hyoid) and 10 mm (cricoid).')
f2 += '\n  (2x halves: one half per file since v6 - two halves side by side need 199 mm\n  of the 180 mm bed. Each half lies on its cut face with the long axis along\n  the bed, 178.8 mm, so there is no brim; the wipe tower is at the left edge.\n  The whole 7-colour model is shifted 15 mm back to clear the tower.)'
f1 = '\n'.join(f'{names[k]:38s} {fmt(k)}' for k in K1)
f1 = f1.replace(f'{names["lifesize_halves_1colour"]:38s} {fmt("lifesize_halves_1colour")}', f'{names["lifesize_halves_1colour"]:38s} {fmt("lifesize_halves_1colour")}\n  Pins: 7.5 mm (hyoid), 4.5 mm (cricoid).')
rev = open(f'{S}/out8/readme_v6_known_limits.txt').read().rstrip() if os.path.exists(f'{S}/out8/readme_v6_known_limits.txt') else '  (see the build notes)'
sec = sec.replace('{FILES2X}', f2).replace('{FILES1X}', f1).replace('{PARTS}', '81').replace('{PRE}', '3.64').replace('{PARA}', '0.44').replace('{FAT}', '4.5').replace('{FOSSA}', '1.73') \
         .replace('{RIMA}', qa.get('rima', '99')).replace('{CIRCLE}', qa.get('circle', '7.7')).replace('{SPHERE}', qa.get('sphere', '7.5')).replace('{REVIEW}', rev)
rd = open(f'{S}/out7/README - Larynx life-size.txt').read()
rd = rd.replace('Five versions live in this folder. Newest first:\n\n', 'Six versions live in this folder. Newest first:\n\n  Larynx_v6_2x_*        version 6, stages 3b and 3c (fat-filled spaces, saccules, joint capsules,\n                        piriform fossae, constrictors, hypopharynx, oesophagus, tongue base), 2x\n  Larynx_v6_lifesize_*  the same geometry at 1:1\n')
assert 'Six versions' in rd
marker = 'VERSION 5 - wider framework and stage 3'
assert marker in rd; rd = rd.replace(marker, sec.rstrip() + '\n\n\n' + marker, 1)
open(f'{S}/out8/README - Larynx life-size.txt', 'w').write(rd)
# notes section
ns = open(f'{S}/out8/v6_notes_section.md').read()
rows = ['| File | Scale | Bambu Studio estimate |', '|---|---|---|']
scale = {'2x_whole_1colour': '2× (179 mm tall)', '2x_halfR_1colour': '2×, one half per file; pins 16 mm hyoid, 10 mm cricoid', '2x_halfL_1colour': '2×, one half per file', '2x_whole_7colour': '2×', '2x_halfR_7colour': '2×, one half per file', '2x_halfL_7colour': '2×, one half per file',
         'lifesize_whole_1colour': '1:1 (81 mm)', 'lifesize_halves_1colour': '1:1; pins 7.5 / 4.5 mm', 'lifesize_whole_7colour': '1:1', 'lifesize_halves_7colour': '1:1'}
for k in names: rows.append(f'| `{names[k]}` | {scale[k]} | {fmt(k)} |')
files = 'Folder `Documents\\Blender\\Larynx life-size\\`, sliced copies in `sliced - ready to print\\`. Seven filament slots (fat is slot 7, sunflower yellow), so the multi-colour files are 7-colour; the A1 mini\'s AMS lite has four, so merge slots in Bambu Studio or accept the manual changes. Everything inside is visible only on the halves; the whole model prints as a block whose only cavities are the airway, vallecula, fossae and oesophageal slit.\n\n' + '\n'.join(rows)
ns = ns.replace('{FILES}', files)
open(f'{S}/out8/v6_notes_section.md', 'w').write(ns)
print('remaining placeholders:', re.findall(r'\{[A-Z0-9]+\}', rd + ns))
