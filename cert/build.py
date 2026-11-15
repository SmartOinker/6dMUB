"""Find a numerical Gram matrix Q (364x364) with  z3(x)^T Q z3(x) ~= N*E_hom - gamma0*N^3  and Q >> 0.
Not part of the proof: the output Q.npy is checked independently by verify.py."""
import sys, time, itertools
import numpy as np, scipy.sparse as sp, cvxpy as cp
from common import n, monos, mult3
gamma0 = float(sys.argv[1]); eps = float(sys.argv[2]); triple = sys.argv[3] if len(sys.argv) > 3 else "T0"
w = np.exp(2j*np.pi/3)
H2 = np.array([[1,1],[1,-1]])/np.sqrt(2)
A = [np.eye(2), H2, np.diag([1,1j])@H2]
F = np.array([[w**(j*k) for k in range(3)] for j in range(3)])/np.sqrt(3)
D = np.diag([1,w,w]); B = [np.eye(3), F, D@F, D@D@F]
Us = [np.kron(A[r], B[r]) for r in range(3)]
if triple == "T1":   # third basis: |0_y> (x) B2 , |1_y> (x) B3
    Us[2] = np.column_stack([np.kron(A[2][:,0], B[2][:,k]) for k in range(3)] + [np.kron(A[2][:,1], B[3][:,k]) for k in range(3)])
Qs = []
for r in range(3):
    U = Us[r]
    for j in range(6):
        P = np.outer(U[:,j], U[:,j].conj())
        R = np.block([[P.real, -P.imag],[P.imag, P.real]])
        Qs.append((R+R.T)/2 - np.eye(12)/6)
def pq(Q):
    p = {}
    for i in range(n):
        for j in range(n):
            if abs(Q[i,j]) > 1e-15:
                e = [0]*n; e[i]+=1; e[j]+=1; p[tuple(e)] = p.get(tuple(e),0)+Q[i,j]
    return p
def pmul(p,q):
    o = {}
    for a,ca in p.items():
        for b,cb in q.items():
            e = tuple(x+y for x,y in zip(a,b)); o[e] = o.get(e,0)+ca*cb
    return o
Np = pq(np.eye(n)); Eh = {}
for Q in Qs:
    q = pq(Q)
    for e,c in pmul(q,q).items(): Eh[e] = Eh.get(e,0)+c
NE = pmul(Np, Eh); N3 = pmul(pmul(Np,Np),Np)
basis = monos(3); full = monos(6); idx = {m:i for i,m in enumerate(full)}; m = len(basis)
grp = np.empty((m,m), dtype=int)
for a in range(m):
    for b in range(m):
        grp[a,b] = idx[tuple(x+y for x,y in zip(basis[a],basis[b]))]
Amap = sp.csr_matrix((np.ones(m*m), (np.arange(m*m), grp.ravel())), shape=(m*m, len(full)))
def vec(p):
    v = np.zeros(len(full))
    for e,c in p.items(): v[idx[e]] += c
    return v
cNE, cN3 = vec(NE), vec(N3)
y = cp.Variable(len(full))
M = cp.reshape(Amap @ y, (m,m), order="C")
cons = [M >> 0, cN3 @ y == 1]
prob = cp.Problem(cp.Minimize(cNE @ y), cons)
t0 = time.time()
prob.solve(solver="SCS", eps=eps, max_iters=2000000, acceleration_lookback=20)
print("status", prob.status, "relaxation value", prob.value, "time %.0fs" % (time.time()-t0), flush=True)
Z = cons[0].dual_value; Z = (Z+Z.T)/2
def gram_coefs(Q):
    return np.bincount(grp.ravel(), weights=Q.ravel(), minlength=len(full))
best = None
for g in (prob.value, float(cons[1].dual_value), -float(cons[1].dual_value)):
    res = np.abs(gram_coefs(Z) - (cNE - g*cN3)).max()
    print("  candidate gamma* = %.8f  max coefficient residual %.2e" % (g, res))
    if best is None or res < best[1]: best = (g, res)
gstar = best[0]
print("gamma* used:", gstar, " min eig of raw dual:", np.linalg.eigvalsh(Z).min())
Q0 = Z + (gstar - gamma0) * np.diag([mult3(a) for a in basis])
target = cNE - gamma0*cN3
cnt = np.bincount(grp.ravel(), minlength=len(full))
for _ in range(3):
    r = target - gram_coefs(Q0)
    Q0 = Q0 + (r/cnt)[grp]
    Q0 = (Q0+Q0.T)/2
print("after projection: max residual %.2e, min eig %.6f" % (np.abs(target-gram_coefs(Q0)).max(), np.linalg.eigvalsh(Q0).min()))
np.save("Q_%s_gamma%s.npy" % (triple, sys.argv[1]), Q0)
