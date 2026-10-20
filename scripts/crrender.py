import sys, os; sys.path.insert(0,'scripts')
import numpy as np, trimesh
from render import render
from PIL import Image, ImageDraw
out=sys.argv[1]; files=sys.argv[2:]
ims=[]
for f in files:
    m=trimesh.load(f,process=False)
    V=m.vertices-[ -0.65,-100.6,m.bounds[0,2]+15]
    for az,el,n in [(0,5,'anterior'),(270,5,'right lateral'),(180,5,'posterior'),(315,25,'antero-lateral'),(90,5,'left lateral')]:
        ims.append((f'{f} {n}',render(V,m.faces,az,el,size=380)))
W=380; nc=5; sheet=Image.new('RGB',(W*nc,W*len(files)),'white'); d=ImageDraw.Draw(sheet)
for i,(n,im) in enumerate(ims):
    sheet.paste(Image.fromarray(im),((i%nc)*W,(i//nc)*W)); d.text(((i%nc)*W+8,(i//nc)*W+8),n,fill='black')
sheet.save(out)
