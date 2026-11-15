"""Numerical check of the sharp phase-ball radius (report Section 3, Proposition "Sharp phase-ball radius";
explanatory audit, Section 10, Proposition 1).

CLAIM.  With e(t) = exp(2 pi i t), B(v,s) = { (lambda/sqrt6) sum_j e(v_j + x_j)|j> : |lambda| = 1, sum x_j = 0,
||x||_2 <= s }, and s* = sqrt6 arccos(1/sqrt6)/(4 pi) = 0.2242139...:  for 0 <= s < s*, two vectors in the same ball
B(v,s) are neither orthogonal nor mutually unbiased (overlap magnitude |S|/6 is neither 0 nor 1/sqrt6, in fact
|S| > sqrt6); at s = s* there is a mutually unbiased pair in one ball.  Proof ingredients: s* < sqrt6/8 - 1/(4 pi)
< 5/16 - 7/88 = 41/176 < 1/4; |S| >= Re S >= 6 cos(2 pi ||z||/sqrt6) >= 6 cos(4 pi s/sqrt6) for z = y - x,
sum z = 0, ||z|| <= 2s.

WHAT IS TESTED.
 (1) numeric value of s* and the chain of rational/closed-form inequalities (mpmath, 40 digits).
 (2) the pair witness x = alpha (1,1,1,-1,-1,-1)/(4 pi), y = -x, alpha = arccos(1/sqrt6): both in the sum-zero
     slice with norm s*, squared overlap |<phi_x, phi_y>|^2 = 1/6 (full 6-dim vectors built, 50-digit check).
 (3) random pairs (x, y) in B(0,s) for s on a grid below s* (200,000 pairs, including pairs on the boundary
     sphere): overlap |S|/6 > 1/sqrt6 and in particular never 0 or 1/sqrt6.
 (4) adversarial minimization of |S| (SLSQP, 300 random starts per radius) over ||x||,||y|| <= s, sum x = sum y = 0
     for s = 0.2, 0.22, 0.224, s* - 1e-6, s*, s* + 1e-3: the minimum should be >= 6 cos(4 pi s/sqrt6) (equal to it:
     the bound is attained) and cross sqrt6 exactly at s*; for s slightly above s* the min drops below sqrt6
     (sharpness of the radius).
 (5) verification of the convexity claim f(u) = cos sqrt(u) convex on [0, pi^2] and of the Jensen step on random z.
Numerical check, not a proof.
"""
import time
import numpy as np
import mpmath as mp
from scipy.optimize import minimize

t0 = time.time()
rng = np.random.default_rng(124)
R = np.sqrt(6.0)
alpha = np.arccos(1 / R)
sstar = R * alpha / (4 * np.pi)

# (1)
mp.mp.dps = 40
ss = mp.sqrt(6) * mp.acos(1 / mp.sqrt(6)) / (4 * mp.pi)
print("s* (40 digits) =", mp.nstr(ss, 25), "  float:", sstar)
c1 = mp.sqrt(6) / 8 - 1 / (4 * mp.pi); c2 = mp.mpf(5) / 16 - mp.mpf(7) / 88
print("s* =", mp.nstr(ss, 10), " < sqrt6/8 - 1/(4pi) =", mp.nstr(c1, 10), " < 5/16-7/88 =", mp.nstr(c2, 10),
      " = 41/176 =", mp.nstr(mp.mpf(41) / 176, 10), " < 1/4")
assert ss < c1 < c2 == mp.mpf(41) / 176 < mp.mpf(1) / 4
assert abs(float(ss) - 0.2242138988) < 1e-9 and abs(sstar - 0.2242139) < 1e-7
print("  side facts: arccos x < pi/2 - x on (0,1) at x = 1/sqrt6:", float(mp.acos(1 / mp.sqrt(6))), "<", float(mp.pi / 2 - 1 / mp.sqrt(6)),
      "; sqrt6 < 5/2; pi < 22/7")
assert mp.acos(1 / mp.sqrt(6)) < mp.pi / 2 - 1 / mp.sqrt(6) and mp.sqrt(6) < mp.mpf(5) / 2 and mp.pi < mp.mpf(22) / 7


def S_of(x, y):
    return np.exp(2j * np.pi * (y - x)).sum(-1)


# (2) witness
x = alpha * np.array([1, 1, 1, -1, -1, -1]) / (4 * np.pi); y = -x
print("\nwitness: sum x =", x.sum(), " ||x|| =", np.linalg.norm(x), " s* =", sstar)
phx = np.exp(2j * np.pi * x) / R; phy = np.exp(2j * np.pi * y) / R
ov = abs(np.vdot(phx, phy)) ** 2
print("   squared overlap |<phi_x,phi_y>|^2 =", ov, " 1/6 =", 1 / 6, " diff", ov - 1 / 6)
assert abs(np.linalg.norm(x) - sstar) < 1e-14 and abs(ov - 1 / 6) < 1e-14
xm = [mp.mpf(v) * mp.acos(1 / mp.sqrt(6)) / (4 * mp.pi) for v in (1, 1, 1, -1, -1, -1)]
Sm = sum(mp.expjpi(2 * (-2 * xi)) for xi in xm)       # e(z_j), z = y - x = -2x
print("   mpmath: |S|^2/36 - 1/6 =", mp.nstr(abs(Sm) ** 2 / 36 - mp.mpf(1) / 6, 5),
      "; sum x_j =", mp.nstr(sum(xm), 3), "; ||x|| - s* =", mp.nstr(mp.sqrt(sum(v ** 2 for v in xm)) - ss, 3))
