"""Builder (NOT the check) for quartic_L_moments.json: constructs an exact Q(sqrt3)-valued degree-four pseudomoment
functional L for the canonical product triple, to be verified independently by check_quartic_sos.py.

Method.  (1) A floating-point SDP (cvxpy/Clarabel) finds a real moment vector y (1365 moments of homogeneous quartics in
12 variables) with M(y) >= 0, M(y) c_l = 0 for the 18 deviation quadratics, L(N^2) = 1, and maximal minimum eigenvalue
(~2.5e-3) on the 63-dimensional complement of span(c_l).  (2) A set S of 320 'free' moments is rounded to rationals
(denominator 10^9); the other 1045 moments are solved EXACTLY over Q(sqrt3) from the linear system (the doubled rational
system [[A, 3B],[B, A]] with flint) so that every linear constraint holds exactly.  Rounding perturbs M by ~1e-9 while the
numerical eigenvalue margin is ~2.5e-3, so strict positivity on the complement survives; positivity is then verified exactly
by check_quartic_sos.py, not assumed.  Output: quartic_L_moments.json.  Runtime a few minutes (not part of the 3-minute checks)."""
import json, os, time, itertools
from fractions import Fraction as Fr
import numpy as np, scipy.sparse as sp, scipy.linalg as sl, cvxpy as cp
from flint import fmpq_mat, fmpq
from check_quartic_sos import QS, exact_quadratics, hankel_index, mons2, mons4, i4, HERE

t0 = time.time()
C = exact_quadratics()
Cf = np.array([[float(c.a) + float(c.b) * np.sqrt(3) for c in row] for row in C])
idx = np.array(hankel_index())
rows, cols, rr = [], [], 0
eq_rows = []   # (row id, list of (col, QS))
for l in range(18):
    for a in range(78):
        ent = {}
        for b in range(78):
            if not C[l][b].iszero():
                j = int(idx[a, b]); ent[j] = ent.get(j, QS()) + C[l][b]
        eq_rows.append(ent)
Cc = np.zeros((1404, 1365))
for i, ent in enumerate(eq_rows):
    for j, v in ent.items():
        Cc[i, j] = float(v.a) + float(v.b) * np.sqrt(3)
nv = np.zeros(1365)
for i in range(12):
    for j in range(12):
        nv[i4[tuple(sorted((i, i, j, j)))]] += 1
# --- (1) numerical interior point
u_, s_, vt = np.linalg.svd(Cf)
Qb = vt[15:].T
Uc, Sc, Vc = np.linalg.svd(Cc)
rk = int((Sc > 1e-9 * Sc[0]).sum())
K = Vc[rk:].T
g = K.T @ nv
yp = K @ g / (g @ g)
z = cp.Variable(K.shape[1]); t = cp.Variable()
Mrows = sp.csr_matrix((np.ones(78 * 78), (np.arange(78 * 78), idx.ravel())), shape=(78 * 78, 1365))
Mq = Qb.T @ cp.reshape(Mrows @ (yp + K @ z), (78, 78), order='C') @ Qb
cp.Problem(cp.Maximize(t), [(Mq + Mq.T) / 2 - t * np.eye(63) >> 0, cp.norm(z) <= 1e3]).solve(solver='CLARABEL')
ys = yp + K @ z.value
ys = ys / (nv @ ys)
ev = np.linalg.eigvalsh(ys[idx])
print(f"numerical SDP done: 63 largest-gap eigenvalues min {ev[15]:.4e}; rank of constraints {rk}; {time.time() - t0:.0f} s")
# --- (2) pivot / free split
A_full = np.vstack([Cc, nv])
_, _, piv = sl.qr(A_full, pivoting=True, mode='economic')
r = rk + 1 if False else int((np.linalg.svd(A_full, compute_uv=False) > 1e-9 * Sc[0]).sum())
P = np.sort(piv[:r]); S = np.sort(piv[r:])
_, _, rp = sl.qr(A_full[:, P].T, pivoting=True, mode='economic')
Rr = np.sort(rp[:r])
print("pivot columns", len(P), "free", len(S), "rows chosen", len(Rr))
DEN = 10 ** 9
yS = {int(j): Fr(int(round(ys[j] * DEN)), DEN) for j in S}
nrow = len(Rr)
# build doubled system
Aq = fmpq_mat(2 * nrow, 2 * nrow)
rhs = fmpq_mat(2 * nrow, 1)
pos = {int(j): k for k, j in enumerate(P)}
for k, i in enumerate(Rr):
    if i < 1404:
        ent = eq_rows[i]
        rhs_a, rhs_b = Fr(0), Fr(0)
    else:
        ent = {int(j): QS(int(nv[j]), 0) for j in np.nonzero(nv)[0]}
        rhs_a, rhs_b = Fr(1), Fr(0)
    for j, v in ent.items():
        if j in pos:
            c = pos[j]
            # (a + b s)(x0 + s x1) = (a x0 + 3 b x1) + s (b x0 + a x1)
            Aq[k, c] = fmpq(v.a.numerator, v.a.denominator); Aq[k, nrow + c] = fmpq(3 * v.b.numerator, v.b.denominator)
            Aq[nrow + k, c] = fmpq(v.b.numerator, v.b.denominator); Aq[nrow + k, nrow + c] = fmpq(v.a.numerator, v.a.denominator)
        else:
            rhs_a -= v.a * yS[j]; rhs_b -= v.b * yS[j]
    rhs[k, 0] = fmpq(rhs_a.numerator, rhs_a.denominator)
    rhs[nrow + k, 0] = fmpq(rhs_b.numerator, rhs_b.denominator)
print(f"solving exact {2 * nrow}x{2 * nrow} rational system ... ({time.time() - t0:.0f} s)", flush=True)
X = Aq.solve(rhs)
print(f"solved ({time.time() - t0:.0f} s)")
moments = [None] * 1365
for j in S:
    moments[int(j)] = [str(yS[int(j)]), "0"]
for c, j in enumerate(P):
    x0, x1 = X[c, 0], X[nrow + c, 0]
    moments[int(j)] = [f"{int(x0.p)}/{int(x0.q)}", f"{int(x1.p)}/{int(x1.q)}"]
err = max(abs(float(Fr(m[0])) + float(Fr(m[1])) * np.sqrt(3) - ys[j]) for j, m in enumerate(moments))
print("max deviation of exact moments from the numerical interior point:", err)
json.dump(dict(description="Exact Q(sqrt3) degree-four pseudomoment functional; each moment [a,b] means a + b*sqrt3",
               monomial_order='combinations_with_replacement(range(12),4)', moments=moments),
          open(os.path.join(HERE, 'quartic_L_moments.json'), 'w'))
print(f"written quartic_L_moments.json ({time.time() - t0:.0f} s)")
