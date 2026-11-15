"""Cyclic 6-roots: find all complex solutions numerically and certify each with
complex Krawczyk (acb).  Equations (z_k, indices mod 6):
   e_m = sum_k z_k z_{k+1} ... z_{k+m-1} = 0  (m=1..5),   e_6 = z_0...z_5 - 1 = 0.
"""
import numpy as np
from flint import acb, arb, acb_mat, arb

N = 6

def _win(k, m):
    return [(k+i) % N for i in range(m)]

def F_np(z):
    out = np.empty(N, complex)
    for m in range(1, N+1):
        s = 0
        for k in range(N if m < N else 1):   # m=6: single product z_0...z_5
            s += np.prod(z[_win(k, m)])
        out[m-1] = s - (1 if m == N else 0)
    return out

def J_np(z):
    J = np.zeros((N, N), complex)
    for m in range(1, N+1):
        for k in range(N if m < N else 1):
            w = _win(k, m)
            for l in set(w):
                J[m-1, l] += np.prod([z[i] for i in w if i != l]) if m > 1 else 1
    return J

def newton_np(z, it=60):
    for _ in range(it):
        try:
            dz = np.linalg.solve(J_np(z), F_np(z))
        except np.linalg.LinAlgError:
            return None
        z = z - dz
        if not np.all(np.isfinite(z)) or np.max(np.abs(z)) > 1e6:
            return None
        if np.max(np.abs(dz)) < 1e-14:
            break
    return z if np.max(np.abs(F_np(z))) < 1e-11 else None

def symmetries(z):
    """Known symmetries of the cyclic-n-roots system: cyclic shift, reversal,
    inversion z -> 1/z, scaling by a 6th root of unity.  Used only to speed up the
    *search*; every orbit member is re-verified by Newton before being kept."""
    out = []
    zeta = np.exp(2j*np.pi/N)
    for rev in (False, True):
        for inv in (False, True):
            y = z[::-1].copy() if rev else z.copy()
            if inv: y = 1/y
            for sh in range(N):
                yy = np.roll(y, sh)
                for a in range(N):
                    out.append(yy*zeta**a)
    return out

def find_all(rng, max_starts=20000, target=156):
    sols = []
    def add(z):
        for q in sols:
            if np.max(np.abs(q-z)) < 1e-6*(1+np.max(np.abs(q))):
                return False
        sols.append(z); return True
    starts = 0
    while starts < max_starts and len(sols) < target:
        starts += 1
        sc = np.exp(rng.uniform(-1, 1))
        z0 = sc*(rng.normal(size=N)+1j*rng.normal(size=N))
        z = newton_np(z0)
        if z is None: continue
        if add(z):
            for y in symmetries(z):
                y2 = newton_np(y, it=8)
                if y2 is not None: add(y2)
    return sols, starts

# ---- complex ball arithmetic ----
def F_acb(z):
    out = []
    for m in range(1, N+1):
        s = acb(0)
        for k in range(N if m < N else 1):
            t = acb(1)
            for i in _win(k, m): t *= z[i]
            s += t
        out.append(s - (1 if m == N else 0))
    return out

def J_acb(z):
    J = acb_mat(N, N)
    for m in range(1, N+1):
        for l in range(N):
            s = acb(0)
            for k in range(N if m < N else 1):
                w = _win(k, m)
                c = w.count(l)
                if c == 0: continue
                t = acb(1)
                for i in w:
                    if i != l: t *= z[i]
                s += t   # each window contains l at most once for m<=6
            J[m-1, l] = s
    return J

def newton_acb(z0, it=8):
    z = [acb(x) for x in z0]
    for _ in range(it):
        f = acb_mat(N, 1, F_acb(z))
        dz = J_acb(z).solve(f)
        z = [acb((z[i]-dz[i, 0]).real.mid(), (z[i]-dz[i, 0]).imag.mid()) for i in range(N)]
    return z

def krawczyk_c(x0, r):
    """x0: list of N acb (exact centres).  Box = centre +- r in Re and Im.
    Returns (ok, K) ; ok proves a UNIQUE zero of the 6x6 system in the box."""
    X = [acb(arb(0).mid()+z.real.mid(), z.imag.mid()) for z in x0]
    Xb = [acb(arb(z.real.mid(), r), arb(z.imag.mid(), r)) for z in x0]
    J0 = J_acb(X)
    C = J0.inv()
    JX = J_acb(Xb)
    f0 = acb_mat(N, 1, F_acb(X))
    I = acb_mat(N, N)
    for i in range(N): I[i, i] = 1
    M = I - C*JX
    d = acb_mat(N, 1, [acb(arb(0, r), arb(0, r)) for _ in range(N)])
    Kv = C*f0
    Md = M*d
    ok = True; K = []
    for i in range(N):
        Ki = X[i] - Kv[i, 0] + Md[i, 0]
        K.append(Ki)
        dev = Ki - X[i]
        if not (arb(dev.real.abs_upper()) < r and arb(dev.imag.abs_upper()) < r):
            ok = False
    return ok, K
