import sys, os, numpy as np, edt
from scipy import ndimage
sys.path.insert(0,'scripts')
from partsconfig import PARTS
B=sys.argv[1]; bx=[float(v) for v in sys.argv[2:8]]
g=np.load(f'{B}/grid.npy'); LO=g[:3]; P=g[3]; NG=g[4:7].astype(int); Z0=g[7]
occ=np.zeros(tuple(NG),bool)
for pid,*_ in PARTS:
    f=f'{B}/occ_{pid:02d}.npz'
    if not os.path.exists(f): continue
    d=np.load(f); o,a,b=d['occ'],d['a'],d['b']; occ[a[0]:b[0],a[1]:b[1],a[2]:b[2]]|=o
k0=int(np.floor((Z0-LO[2])/P)); occ[:,:,:k0]=True
D=edt.edt(~occ,anisotropy=(P,P,P),black_border=False)
i0=((np.array([bx[0],bx[2],bx[4]+Z0])-LO)/P).astype(int); i1=((np.array([bx[1],bx[3],bx[5]+Z0])-LO)/P).astype(int)
sub=D[i0[0]:i1[0],i0[1]:i1[1],i0[2]:i1[2]]; k=np.unravel_index(sub.argmax(),sub.shape); sv=tuple(i0+np.array(k)); seed=LO+np.array(sv)*P
print('seed', np.round(seed-[0,0,Z0],1), 'width %.1f' % (2*sub.max()))
for r in np.arange(0.3,4.0,0.2):
    lab,n=ndimage.label(D>=r); s_=int(lab[sv])
    if s_==0: print('swallowed at %.1f' % r); break
    c=lab==s_; t=c[0].any() or c[-1].any() or c[:,0].any() or c[:,-1].any() or c[:,:,-1].any() or c[:,:,k0].any()
    sl=ndimage.find_objects(c.astype(np.int8))[0]; mn=LO+np.array([q.start for q in sl])*P; mx=LO+np.array([q.stop for q in sl])*P
    print(f'r {r:.1f}: comp {c.sum()*P**3:.0f} mm3 outside {t}  x {mn[0]:.1f}..{mx[0]:.1f} y {mn[1]:.1f}..{mx[1]:.1f} z {mn[2]-Z0:.1f}..{mx[2]-Z0:.1f}')
    if not t: break
