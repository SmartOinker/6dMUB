"""EXACT check of Proposition "Quartic SOS obstruction" (report Section 4.4; structure paper Section 4).

CLAIM.  For the canonical product triple T0, the degree-four relaxation  E_hom - gamma N^2 = sum p_a^2  (p_a real
homogeneous quadratics in the 12 real coordinates of psi in C^6) has optimum exactly 0, because there is a linear
functional L on homogeneous quartics with  L(p^2) >= 0 for every quadratic p,  L(E_hom) = 0,  L(N^2) = 1; its
78 x 78 pseudomoment matrix M_{ab} = L(m_a m_b) (over the 78 degree-two monomials) is positive semidefinite of
rank 63.  (Report: "positive semidefinite of exact rank 63".)

WHAT THIS SCRIPT DOES (all verification steps exact; one float64 cross-check of the symbolic rebuild is printed as a sanity check; no optimizer).
  Source of L.  The structure paper does NOT print the 342 nonzero moments, so this check cannot reuse them.  Instead
  the file quartic_L_moments.json (written by build_quartic_functional.py, which uses a floating-point SDP only as a
  heuristic and then solves the linear constraints EXACTLY over Q(sqrt3)) contains our OWN functional: 1365 moments
  L(x^alpha), alpha a degree-four monomial, each a + b sqrt3 with a, b rational.  It is therefore an independent
  re-construction of a functional with the properties claimed; it is not the structure paper's functional (its moments
  are not available to us).  Everything below re-derives the objects from the physical definitions and tests L exactly.
  Steps, all in exact arithmetic over Q(sqrt3) (python Fractions and sympy):
   (1) rebuild the 18 projectors P_l = u u* of T0 (U_r = A_r (x) B_r, A = [I,H2,diag(1,i)H2], B = [I3,F3,DF3],
       D = diag(1,w,w)) symbolically, the 18 quadratics q_l(x) = psi* P_l psi - N/6 as coefficient vectors c_l over
       the 78 monomials, and E_hom = sum q_l^2;
   (2) M = Hankel matrix of the moments; exactly verify symmetry, M c_l = 0 for all 18 l (1,404 equations),
       L(N^2) = 1, and L(E_hom) = c-form sum_l c_l^T M c_l = 0;
   (3) exact pivoted LDL^T of M over Q(sqrt3): every accepted pivot is checked > 0 by exact sign tests, the elimination
       ends with a Schur complement that is exactly zero.  Hence M is PSD and the rank equals the number of pivots;
   (4) exact rank of the 18 x 78 coefficient matrix [c_l] (should be 15) and check that kernel(M) = span(c_l),
       i.e. rank M + rank C = 78.
The consequence  optimum = 0  follows from L as in the report's two-line argument (gamma <= 0 from L; gamma = 0 feasible
since E_hom is a sum of squares); that argument is not re-checked here.
Range: exact, the one concrete functional in quartic_L_moments.json.  Numerical-free check, but Python/sympy and
Fraction arithmetic are in the trust base.
"""
import itertools, json, os, sys, time
from fractions import Fraction as Fr
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))


# ---------------- exact arithmetic in Q(sqrt3) ----------------
class QS:
    __slots__ = ('a', 'b')

    def __init__(self, a=0, b=0):
        self.a, self.b = Fr(a), Fr(b)

    def __add__(s, o): o = _q(o); return QS(s.a + o.a, s.b + o.b)
    __radd__ = __add__
    def __sub__(s, o): o = _q(o); return QS(s.a - o.a, s.b - o.b)
    def __rsub__(s, o): return _q(o) - s
    def __neg__(s): return QS(-s.a, -s.b)
    def __mul__(s, o): o = _q(o); return QS(s.a * o.a + 3 * s.b * o.b, s.a * o.b + s.b * o.a)
    __rmul__ = __mul__
    def inv(s):
        n = s.a * s.a - 3 * s.b * s.b
        assert n != 0
        return QS(s.a / n, -s.b / n)
    def __truediv__(s, o): return s * _q(o).inv()
    def iszero(s): return s.a == 0 and s.b == 0
    def __eq__(s, o): o = _q(o); return s.a == o.a and s.b == o.b
    def sign(s):
        a, b = s.a, s.b
        if a == 0 and b == 0: return 0
        if a >= 0 and b >= 0: return 1
        if a <= 0 and b <= 0: return -1
        d = a * a - 3 * b * b            # sign of a + b sqrt3 when a, b have opposite signs
        return (1 if a > 0 else -1) * (1 if d > 0 else -1) if d != 0 else 0
    def __repr__(s): return f"({s.a} + {s.b}*sqrt3)"
    def to_json(s): return [str(s.a), str(s.b)]


