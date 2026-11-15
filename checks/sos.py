"""Moment (dual SOS) relaxations for min E on the unit sphere, canonical product triple.
deg=4 : min L(E_hom)   s.t. L(N^2)=1, M_2(L) >= 0      (workstream B's Theorem 7.1 claims optimum 0)
deg=6 : min L(N*E_hom) s.t. L(N^3)=1, M_3(L) >= 0      (next level; untested in either report)
"""
import sys, itertools, time
import numpy as np
import scipy.sparse as sp
import cvxpy as cp

deg = int(sys.argv[1])
solver = sys.argv[2] if len(sys.argv) > 2 else "CLARABEL"
n = 12
w = np.exp(2j * np.pi / 3)
H2 = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
A = [np.eye(2), H2, np.diag([1, 1j]) @ H2]
F = np.array([[w ** (j * k) for k in range(3)] for j in range(3)]) / np.sqrt(3)
D = np.diag([1, w, w])
B = [np.eye(3), F, D @ F]
U = [np.kron(A[r], B[r]) for r in range(3)]

# real 12x12 symmetric matrices of the 18 deviation quadratics q_l = psi^dag P psi - N/6
Qs = []
for r in range(3):
    for j in range(6):
        u = U[r][:, j]
        P = np.outer(u, u.conj())
        R = np.block([[P.real, -P.imag], [P.imag, P.real]])
        Qs.append((R + R.T) / 2 - np.eye(12) / 6)


def poly_from_quadratic(Q):
    p = {}
    for i in range(n):
        for j in range(n):
            if abs(Q[i, j]) > 1e-15:
                e = [0] * n; e[i] += 1; e[j] += 1
                p[tuple(e)] = p.get(tuple(e), 0) + Q[i, j]
    return p


def pmul(p, q):
    out = {}
    for a, ca in p.items():
        for b, cb in q.items():
            e = tuple(x + y for x, y in zip(a, b))
            out[e] = out.get(e, 0) + ca * cb
    return out


def padd(p, q):
    out = dict(p)
    for a, c in q.items():
        out[a] = out.get(a, 0) + c
    return out


Npoly = poly_from_quadratic(np.eye(n))
Ehom = {}
for Q in Qs:
    ql = poly_from_quadratic(Q)
    Ehom = padd(Ehom, pmul(ql, ql))
N2 = pmul(Npoly, Npoly)
if deg == 4:
    obj_poly, norm_poly, half = Ehom, N2, 2
else:
    obj_poly, norm_poly, half = pmul(Npoly, Ehom), pmul(N2, Npoly), 3


def monos(d):
    out = []
    for c in itertools.combinations_with_replacement(range(n), d):
        e = [0] * n
        for i in c:
            e[i] += 1
        out.append(tuple(e))
    return out


basis = monos(half)
full = monos(2 * half)
idx = {m: i for i, m in enumerate(full)}
m = len(basis)
print(f"deg {deg}: moment matrix {m}x{m}, {len(full)} moment variables", flush=True)

rows, cols = [], []
for a in range(m):
    for b in range(m):
        e = tuple(x + y for x, y in zip(basis[a], basis[b]))
        rows.append(a * m + b); cols.append(idx[e])
Amap = sp.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(m * m, len(full)))


def vec(p):
    v = np.zeros(len(full))
    for e, c in p.items():
        v[idx[e]] += c
    return v


y = cp.Variable(len(full))
M = cp.reshape(Amap @ y, (m, m), order="C")
prob = cp.Problem(cp.Minimize(vec(obj_poly) @ y), [M >> 0, vec(norm_poly) @ y == 1])
t0 = time.time()
kw = dict(verbose=False)
if solver == "SCS":
    kw.update(eps=float(sys.argv[3]) if len(sys.argv) > 3 else 1e-5, max_iters=400000, verbose=True, acceleration_lookback=20)
prob.solve(solver=solver, **kw)
print(f"status {prob.status}; relaxation optimum = {prob.value:.10f}; time {time.time()-t0:.1f}s")
print("reference: 1/72 = %.6f, 18*(0.030224)^2 = %.6f, (4-sqrt6)/40 = %.10f" % (1 / 72, 18 * 0.030224 ** 2, (4 - np.sqrt(6)) / 40))
if deg == 4:
    Mv = (Amap @ y.value).reshape(m, m)
    ev = np.linalg.eigvalsh(Mv)
    print("moment matrix: min eig %.2e, numerical rank (>1e-7) %d (claimed rank 63 for their certificate)" % (ev.min(), (ev > 1e-7).sum()))
