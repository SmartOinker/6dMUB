"""Numerical test of Theorem "From a vector to a basis" and of the explicit four-basis sets, with an own implementation.

(a) Theorem (a),(b): for the product triples T0 and T1 and many fourth orthonormal bases G (5,000 Haar-random ones, plus
    local minimisations of the game loss from 20 random starts), check
        bias(G)  >= sqrt(gamma/18)          for every column of G separately and for the set,
        loss(G)  >= c gamma/72              with  loss = 1/2 + sqrt6/12 - score,  c = 3 sqrt6/(sqrt6+1)^2,
    with gamma the certified energy bounds 0.038499999998 (T0) and 0.023499999997 (T1).  Reports the smallest ratios.
(b) the stored explicit sets (bases_d6_delta.npy, bases_d6_P4.npy): replace each basis by its exact unitary polar factor
    (numpy SVD), recompute bias, game loss and score in float64, and check the structural statements of the report:
    delta-set: all six pairs attain the maximal deviation, no pair exactly unbiased; P4-set: one basis unbiased to the
    other three, the other three pairs biased, so no exactly mutually unbiased triple; score 0.7038884.
(c) the dimension-four control: psi = (1,1,i,-i)/2 is exactly uniform for ZZ, XX, YY and has energy 0.
Not a proof (random and local-search points, floating point).  Prints OK or raises.  About 20 s.
"""
import itertools, os
import numpy as np
from scipy.optimize import minimize
from scipy.linalg import expm
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
rng = np.random.default_rng(1124)
s6 = np.sqrt(6.0); c = 3*s6/(s6 + 1)**2; mu = 0.5 + s6/12

w = np.exp(2j*np.pi/3); H2 = np.array([[1, 1], [1, -1]])/np.sqrt(2)
F3 = np.array([[w**((j*k) % 3) for k in range(3)] for j in range(3)])/np.sqrt(3)
D = np.diag([1, w, w]); D2 = np.diag([1, w*w, w*w])
A = [np.eye(2), H2, np.diag([1, 1j]) @ H2]; B = [np.eye(3), F3, D @ F3, D2 @ F3]
T0 = [np.kron(A[r], B[r]) for r in range(3)]
T1 = [T0[0], T0[1], np.array([np.kron(A[2][:, 0], B[2][:, k]) for k in range(3)] + [np.kron(A[2][:, 1], B[3][:, k]) for k in range(3)]).T]

def probs(T, G): return np.array([np.abs(U.conj().T @ G)**2 for U in T])          # shape 3 x 6 x 6 (r, k, j)
def bias(T, G): return np.abs(probs(T, G) - 1/6).max()
def per_vector_bias(T, G): return np.abs(probs(T, G) - 1/6).max(axis=(0, 1))     # for each column j
def score(T, G):                                                                  # four-basis game score, six pairs
    bases = list(T) + [G]; tot = 0.0
    for a, b in itertools.combinations(range(4), 2): tot += np.abs(bases[a].conj().T @ bases[b]).sum()
    return 0.5 + tot/(6*72)
def loss(T, G): return mu - score(T, G)
def haar(): z = rng.normal(size=(6, 6)) + 1j*rng.normal(size=(6, 6)); q, r = np.linalg.qr(z); return q*(np.diag(r)/abs(np.diag(r)))
def unitary(x):
    X = (x[:36].reshape(6, 6) + 1j*x[36:].reshape(6, 6)); return expm(1j*(X + X.conj().T)/2)

