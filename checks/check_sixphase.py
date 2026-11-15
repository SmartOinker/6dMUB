"""Numerical check of the sharp six-phase bound (report, Proposition "Sharp six-phase bound";
structure paper Theorem 12.3).

CLAIM.  If z_1..z_6 are unimodular with sum z_j = sqrt(6), then |sum z_j^3| <= 7 sqrt(6)/3 = 5.71547607...,
with equality exactly (up to permutation) at three copies of (1 + i sqrt5)/sqrt6 and three of its conjugate.

WHAT IS TESTED.  (1) The claimed extremal configuration is feasible and attains the bound (value computed
in double precision and in 50-digit mpmath).  (2) 4000 random starts (angles uniform on [0, 2 pi)) are
projected onto the constraint set {sum cos = sqrt6, sum sin = 0} by SLSQP and then |sum e^{3 i theta}|^2 is
maximized by SLSQP under the same two real equality constraints.  The largest value found, the gap to the
bound, and the number of starts converging to the bound are reported.  (3) The distinct local-maximum values
found are tabulated.  (4) About 300,000 further exactly feasible points (4 random phases, the other two solved
from the constraints) are checked against the bound.

RANGE.  4000 random starts, 6 phases each; this is a numerical check, NOT a proof.
"""
import time
import numpy as np
from scipy.optimize import minimize
import mpmath as mp

t0 = time.time()
rng = np.random.default_rng(6)
R = np.sqrt(6.0)
BOUND = 7 * R / 3

# (1) the claimed extremal configuration
z0 = (1 + 1j * np.sqrt(5.0)) / R
cfg = np.array([z0] * 3 + [np.conj(z0)] * 3)
mp.mp.dps = 50
z0m = (1 + 1j * mp.sqrt(5)) / mp.sqrt(6)
cfgm = [z0m] * 3 + [mp.conj(z0m)] * 3
print("extremal configuration: |z|        =", abs(cfg))
print("   sum z_j     =", cfg.sum(), " (target sqrt6 =", R, ")")
print("   |sum z_j^3| =", abs((cfg ** 3).sum()), " bound 7 sqrt6/3 =", BOUND)
sm = sum(cfgm); s3 = sum(z ** 3 for z in cfgm)
print("   mpmath (50 digits): |sum z - sqrt6| =", mp.nstr(abs(sm - mp.sqrt(6)), 3),
      "  | |sum z^3| - 7 sqrt6/3 | =", mp.nstr(abs(abs(s3) - 7 * mp.sqrt(6) / 3), 3))
assert abs(cfg.sum() - R) < 1e-14 and abs(abs((cfg ** 3).sum()) - BOUND) < 1e-13
assert abs(sm - mp.sqrt(6)) < mp.mpf(10) ** -45 and abs(abs(s3) - 7 * mp.sqrt(6) / 3) < mp.mpf(10) ** -45

# (2) random-start maximization
cons = [{'type': 'eq', 'fun': lambda t: np.cos(t).sum() - R, 'jac': lambda t: -np.sin(t)},
        {'type': 'eq', 'fun': lambda t: np.sin(t).sum(), 'jac': lambda t: np.cos(t)}]


def p3sq(t):
    return np.abs(np.exp(3j * t).sum()) ** 2


def p3sq_grad(t):
    s = np.exp(3j * t).sum()
    return 2 * (s.real * (-3 * np.sin(3 * t)) + s.imag * (3 * np.cos(3 * t)))


def project(t):
    r = minimize(lambda u: ((u - t) ** 2).sum(), t, jac=lambda u: 2 * (u - t), constraints=cons,
                 method='SLSQP', options={'ftol': 1e-14, 'maxiter': 200})
    return r.x


best, nstart, nhit, nbad = 0.0, 4000, 0, 0
maxima = []
for k in range(nstart):
    t = project(rng.uniform(0, 2 * np.pi, 6))
    r = minimize(lambda u: -p3sq(u), t, jac=lambda u: -p3sq_grad(u), constraints=cons, method='SLSQP',
                 options={'ftol': 1e-15, 'maxiter': 500})
    u = r.x
    feas = abs(np.cos(u).sum() - R) < 1e-9 and abs(np.sin(u).sum()) < 1e-9
    if not feas:
        nbad += 1
        continue
    v = np.sqrt(p3sq(u))
    maxima.append(v)
    best = max(best, v)
    if v > BOUND - 1e-6:
        nhit += 1
maxima = np.array(maxima)
print(f"\nrandom starts: {nstart}, feasible local solutions: {len(maxima)}, infeasible/failed: {nbad}")
print(f"largest |sum z^3| found      : {best:.10f}")
print(f"bound 7 sqrt6/3              : {BOUND:.10f}")
print(f"gap (bound - largest found)  : {BOUND - best:.3e}")
print(f"starts reaching the bound within 1e-6: {nhit}")
vals, counts = np.unique(np.round(maxima, 4), return_counts=True)
print("distinct local-maximum values (rounded 1e-4) and counts, top 8 by value:")
for v, c in list(zip(vals, counts))[::-1][:8]:
    print(f"   {v:.4f}  x {c}")
assert best <= BOUND + 1e-9, "VIOLATION of the bound"
assert nhit > 0

# (4) feasible random points by projection, check bound
nchk, worst = 300000, 0.0
for _ in range(nchk // 1000):
    # cheap feasible sampling: pick 4 random phases, solve for two remaining phases so both constraints hold
    t = rng.uniform(0, 2 * np.pi, (1000, 4))
    w = np.sqrt(6.0) - np.cos(t).sum(1)
    im = -np.sin(t).sum(1)           # need e^{ia}+e^{ib} = w + i im =: c
    c = w + 1j * im
    ok = np.abs(c) <= 2
    c = c[ok]; t = t[ok]
    m = np.angle(c); h = np.arccos(np.clip(np.abs(c) / 2, -1, 1))
    for sgn in (1, -1):
        a, b = m + sgn * h, m - sgn * h
        z = np.concatenate([np.exp(1j * t), np.exp(1j * a)[:, None], np.exp(1j * b)[:, None]], axis=1)
        assert np.abs(z.sum(1) - R).max() < 1e-9
        worst = max(worst, np.abs((z ** 3).sum(1)).max())
print(f"\nexactly feasible random points tested (4 free phases + 2 solved): about {nchk}; largest |sum z^3| = {worst:.8f}")
assert worst <= BOUND + 1e-9
print(f"\nruntime {time.time() - t0:.1f} s")
print("OK")
