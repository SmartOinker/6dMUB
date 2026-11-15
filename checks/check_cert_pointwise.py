"""Second, independent numerical check of the stored degree-six energy certificates (NOT a proof, a cross-check).

The interval checker cert/verify.py (and d6_fourier/sos_general.py) proves
    N(x) E_hom(x) - gamma0 N(x)^3 = z(x)^T Q z(x) + r(x),   sum of |coefficients of r| = S <= about 3e-12,
by expanding polynomials coefficient by coefficient in ball arithmetic.  This script re-tests the same stored Q
matrices with a completely different code path: the 18 vectors are rebuilt with numpy (complex128, Kronecker products),
and the identity is evaluated at random points x in R^12 by direct complex arithmetic, without any monomial expansion.
If the checker's monomial bookkeeping were wrong, the pointwise residual would not be of the size of S.
Also reports the smallest eigenvalue of every Q (numpy eigvalsh).  Independent of the Arb code except for the
monomial ordering of z (itertools.combinations_with_replacement, the file format of the stored Q).

What it does NOT show: rigorous positive semidefiniteness (floating eigenvalues) nor a bound for all x
(random points).  Prints OK or raises.  Run from anywhere:  python3 checks/check_cert_pointwise.py   (about 10 s)
"""
import itertools, json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
rng = np.random.default_rng(20261115)
w = np.exp(2j*np.pi/3)
H2 = np.array([[1, 1], [1, -1]])/np.sqrt(2)
F3 = np.array([[w**((j*k) % 3) for k in range(3)] for j in range(3)])/np.sqrt(3)
D = np.diag([1, w, w]); D2 = np.diag([1, w*w, w*w])
A = [np.eye(2), H2, np.diag([1, 1j]) @ H2]
B = [np.eye(3), F3, D @ F3, D2 @ F3]
T0 = [np.kron(A[r], B[r]) for r in range(3)]
# second product triple: third basis |0_y> (x) D F3 columns and |1_y> (x) D^2 F3 columns
cols = [np.kron(A[2][:, 0], B[2][:, k]) for k in range(3)] + [np.kron(A[2][:, 1], B[3][:, k]) for k in range(3)]
T1 = [T0[0], T0[1], np.array(cols).T]
for name, T in (("T0", T0), ("T1", T1)):
    for r in range(3):
        assert np.allclose(T[r].conj().T @ T[r], np.eye(6), atol=1e-13)
        for s in range(r + 1, 3):
            assert np.allclose(abs(T[r].conj().T @ T[s])**2, 1/6, atol=1e-13), (name, r, s)

idx = np.array(list(itertools.combinations_with_replacement(range(12), 3)))      # 364 cubic monomials, file order
assert len(idx) == 364

def residual(vectors, Q, gamma0, X):
    """r(x) = N E_hom - gamma0 N^3 - z^T Q z at the rows of X (shape m x 12), divided by N^3."""
    psi = X[:, :6] + 1j*X[:, 6:]; N = (X**2).sum(1)
    Ehom = np.zeros(len(X))
    for U in vectors:
        p = np.abs(psi @ U.conj())**2                      # |<u_k, psi>|^2, shape m x 6
        Ehom += ((p - N[:, None]/6)**2).sum(1)
    z = X[:, idx[:, 0]]*X[:, idx[:, 1]]*X[:, idx[:, 2]]
    zQz = ((z @ Q) * z).sum(1)
    return (N*Ehom - gamma0*N**3 - zQz)/N**3

def run(label, vectors, qfile, gamma0, bound):
    Q = np.load(qfile); assert Q.shape == (364, 364) and np.array_equal(Q, Q.T)
    X = rng.normal(size=(4000, 12)) * rng.choice([0.3, 1.0, 3.0], size=(4000, 1))
    X[:1000] /= np.linalg.norm(X[:1000], axis=1, keepdims=True)           # include unit vectors
    rr = np.abs(residual(vectors, Q, gamma0, X)).max()
    lam = np.linalg.eigvalsh(Q).min()
    print(f"{label}: max |r(x)|/N^3 over 4,000 points = {rr:.2e} (checker bound S <= {bound:.2e});  min eigenvalue of Q = {lam:.3e}")
    assert rr <= 2*bound + 1e-13, "pointwise residual larger than the interval residual bound"
    assert lam > 1e-6, "Q not positive definite in floating point"
    return rr

run("T0 (Q_T0_gamma0.0385)", T0, os.path.join(ROOT, "cert/Q_T0_gamma0.0385.npy"), 0.0385, 2.189e-12)
run("T1 (Q_T1_gamma0.0235)", T1, os.path.join(ROOT, "cert/Q_T1_gamma0.0235.npy"), 0.0235, 2.807e-12)

# the 16 triples containing {I, F_6}
F6 = np.exp(2j*np.pi*np.outer(np.arange(6), np.arange(6))/6)/np.sqrt(6)
Dd = json.load(open(os.path.join(ROOT, "d6_fourier/fourier6.json"))); V = np.load(os.path.join(ROOT, "d6_fourier/fourier6_vecs.npy"))
assert V.shape == (48, 6) and np.allclose(abs(V), 1, atol=1e-12)
gam = {0.0387628: "0.0385", 0.0238354: "0.0235", 0.0326759: "0.0324"}
worst = 0.0; counts = {}
for bi, o in enumerate(Dd["energy"]):
    g = gam[round(o["Emin"], 7)]; counts[g] = counts.get(g, 0) + 1
    Bm = V[list(o["basis"])].T/np.sqrt(6)
    for a, b in ((np.eye(6), F6), (np.eye(6), Bm), (F6, Bm)):
        assert np.allclose(abs(a.conj().T @ b)**2, 1/6, atol=1e-12), ("not MU", bi)
    worst = max(worst, run(f"Fourier-pair triple {bi:02d}", [np.eye(6), F6, Bm], os.path.join(ROOT, f"d6_fourier/Q_fourier6_triple{bi:02d}_gamma{g}.npy"), float(g), 5.8e-12))
print("Fourier-pair triples by certified level:", counts, "; worst pointwise residual", f"{worst:.2e}")
assert counts == {"0.0324": 12, "0.0235": 2, "0.0385": 2}
print("OK")