for name, T, g in (("T0", T0, 0.038499999998), ("T1", T1, 0.023499999997)):
    b_lo, l_lo = np.sqrt(g/18), c*g/72
    assert abs(sum(np.abs(T[a].conj().T @ T[b]).sum() for a, b in itertools.combinations(range(3), 2)) - 3*6*s6) < 1e-10      # MU triple: pair sum 6 sqrt6
    rb = rl = 1e9; rv = 1e9
    for _ in range(5000):
        G = haar(); rb = min(rb, bias(T, G)/b_lo); rl = min(rl, loss(T, G)/l_lo); rv = min(rv, per_vector_bias(T, G).min()/b_lo)
    best_l = 1e9
    for _ in range(20):
        r1 = minimize(lambda x: loss(T, unitary(x)), rng.normal(size=72)*0.5, method="BFGS", options={"maxiter": 400}); best_l = min(best_l, loss(T, unitary(r1.x)))
    print("(a) %s: gamma = %.12f: smallest bias/(sqrt(g/18)) over 5,000 random bases = %.3f, per-vector = %.3f; smallest loss/(c g/72) = %.2f; "
          "best loss found by local search %.3e (bound %.3e)" % (name, g, rb, rv, rl, best_l, l_lo))
    assert rb >= 1 and rv >= 1 and rl >= 1 and best_l >= l_lo

def polar(M): u, s, vh = np.linalg.svd(M); return u @ vh
for fn in ("bases_d6_delta.npy", "bases_d6_P4.npy"):
    S = [polar(M) for M in np.load(os.path.join(ROOT, "near_misses/repo/results/visibility", fn))]
    dev = {(a, b): np.abs(np.abs(S[a].conj().T @ S[b])**2 - 1/6) for a, b in itertools.combinations(range(4), 2)}
    pm = {k: v.max() for k, v in dev.items()}; bs = max(pm.values()); tot = sum(np.abs(S[a].conj().T @ S[b]).sum() for a, b in itertools.combinations(range(4), 2))
    sc = 0.5 + tot/(6*72)
    print("(b) %s: bias %.9f, score %.10f, game loss %.7e; per-pair maximal deviations %s" % (fn, bs, sc, mu - sc, ["%.6f" % v for v in pm.values()]))
    if "delta" in fn:
        assert abs(bs - 0.030223872) < 2e-9 and max(pm.values()) - min(pm.values()) < 1e-9 and min(pm.values()) > 0.03 and abs((mu - sc) - 6.180869e-4) < 2e-10
    else:
        unb = [k for k, v in pm.items() if v < 1e-6]; bia = [k for k, v in pm.items() if v > 1e-3]   # basis 0 is unbiased to the others only to about 4e-8 (numerical optimum)
        assert abs(bs - 0.040598665) < 2e-9 and abs(sc - 0.7038883627) < 2e-10 and abs((mu - sc) - 2.357825e-4) < 2e-10
        assert sorted(unb) == [(0, 1), (0, 2), (0, 3)] and len(bia) == 3          # one basis unbiased to the other three, no exactly MU triple
        for tri in itertools.combinations(range(4), 3): assert any(pm[p] > 1e-3 for p in itertools.combinations(tri, 2)), "contains an MU triple"
print("(b) delta set: all six pairs attain the maximal deviation, none exactly unbiased; P4 set: basis 0 unbiased to 1,2,3; pairs (1,2),(1,3),(2,3) biased; no MU triple inside")

psi = np.array([1, 1, 1j, -1j])/2; sx = np.array([[0, 1], [1, 0]]); sy = np.array([[0, -1j], [1j, 0]]); sz = np.diag([1, -1])
Eg = 0.0
for s in (sz, sx, sy):
    # setting s(x)s: product of the eigenbases of s on both qubits (common eigenbasis of s(x)1 and 1(x)s, non-degenerate)
    ev1, U1 = np.linalg.eigh(np.kron(s, np.eye(2)) + 2*np.kron(np.eye(2), s)); p = np.abs(U1.conj().T @ psi)**2
    Eg += ((p - 1/4)**2).sum(); assert np.abs(p - 1/4).max() < 1e-15
print("(c) d = 4 control: psi = (1,1,i,-i)/2 has outcome probabilities exactly 1/4 in the ZZ, XX, YY eigenbases (energy %.1e)" % Eg)
print("OK")
