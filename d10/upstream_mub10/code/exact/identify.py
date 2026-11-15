import numpy as np, json
d=10; P=np.load('data/bu10_phases.npy'); A=json.load(open('data/d10_analysis.json'))
X=np.exp(1j*np.concatenate([np.zeros((len(P),1)),P],1))
w=np.exp(2j*np.pi/d); Xs=np.roll(np.eye(d),1,0); Z=np.diag(w**np.arange(d))
bases=A['bases']; borb=A['basis_orbit']
for o,rep in enumerate(A['basis_orbit_reps']):
    B=X[bases[rep]].T/np.sqrt(d)
    ops=[]
    for a in range(d):
        for b in range(d):
            if a==0 and b==0: continue
            M=np.linalg.matrix_power(Xs,a)@np.linalg.matrix_power(Z,b)
            D=B.conj().T@M@B
            if np.abs(D-np.diag(np.diag(D))).max()<1e-9: ops.append((a,b))
    # product structure under CRT j <-> (j%2, j%5): check rank-1 of each vector reshaped
    perm=[ (5*(j%2)+ (j%5)) for j in range(d)]
    r1=all(np.linalg.svd(np.array([v[[j for j in range(d) if j%2==s]] for s in (0,1)])[:, [ [j for j in range(d) if j%2==0].index(k) for k in [j for j in range(d) if j%2==0]]],compute_uv=False)[1]<1e-9 for v in X[bases[rep]]) if False else None
    # tensor test: v_{j} with j=CRT(s,t), s=j%2, t=j%5 ; matrix M[s,t]
    def prodtest(v):
        M=np.zeros((2,5),complex)
        for j in range(d): M[j%2,j%5]=v[j]
        return np.linalg.svd(M,compute_uv=False)[1]
    pt=max(prodtest(v) for v in X[bases[rep]])
    sym=sum(1 for i in bases[rep] if np.allclose(X[i],X[i][(-np.arange(d))%d]))
    print(f"basis orbit {o:2d} size {A['basis_orbit_sizes'][o]:3d}: Weyl ops diagonalised {ops[:6]}{'...' if len(ops)>6 else ''} (#{len(ops)}), product(CRT 2x5) {pt<1e-9}")
