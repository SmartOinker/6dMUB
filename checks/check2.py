"""(a) replicate the cube-rank enumeration counts; (b) bridge numerics: game deficit with product triple fixed."""
import itertools
import numpy as np
from scipy.optimize import minimize
from scipy.linalg import expm

w = np.exp(2j * np.pi / 3)

# ---------- (a) cube-rank enumeration ----------
vecs = []
for e in itertools.product(range(3), repeat=5):
    ex = (0,) + e
    if all(ex.count(c) == 2 for c in range(3)):
        vecs.append(ex)
print("dephased root vectors:", len(vecs))
V = np.array([[w ** c for c in ex] for ex in vecs])
G = np.abs(V.conj() @ V.T) < 1e-9
np.fill_diagonal(G, False)
n = len(vecs)


def cliques(size):
    out = []
    def rec(cur, cand):
        if len(cur) == size:
            out.append(tuple(cur)); return
        for i in cand:
            rec(cur + [i], [j for j in cand if j > i and G[i, j]])
    rec([], list(range(n)))
    return out


cl = {s: cliques(s) for s in range(6)}
print("clique counts sizes 0..5:", [len(cl[s]) for s in range(6)], " (claimed 1,30,135,120,60,12)")

ones = np.ones(6, dtype=complex)
r_idx = vecs.index((0, 0, 1, 1, 2, 2))


def nullity(X, Y):
    rows = [X[:, a].conj() * Y[:, b] for a in range(X.shape[1]) for b in range(Y.shape[1])]
    sv = np.linalg.svd(np.array(rows), compute_uv=False)
    rank = int((sv > 1e-9).sum())
    return 6 - rank


tab = {}
for k in (1, 2, 3):
    counts = {}
    if k == 1:
        Xs = [np.column_stack([ones])]
    elif k == 2:
        Xs = [np.column_stack([ones, V[r_idx]])]
    else:
        Xs = [np.column_stack([ones, V[r_idx], V[j]]) for j in range(n) if G[r_idx, j]]
    for X in Xs:
        for c in cl[5 - k]:
            Y = np.column_stack([ones] + [V[i] for i in c])
            nu = nullity(X, Y)
            counts[nu] = counts.get(nu, 0) + 1
    tab[k] = counts
    print("k =", k, "systems:", sum(counts.values()), "nullity histogram:", dict(sorted(counts.items())))
print("claimed: k=1: 60 (all nullity 1); k=2: 120 = 112 + 8; k=3: 1215 = 1160 + 54 + 1 (nullity 3)")

# ---------- (b) game deficit with the product triple fixed ----------
H2 = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
A = [np.eye(2), H2, np.diag([1, 1j]) @ H2]
F = np.array([[w ** (j * k) for k in range(3)] for j in range(3)]) / np.sqrt(3)
D = np.diag([1, w, w])
B = [np.eye(3), F, D @ F]
U = [np.kron(A[r], B[r]) for r in range(3)]
rng = np.random.default_rng(1)


def unitary(x):
    Z = (x[:36] + 1j * x[36:]).reshape(6, 6)
    K = Z - Z.conj().T
    return expm(K)


def stats(Gm):
    S = 0.0; Etot = 0.0; dev = 0.0
    for r in range(3):
        P = np.abs(U[r].conj().T @ Gm) ** 2
        S += np.sqrt(P).sum()
        Etot += ((P - 1 / 6) ** 2).sum()
        dev = max(dev, np.abs(P - 1 / 6).max())
    return S, Etot, dev


def negS(x):
    return -stats(unitary(x))[0]


def Etot(x):
    return stats(unitary(x))[1]


bestS, bestE = -1, 1e9
for it in range(60):
    x0 = rng.normal(size=72) * 0.7
    r1 = minimize(negS, x0, method="L-BFGS-B", options={"maxiter": 4000, "ftol": 1e-15, "gtol": 1e-10})
    if -r1.fun > bestS:
        bestS, bestSx = -r1.fun, r1.x
    r2 = minimize(Etot, x0, method="L-BFGS-B", options={"maxiter": 4000, "ftol": 1e-15, "gtol": 1e-10})
    if r2.fun < bestE:
        bestE, bestEx = r2.fun, r2.x

mu = 0.5 + 0.5 / np.sqrt(6)
sum_def = 3 * mu - (1.5 + bestS / 72)          # summed deficit of the three pairs (B_r, G)
print("\nbest fourth basis for the game, product triple fixed:")
print("  sum_r sum_ij |<u_ri,g_j>| =", bestS, " (MU value 18*sqrt6 =", 18 * np.sqrt(6), ")")
print("  P_4 deficit (average over 6 pairs) =", sum_def / 6, "  proved lower bound 1/41472 =", 1 / 41472)
print("  with conjectured Emin:", 6 * (4 - np.sqrt(6)) / 40 / 8 / 72 / 6)
S, Et, dv = stats(unitary(bestSx))
print("  at that basis: sum_j E(g_j) =", Et, " max dev =", dv)
print("min over fourth bases of sum_j E(g_j):", bestE, "  6*Emin =", 6 * (4 - np.sqrt(6)) / 40, "  6/72 =", 6 / 72)
S, Et, dv = stats(unitary(bestEx))
print("  at that basis: game deficit avg =", (3 * mu - (1.5 + S / 72)) / 6, " max dev =", dv)

# check inequality sum_i sqrt(p_i) <= sqrt6 - (1/8) sum (p_i-1/6)^2 on random distributions
worst = 1e9
for _ in range(200000):
    p = rng.dirichlet(np.ones(6) * rng.choice([0.2, 1, 5, 50]))
    worst = min(worst, np.sqrt(6) - ((p - 1 / 6) ** 2).sum() / 8 - np.sqrt(p).sum())
print("min slack of sqrt inequality over random distributions (should be >= 0):", worst)
