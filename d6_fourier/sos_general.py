"""Degree-six sum-of-squares certificates  E(psi) >= gamma  for an arbitrary set of 18 unit vectors in C^6 (three bases).
build():  numerical Gram matrix (not part of the proof).   verify():  Arb ball arithmetic; the 18 vectors may be balls."""
import itertools, numpy as np, scipy.sparse as sp
from flint import arb, acb, arb_mat, ctx
from common import n, monos, mult3
basis = monos(3); full = monos(6); idx = {m: i for i, m in enumerate(full)}; m_ = len(basis)
grp = np.empty((m_, m_), dtype=int)
for a in range(m_):
    for b in range(m_):
        grp[a, b] = idx[tuple(x + y for x, y in zip(basis[a], basis[b]))]
cnt = np.bincount(grp.ravel(), minlength=len(full))

def build(vecs, gamma0, eps=1e-5):
    import cvxpy as cp
    Qs = []
    for u in vecs:
        P = np.outer(u, u.conj()); R = np.block([[P.real, -P.imag], [P.imag, P.real]]); Qs.append((R + R.T)/2 - np.eye(12)/6)
    def pq(Q):
        p = {}
        for i in range(n):
            for j in range(n):
                if abs(Q[i, j]) > 1e-15:
                    e = [0]*n; e[i] += 1; e[j] += 1; p[tuple(e)] = p.get(tuple(e), 0) + Q[i, j]
        return p
    def pmul(p, q):
        o = {}
        for a, ca in p.items():
            for b, cb in q.items():
                e = tuple(x + y for x, y in zip(a, b)); o[e] = o.get(e, 0) + ca*cb
        return o
    Np = pq(np.eye(n)); Eh = {}
    for Q in Qs:
        q = pq(Q)
        for e, c in pmul(q, q).items(): Eh[e] = Eh.get(e, 0) + c
    NE = pmul(Np, Eh); N3 = pmul(pmul(Np, Np), Np)
    def vec(p):
        v = np.zeros(len(full))
        for e, c in p.items(): v[idx[e]] += c
        return v
    cNE, cN3 = vec(NE), vec(N3)
    Amap = sp.csr_matrix((np.ones(m_*m_), (np.arange(m_*m_), grp.ravel())), shape=(m_*m_, len(full)))
    y = cp.Variable(len(full)); M = cp.reshape(Amap @ y, (m_, m_), order="C")
    cons = [M >> 0, cN3 @ y == 1]; prob = cp.Problem(cp.Minimize(cNE @ y), cons)
    prob.solve(solver="SCS", eps=eps, max_iters=2000000, acceleration_lookback=20)
    Z = cons[0].dual_value; Z = (Z + Z.T)/2; gstar = prob.value
    Q0 = Z + (gstar - gamma0)*np.diag([mult3(a) for a in basis]); target = cNE - gamma0*cN3
    for _ in range(3):
        r = target - np.bincount(grp.ravel(), weights=Q0.ravel(), minlength=len(full))
        Q0 = Q0 + (r/cnt)[grp]; Q0 = (Q0 + Q0.T)/2
    return Q0, float(gstar), float(np.linalg.eigvalsh(Q0).min())

def verify(vecs_acb, gamma0_str, Qf, tau=1e-5):
    """vecs_acb: 18 lists of 6 acb (balls allowed) enclosing unit vectors.  Returns a rigorous lower bound on min E."""
    ctx.prec = 160
    assert Qf.dtype == np.float64 and Qf.shape == (364, 364) and np.array_equal(Qf, Qf.T)
    def mono2(i, j):
        e = [0]*n; e[i] += 1; e[j] += 1; return tuple(e)
    def padd(e, f): return tuple(x + y for x, y in zip(e, f))
    Eh = {}
    for u in vecs_acb:
        q = {}
        for a in range(6):
            for b in range(6):
                P = u[a]*u[b].conjugate()
                for (i, jj, val) in ((a, b, P.real), (a+6, b+6, P.real), (a, b+6, -P.imag), (a+6, b, P.imag)):
                    key = (min(i, jj), max(i, jj)); q[key] = q.get(key, arb(0)) + val
        for i in range(n): q[(i, i)] = q.get((i, i), arb(0)) - arb(1)/6
        items = [(mono2(i, j), c) for (i, j), c in q.items()]
        for e1, c1 in items:
            for e2, c2 in items:
                e = padd(e1, e2); Eh[e] = Eh.get(e, arb(0)) + c1*c2
    NE = {}
    for e, c in Eh.items():
        for i in range(n):
            f = padd(e, mono2(i, i)); NE[f] = NE.get(f, arb(0)) + c
    target = {m: NE.get(m, arb(0)) for m in full}; g0 = arb(gamma0_str)
    for a in basis:
        mm = tuple(2*k for k in a); target[mm] = target[mm] - g0*mult3(a)
    gram = {m: arb(0) for m in full}
    for a in range(364):
        ea = basis[a]; row = Qf[a]
        for b in range(364):
            mm = padd(ea, basis[b]); gram[mm] = gram[mm] + arb(float(row[b]))
    S = arb(0)
    for m in full: S += abs(target[m] - gram[m])
    L = np.linalg.cholesky(Qf - tau*np.eye(364))
    Qm = arb_mat(364, 364, [arb(float(v)) for v in Qf.ravel()]); Lm = arb_mat(364, 364, [arb(float(v)) for v in L.ravel()])
    Rm = Qm - arb_mat(364, 364, [arb(tau) if i == j else arb(0) for i in range(364) for j in range(364)]) - Lm*Lm.transpose()
    fro2 = arb(0)
    for i in range(364):
        for j in range(364): fro2 += Rm[i, j]*Rm[i, j]
    fro = float(fro2.sqrt().upper()); assert fro < tau, "PSD check failed"
    return float((g0 - S).lower()), float(S.upper()), fro
