"""Rigorous evaluation (Arb balls) of two explicit four-basis sets stored as float64 arrays.
A stored matrix B~ is only approximately unitary.  With eps = ||B~^dag B~ - I||_F, its polar factor U is exactly
unitary and ||U - B~||_2 <= eps.  Overlaps of the exact bases then differ from the stored ones by at most
t = (eps_a + eps_b)(1 + max eps), and squared overlaps by at most t(2(1+eps)^2 + t)  -- added to all bounds below."""
import sys, numpy as np
from flint import arb, acb, ctx
ctx.prec = 160
def load(path):
    B = np.load(path); assert B.shape == (4, 6, 6)
    return [[[acb(float(B[k][i][j].real), float(B[k][i][j].imag)) for j in range(6)] for i in range(6)] for k in range(4)]
import math
def up(x, d):    # decimal rounded UP to d places (for printed upper bounds)
    return math.ceil(x * 10**d + 1e-6) / 10**d
def down(x, d):  # decimal rounded DOWN to d places (for printed lower bounds)
    return math.floor(x * 10**d - 1e-6) / 10**d
def study(path):
    Bs = load(path); eps = []
    for B in Bs:
        f = arb(0)
        for a in range(6):
            for b in range(6):
                g = sum((B[i][a].conjugate() * B[i][b] for i in range(6)), acb(0)) - (1 if a == b else 0)
                f += g.real ** 2 + g.imag ** 2
        eps.append(f.sqrt())
    emax = max(eps, key=lambda e: float(e.upper()))
    delta = arb(0); Psum = arb(0); sixth = arb(1) / 6
    for a in range(4):
        for b in range(a + 1, 4):
            t = (eps[a] + eps[b]) * (1 + emax)
            t2 = t * (2 * (1 + emax) ** 2 + t)
            s = arb(0)
            for i in range(6):
                for j in range(6):
                    ip = sum((Bs[a][k][i].conjugate() * Bs[b][k][j] for k in range(6)), acb(0))
                    m2 = ip.real ** 2 + ip.imag ** 2
                    dev = abs(m2 - sixth) + t2
                    if float(dev.upper()) > float(delta.upper()): delta = dev
                    s += m2.sqrt() - t                       # lower bound on the exact overlap modulus
            Psum += arb(1) / 2 + s / 72
    P4 = Psum / 6
    mu = arb(1) / 2 + 1 / (2 * arb(6).sqrt())
    print(path.split("/")[-1])
    print("  unitarity defects eps <= %.2e" % float(emax.upper()))
    print("  exact set has worst-case bias delta <= %.9f   (rounded up)" % up(float(delta.upper()), 9))
    print("  exact set has game score P_4 >= %.10f (rounded down), i.e. shortfall <= %.10f (rounded up)" % (down(float(P4.lower()), 10), up(float((mu - P4).upper()), 10)))
for p in sys.argv[1:]:
    study(p)
c = 3 * arb(6).sqrt() / (arb(6).sqrt() + 1) ** 2
# g = certified energy bounds rounded down: verify.py proves E > 0.03849999999 (T0) and E > 0.02349999999 (T1).
for nm, g in (("T0", arb("0.03849999999")), ("T1", arb("0.02349999999"))):
    print("%s: any 4 bases containing it:  delta >= sqrt(g/18) > %.6f ;  game shortfall >= c*g/72 > %.10f   (both rounded down)" % (nm, down(float((g / 18).sqrt().lower()), 6), down(float((c * g / 72).lower()), 10)))
