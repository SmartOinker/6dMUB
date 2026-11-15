import numpy as np, json, itertools
from collections import Counter, defaultdict
d=10; P=np.load('/home/claude/mub10/exact/data/bu10_phases.npy'); A=json.load(open('/home/claude/mub10/exact/data/d10_analysis.json'))
X=np.exp(1j*np.c_[np.zeros(len(P)),P]); w=np.exp(2j*np.pi/d)
F=w**np.outer(np.arange(d),np.arange(d))/np.sqrt(d); I=np.eye(d)
bases=A['bases']
def U(b): return X[b].T/np.sqrt(d)
def rk(z,dec=6): return (round(z.real,dec)+0.0, round(z.imag,dec)+0.0)
def tripinv(U1,U2,U3,conj_sym=True):
    G12=U1.conj().T@U2; G23=U2.conj().T@U3; G31=U3.conj().T@U1
    T=np.einsum('ab,bc,ca->abc',G12,G23,G31).ravel()*d**1.5
    k1=tuple(sorted(rk(t) for t in T))
    if not conj_sym: return k1
    k2=tuple(sorted(rk(np.conj(t)) for t in T)); return min(k1,k2)
def haag(H):
    L=np.einsum('ij,kl,il,kj->ijkl',H,H,H.conj(),H.conj()).ravel()
    return frozenset(rk(z,5) for z in L)
def defect(H):
    N=len(H); rows=[]
    for i in range(N):
        for k in range(i+1,N):
            c=H[i]*H[k].conj()     # sum_j c_j (R_ij - R_kj)=0
            for part in (c.real,c.imag):
                r=np.zeros((N,N)); r[i]+=part; r[k]-=part; rows.append(r.ravel())
    M=np.array(rows); s=np.linalg.svd(M,compute_uv=False); rank=(s>1e-8*s[0]).sum()
    return N*N-rank-(2*N-1)
print("defect F10:",defect(np.sqrt(d)*F))
inv=[]; 
for k,b in enumerate(bases):
    inv.append(tripinv(I,F,U(b)))
cls=defaultdict(list)
for k,v in enumerate(inv): cls[v].append(k)
print("distinct triple-product multisets (conj-symmetrised):",len(cls))
inv2=[tripinv(I,F,U(b),False) for b in bases]; print("without conj symmetrisation:",len(set(inv2)))
borb=A['basis_orbit']
# compare with basis orbits
for v,ks in cls.items():
    pass
orb_to_cls={}
cl_index={v:i for i,v in enumerate(cls)}
for k in range(len(bases)): orb_to_cls.setdefault(borb[k],set()).add(cl_index[inv[k]])
print("orbit -> invariant class:",{o:sorted(s) for o,s in sorted(orb_to_cls.items())})
hF=haag(np.sqrt(d)*F)
out=[]
for o,rep in enumerate(A['basis_orbit_reps']):
    B=U(bases[rep]); H1=np.sqrt(d)*B; H2=np.sqrt(d)*F.conj().T@B
    h1=haag(H1); h2=haag(H2)
    ent=np.angle(H1)/(2*np.pi); butson=[n for n in (2,4,5,10,20,40,60,120) if np.allclose(np.round(ent*n),ent*n,atol=1e-8)]
    r=dict(orbit=o,size=A['basis_orbit_sizes'][o],cls=cl_index[inv[rep]],defect_IB=int(defect(H1)),defect_FB=int(defect(H2)),
      haag_IB=len(h1),haag_FB=len(h2),IB_equiv_F_haag=(h1==hF),FB_equiv_F_haag=(h2==hF),butson_IB=butson[:1])
    print(r); out.append(r)
json.dump(dict(n_classes_lower=len(cls),orbit_to_class={int(o):sorted(s) for o,s in orb_to_cls.items()},orbits=out),open('/home/claude/mub10/exact/data/d10_triple_classes.json','w'),default=str)
