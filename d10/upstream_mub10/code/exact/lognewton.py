import numpy as np, sys, time
sys.path.insert(0,'/home/claude/mub10/exact/code'); from cyclic import G, newton, key, closure
d=10
def GL(U):
    B=len(U); u=np.concatenate([np.zeros((B,1),complex),U],1)
    r=np.empty((B,d-1),complex); J=np.empty((B,d-1,d-1),complex)
    for k in range(1,d):
        t=np.exp(np.roll(u,-k,1)-u); r[:,k-1]=t.sum(1)
        J[:,k-1,:]=(np.roll(t,k,1)-t)[:,1:]
    return r,J
def lnewton(U,iters=100):
    for it in range(iters):
        with np.errstate(all='ignore'):
            r,J=GL(U); f=np.abs(r).max(1)
            dx=np.linalg.solve(J+1e-300,-r[:,:,None])[:,:,0]
            nrm=np.abs(dx).max(1); s=np.minimum(1,0.5/np.maximum(nrm,1e-300))  # trust region in log coords
            U=U+s[:,None]*dx
            U=np.where(np.isfinite(U),U,0)
    r,J=GL(U); return U,np.abs(r).max(1)
S=np.load(sys.argv[1]); known=set(key(S)); rng=np.random.default_rng(int(sys.argv[2])); found=[]
t0=time.time()
for b in range(int(sys.argv[3])):
    U0=rng.normal(0,float(sys.argv[4]),(5000,9))+1j*rng.uniform(0,2*np.pi,(5000,9))
    U,f=lnewton(U0)
    X=np.exp(U[f<1e-9]); X,ff=newton(X,d,iters=3); X=X[ff<1e-11]
    for v,k in zip(X,key(X)):
        if k not in known: known.add(k); found.append(v)
    print(b,(f<1e-9).sum(),len(found),f"{time.time()-t0:.0f}s",flush=True)
if found:
    S2=closure(np.concatenate([S,np.array(found)]),d); print("after closure",len(S2)); np.save(sys.argv[5],S2)
