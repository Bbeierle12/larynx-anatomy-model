"""Fill the slice results into the v5 README and build-notes section. Input: slice.json (from the PC)."""
import json, sys, re
S = '/tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad'
res = json.load(open(f'{S}/out7/slice.json'))
def fmt(n):
    r = res.get(n)
    if not r or r.get('exit') != 0: return 'did not slice'
    s = int(r['secs']); h, m = divmod(s // 60, 60); t = f'{h} h {m:02d} min'
    g = r['grams']; ch = r.get('changes', 0)
    return f'{t}, {g:.0f} g' + (f', {ch} colour changes (mostly purge)' if ch else '')
names = {'2x_whole_1colour': 'Larynx_v5_2x_whole_1colour.3mf', '2x_halves_1colour': 'Larynx_v5_2x_halves_1colour.3mf', '2x_whole_6colour': 'Larynx_v5_2x_whole_6colour.3mf',
         '2x_halfR_6colour': 'Larynx_v5_2x_halfR_6colour.3mf', '2x_halfL_6colour': 'Larynx_v5_2x_halfL_6colour.3mf',
         'lifesize_whole_1colour': 'Larynx_v5_lifesize_whole_1colour.3mf', 'lifesize_halves_1colour': 'Larynx_v5_lifesize_halves_1colour.3mf',
         'lifesize_whole_6colour': 'Larynx_v5_lifesize_whole_6colour.3mf', 'lifesize_halves_6colour': 'Larynx_v5_lifesize_halves_6colour.3mf'}
# README
rd = open(f'{S}/out7/README - Larynx life-size.txt').read()
f2 = '\n'.join(f'{names[k]:38s} {fmt(k)}' for k in ('2x_whole_1colour', '2x_halves_1colour', '2x_whole_6colour', '2x_halfR_6colour', '2x_halfL_6colour'))
f2 = f2.replace(f'{names["2x_halves_1colour"]:38s} {fmt("2x_halves_1colour")}', f'{names["2x_halves_1colour"]:38s} {fmt("2x_halves_1colour")}\n  Pins: 1.75 mm filament cut to 16 mm (hyoid) and 10 mm (cricoid).')
f2 += '\n  (halves 6-colour: one half per file, lying on its side along the bed; the\n  six-slot wipe tower sits in the front-left corner)'
f1 = '\n'.join(f'{names[k]:38s} {fmt(k)}' for k in ('lifesize_whole_1colour', 'lifesize_halves_1colour', 'lifesize_whole_6colour', 'lifesize_halves_6colour'))
f1 = f1.replace(f'{names["lifesize_halves_1colour"]:38s} {fmt("lifesize_halves_1colour")}', f'{names["lifesize_halves_1colour"]:38s} {fmt("lifesize_halves_1colour")}\n  Pins: 7.5 mm (hyoid), 4.5 mm (cricoid).')
rd = rd.replace('{FILES2X}', f2).replace('{FILES1X}', f1)
open(f'{S}/out7/README - Larynx life-size.txt', 'w').write(rd)
# notes section
ns = open(f'{S}/out7/v5_notes_section.md').read()
rows = ['| File | Scale | Bambu Studio estimate |', '|---|---|---|']
scale = {'2x_whole_1colour': '2× (162 mm tall)', '2x_halves_1colour': '2×; pins 16 mm hyoid, 10 mm cricoid', '2x_whole_6colour': '2×', '2x_halfR_6colour': '2×, one half per file', '2x_halfL_6colour': '2×, one half per file',
         'lifesize_whole_1colour': '1:1 (81 mm)', 'lifesize_halves_1colour': '1:1; pins 7.5 / 4.5 mm', 'lifesize_whole_6colour': '1:1', 'lifesize_halves_6colour': '1:1'}
for k in names: rows.append(f'| `{names[k]}` | {scale[k]} | {fmt(k)} |')
files = 'Folder `Documents\\Blender\\Larynx life-size\\`, sliced copies in `sliced - ready to print\\`. Muscle (slot 5, red) and mucosa (slot 6, salmon) have their own filament slots, so the multi-colour files are 6-colour; the A1 mini\'s AMS lite has four slots, so merge mucosa into slot 4 and muscle into another in Bambu Studio, or accept two manual changes.\n\n' + '\n'.join(rows)
ns = ns.replace('{FILES}', files)
open(f'{S}/out7/v5_notes_section.md', 'w').write(ns)
print('remaining placeholders:', re.findall(r'\{[A-Z0-9]+\}', rd + ns))
