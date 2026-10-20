import sys, numpy as np
from PIL import Image
def rot(az,el):
    az,el=np.radians(az),np.radians(el)
    Rz=np.array([[np.cos(az),-np.sin(az),0],[np.sin(az),np.cos(az),0],[0,0,1]])
    Rx=np.array([[1,0,0],[0,np.cos(el),-np.sin(el)],[0,np.sin(el),np.cos(el)]])
    return Rx@Rz
def render(V,F,az,el,size=700,colors=None,light=(0.3,-0.6,0.75)):
    # camera looks along +y in rotated frame; screen x = X, screen y = Z
    R=rot(az,el); P=V@R.T
    # view direction: looking from -y toward +y
    xs=P[:,0]; zs=P[:,2]; depth=P[:,1]
    lo=np.array([xs.min(),zs.min()]); hi=np.array([xs.max(),zs.max()])
    sc=(size*0.9)/max(hi-lo); off=(size-(hi-lo)*sc)/2
    sx=(xs-lo[0])*sc+off[0]; sy=size-((zs-lo[1])*sc+off[1])
    tri=P[F]; n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]); n/=np.linalg.norm(n,axis=1,keepdims=True)+1e-12
    L=np.array(light,float); L/=np.linalg.norm(L)
    # facing camera: normal y < 0 means facing viewer at -y
    shade=np.clip(np.abs(n@L),0,1)*0.75+0.25
    back=n[:,1]>0
    zb=np.full((size,size),np.inf); img=np.ones((size,size,3))
    X=sx[F]; Y=sy[F]; D=depth[F]
    for i in range(len(F)):
        x0,x1=int(max(0,np.floor(X[i].min()))),int(min(size-1,np.ceil(X[i].max())))
        y0,y1=int(max(0,np.floor(Y[i].min()))),int(min(size-1,np.ceil(Y[i].max())))
        if x1<x0 or y1<y0: continue
        gx,gy=np.meshgrid(np.arange(x0,x1+1)+0.5,np.arange(y0,y1+1)+0.5)
        (ax,bx,cx),(ay,by,cy)=X[i],Y[i]
        den=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
        if abs(den)<1e-12: continue
        w0=((by-cy)*(gx-cx)+(cx-bx)*(gy-cy))/den
        w1=((cy-ay)*(gx-cx)+(ax-cx)*(gy-cy))/den
        w2=1-w0-w1
        m=(w0>=-1e-6)&(w1>=-1e-6)&(w2>=-1e-6)
        if not m.any(): continue
        d=w0*D[i,0]+w1*D[i,1]+w2*D[i,2]
        sub=zb[y0:y1+1,x0:x1+1]; upd=m&(d<sub)
        sub[upd]=d[upd]
        base=np.array(colors[i]) if colors is not None else np.array([0.93,0.9,0.85])
        if back[i]: base=np.array([0.85,0.35,0.35])  # inside-out faces show red
        img[y0:y1+1,x0:x1+1][upd]=base*shade[i]
    return (img*255).astype(np.uint8)
if __name__=='__main__':
    sys.path.insert(0,sys.argv[3]); from load import load
    m=load(sys.argv[1]); out=sys.argv[2]
    V=m.vertices-m.bounds.mean(0); F=m.faces
    views=[(0,5,'front_negY'),(180,5,'back_posY'),(90,5,'side_a'),(270,5,'side_b'),(0,89,'top'),(0,-89,'bottom'),(35,25,'iso1'),(215,25,'iso2')]
    for az,el,name in views:
        im=render(V,F,az,el)
        Image.fromarray(im).save(f'{out}/{name}.png'); print(name)
