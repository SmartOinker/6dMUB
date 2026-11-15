"""Rigorous (Arb ball arithmetic, python-flint) certification of cyclic 10-roots found by find_roots.py.

System: x in (C*)^10, x_0 = 1, g_k(x) = sum_j x_{j+k}/x_j = 0 for k=1..9 (unknowns x_1..x_9).
Precision: 128 bits.  Box for root i: X_i = { x : |Re x_m - Re c_m| <= r_m, |Im x_m - Im c_m| <= r_m },
  c = the complex128 midpoint (converted EXACTLY to a ball), r_m = 2^-30 * max(1, ceil|c_m|)   (about 9.3e-10 * max(1,|c_m|)).

For each root, three certificates:
 (1) Krawczyk: with Y a float64 approximate inverse of J(c) (any matrix is allowed; rigor does not depend on Y),
     K = c - Y g(c) + (I - Y J(X)) (X - c).  If |Re(K_m - c_m)| < r_m and |Im(K_m - c_m)| < r_m for all m (strict, tested
     with certified Arb comparisons) then X contains exactly one root, and it lies in K.  (J(X) is an enclosure of the
     Jacobian over the box X; X is required not to contain 0 in any coordinate, otherwise Arb gives non-finite balls and the test fails.)
 (2) Unimodular:     sigma(x) = 1/conj(x) satisfies g_k(sigma x) = conj(g_{-k}(x)), so sigma maps roots to roots.
     If sigma(K) is inside X (strictly, certified) then sigma(root) is a root in X, hence = root by uniqueness,
     so root = 1/conj(root), i.e. |x_m| = 1 for all m.
     Not unimodular: some coordinate m with the ball |K_m| not containing 1 (certified).  Otherwise: undecided.
 (3) Pairwise disjointness of the boxes X_i (=> at least N distinct roots, since each box holds exactly one root):
     Let rho_i = r_i + 0 (boxes are centred at the complex128 midpoints m_i themselves).  Sort roots by float Re(x_1).
     Two boxes are disjoint as soon as some one of the 18 real components of the centres differs by more than
     rho_i + rho_j (componentwise).  For every pair with float |Re x_1 - Re x_1'| <= 1e-6 (the window; all radii are
     < 1e-7, so every pair outside the window is disjoint because the float64 subtraction error is < 1e-12), the componentwise test
     is done in float64 with a safety margin of 1e-9 (float64 rounding error is < 1e-13 for |c| < 1e3; asserted), and
     any pair that does not pass the float test with the margin is re-tested in EXACT rational arithmetic (fractions.Fraction,
     centres are exact floats and radii exact dyadic).  Any pair failing both tests is reported (should not happen).
 Matching the stored unimodular list (bu10hp_unimod.txt, 3040 points with 40-digit coordinates): stored point p is in
     box X_i if |Re p_m - Re c_m| < r_m and |Im p_m - Im c_m| < r_m for all m (certified Arb comparison, p taken as an exact
     decimal ball of radius 1e-40).  The stored points are each separately certified to be within 1e-30 of a root by
     check_d10.py (unique root in a 1e-30 box); a root within 1e-30 of p, with p inside the strict box, lies in X_i, so it is THE root of X_i.
Output: counts, certificates in cyclic10_roots.npz (midpoints, status codes, K radii, match index), log to stdout.
Usage (input .npy of N x 9 complex, or a previous .npz):
  python3 certify_roots.py roots_found.npy cyclic10_roots.npz [stored_unimod.txt] [nproc]
"""
import numpy as np, sys, time, math
from fractions import Fraction
from multiprocessing import Pool
from flint import arb, acb, acb_mat, ctx

ctx.prec = 128
d = 10
R_EXP = 30

def radius(c):
    return math.ldexp(max(1, math.ceil(abs(c))), -R_EXP)

def exact_acb(z):
    return acb(arb(float(z.real)), arb(float(z.imag)))

def gfun(x):
    ix = [1 / v for v in x]
    return [sum((x[(j + k) % d] * ix[j] for j in range(d)), acb(0)) for k in range(1, d)], ix

def jac(x, ix):
    return [[ix[(m - k) % d] - x[(m + k) % d] * ix[m] * ix[m] for m in range(1, d)] for k in range(1, d)]

# status codes
UNIMOD, NONUNIMOD, UNDECIDED, KRAW_FAIL = 1, 2, 0, -1

def certify_one(v):
    c = [exact_acb(z) for z in v]
    rr = [radius(z) for z in v]
    x = [acb(1)] + c
    g, ix = gfun(x)
    Jc = jac(x, ix)
    Jf = np.array([[complex(float(e.real.mid()), float(e.imag.mid())) for e in row] for row in Jc])
    try:
        Yf = np.linalg.inv(Jf)
    except np.linalg.LinAlgError:
        return KRAW_FAIL, 0.0
    Y = acb_mat(9, 9, [acb(float(z.real), float(z.imag)) for z in Yf.ravel()])
    discs = [acb(arb(0, r), arb(0, r)) for r in rr]
    X = [acb(1)] + [c[i] + discs[i] for i in range(9)]
    gX, ixX = gfun(X)
    JX = acb_mat(9, 9, [e for row in jac(X, ixX) for e in row])
    I9 = acb_mat(9, 9, [acb(1) if i == j else acb(0) for i in range(9) for j in range(9)])
    dev = (Y * acb_mat(9, 1, g)) * (-1) + (I9 - Y * JX) * acb_mat(9, 1, discs)    # K - c
    ok = True; K = []; krad = 0.0
    for i in range(9):
        e = dev[i, 0]
        ok &= bool(abs(e.real) < arb(rr[i])) and bool(abs(e.imag) < arb(rr[i]))
        K.append(c[i] + e)
        krad = max(krad, float(max(abs(e.real).upper(), abs(e.imag).upper())))
    if not ok:
        return KRAW_FAIL, krad
    # sigma test
    uni = True
    for i in range(9):
        s = 1 / K[i].conjugate() - c[i]
        uni &= bool(abs(s.real) < arb(rr[i])) and bool(abs(s.imag) < arb(rr[i]))
    if uni:
        return UNIMOD, krad
    for i in range(9):
        m = abs(K[i])
        if bool(m.upper() < 1) or bool(m.lower() > 1):
            return NONUNIMOD, krad
    return UNDECIDED, krad

