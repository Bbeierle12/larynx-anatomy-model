"""Patch keys in a 3MF's Metadata/project_settings.config (JSON) in place: patch3mf.py file.3mf key=value ..."""
import sys, zipfile, json, shutil, os
fn = sys.argv[1]; kv = dict(a.split('=', 1) for a in sys.argv[2:])
tmp = fn + '.tmp'
with zipfile.ZipFile(fn) as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == 'Metadata/project_settings.config':
            d = json.loads(data)
            for k, v in kv.items(): d[k] = v if not isinstance(d.get(k), list) else [v]
            data = json.dumps(d, indent=4).encode()
        zout.writestr(item, data)
shutil.move(tmp, fn); print('patched', fn, kv)
