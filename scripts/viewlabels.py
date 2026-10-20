import sys, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
sys.path.insert(0,'scripts'); from partsconfig import PARTS
B='build'; g=np.load(f'{B}/grid.npy'); lo=g[:3]; P=g[3]
L=np.load(sys.argv[1], mmap_mode='r')
gc={1:(0.85,0.82,0.74),2:(0.36,0.61,0.84),3:(0.88,0.69,0.13),4:(0.82,0.32,0.38)}
lut=np.ones((256,3)); 
for pid,name,c,grp,*_ in PARTS: lut[pid]=gc[grp]
specs=[s.split(':') for s in sys.argv[3].split(',')]
n=len(specs); cols=min(4,n); rows=(n+cols-1)//cols
fig,axs=plt.subplots(rows,cols,figsize=(6*cols,6*rows))
for ax,(ax_name,val) in zip(np.ravel(axs),specs):
    v=float(val); i='xyz'.index(ax_name); k=int(round((v-lo[i])/P))
    sl=[slice(None)]*3; sl[i]=k; img=np.asarray(L[tuple(sl)])
    rgb=lut[img]
    other=[j for j in range(3) if j!=i]
    ext=[lo[other[0]], lo[other[0]]+P*img.shape[0], lo[other[1]], lo[other[1]]+P*img.shape[1]]
    ax.imshow(np.transpose(rgb,(1,0,2)),origin='lower',extent=ext,interpolation='nearest')
    ax.set_title(f'{ax_name}={v}'); ax.set_xlabel('xyz'[other[0]]); ax.set_ylabel('xyz'[other[1]])
plt.tight_layout(); plt.savefig(sys.argv[2],dpi=60)
