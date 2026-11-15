#!/usr/bin/env python3
"""Independent quick numerical checks of the seed-geometry claims of the structure paper (supplementary/structure_paper.pdf, Section 13).
Written from the paper's displayed formulas only; imports nothing from other code.
Conjugation bars were lost in the text extraction; where a formula is ambiguous the
variant is selected by the physical requirement stated in the paper and this is printed."""
import itertools
import numpy as np
rng = np.random.default_rng(20261115)
w = np.exp(2j*np.pi/3)
def is_hadamard_res(H):
    n = H.shape[0]
    return max(np.abs(np.abs(H)-1).max(), np.abs(H.conj().T@H - n*np.eye(n)).max())
def report(name, npts, res, tol):
    print(f"[{'PASS' if res < tol else 'FAIL'}] {name}: {npts} points, max residual {res:.3e} (tol {tol:g})")

print("== Check 1a: indirect product point p of Sec 13.5 (explicit A,B; C=A*B/sqrt6) ==")
A = np.zeros((6,6),complex); B = np.zeros((6,6),complex)
for j,a,k,b in itertools.product(range(3),range(2),range(3),range(2)):
    A[2*j+a,2*k+b] = w**(j*k)*(-1)**(a*b)
    B[2*j+a,2*k+b] = w**((1+b)*j*j+j*k)*(1j)**a*(-1)**(a*b)
C = A.conj().T@B/np.sqrt(6)
r = max(is_hadamard_res(A), is_hadamard_res(B), is_hadamard_res(C))
report("A,B,C phase Hadamard => {I, A/sqrt6, B/sqrt6} pairwise MUB (index order 2j+a)", 1, r, 1e-12)
def cuberes(H): H3=H**3; return np.abs(H3@H3.conj().T@H3-18*H3).max()
print(f"   cube residuals R(A),R(B),R(C) at p: {cuberes(A):.2e} {cuberes(B):.2e} {cuberes(C):.2e} (paper: all three vanish)")
report("all three cube residuals vanish at p", 1, max(cuberes(A),cuberes(B),cuberes(C)), 1e-9)

print("== Check 1b/2: seed third transition from the S-surface parametrization (Sec 13.6-13.7) ==")
def gam(f): return sum(f[(r+1)%3]*np.conj(f[r]) for r in range(3))
def sample_seed():
    while True:
        u = np.exp(1j*rng.uniform(0,2*np.pi,3)); u[0]=1
        g = gam(u); t = -g
        z = np.roots([1,-t,np.conj(t),-1])
        if np.abs(np.abs(z)-1).max() < 1e-9:   # -gamma(u) in deltoid: v exists
            v = np.array([1, z[0], z[0]*z[1]])
            v = v/np.abs(v)
            return u, v, abs(g)**2
def buildC(u, v, cu, cv):
    # C_{lb,md} = [[u_r, i v_{-r}],[i v_r, u_{-r}]]_{bd}, r=l+m; cu/cv choose conj on the
    # entries i v_{-r} and u_{-r} (bars lost in extraction; reading with bars: [[u_r, i conj(v_-r)],[i v_r, conj(u_-r)]]); chosen by unitarity of C/sqrt6.
    C = np.zeros((6,6),complex)
    for l,m in itertools.product(range(3),range(3)):
        r=(l+m)%3; s=(-r)%3
        C[2*l,2*m]=u[r]; C[2*l,2*m+1]=1j*(np.conj(v[s]) if cv else v[s])
        C[2*l+1,2*m]=1j*v[r]; C[2*l+1,2*m+1]=(np.conj(u[s]) if cu else u[s])
    return C
pts=[sample_seed() for _ in range(200)]
good=[]
for cu,cv in itertools.product([0,1],[0,1]):
    rr=max(is_hadamard_res(buildC(u,v,cu,cv)) for u,v,_ in pts[:20])
    print(f"   conj variant (u_-r conj={cu}, v_-r conj={cv}): Hadamard residual {rr:.2e}")
    if rr<1e-9: good.append((cu,cv))
if not good:
    print("[NOT CHECKED] no conjugation variant of the extracted block formula is Hadamard; spectrum check skipped")
