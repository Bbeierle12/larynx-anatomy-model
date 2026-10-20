import sys; sys.path.insert(0,'scripts')
import numpy as np, trimesh
from render import render
from PIL import Image, ImageDraw
from partsconfig import PARTS, GROUPS
import os
B=os.environ.get('BUILD','build')
cols={1:(0.94,0.91,0.84),2:(0.55,0.74,0.9),3:(0.95,0.8,0.32),4:(0.85,0.45,0.5)}
Vs=[];Fs=[];C=[];off=0
for pid,name,concepts,grp,pri,kind in PARTS:
    import os
    fp=f'{B}/final_{pid:02d}.ply'
    if not os.path.exists(fp): continue
    m=trimesh.load(fp)
    Vs.append(m.vertices); Fs.append(m.faces+off); off+=len(m.vertices); C+=[cols[grp]]*len(m.faces)
V=np.vstack(Vs); F=np.vstack(Fs); C=np.array(C)
c=(V.min(0)+V.max(0))/2; V0=V-c
views=[(0,8,'anterior'),(180,8,'posterior'),(90,8,'lateral (left side)'),(270,8,'lateral (right side)'),(180,60,'posterior-superior (laryngeal inlet)'),(0,-89,'from below (up the trachea)')]
size=int(sys.argv[2]) if len(sys.argv)>2 else 560
ims=[(n,render(V0,F,az,el,size=size,colors=C)) for az,el,n in views]
W=size; sheet=Image.new('RGB',(W*3,W*2),'white'); d=ImageDraw.Draw(sheet)
for i,(n,im) in enumerate(ims):
    sheet.paste(Image.fromarray(im),((i%3)*W,(i//3)*W)); d.text(((i%3)*W+8,(i//3)*W+8),n,fill='black')
sheet.save(sys.argv[1])
