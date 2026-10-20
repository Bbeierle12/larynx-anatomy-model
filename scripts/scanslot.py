import numpy as np, os, sys
sys.path.insert(0,'scripts'); from partsconfig import PARTS
B='build8'; G=np.load(f'{B}/grid.npy'); P=G[3]; LO=G[:3]; NG=G[4:7].astype(int); Z0=1359.0; CX=-0.65
occ=np.zeros(tuple(NG),np.int16)
for pid,name,*_ in PARTS:
    f=f'{B}/occ_{pid:02d}.npz'
    if not os.path.exists(f) or pid in (68,69,70): continue
    d=np.load(f); o,a,b=d['occ'],d['a'],d['b']; sub=occ[a[0]:b[0],a[1]:b[1],a[2]:b[2]]; sub[o & (sub==0)]=pid
names={p[0]:p[1] for p in PARTS}
def at(x,y,z):
    i=((np.array([x,y,z+Z0])-LO)/P).astype(int); v=occ[tuple(i)]; return names.get(int(v),'air' if v==0 else str(v))
for y in (-106,-104,-102,-100):
    for z in (48,50,52):
        xs=np.arange(-3,-17,-0.5); row=[at(x,y,z) for x in xs]; out=[]
        for x,n in zip(xs,row):
            if not out or out[-1][1]!=n: out.append([x,n])
        print(f'y{y} z{z}: '+' | '.join(f'{x:.1f} {n[:16]}' for x,n in out))
