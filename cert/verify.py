"""Rigorous check (Arb ball arithmetic via python-flint) that for the canonical qubit-qutrit product
MUB triple U_r = A_r (x) B_r,
        E(psi) = sum_{r,j} ( |<u_rj, psi>|^2 - 1/6 )^2  >=  gamma0 - S        for every unit psi in C^6,
where S (printed) is a rigorous bound on the certificate's coefficient residual.

Proof scheme.  x in R^12, psi = x[:6] + i x[6:], N = |x|^2, z = vector of the 364 cubic monomials.
  (1) Q := Q.npy, a float64 matrix read as exact dyadic rationals.
  (2) Q - tau*I - L L^T = R with ||R||_F <= tau  (L: floating Cholesky factor, R evaluated in balls)
        =>  Q = L L^T + (tau*I + R) is positive semidefinite.
  (3) r(x) := N*E_hom(x) - gamma0*N^3 - z^T Q z, coefficients enclosed in balls;  S := sum_m |r_m|.
      Every degree-6 monomial satisfies |x^m| <= N^3, so |r(x)| <= S*N^3.
  Hence N*E_hom >= (gamma0 - S) N^3, i.e. E >= gamma0 - S on N = 1.
Trusted: python-flint/Arb, numpy only for file loading and the (unverified, then checked) Cholesky factor."""
import sys
import numpy as np
from flint import arb, acb, arb_mat, ctx
from common import n, monos, mult3
ctx.prec = 160
gamma0 = sys.argv[1]
Qf = np.load(sys.argv[2]); triple = sys.argv[3] if len(sys.argv) > 3 else "T0"
assert Qf.dtype == np.float64 and Qf.shape == (364, 364) and np.array_equal(Qf, Qf.T)
g0 = arb(gamma0)                                   # decimal string -> ball containing it

# ---- the 18 projectors, in balls
s2, s3 = arb(2).sqrt(), arb(3).sqrt()
I = acb(0, 1); w = acb(-1, 0) / 2 + I * s3 / 2    # exp(2 pi i/3)
one = acb(1)
def kron(a, b):
    return [[a[i][k] * b[j][l] for k in range(len(a[0])) for l in range(len(b[0]))] for i in range(len(a)) for j in range(len(b))]
H2 = [[one / s2, one / s2], [one / s2, -one / s2]]
A = [[[one, acb(0)], [acb(0), one]], H2, [[H2[0][0], H2[0][1]], [I * H2[1][0], I * H2[1][1]]]]
F = [[w ** ((j * k) % 3) / s3 for k in range(3)] for j in range(3)]
d = [one, w, w]
B = [[[one if i == j else acb(0) for j in range(3)] for i in range(3)], F, [[d[j] * F[j][k] for k in range(3)] for j in range(3)]]
d2 = [one, w * w, w * w]
B.append([[d2[j] * F[j][k] for k in range(3)] for j in range(3)])     # fourth qutrit MUB D^2 F
Us = [kron(A[r], B[r]) for r in range(3)]
if triple == "T1":                                  # third basis: |0_y> (x) B2 , |1_y> (x) B3
    cols = [[A[2][a][0] * B[2][q][k] for a in range(2) for q in range(3)] for k in range(3)] + \
           [[A[2][a][1] * B[3][q][k] for a in range(2) for q in range(3)] for k in range(3)]
    Us[2] = [[cols[c][i] for c in range(6)] for i in range(6)]
quads = []                                          # each: dict {(i,j) i<=j : arb coefficient}
for r in range(3):
    U = Us[r]
    # sanity: columns orthonormal
    for a in range(6):
        for b in range(6):
            ip = sum((U[i][a].conjugate() * U[i][b] for i in range(6)), acb(0))
            assert (ip - (1 if a == b else 0)).abs_upper() < 1e-40
    for j in range(6):
        u = [U[i][j] for i in range(6)]
        q = {}
        for a in range(6):
            for b in range(6):
                P = u[a] * u[b].conjugate()
                # psi^dag P psi with psi_a = x_a + i x_{a+6}: real symmetric form [[Re P, -Im P],[Im P, Re P]]
                for (i, jj, val) in ((a, b, P.real), (a + 6, b + 6, P.real), (a, b + 6, -P.imag), (a + 6, b, P.imag)):
                    key = (min(i, jj), max(i, jj)); q[key] = q.get(key, arb(0)) + val
        for i in range(n):
            q[(i, i)] = q.get((i, i), arb(0)) - arb(1) / 6
        quads.append(q)
# mutual unbiasedness of the triple (sanity)
for r in range(3):
    for s in range(r + 1, 3):
        for a in range(6):
            for b in range(6):
                ip = sum((Us[r][i][a].conjugate() * Us[s][i][b] for i in range(6)), acb(0))
                assert ((ip.real ** 2 + ip.imag ** 2) - arb(1) / 6).abs_upper() < 1e-40

def mono2(i, j):
    e = [0] * n; e[i] += 1; e[j] += 1; return tuple(e)
def padd(e, f):
    return tuple(x + y for x, y in zip(e, f))
Eh = {}
for q in quads:
    items = [(mono2(i, j), c) for (i, j), c in q.items()]
    for e1, c1 in items:
        for e2, c2 in items:
            e = padd(e1, e2); Eh[e] = Eh.get(e, arb(0)) + c1 * c2
NE = {}
for e, c in Eh.items():
    for i in range(n):
        f = padd(e, mono2(i, i)); NE[f] = NE.get(f, arb(0)) + c
basis = monos(3); full = monos(6)
target = {m: NE.get(m, arb(0)) for m in full}
assert set(NE) <= set(full)
for a in basis:                                     # N^3 = sum_a mult3(a) x^(2a)
    m = tuple(2 * k for k in a); target[m] = target[m] - g0 * mult3(a)
# ---- (3) residual
gram = {m: arb(0) for m in full}
for a in range(364):
    ea = basis[a]; row = Qf[a]
    for b in range(364):
        m = padd(ea, basis[b]); gram[m] = gram[m] + arb(float(row[b]))
S = arb(0)
for m in full:
    S += abs(target[m] - gram[m])
S_up = float(S.upper())
print("(3) residual bound S <= %.3e" % S_up)
# ---- (2) positive semidefiniteness
tau = 1e-5
L = np.linalg.cholesky(Qf - tau * np.eye(364))
Qm = arb_mat(364, 364, [arb(float(v)) for v in Qf.ravel()])
Lm = arb_mat(364, 364, [arb(float(v)) for v in L.ravel()])
R = Qm - arb_mat(364, 364, [arb(tau) if i == j else arb(0) for i in range(364) for j in range(364)]) - Lm * Lm.transpose()
fro2 = arb(0)
for i in range(364):
    for j in range(364):
        fro2 += R[i, j] * R[i, j]
fro = float(fro2.sqrt().upper())
print("(2) ||Q - tau I - L L^T||_F <= %.3e  (tau = %.0e)" % (fro, tau))
assert fro < tau, "PSD check failed"
bound = arb(gamma0) - S
print("CERTIFIED (%s):  E(psi) >= %s - S  >  %.12f  for every unit psi" % (triple, gamma0, float(bound.lower())))
