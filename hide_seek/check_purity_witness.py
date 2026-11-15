"""Numerical check of the purity-witness proposition (report, Proposition "A purity witness").

For a mutually unbiased triple in C^6 and any state rho, with E(rho) = sum_{r,k} (tr(rho P_{r,k}) - 1/6)^2:
  (a) E(rho) <= tr(rho^2) - 1/6;
  (b) if E(psi) >= gamma for all pure psi, then lambda_max(rho) <= (sqrt(E(rho)) + sqrt(5/6)) / (sqrt(gamma) + sqrt(5/6)).
Tested on 100,000 random mixed states of random rank and spectrum for the canonical product triple, with the
certified gamma = 0.0384999.  A check, not a proof (the proof is in the report).
"""
import numpy as np
rng = np.random.default_rng(7)
w = np.exp(2j*np.pi/3); H = np.array([[1, 1], [1, -1]])/np.sqrt(2)
F = np.array([[1, 1, 1], [1, w, w*w], [1, w*w, w]])/np.sqrt(3); D = np.diag([1, w, w])
A = [np.eye(2), H, np.diag([1, 1j]) @ H]; B = [np.eye(3), F, D @ F]
U = [np.kron(A[r], B[r]) for r in range(3)]
for r in range(3):
    for s in range(r+1, 3):
        assert np.allclose(np.abs(U[r].conj().T @ U[s])**2, 1/6)          # mutually unbiased
g = 0.0384999; worst_a = -1.0; worst_b = -1.0
for _ in range(100000):
    k = int(rng.integers(1, 7))
    Z = rng.normal(size=(6, k)) + 1j*rng.normal(size=(6, k)); Q, _ = np.linalg.qr(Z)
    lam = rng.dirichlet(np.full(k, rng.choice([0.2, 1.0, 5.0])))
    rho = (Q*lam) @ Q.conj().T
    P = np.array([np.real(np.einsum('ik,ij,jk->k', Ur.conj(), rho, Ur)) for Ur in U])
    E = float(((P - 1/6)**2).sum()); pur = float(np.real(np.trace(rho @ rho)))
    worst_a = max(worst_a, E - (pur - 1/6))
    worst_b = max(worst_b, lam.max() - (np.sqrt(E) + np.sqrt(5/6))/(np.sqrt(g) + np.sqrt(5/6)))
print("(a) max of E(rho) - (tr rho^2 - 1/6) over 100,000 states:", worst_a)
print("(b) max of lambda_max - bound over 100,000 states:", worst_b)
print("bound at E = 0:", np.sqrt(5/6)/(np.sqrt(g) + np.sqrt(5/6)))
assert worst_a <= 1e-12 and worst_b <= 1e-12
print("OK")