def _q(x): return x if isinstance(x, QS) else QS(x, 0)


def from_json(p): return QS(Fr(p[0]), Fr(p[1]))


# ---------------- exact physical data ----------------
n = 12
mons2 = list(itertools.combinations_with_replacement(range(n), 2))      # 78
mons4 = list(itertools.combinations_with_replacement(range(n), 4))      # 1365
i4 = {m: i for i, m in enumerate(mons4)}


def exact_quadratics():
    """18 coefficient vectors c_l (length 78, entries QS) of q_l = psi* P_l psi - N/6 in the monomials x_i x_j (i<=j)."""
    s2, s3, I = sp.sqrt(2), sp.sqrt(3), sp.I
    w = (-1 + I * s3) / 2
    H2 = sp.Matrix([[1, 1], [1, -1]]) / s2
    A = [sp.eye(2), H2, sp.diag(1, I) * H2]
    F = sp.Matrix(3, 3, lambda j, k: w ** ((j * k) % 3)) / s3
    D = sp.diag(1, w, w)
    B = [sp.eye(3), F, D * F]
    out = []
    for r in range(3):
        U = sp.kronecker_product(A[r], B[r])
        for j in range(6):
            u = U[:, j]
            P = (u * u.H).applyfunc(sp.expand)
            Re = P.applyfunc(lambda e: sp.expand(sp.re(sp.expand(e))))
            Im = P.applyfunc(lambda e: sp.expand(sp.im(sp.expand(e))))
            R = sp.zeros(12, 12)
            R[:6, :6], R[:6, 6:], R[6:, :6], R[6:, 6:] = Re, -Im, Im, Re          # psi* P psi = x^T R x
            R = ((R + R.T) / 2).applyfunc(sp.expand)
            c = []
            for (a, b) in mons2:
                e = R[a, a] - (sp.Rational(1, 6) if a == b else 0) if a == b else 2 * R[a, b]
                e = sp.expand(e)
                a0 = e.subs(s3, 0) if e.has(s3) else e
                b0 = sp.expand((e - a0) / s3)
                assert not b0.has(s3) and not a0.has(s3)
                c.append(QS(Fr(int(sp.numer(a0)), int(sp.denom(a0))), Fr(int(sp.numer(b0)), int(sp.denom(b0)))))
            out.append(c)
    return out


def hankel_index():
    return [[i4[tuple(sorted(mons2[a] + mons2[b]))] for b in range(78)] for a in range(78)]


def ldl_exact(M):
    """Pivoted LDL^T over Q(sqrt3).  Returns (pivots, order, rank, final Schur block zero?)."""
    m = len(M)
    M = [row[:] for row in M]
    active = list(range(m))
    pivots = []
    while active:
        # pick an active diagonal element that is nonzero (largest-index-first is irrelevant for exactness)
        piv = next((i for i in active if not M[i][i].iszero()), None)
        if piv is None:
            break
        d = M[piv][piv]
        sg = d.sign()
        assert sg > 0, f"negative/zero pivot at {piv}: not PSD"
        pivots.append(d)
        active.remove(piv)
        dinv = d.inv()
        for i in active:
            f = M[i][piv] * dinv
            if f.iszero():
                continue
            for j in active:
                M[i][j] = M[i][j] - f * M[piv][j]
    # remaining Schur block must be exactly zero (otherwise a nonzero off-diagonal 2x2 with zero diagonal => indefinite)
    zero_block = all(M[i][j].iszero() for i in active for j in active)
    return pivots, len(pivots), zero_block, len(active)


