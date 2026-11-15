"""Own-code check of the numerical energy minima on the two product triples and of the closed-form minimiser of the report.

(a) closed form of Section 6.1: psi_* = sqrt(x) e^{i pi/3} q_- (x) w_0 + sqrt(y) e^{2 i pi/3} q_- (x) w_1 + sqrt(z) q_+ (x) w_2
    with the constants printed in the report; checks x + y + z = 1, ||psi_*|| = 1, E(psi_*) = (4 - sqrt6)/40 (50 digits in mpmath
    and in float64) and the largest single-outcome deviation 0.0575.
(b) 60 random-start BFGS minimisations (own gradient-free-of-scipy-jac code: finite differences) of E on T0 and on T1: the smallest
    value is (4 - sqrt6)/40 = 0.0387627564 on T0 and 0.0238354 on T1, and the set of distinct local-minimum values is printed.
Numerical evidence, not a proof of the minimum.  Prints OK or raises.  About 15 s.
"""
import numpy as np, mpmath as mp
from scipy.optimize import minimize
rng = np.random.default_rng(77)
w = np.exp(2j*np.pi/3); H2 = np.array([[1, 1], [1, -1]])/np.sqrt(2)
F3 = np.array([[w**((j*k) % 3) for k in range(3)] for j in range(3)])/np.sqrt(3); D = np.diag([1, w, w]); D2 = np.diag([1, w*w, w*w])
A = [np.eye(2), H2, np.diag([1, 1j]) @ H2]; B = [np.eye(3), F3, D @ F3, D2 @ F3]
T0 = [np.kron(A[r], B[r]) for r in range(3)]
T1 = [T0[0], T0[1], np.array([np.kron(A[2][:, 0], B[2][:, k]) for k in range(3)] + [np.kron(A[2][:, 1], B[3][:, k]) for k in range(3)]).T]
def probs(T, psi): return np.concatenate([np.abs(U.conj().T @ psi)**2 for U in T])
def E(T, psi): return float(((probs(T, psi) - 1/6)**2).sum())

# (a) closed form, in mpmath
mp.mp.dps = 50; s2, s3, s6 = mp.sqrt(2), mp.sqrt(3), mp.sqrt(6); I = mp.mpc(0, 1); om = mp.e**(2*mp.pi*I/3)
h = mp.sqrt((3 + s3)/6); l = mp.sqrt((3 - s3)/6); eta = (1 + I)/s2
qm = [l, eta*h]; qp = [-h, eta*l]; u = s3/2; v = mp.sqrt((11 - 4*s6)/20); x = ((u - v)/2)**2; y = ((u + v)/2)**2; z = (7 + 2*s6)/20
assert abs(x + y + z - 1) < mp.mpf(10)**-45
Fm = [[om**((j*k) % 3)/s3 for k in range(3)] for j in range(3)]; D2m = [1, om**2, om**2]
col = lambda k: [D2m[j]*Fm[j][k] for j in range(3)]               # columns of D^2 F_3
kron = lambda a, b: [ai*bj for ai in a for bj in b]
terms = [(mp.sqrt(x)*mp.e**(I*mp.pi/3), qm, col(0)), (mp.sqrt(y)*mp.e**(2*I*mp.pi/3), qm, col(1)), (mp.sqrt(z), qp, col(2))]
psi = [sum(c*kron(q, ww)[i] for c, q, ww in terms) for i in range(6)]
assert abs(sum(abs(t)**2 for t in psi) - 1) < mp.mpf(10)**-45
T0m = [np.array([[complex(e) for e in row] for row in T.tolist()]) for T in T0]
pv = []
for U in T0:
    for k in range(6):
        ip = sum(mp.mpc(U[i, k].real, U[i, k].imag).conjugate()*psi[i] for i in range(6)); pv.append(abs(ip)**2)
Ex = sum((p - mp.mpf(1)/6)**2 for p in pv); mx = max(abs(p - mp.mpf(1)/6) for p in pv)
print("(a) closed form: x + y + z = 1, norm 1; E(psi_*) = %s, (4 - sqrt6)/40 = %s (difference %.1e, limited by the double-precision matrices); max deviation %.5f" % (mp.nstr(Ex, 12), mp.nstr((4 - s6)/40, 12), float(abs(Ex - (4 - s6)/40)), float(mx)))
assert abs(Ex - (4 - s6)/40) < 1e-14 and abs(mx - mp.mpf("0.0575")) < 1e-4

# (b) own minimisation
def minimise(T, starts):
    vals = []
    def f(x): psi_ = x[:6] + 1j*x[6:]; return E(T, psi_/np.linalg.norm(psi_))
    for _ in range(starts):
        r = minimize(f, rng.normal(size=12), method="BFGS", options={"gtol": 1e-11, "maxiter": 500}); vals.append(r.fun)
    return np.array(vals)
for name, T, expect in (("T0", T0, (4 - np.sqrt(6))/40), ("T1", T1, 0.0238354)):
    vals = minimise(T, 60); distinct = sorted(set(np.round(vals, 6)))
    print("(b) %s: smallest of 60 BFGS starts %.10f (expected %.10f); distinct local-minimum values %s; %d of 60 starts reach the smallest" % (name, vals.min(), expect, distinct, int((vals < vals.min() + 1e-8).sum())))
    assert abs(vals.min() - expect) < (1e-9 if name == "T0" else 5e-8) and vals.min() > (0.0385 if name == "T0" else 0.0235)
print("OK")
