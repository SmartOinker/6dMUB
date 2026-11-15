"""Vectors unbiased to I and H = F_10(a,b,c,d)/sqrt10 (affine family F_10^(4)); bases; MU pairs; extensions.
R_{jk} = params[(k mod 5)-1] for j odd and k mod 5 != 0, else 0.   Usage: python3 affine.py seed nstarts"""
import numpy as np, sys, itertools, networkx as nx
from collections import Counter
d=10; seed=int(sys.argv[1]); ns=int(sys.argv[2]); rng=np.random.default_rng(seed)
par=rng.uniform(0,2*np.pi,4) if seed>0 else np.zeros(4)
w=np.exp(2j*np.pi/d); R=np.zeros((d,d))
for j in range(1,d,2):
    for k in range(d):
        if k%5: R[j,k]=par[k%5-1]
H=(w**np.outer(np.arange(d),np.arange(d)))*np.exp(1j*R)/np.sqrt(d)
assert np.allclose(H.conj().T@H,np.eye(d))
Hd=H.conj().T
def rj(P):
    x=np.exp(1j*np.c_[np.zeros(len(P)),P]); y=x@Hd.T
    r=np.abs(y)**2-1
    # d|y_k|^2/dp_m = 2 Re(conj(y_k) * Hd[k,m] * i x_m)
    J=2*np.real(np.conj(y)[:,:,None]*Hd[None,:,1:]*1j*x[:,None,1:])
    return r,J
def solve(P,it=150):
    lam=np.full(len(P),1e-2); r,J=rj(P); f=(r*r).sum(1)
    for _ in range(it):
        JT=J.transpose(0,2,1); dP=-np.linalg.solve(JT@J+lam[:,None,None]*np.eye(9),(JT@r[:,:,None]))[:,:,0]
        rn,Jn=rj(P+dP); fn=(rn*rn).sum(1); a=fn<f
        P=np.where(a[:,None],P+dP,P); r=np.where(a[:,None],rn,r); J=np.where(a[:,None,None],Jn,J); f=np.where(a,fn,f)
        lam=np.where(a,np.maximum(lam/5,1e-15),lam*4)
    return np.mod(P,2*np.pi),np.sqrt(f)
Ps=[]
for b in range(0,ns,20000):
    P,f=solve(rng.uniform(0,2*np.pi,(20000,9))); Ps.append(P[f<1e-11])
P=np.concatenate(Ps); X=np.exp(1j*np.c_[np.zeros(len(P)),P])
keys=Counter(); rep={}
for v in X:
    k=tuple(np.round(np.r_[v.real,v.imag],6)+0.); keys[k]+=1; rep.setdefault(k,v)
U=np.array(list(rep.values())); hits=np.array(list(keys.values())); N=len(U)
G=np.abs(U.conj()@U.T); o=G<1e-8; np.fill_diagonal(o,False)
Gr=nx.Graph(); Gr.add_nodes_from(range(N)); Gr.add_edges_from(zip(*np.nonzero(np.triu(o))))
B=[sorted(c) for c in nx.find_cliques(Gr) if len(c)==d]
unb=np.abs(G**2-d)<1e-8
mu=sum(1 for a,b in itertools.combinations(B,2) if unb[np.ix_(a,b)].all())
ext=Counter(int(unb[:,b].all(1).sum()) for b in B)
print(f"params={np.round(par,4).tolist()} starts={ns} conv={len(P)} vectors={N} minhits={hits.min()} orthpairs={o.sum()//2} bases={len(B)} MUpairs={mu} ext={dict(ext)} min_nonorth={G[~o&~np.eye(N,dtype=bool)].min():.3e}")