def work(chunk):
    return [certify_one(v) for v in chunk]

def disjointness(C, rad):
    """C: (N,9) complex128 centres, rad: (N,9) float radii. Returns (#pairs in window, #exact fallbacks, #failures)."""
    N = len(C); assert np.abs(C).max() < 1e3 and rad.max() < 1e-7
    P = np.concatenate([C.real, C.imag], 1); Rr = np.concatenate([rad, rad], 1)
    order = np.argsort(C[:, 0].real, kind="stable"); key = C[order, 0].real
    hi = np.searchsorted(key, key + 1e-6, side="right")
    npairs = nexact = nfail = 0
    for a in range(N):
        b0, b1 = a + 1, hi[a]
        if b1 <= b0: continue
        i = order[a]; js = order[b0:b1]; npairs += len(js)
        sep = np.abs(P[js] - P[i]) > (Rr[js] + Rr[i] + 1e-9)
        bad = js[~sep.any(1)]
        for j in bad:
            nexact += 1
            ok = any(abs(Fraction(float(P[i, t])) - Fraction(float(P[j, t]))) > Fraction(float(Rr[i, t])) + Fraction(float(Rr[j, t]))
                     for t in range(18))
            if not ok: nfail += 1
    return npairs, nexact, nfail

def parse_stored(path):
    pts = []
    for l in open(path):
        t = l.split()
        if not t: continue
        pts.append([(t[1 + 2 * i], t[2 + 2 * i]) for i in range(9)])
    return pts

if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    stored = sys.argv[3] if len(sys.argv) > 3 else None
    nproc = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    t0 = time.time()
    C = np.load(src); C = (C['x1_to_x9'] if src.endswith('.npz') else C).astype(complex); N = len(C)
    print(f"loaded {N} candidate roots; prec={ctx.prec} bits, box half-width 2^-{R_EXP}*max(1,ceil|c|)", flush=True)
    chunks = [C[i:i + 200] for i in range(0, N, 200)]
    res = []
    with Pool(nproc) as pool:
        for n, r in enumerate(pool.imap(work, chunks)):
            res += r
            if n % 20 == 0: print(f"  krawczyk {len(res)}/{N}  {time.time()-t0:.0f}s", flush=True)
    status = np.array([s for s, _ in res], dtype=np.int8); krad = np.array([k for _, k in res])
    rad = np.array([[radius(z) for z in row] for row in C])
    cert = int((status != KRAW_FAIL).sum())
    print(f"Krawczyk: {cert}/{N} boxes certified (unique root each); max K-deviation {krad.max():.2e}; max box half-width {rad.max():.2e}; {time.time()-t0:.0f}s", flush=True)
    good = status != KRAW_FAIL
    npairs, nexact, nfail = disjointness(C[good], rad[good])
    print(f"Disjointness of the {cert} certified boxes: window pairs examined {npairs}, exact-rational fallbacks {nexact}, pairs NOT shown disjoint {nfail}; {time.time()-t0:.0f}s", flush=True)
    nu = int((status == UNIMOD).sum()); nn = int((status == NONUNIMOD).sum()); nund = int((status == UNDECIDED).sum())
    match = -np.ones(N, dtype=np.int32)
    if stored:
        pts = parse_stored(stored)
        from scipy.spatial import cKDTree
        F = np.array([[complex(float(a), float(b)) for a, b in p] for p in pts])
        tree = cKDTree(np.concatenate([C.real, C.imag], 1))
        _, nearest = tree.query(np.concatenate([F.real, F.imag], 1))
        hit = 0
        for s, (p, i) in enumerate(zip(pts, nearest)):
            ok = True
            for m, (a, b) in enumerate(p):
                r = arb(rad[i, m])
                ok &= bool(abs(arb(a) - arb(float(C[i, m].real))) < r) and bool(abs(arb(b) - arb(float(C[i, m].imag))) < r)
            if ok:
                hit += 1
                assert match[i] == -1 or match[i] == s; match[i] = s
        matched_idx = set(np.nonzero(match >= 0)[0].tolist()); uni_idx = set(np.nonzero(status == UNIMOD)[0].tolist())
        print(f"Stored list: {len(pts)} points, {hit} lie strictly inside a certified box; boxes hit: {len(matched_idx)}", flush=True)
        print(f"  sigma-unimodular boxes: {len(uni_idx)}; equal to matched set: {matched_idx == uni_idx}; "
              f"matched boxes not certified unimodular: {len(matched_idx - uni_idx)}; unimodular boxes with no stored point: {len(uni_idx - matched_idx)}", flush=True)
    print(f"COUNTS: found={N} certified={cert} unimodular={nu} certified_non_unimodular={nn} undecided={nund} krawczyk_failed={N-cert}; "
          f"total time {time.time()-t0:.0f}s", flush=True)
    np.savez_compressed(out, x1_to_x9=C, status=status, kdev_max=krad.astype(np.float32), stored_match=match,
                        note=np.array("status: 1 unimodular(sigma test), 2 certified non-unimodular, 0 undecided, -1 Krawczyk failed. x_0=1; box half-width 2^-30*max(1,ceil|c|) per coordinate"))