else:
    cu,cv=good[0]
    print(f"   using variant {good[0]} (unique: {len(good)==1})")
    hr=0; er=0; dr=0; qs=[]
    for u,v,q in pts:
        Cm=buildC(u,v,cu,cv); hr=max(hr,is_hadamard_res(Cm))
        ev=np.sort(np.linalg.eigvalsh((Cm**3).conj().T@(Cm**3)))
        tgt=np.sort([18-12*q]*2+[6*q]*4); er=max(er,np.abs(ev-tgt).max())
        N=Cm**3/(6*np.sqrt(6)); dC=1/72-np.trace(np.linalg.matrix_power(N.conj().T@N,2)).real
        R=(Cm**3)@(Cm**3).conj().T@(Cm**3)-18*Cm**3
        dr=max(dr,abs(dC-q*(2-q)/108),abs(np.linalg.norm(R)**2-2592*q*(3-q*q))/5184)
        qs.append(q)
    report("seed third transition C is a phase Hadamard (unbiased to standard basis)",len(pts),hr,1e-9)
    report("spec (C^3)*(C^3) = {18-12q (x2), 6q (x4)}, q=|gamma(u)|^2",len(pts),er,1e-8)
    report("deficit q(2-q)/108 and ||R_C||^2 = 2592 q(3-q^2) (eq. 50; rel. err)",len(pts),dr,1e-9)
    qs=np.array(qs); qstar=6*np.sqrt(3)-9
    print(f"   q range sampled [{qs.min():.4f},{qs.max():.4f}], paper bound q <= q* = {qstar:.6f}: {'PASS' if qs.max()<=qstar+1e-12 else 'FAIL'}")
print("   NOTE: A and B of the seed (Sec 13.2) were NOT built: their extracted formulas are garbled;")
print("   C was built from the Sec 13.6 block formula; full three-basis unbiasedness of the seed is not checked.")

print("== Check 3: physical Jacobian rank 53 ==")
print("[NOT CHECKED] requires the 55-variable dephased gauge chart and the seed A,B (garbled in extraction); not faithfully implementable in budget.")

print("== Check 4: Theorem 12.3, rho^2-rho^3 >= rho^2/144 and 1-tr rho^3 > 1/144 ==")
H2=np.array([[1,1],[1,-1]]); F=np.array([[w**(j*k) for k in range(3)] for j in range(3)])
bases=None
for D in [np.diag([1,w,w]), np.diag([1,w,np.conj(w)])]:
    U=[np.eye(6), np.kron(H2,F)/np.sqrt(6), np.kron(np.diag([1,1j])@H2, D@F)/np.sqrt(6)]
    mr=max(np.abs(np.abs(U[a].conj().T@U[b])**2-1/6).max() for a,b in [(0,1),(0,2),(1,2)])
    if mr<1e-12: bases=U; print(f"   canonical triple I, H2(x)F, diag(1,i)H2(x)DF with D=diag{np.round(np.diag(D),3).tolist()}: MUB residual {mr:.1e}"); break
if bases is None:
    print("[NOT CHECKED] canonical triple as extracted is not MUB")
else:
    P=[np.outer(U[:,k],U[:,k].conj()) for U in bases for k in range(6)]
    # real basis of traceless Hermitian 6x6
    herm=[]
    for i in range(6):
        for j in range(i,6):
            E=np.zeros((6,6),complex)
            if i==j: E[i,i]=1; herm.append(E)
            else:
                E[i,j]=E[j,i]=1; herm.append(E.copy()); E=np.zeros((6,6),complex); E[i,j]=-1j; E[j,i]=1j; herm.append(E)
    M=np.array([[np.trace(Pk@Hb).real for Hb in herm] for Pk in P])  # 18 x 36
    _,s,Vt=np.linalg.svd(M); rank=(s>1e-10).sum(); K=Vt[rank:]  # null space: tr(P X)=0 for all P
    print(f"   affine solution space dimension {K.shape[0]} (tr(P rho)=1/6 for all 18 outcomes; positivity NOT imposed)")
    worst=np.inf; worst_tr=np.inf; npts=20000; minev=np.inf
    for _ in range(npts):
        c=K.T@rng.normal(size=K.shape[0]); X=sum(ci*Hb for ci,Hb in zip(c,herm))
        X=X*np.sqrt((1-1/6)/np.trace(X@X).real); rho=np.eye(6)/6+X
        Q=rho@rho-rho@rho@rho-rho@rho/144
        ev=np.linalg.eigvalsh((Q+Q.conj().T)/2); worst=min(worst,ev.min())
        worst_tr=min(worst_tr,1-np.trace(rho@rho@rho).real-1/144); minev=min(minev,np.linalg.eigvalsh(rho).min())
    print(f"   {npts} random admissible rho (tr rho^2=1); most negative eigenvalue of rho rho^... min lambda(rho) seen {minev:.3f} (non-states included)")
    report("lambda_min(rho^2 - rho^3 - rho^2/144) >= 0", npts, max(0,-worst), 1e-10)
    print(f"   smallest lambda_min observed {worst:.3e}; smallest 1 - tr rho^3 - 1/144 observed {worst_tr:.3e}")
    report("1 - tr rho^3 > 1/144", npts, 0 if worst_tr>0 else -worst_tr, 1e-15)
