"""Numerical test of the square-root lemma (report, Lemma "A quadratic cap on the square root").

    sqrt(p) <= 1/sqrt6 + (sqrt6/2)(p - 1/6) - c (p - 1/6)^2   for p in [0,1],   c = 3 sqrt6/(sqrt6+1)^2,

with equality exactly at p = 1/6 and p = 1.  This is a sanity check, not the proof (the proof is six lines in the
report).  It samples 1.8 million points: 50,000 random 6 x 6 arrays of squared overlaps of two random unitary
bases (36 entries each), plus a fine grid on [0,1], and reports the smallest slack.
"""
import numpy as np
rng = np.random.default_rng(124)
s6 = np.sqrt(6.0); c = 3*s6/(s6 + 1)**2
slack = lambda p: 1/s6 + (s6/2)*(p - 1/6) - c*(p - 1/6)**2 - np.sqrt(p)
worst = np.inf; n = 0
for _ in range(50000):
    z = rng.normal(size=(6, 6)) + 1j*rng.normal(size=(6, 6))
    q, r = np.linalg.qr(z)
    p = np.abs(q)**2                      # squared overlaps of the standard basis with a random basis
    worst = min(worst, slack(p).min()); n += p.size
    # pair-sum form: sum sqrt(p) <= 6 sqrt6 - c sum (p - 1/6)^2
    assert np.sqrt(p).sum() <= 6*s6 - c*((p - 1/6)**2).sum() + 1e-12
g = np.linspace(0.0, 1.0, 2_000_001)
gs = slack(g)
print("c =", c, "  closed form (21 sqrt6 - 36)/25 =", (21*s6 - 36)/25)
print("random points tested:", n, "  smallest slack:", worst)
print("grid points tested:", g.size, "  smallest slack on the grid:", gs.min(), " at p =", g[gs.argmin()])
print("slack at p = 1/6:", slack(np.array(1/6)), "  slack at p = 1:", slack(np.array(1.0)))
assert worst > -1e-13 and gs.min() > -1e-13
print("OK: no violation")
