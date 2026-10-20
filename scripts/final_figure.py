import sys, os; sys.path.insert(0,'scripts')
import numpy as np, trimesh
from load import load
from render import rot
from PIL import Image, ImageDraw, ImageFont
from partsconfig import PARTS
import render as R
cols={1:(0.97,0.90,0.87),2:(0.30,0.62,0.88),3:(0.96,0.88,0.25),4:(0.93,0.45,0.52)}
Vs=[];Fs=[];C=[];off=0
for pid,name,c,grp,*_ in PARTS:
    f=f'build/final_{pid:02d}.ply'
    if not os.path.exists(f): continue
    m=trimesh.load(f,process=False); Vs.append(m.vertices); Fs.append(m.faces+off); off+=len(m.vertices); C+=[cols[grp]]*len(m.faces)
V=np.vstack(Vs); F=np.vstack(Fs); C=np.array(C)
V=V-[(V[:,0].min()+V[:,0].max())/2,(V[:,1].min()+V[:,1].max())/2,V[:,2].min()]
O=load('extract/3D/Objects/object_2.model'); OV=O.vertices-[0,0,O.vertices[:,2].min()]; OF=O.faces
def render_fixed(V,F,az,el,mm_per_px,size,colors=None,zc=None):
    # render with a fixed scale so models are comparable
    Rm=rot(az,el); P=V@Rm.T
    xs=P[:,0]; zs=P[:,2]
    cx=0; cz=zc if zc is not None else (zs.min()+zs.max())/2
    pad=np.array([[cx-size*mm_per_px/2, cz-size*mm_per_px/2],[cx+size*mm_per_px/2, cz+size*mm_per_px/2]])
    Vb=np.vstack([V, np.linalg.solve(Rm, np.array([[pad[0,0],0,pad[0,1]],[pad[1,0],0,pad[1,1]]]).T).T])
    Fb=F
    return R.render(Vb,Fb,az,el,size=size,colors=colors)
size=700; mmpx=125/ (size*0.9)
a=render_fixed(OV,OF,0,8,mmpx,size,zc=62)
b=render_fixed(V,F,0,8,mmpx,size,colors=C,zc=62)
views=[R.render(V,F,az,el,size=520,colors=C) for az,el in [(0,8),(90,8),(180,8),(180,55)]]
W=1400+520*0; sheet=Image.new('RGB',(2080,1040),'white'); d=ImageDraw.Draw(sheet)
try: fnt=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22); fs=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
except: fnt=fs=None
sheet.paste(Image.fromarray(a),(0,40)); sheet.paste(Image.fromarray(b),(640,40))
d.text((20,8),'Same scale: original MakerWorld file (left, ~1.4x life size, one merged shell)  vs  rebuild (right, 1:1, 32 named parts)',fill='black',font=fnt)
labels=['anterior','right lateral','posterior','laryngeal inlet from above-behind']
for i,im in enumerate(views):
    x=1300+(i%2)*390; y=40+(i//2)*600
    imc=Image.fromarray(im).resize((390,390))
    sheet.paste(imc,(x,y+20)); d.text((x+10,y),labels[i],fill='black',font=fs)
leg=[('Bone',cols[1]),('Hyaline cartilage',cols[2]),('Elastic cartilage',cols[3]),('Ligament, membrane, vocal-fold muscle',cols[4])]
for i,(t,c) in enumerate(leg):
    y=760+i*34; d.rectangle([660,y,688,y+24],fill=tuple(int(255*v) for v in c),outline='black'); d.text((700,y),t,fill='black',font=fs)
d.text((660,920),'Life size: 38.6 x 36.1 x 73.8 mm  |  1 h 38 min, 17.4 g PLA on the A1 mini (single colour)',fill='black',font=fs)
d.text((660,950),'Source: BodyParts3D 4.0, (c) DBCLS, CC BY 4.0',fill='black',font=fs)
sheet.save('renders/final_summary.png')
