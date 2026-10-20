"""Fill the slice results into the v4 README and build-notes section. Input: slice.json (from the PC)."""
import json, sys, re
S = '/tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad'
res = json.load(open(f'{S}/out6/slice.json'))
def fmt(n):
    r = res.get(n)
    if not r or r.get('exit') != 0: return 'did not slice'
    s = int(r['secs']); h, m = divmod(s // 60, 60); t = f'{h} h {m:02d} min'
    g = r['grams']; ch = r.get('changes', 0)
    return f'{t}, {g:.0f} g' + (f', {ch} colour changes (mostly purge)' if ch else '')
names = {'2x_whole_1colour': 'Larynx_v4_2x_whole_1colour.3mf', '2x_halves_1colour': 'Larynx_v4_2x_halves_1colour.3mf', '2x_whole_5colour': 'Larynx_v4_2x_whole_5colour.3mf',
         '2x_halfR_5colour': 'Larynx_v4_2x_halfR_5colour.3mf', '2x_halfL_5colour': 'Larynx_v4_2x_halfL_5colour.3mf',
         'lifesize_whole_1colour': 'Larynx_v4_lifesize_whole_1colour.3mf', 'lifesize_halves_1colour': 'Larynx_v4_lifesize_halves_1colour.3mf',
         'lifesize_whole_5colour': 'Larynx_v4_lifesize_whole_5colour.3mf', 'lifesize_halves_5colour': 'Larynx_v4_lifesize_halves_5colour.3mf'}
# README
rd = open(f'{S}/out6/README - Larynx life-size.txt').read()
f2 = '\n'.join(f'{names[k]:38s} {fmt(k)}' for k in ('2x_whole_1colour', '2x_halves_1colour', '2x_whole_5colour', '2x_halfR_5colour', '2x_halfL_5colour'))
f2 = f2.replace(f'{names["2x_halves_1colour"]:38s} {fmt("2x_halves_1colour")}', f'{names["2x_halves_1colour"]:38s} {fmt("2x_halves_1colour")}\n  Pins: 1.75 mm filament cut to 16 mm (hyoid) and 10 mm (cricoid).')
f2 += '\n  (halves 5-colour: one half per file, as in v3)'
f1 = '\n'.join(f'{names[k]:38s} {fmt(k)}' for k in ('lifesize_whole_1colour', 'lifesize_halves_1colour', 'lifesize_whole_5colour', 'lifesize_halves_5colour'))
f1 = f1.replace(f'{names["lifesize_halves_1colour"]:38s} {fmt("lifesize_halves_1colour")}', f'{names["lifesize_halves_1colour"]:38s} {fmt("lifesize_halves_1colour")}\n  Pins: 7.5 mm (hyoid), 4.5 mm (cricoid).')
rd = rd.replace('{FILES2X}', f2).replace('{FILES1X}', f1)
rd = rd.replace('{REVIEW}', open(f'{S}/out6/review_residuals.txt').read().rstrip())
open(f'{S}/out6/README - Larynx life-size.txt', 'w').write(rd)
# notes section
ns = open(f'{S}/out6/v4_notes_section.md').read()
rows = ['| File | Scale | Bambu Studio estimate |', '|---|---|---|']
scale = {'2x_whole_1colour': '2× (162 mm tall)', '2x_halves_1colour': '2×; pins 16 mm hyoid, 10 mm cricoid', '2x_whole_5colour': '2×', '2x_halfR_5colour': '2×, one half per file', '2x_halfL_5colour': '2×, one half per file',
         'lifesize_whole_1colour': '1:1 (81 mm)', 'lifesize_halves_1colour': '1:1; pins 7.5 / 4.5 mm', 'lifesize_whole_5colour': '1:1', 'lifesize_halves_5colour': '1:1'}
for k in names: rows.append(f'| `{names[k]}` | {scale[k]} | {fmt(k)} |')
files = 'Folder `Documents\\Blender\\Larynx life-size\\`, sliced copies in `sliced - ready to print\\`. Muscle has its own filament slot (5, red), so the multi-colour files are 5-colour; the A1 mini\'s AMS lite needs one manual change, or merge muscle into slot 4 in Bambu Studio.\n\n' + '\n'.join(rows)
ns = ns.replace('{FILES}', files)
open(f'{S}/out6/v4_notes_section.md', 'w').write(ns)
print('remaining placeholders:', re.findall(r'\{[A-Z0-9]+\}', rd + ns))
