"""Read the parts of a Bambu 3MF (one <object> per part) as trimesh meshes, keyed by part name."""
import re, zipfile, numpy as np, trimesh


def read_parts(path):
    z = zipfile.ZipFile(path)
    ms = z.read('Metadata/model_settings.config').decode()
    names = dict(re.findall(r'<part id="(\d+)" subtype="normal_part">\s*<metadata key="name" value="([^"]*)"', ms))
    obj = z.read('3D/Objects/object_1.model')
    out = {}
    for m in re.finditer(rb'<object id="(\d+)"[^>]*>(.*?)</object>', obj, re.S):
        oid = m.group(1).decode()
        body = m.group(2)
        v = np.array(re.findall(rb'x="([-\d.]+)" y="([-\d.]+)" z="([-\d.]+)"', body), dtype=float)
        f = np.array(re.findall(rb'v1="(\d+)" v2="(\d+)" v3="(\d+)"', body), dtype=int)
        out.setdefault(names.get(oid, '?'), []).append((oid, trimesh.Trimesh(v, f, process=False)))
    return out


def one(parts, name, which=0):
    return parts[name][which][1]
