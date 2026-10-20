import numpy as np, trimesh
from lxml import etree
def load(path):
    ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
    t=etree.parse(path)
    V=np.array([[float(v.get('x')),float(v.get('y')),float(v.get('z'))] for v in t.iterfind('.//m:vertex',ns)])
    F=np.array([[int(f.get('v1')),int(f.get('v2')),int(f.get('v3'))] for f in t.iterfind('.//m:triangle',ns)])
    return trimesh.Trimesh(V,F,process=False)
