"""Core arb/acb helpers for the dimension-6 {I, Fourier} unbiased-vector problem.

Unknowns: phases p_1..p_5 (p_0 = 0); v_k = exp(i p_k).
Equation j (j=0..5):  f_j(p) = |s_j|^2 - 6,  s_j = sum_k w^{-jk} v_k,  w = exp(2 pi i/6).
(F is symmetric so conj(F[k,j]) = w^{-jk}.)  Sum_j f_j = 0 identically (Parseval).
"""
import numpy as np
from flint import arb, acb, arb_mat, ctx

W = 6

def set_prec(bits):
    ctx.prec = bits

# ---------------- floating point (numpy) ----------------
_w = np.exp(-2j*np.pi*np.outer(np.arange(W), np.arange(W))/W)   # w^{-jk}

def f_float(p5):
    v = np.exp(1j*np.concatenate([[0.0], p5]))
    s = _w @ v
    return np.abs(s)**2 - 6.0

def jac_float(p5):
    v = np.exp(1j*np.concatenate([[0.0], p5]))
    s = _w @ v
    ds = _w[:, 1:] * (1j*v[1:])[None, :]
    return 2*np.real(np.conj(s)[:, None]*ds)

# ---------------- arb (ball arithmetic) ----------------
def _wk(m):
    """w^{-m} as acb at the current precision."""
    return acb(0, -2*arb.pi()*(m % W)/W).exp()

def f_arb(p):
    """p: list of 5 arb (phases p_1..p_5). Returns list of 6 arb f_j."""
    v = [acb(1)] + [acb(0, x).exp() for x in p]
    out = []
    for j in range(W):
        s = acb(0)
        for k in range(W):
            s += _wk(j*k)*v[k]
        out.append(s.real**2 + s.imag**2 - 6)
    return out

def jac_arb(p, rows):
    """Jacobian of f_j (j in rows) wrt p_1..p_5, as arb_mat."""
    v = [acb(1)] + [acb(0, x).exp() for x in p]
    s = []
    for j in range(W):
        t = acb(0)
        for k in range(W):
            t += _wk(j*k)*v[k]
        s.append(t)
    J = arb_mat(len(rows), 5)
    for a, j in enumerate(rows):
        sc = s[j].conjugate()
        for k in range(1, W):
            d = _wk(j*k)*acb(0, 1)*v[k]
            J[a, k-1] = 2*(sc*d).real
    return J

def newton_arb(p0, rows, iters=12):
    """High precision Newton on the 5 equations `rows` (midpoints only)."""
    p = [arb(x) for x in p0]
    for _ in range(iters):
        f = f_arb(p)
        J = jac_arb(p, rows)
        rhs = arb_mat(5, 1, [f[j] for j in rows])
        dx = J.solve(rhs)
        p = [(p[i] - dx[i, 0]).mid() for i in range(5)]
    return p

def krawczyk(x0, rows, r):
    """Krawczyk test on box x0 +- r for the square system f_rows = 0.
    x0: list of 5 arb (exact midpoints). r: arb radius.
    Returns (ok, Kbox) where ok==True PROVES a unique zero of the 5x5 system in the box,
    and Kbox is a list of 5 arb enclosing that zero (K(X), contained in the box interior)."""
    X = [arb(x0[i]).mid() + arb(0, r) for i in range(5)]   # ball centred at x0 with radius r
    J0 = jac_arb([a.mid() for a in x0], rows)
    C = J0.inv()
    C = arb_mat(5, 5, [C[i, j].mid() for i in range(5) for j in range(5)])  # any C is valid
    JX = jac_arb(X, rows)
    f0 = f_arb([a.mid() for a in x0])
    fv = arb_mat(5, 1, [f0[j] for j in rows])
    I5 = arb_mat(5, 5)
    for i in range(5): I5[i, i] = 1
    M = I5 - C*JX
    d = arb_mat(5, 1, [arb(0, r) for _ in range(5)])      # X - x0
    Kv = C*fv
    Md = M*d
    K = []
    ok = True
    for i in range(5):
        Ki = arb(x0[i]).mid() - Kv[i, 0] + Md[i, 0]
        K.append(Ki)
        # strict containment K_i in interior of X_i  <=>  |K_i - x0_i| < r
        dev = (Ki - arb(x0[i]).mid()).abs_upper()
        if not (arb(dev) < arb(r)):
            ok = False
    return ok, K
