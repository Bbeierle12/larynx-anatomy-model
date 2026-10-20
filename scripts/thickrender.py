import sys; sys.path.insert(0,sys.argv[2]); from load import load; from render import render
import numpy as np
from PIL import Image, ImageDraw
m=load(sys.argv[1]); m.merge_vertices(); T=np.load(sys.argv[3])
V=m.vertices-m.bounds.mean(0); F=m.faces
col=np.tile([0.93,0.9,0.85],(len(F),1))
col[T<1.2]=[0.98,0.85,0.3]; col[T<0.8]=[0.98,0.55,0.15]; col[T<0.4]=[0.85,0.1,0.1]
col[np.isnan(T)]=[0.5,0.2,0.8]
out=[]
for az,el,name in [(0,5,'front'),(180,5,'back'),(90,5,'side'),(0,89,'top')]:
    out.append((name,render(V,F,az,el,size=600,colors=col)))
# half model: keep faces with centroid x>0, view from -x (az=-90?) to see interior
C=V[F].mean(1); keep=C[:,0]>0
for az,name in [(270,'interior_right_half'),]:
    pass
im=render(V,F[keep],-90,5,size=600,colors=col[keep]); out.append(('interior (right half, viewed from midline)',im))
im=render(V,F[keep],-60,40,size=600,colors=col[keep]); out.append(('interior oblique',im))
W=600; sheet=Image.new('RGB',(W*3,W*2+40),'white'); d=ImageDraw.Draw(sheet)
for i,(n,im) in enumerate(out):
    sheet.paste(Image.fromarray(im),((i%3)*W,(i//3)*W+40)); d.text(((i%3)*W+8,(i//3)*W+44),n,fill='black')
d.text((8,8),'Wall thickness: red <0.4 mm (below one 0.4 mm extrusion)   orange 0.4-0.8 mm (1-2 lines)   yellow 0.8-1.2 mm   beige >1.2 mm',fill='black')
sheet.save(sys.argv[4])
