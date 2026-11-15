import numpy as np, sys
sys.path.insert(0,'/home/claude/mub10/exact/code'); from cyclic import *
from collections import Counter
S=np.load(sys.argv[1]); d=10; idx={k:i for i,k in enumerate(key(S))}
imgs=[ [idx.get(k,-1) for k in key(np.round(im,12))] for im in sym_images(S,d)]
imgs=np.array(imgs); print("missing images:",(imgs<0).sum())
par=list(range(len(S)))
def f(a):
    while par[a]!=a: par[a]=par[par[a]]; a=par[a]
    return a
for g in imgs:
    for i,j in enumerate(g): par[f(i)]=f(j)
roots=[f(i) for i in range(len(S))]; c=Counter(roots)
sz=Counter(c.values()); print("orbits",len(c),"size distribution",sorted(sz.items()))
uni=np.abs(np.abs(S)-1).max(1)<1e-8; print("unimodular:",uni.sum())
np.save(sys.argv[1].replace('.npy','_orb.npy'),np.array(roots))
