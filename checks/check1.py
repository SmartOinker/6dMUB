"""Independent checks of the canonical product-triple claims in xinrui.pdf."""
import numpy as np
from scipy.optimize import minimize

rng = np.random.default_rng(0)
w = np.exp(2j * np.pi / 3)
H2 = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
A = [np.eye(2), H2, np.diag([1, 1j]) @ H2]
F = np.array([[w ** (j * k) for k in range(3)] for j in range(3)]) / np.sqrt(3)
D = np.diag([1, w, w])
B = [np.eye(3), F, D @ F]
U = [np.kron(A[r], B[r]) for r in range(3)]

# mutual unbiasedness of the triple
for r in range(3):
    assert np.allclose(U[r].conj().T @ U[r], np.eye(6))
    for s in range(r + 1, 3):
        assert np.allclose(np.abs(U[r].conj().T @ U[s]) ** 2, 1 / 6)
print("triple is MU: ok")


def probs(psi):
    return np.array([np.abs(U[r].conj().T @ psi) ** 2 for r in range(3)])  # 3x6


def E(psi):
    return float(((probs(psi) - 1 / 6) ** 2).sum())


# ---- Lemma 3.1: E = s + |a|^2/6 + |t|^2/3
C = D @ D @ F
sig = [np.array([[1, 0], [0, -1]]), np.array([[0, 1], [1, 0]]), np.array([[0, -1j], [1j, 0]])]
X3 = np.roll(np.eye(3), 1, axis=0)  # |k> -> |k+1>
Z3 = np.diag([1, w, w ** 2])
maxerr = 0
for _ in range(2000):
    psi = rng.normal(size=6) + 1j * rng.normal(size=6)
    psi /= np.linalg.norm(psi)
    # coordinates in C basis: psi = sum_k v_k (x) C[:,k]
    M = psi.reshape(2, 3)  # M[a, q]
    V = M @ C.conj()  # V[a,k] = sum_q M[a,q] conj(C[q,k])
    v = [V[:, k] for k in range(3)]
    s = sum(abs(np.vdot(v[(k + 1) % 3], v[k])) ** 2 for k in range(3))
    # operators in C coordinates: act on coefficient vector c = vec(V) (a,k)
    c = V.reshape(6)
    a = np.array([np.vdot(c, np.kron(sig[r], np.eye(3)) @ c).real for r in range(3)])
    t = np.array([np.vdot(c, np.kron(sig[r], X3 @ np.linalg.matrix_power(Z3, r)) @ c) for r in range(3)])
    rhs = s + (a @ a) / 6 + (np.abs(t) ** 2).sum() / 3
    maxerr = max(maxerr, abs(E(psi) - rhs))
print("Lemma 3.1 max |E - (s+|a|^2/6+|t|^2/3)| over 2000 random states:", maxerr)


# ---- global minimum of E
def f(x):
    psi = x[:6] + 1j * x[6:]
    psi = psi / np.linalg.norm(psi)
    return E(psi)


best = []
for _ in range(400):
    res = minimize(f, rng.normal(size=12), method="BFGS", options={"gtol": 1e-12})
    best.append(res.fun)
best = np.array(best)
target = (4 - np.sqrt(6)) / 40
print("min E over 400 starts:", best.min(), " claimed (4-sqrt6)/40 =", target, " 1/72 =", 1 / 72)
print("fraction of starts reaching the min (1e-9):", np.mean(best < best.min() + 1e-9))
print("distinct local minima values:", np.unique(np.round(best, 7))[:8])

# ---- the explicit witness (eq. 20)
h = np.sqrt((3 + np.sqrt(3)) / 6)
l = np.sqrt((3 - np.sqrt(3)) / 6)
eta = (1 + 1j) / np.sqrt(2)
qm = np.array([l, eta * h])
qp = np.array([-h, eta * l])
u_ = np.sqrt(3) / 2
v_ = np.sqrt((11 - 4 * np.sqrt(6)) / 20)
x = ((u_ - v_) / 2) ** 2
y = ((u_ + v_) / 2) ** 2
z = (7 + 2 * np.sqrt(6)) / 20
W = C
psi_star = (np.sqrt(x) * np.exp(1j * np.pi / 3) * np.kron(qm, W[:, 0])
            + np.sqrt(y) * np.exp(2j * np.pi / 3) * np.kron(qm, W[:, 1])
            + np.sqrt(z) * np.kron(qp, W[:, 2]))
print("witness: x+y+z =", x + y + z, " norm =", np.linalg.norm(psi_star), " E =", E(psi_star), " diff from claim:", E(psi_star) - target)


# ---- minimax single-outcome deviation over all pure states (worst-case bias for one extra vector)
def minimax():
    bestv, bestpsi = 1, None
    for _ in range(300):
        x0 = rng.normal(size=12)
        for p in (4, 8, 16, 32, 64, 128):
            def g(xx):
                psi = xx[:6] + 1j * xx[6:]
                psi = psi / np.linalg.norm(psi)
                d = np.abs(probs(psi) - 1 / 6).ravel()
                m = d.max()
                return m * ((d / m) ** p).sum() ** (1 / p)
            x0 = minimize(g, x0, method="BFGS").x
        psi = x0[:6] + 1j * x0[6:]
        psi /= np.linalg.norm(psi)
        val = np.abs(probs(psi) - 1 / 6).max()
        if val < bestv:
            bestv, bestpsi = val, psi
    return bestv, bestpsi


bv, bp = minimax()
print("min over states of max_b |p_b - 1/6| (numerical upper bound):", bv, " proved lower bound 1/36 =", 1 / 36)
print("  E at that state:", E(bp))
print("  sqrt(Emin/18) =", np.sqrt(target / 18))