def exact_rank(rows):
    m = [r[:] for r in rows]
    rk, ncol = 0, len(m[0])
    for c in range(ncol):
        p = next((i for i in range(rk, len(m)) if not m[i][c].iszero()), None)
        if p is None: continue
        m[rk], m[p] = m[p], m[rk]
        pi = m[rk][c].inv()
        for i in range(rk + 1, len(m)):
            if not m[i][c].iszero():
                f = m[i][c] * pi
                m[i] = [x - f * y for x, y in zip(m[i], m[rk])]
        rk += 1
        if rk == len(m): break
    return rk


def main():
    t0 = time.time()
    data = json.load(open(os.path.join(HERE, 'quartic_L_moments.json')))
    y = [from_json(p) for p in data['moments']]
    assert len(y) == 1365 and data['monomial_order'] == 'combinations_with_replacement(range(12),4)'
    print("moments loaded:", len(y), " nonzero:", sum(not v.iszero() for v in y))
    C = exact_quadratics()
    print(f"exact quadratics rebuilt ({time.time() - t0:.0f} s)")
    # sanity cross-check of the symbolic rebuild against an independent float64 numpy construction (sanity only)
    import numpy as np
    w = np.exp(2j * np.pi / 3); H2n = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
    An = [np.eye(2), H2n, np.diag([1, 1j]) @ H2n]
    Fn = np.array([[w ** (j * k) for k in range(3)] for j in range(3)]) / np.sqrt(3)
    Bn = [np.eye(3), Fn, np.diag([1, w, w]) @ Fn]
    dev = 0.0
    for r in range(3):
        Un = np.kron(An[r], Bn[r])
        for j in range(6):
            u = Un[:, j]; P = np.outer(u, u.conj())
            R = np.block([[P.real, -P.imag], [P.imag, P.real]]); R = (R + R.T) / 2 - np.eye(12) / 6
            for k, (a, b) in enumerate(mons2):
                ref = R[a, a] if a == b else 2 * R[a, b]
                ex = C[6 * r + j][k]
                dev = max(dev, abs(ref - (float(ex.a) + float(ex.b) * 3 ** .5)))
    print("max |exact c_l - float64 c_l| over 18 x 78 coefficients:", dev)
    assert dev < 1e-13
    H = hankel_index()
    M = [[y[H[a][b]] for b in range(78)] for a in range(78)]
    assert all(M[a][b] == M[b][a] for a in range(78) for b in range(78))
    # (2)
    neq = 0
    for l in range(18):
        for a in range(78):
            s = QS()
            for b in range(78):
                if not C[l][b].iszero():
                    s = s + C[l][b] * M[a][b]
            assert s.iszero(), f"M c_{l} != 0 at row {a}"
            neq += 1
    print(f"M c_l = 0 verified exactly: {neq} equations (18 x 78)")
    LN2 = QS()
    for i in range(12):
        for j in range(12):
            LN2 = LN2 + y[i4[tuple(sorted((i, i, j, j)))]]
    assert LN2 == 1
    print("L(N^2) = 1 verified exactly")
    LE = QS()
    for l in range(18):
        for a in range(78):
            for b in range(78):
                if not C[l][a].iszero() and not C[l][b].iszero():
                    LE = LE + C[l][a] * C[l][b] * M[a][b]
    assert LE.iszero()
    print("L(E_hom) = sum_l c_l^T M c_l = 0 verified exactly")
    # (3)
    t1 = time.time()
    piv, rank, zb, nrem = ldl_exact(M)
    print(f"exact LDL^T: {rank} strictly positive pivots, remaining Schur block {nrem}x{nrem} exactly zero: {zb}  ({time.time() - t1:.0f} s)")
    assert zb
    # (4)
    rc = exact_rank(C)
    print("exact rank of the 18 x 78 matrix [c_l]:", rc, "; rank M + rank C =", rank + rc, "(= 78 iff kernel M = span c_l)")
    print("pivot sign tests all strictly positive; smallest pivot (float):", min(float(p.a) + float(p.b) * 3 ** .5 for p in piv))
    assert rank == 63 and rc == 15 and rank + rc == 78
    print(f"\nruntime {time.time() - t0:.1f} s")
    print("OK")


if __name__ == '__main__':
    main()