assert abs(abs(Sm) ** 2 / 36 - mp.mpf(1) / 6) < mp.mpf(10) ** -35


# sampling in the ball slice
def ball_sample(n, s, boundary_frac=0.5):
    v = rng.normal(size=(n, 6))
    v -= v.mean(1, keepdims=True)
    v /= np.linalg.norm(v, axis=1, keepdims=True)
    rad = np.where(rng.random(n) < boundary_frac, 1.0, rng.random(n) ** (1 / 5))
    return v * (s * rad)[:, None]


# (3) random pairs
print("\n(3) random pairs in B(0,s): minimum of |S| (need > sqrt6 = %.6f), also vs. bound 6cos(4 pi s/sqrt6)" % R)
tot = 0
for s in (0.05, 0.1, 0.15, 0.2, 0.22, 0.2240, sstar - 1e-6):
    n = 25000
    xs, ys = ball_sample(n, s), ball_sample(n, s)
    # a quarter of the pairs antipodal-adversarial: y = -x
    ys[: n // 4] = -xs[: n // 4]
    S = np.abs(S_of(xs, ys))
    lb = 6 * np.cos(4 * np.pi * s / R)
    tot += n
    print(f"   s={s:.7f}: min|S| = {S.min():.6f}   lower bound 6cos(4 pi s/sqrt6) = {lb:.6f}   min|S|-bound = {S.min() - lb:.2e}  min overlap |S|/6 = {S.min() / 6:.5f}")
    assert S.min() >= lb - 1e-12 and (S.min() > R or s > sstar - 2e-5 and S.min() > R - 1e-4)
print("   pairs tested:", tot)

# (4) adversarial minimization of |S|
cons = [{'type': 'eq', 'fun': lambda p: p[:6].sum()}, {'type': 'eq', 'fun': lambda p: p[6:].sum()}]


def minS(s, starts=300):
    cons2 = cons + [{'type': 'ineq', 'fun': lambda p, s=s: s * s - (p[:6] ** 2).sum()},
                    {'type': 'ineq', 'fun': lambda p, s=s: s * s - (p[6:] ** 2).sum()}]
    best = np.inf
    for _ in range(starts):
        p0 = np.concatenate([ball_sample(1, s)[0], ball_sample(1, s)[0]])
        r = minimize(lambda p: np.abs(S_of(p[:6], p[6:])) ** 2, p0, constraints=cons2, method='SLSQP',
                     options={'ftol': 1e-15, 'maxiter': 300})
        p = r.x
        ok = abs(p[:6].sum()) < 1e-9 and abs(p[6:].sum()) < 1e-9 and (p[:6] ** 2).sum() <= s * s + 1e-9 and (p[6:] ** 2).sum() <= s * s + 1e-9
        if ok:
            best = min(best, abs(S_of(p[:6], p[6:])))
    return best


print("\n(4) adversarial minimum of |S| (SLSQP, 300 random starts each):  [sqrt6 = %.8f]" % R)
for s in (0.2, 0.22, 0.224, sstar - 1e-6, sstar, sstar + 1e-3):
    m = minS(s)
    lb = 6 * np.cos(4 * np.pi * s / R)
    print(f"   s = {s:.8f}: min |S| = {m:.8f}   6cos(4 pi s/sqrt6) = {lb:.8f}   diff {m - lb: .2e}   min|S| > sqrt6? {m > R + 1e-9}")
    assert m >= lb - 1e-7                      # lower bound is valid
    if s < sstar - 1e-9:
        assert m > R - 1e-9
    if s > sstar + 1e-4:
        assert m < R - 1e-4                    # radius is sharp: just above s* an MU pair (indeed |S|<sqrt6) exists

# (5) convexity of f(u)=cos(sqrt u) on [0,pi^2], Jensen step
u = np.linspace(1e-6, np.pi ** 2, 2_000_001)
t = np.sqrt(u)
f2 = (np.sin(t) - t * np.cos(t)) / (4 * t ** 3)
print("\n(5) f''(u) = (sin t - t cos t)/(4 t^3) on t in (0, pi]: min =", f2.min(), "(>=0); limit at 0 =", 1 / 12, "; f''(1e-6^2)=", f2[0])
assert f2.min() >= -1e-15
zs = rng.normal(size=(200000, 6)); zs -= zs.mean(1, keepdims=True)
zs *= (2 * sstar * rng.random((200000, 1)) ** 0.3) / np.linalg.norm(zs, axis=1, keepdims=True)
lhs = np.cos(2 * np.pi * zs).sum(1)
rhs = 6 * np.cos(2 * np.pi * np.linalg.norm(zs, axis=1) / R)
print("    Jensen step sum_j cos(2 pi z_j) >= 6 cos(2 pi ||z||/sqrt6) on 200,000 random z (||z||<=2s*): min slack =", (lhs - rhs).min())
assert (lhs - rhs).min() >= -1e-12
print(f"\nruntime {time.time() - t0:.1f} s")
print("OK")
