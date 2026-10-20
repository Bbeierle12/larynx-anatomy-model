import sys; sys.path.insert(0,sys.argv[2]); from load import load; from render import render
import numpy as np
from PIL import Image, ImageDraw
m=load(sys.argv[1]); m.merge_vertices(); T=np.load(sys.argv[3])
zmin=m.bounds[0,2]; V=m.vertices-m.bounds.mean(0); V[:,2]=m.vertices[:,2]-zmin; F=m.faces
col=np.tile([0.93,0.9,0.85],(len(F),1))
col[T<1.2]=[0.98,0.85,0.3]; col[T<0.8]=[0.98,0.55,0.15]; col[T<0.4]=[0.85,0.1,0.1]
C=V[F].mean(1)
out=[]
k=C[:,2]<64
out.append(('glottis from above (cut at z=64)',render(V,F[k],0,89,size=600,colors=col[k])))
out.append(('glottis oblique from posterior-above',render(V,F[k],180,50,size=600,colors=col[k])))
k2=C[:,0]<0
out.append(('left half, viewed from midline',render(V,F[k2],90,5,size=600,colors=col[k2])))
k3=C[:,0]>0
out.append(('right half, viewed from midline',render(V,F[k3],-90,5,size=600,colors=col[k3])))
k4=(C[:,2]<64)&(C[:,2]>20)
out.append(('subglottis from below (z 20-64)',render(V,F[k4],0,-89,size=600,colors=col[k4])))
k5=(C[:,2]>20)&(C[:,2]<45)
out.append(('cricoid + cricothyroid zone, front',render(V,F[k5],0,10,size=600,colors=col[k5])))
W=600; sheet=Image.new('RGB',(W*3,W*2),'white'); d=ImageDraw.Draw(sheet)
for i,(n,im) in enumerate(out):
    sheet.paste(Image.fromarray(im),((i%3)*W,(i//3)*W)); d.text(((i%3)*W+8,(i//3)*W+8),n,fill='black')
sheet.save(sys.argv[4])
