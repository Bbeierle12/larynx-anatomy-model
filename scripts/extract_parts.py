import zipfile, collections, sys, os, trimesh, numpy as np, json
B='/tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad/bp4'
z=zipfile.ZipFile(f'{B}/isa_BP3D_4.0_obj_99.zip'); names={os.path.basename(n)[:-4]:n for n in z.namelist() if n.endswith('.obj')}
zp=zipfile.ZipFile(f'{B}/partof_BP3D_4.0_obj_99.zip'); pnames={os.path.basename(n)[:-4]:n for n in zp.namelist() if n.endswith('.obj')}
rows=[l.rstrip('\n').split('\t') for l in open(f'{B}/isa_element_parts.txt') if l.strip()]
d=collections.defaultdict(list)
for r in rows:
    if len(r)>=3: d[r[1]].append(r[2])
want=sys.argv[1:] if len(sys.argv)>1 else []
os.makedirs(f'{B}/parts',exist_ok=True)
inv=json.load(open(f'{B}/parts/inventory.json')) if os.path.exists(f'{B}/parts/inventory.json') else {}
for w in want:
    els=sorted(set(d.get(w,[])))
    for e in els:
        src = z if e in names else (zp if e in pnames else None)
        if src is None: print('MISSING',w,e); continue
        data=src.read(names.get(e) or pnames.get(e)); open(f'{B}/parts/{e}.obj','wb').write(data)
        hdr=[l for l in data.decode(errors='ignore').splitlines()[:16] if 'English name' in l or 'Bounds' in l]
        m=trimesh.load(f'{B}/parts/{e}.obj',force='mesh')
        print(f'{w:34s} {e} faces {len(m.faces):6d} wt {m.is_watertight!s:5} bodies {len(m.split(only_watertight=False))} ext {np.round(m.extents,1)} | {hdr[0].split(":")[1].strip() if hdr else ""}')
        inv.setdefault(w,[]).append(e)
json.dump(inv,open(f'{B}/parts/inventory.json','w'),indent=1)
