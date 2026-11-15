#!/usr/bin/env python3
"""Cyclic 6-roots: find all isolated roots numerically, then certify them in Arb ball arithmetic.

This is `d10/roots_full/find_roots.py` and `certify_roots.py` adapted to n = 6.
What is checked, and with which arithmetic:

  System: x in (C*)^6, x_0 = 1, g_k(x) = sum_j x_{j+k}/x_j = 0 (k = 1..5), equivalent to the cyclic
  6-roots system via z_j = x_{j+1}/x_j (then prod z_j = 1 holds automatically).  A unit vector of C^6
  unbiased to I and F_6 is, up to a phase, x/sqrt(6) with all |x_j| = 1 and g_k(x) = 0 (see the report).

  1. SEARCH (heuristic, double precision, not part of any proof): damped Newton from random starts,
     closure under the symmetry group of order 288 (dilation j -> a j with a in {1,5}, inversion,
     complex conjugation, cyclic shift, modulation by 6th roots of unity).  Each generator is checked
     numerically on found roots before the closure is used.
  2. CERTIFICATION (python-flint / Arb, 128-bit balls):
     (a) Krawczyk: each box centred at a complex128 midpoint (converted exactly) with half-width
         2^-30 * max(1, ceil|c|) per real and imaginary part contains exactly one root;
     (b) the boxes are pairwise disjoint (float window test with margin, exact rational fallback), so
         there are at least as many distinct roots as boxes;
     (c) unimodular: sigma(x) = 1/conj(x) maps roots to roots; if sigma(K) lies strictly inside the box,
         the root equals its image, hence |x_j| = 1 for all j;  non-unimodular: some |K_j| excludes 1;
     (d) the stored 48 vectors of fourier6.json (200-bit midpoints of the second program) lie strictly
         inside the certified unimodular boxes, one in each.
  What is NOT proved: that there are no further roots.  "156 is all of them" is the classical count
  (Bjorck-Froberg, cited).  Enclosures are rigorous only for the boxes; the search is heuristic.

Usage (from this folder, python3 -I is fine):
  python3 -I certify_d6_roots.py find   cyclic6_roots.npz [seed] [fourier6.json]   # search + certify (seconds)
  python3 -I certify_d6_roots.py verify cyclic6_roots.npz [fourier6.json]          # certify the shipped midpoints only
Prints a line starting with COUNTS: found=... certified=... unimodular=... certified_non_unimodular=... ;
exits 1 unless these are 156, 156, 48, 108, undecided 0, boxes disjoint, and the 48 stored vectors match.
"""
import itertools, json, math, os, sys, time
from fractions import Fraction

import numpy as np
from flint import acb, acb_mat, arb, ctx

d = 6
TARGET = 156
R_EXP = 30
ctx.prec = 128
W = np.exp(2j * np.pi / d)
HERE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------ numerical search
def G(Xv):
    B = Xv.shape[0]
    x = np.concatenate([np.ones((B, 1), complex), Xv], 1)
    ix = 1 / x
    r = np.empty((B, d - 1), complex)
    J = np.empty((B, d - 1, d - 1), complex)
    for k in range(1, d):
        xk = np.roll(x, -k, 1)
        t = xk * ix
        r[:, k - 1] = t.sum(1)
        J[:, k - 1, :] = (np.roll(ix, k, 1) - t * ix)[:, 1:]
    return r, J


def newton_x(Xv, iters=60):
    with np.errstate(all="ignore"):
        r, J = G(Xv)
        f = np.abs(r).max(1)
        for _ in range(iters):
            dx = np.linalg.solve(J, -r[:, :, None])[:, :, 0]
            step = np.ones(len(Xv))
            best = Xv.copy()
            bf = f.copy()
            for _ in range(6):
                Xn = Xv + step[:, None] * dx
                rn, _ = G(Xn)
                fn = np.abs(rn).max(1)
                ok = np.isfinite(fn) & (fn < bf)
                best = np.where(ok[:, None], Xn, best)
                bf = np.where(ok, fn, bf)
                step = np.where(ok, step, step / 2)
                if ok.all():
                    break
            Xv = best
            r, J = G(Xv)
            f = np.abs(r).max(1)
    return Xv, f


def newton_log(U, iters=80):
    with np.errstate(all="ignore"):
        for _ in range(iters):
            X = np.exp(U)
            r, J = G(X)
            Jl = J * X[:, None, :]
            dx = np.linalg.solve(Jl, -r[:, :, None])[:, :, 0]
            s = np.minimum(1, 0.5 / np.maximum(np.abs(dx).max(1), 1e-300))
            U = U + s[:, None] * dx
            U = np.where(np.isfinite(U), U, 0)
        X = np.exp(U)
        r, _ = G(X)
    return X, np.abs(r).max(1)


def resid(Xv):
    with np.errstate(all="ignore"):
        r, _ = G(Xv)
    return np.abs(r).max(1)


UNITS = [a for a in range(1, d) if math.gcd(a, d) == 1]          # [1, 5]
GROUP = list(itertools.product(UNITS, [0, 1], [0, 1], range(d), range(d)))
assert len(GROUP) == 288


def image(x, a, inv, cj, s, m):
    y = x[:, (a * np.arange(d)) % d]
    if inv:
        y = 1 / y
    if cj:
        y = y.conj()
    y = np.roll(y, -s, 1)
    y = y / y[:, :1]
    return y * W ** (m * np.arange(d))


def orbit(x):
    x10 = np.concatenate([[1], x])[None]
    return np.array([image(x10, *g)[0, 1:] for g in GROUP])


def key(X, dec=6):
    a = np.round(np.concatenate([X.real, X.imag], 1), dec) + 0.0
    return [tuple(v) for v in a]


def verify_symmetries(X):
    x10 = np.concatenate([np.ones((len(X), 1), complex), X], 1)
    gens = {"dilation5(reversal)": (5, 0, 0, 0, 0), "inversion": (1, 1, 0, 0, 0), "conjugation": (1, 0, 1, 0, 0),
            "shift": (1, 0, 0, 1, 0), "modulation": (1, 0, 0, 0, 1)}
    for name, g in gens.items():
        r = resid(image(x10, *g)[:, 1:]).max()
        print(f"symmetry check {name}: max residual of images = {r:.2e}", flush=True)
        assert r < 1e-9, name


def find_roots(seed, time_limit=240.0):
    rng = np.random.default_rng(seed)
    t0 = time.time()
    roots, known = [], set()
    starts, batch, it, checked = 0, 2000, 0, False
    while time.time() - t0 < time_limit and len(roots) < TARGET:
        it += 1
        sig = rng.choice([0.4, 0.7, 1.0, 2.0])
        if it % 2:
            X0 = np.exp(rng.normal(0, sig, (batch, d - 1)) + 1j * rng.uniform(0, 2 * np.pi, (batch, d - 1)))
            X, f = newton_x(X0)
        else:
            X, f = newton_log(rng.normal(0, sig, (batch, d - 1)) + 1j * rng.uniform(0, 2 * np.pi, (batch, d - 1)))
        starts += batch
        good = X[f < 1e-9]
        if len(good):
            good, f2 = newton_x(good, 4)
            good = good[f2 < 1e-12]
        if len(good) and not checked:
            verify_symmetries(good[:50])
            checked = True
        new = [v for v, k in zip(good, key(good)) if k not in known]
        for v in new:
            if tuple(key(v[None])[0]) in known:
                continue
            orb = orbit(v)
            orb = orb[resid(orb) < 1e-9]
            for o, k in zip(orb, key(orb)):
                if k not in known:
                    known.add(k)
                    roots.append(o)
        print(f"starts {starts} converged {len(good)} distinct_roots {len(roots)} t={time.time()-t0:.0f}s", flush=True)
    return np.array(roots), starts


# ------------------------------------------------------------------ certification (Arb)
def radius(c):
    return math.ldexp(max(1, math.ceil(abs(c))), -R_EXP)


def exact_acb(z):
    return acb(arb(float(z.real)), arb(float(z.imag)))


def gfun(x):
    ix = [1 / v for v in x]
    return [sum((x[(j + k) % d] * ix[j] for j in range(d)), acb(0)) for k in range(1, d)], ix


def jac(x, ix):
    return [[ix[(m - k) % d] - x[(m + k) % d] * ix[m] * ix[m] for m in range(1, d)] for k in range(1, d)]


UNIMOD, NONUNIMOD, UNDECIDED, KRAW_FAIL = 1, 2, 0, -1


def krawczyk_box(v, rr):
    """v: complex128 midpoints (5,), rr: half-widths.  Returns (ok, K list of acb, centre list c)."""
    c = [exact_acb(z) for z in v]
    x = [acb(1)] + c
    g, ix = gfun(x)
    Jc = jac(x, ix)
    Jf = np.array([[complex(float(e.real.mid()), float(e.imag.mid())) for e in row] for row in Jc])
    try:
        Yf = np.linalg.inv(Jf)
    except np.linalg.LinAlgError:
        return False, None, c
    n = d - 1
    Y = acb_mat(n, n, [acb(float(z.real), float(z.imag)) for z in Yf.ravel()])
    discs = [acb(arb(0, r), arb(0, r)) for r in rr]
    X = [acb(1)] + [c[i] + discs[i] for i in range(n)]
    gX, ixX = gfun(X)
    JX = acb_mat(n, n, [e for row in jac(X, ixX) for e in row])
    I5 = acb_mat(n, n, [acb(1) if i == j else acb(0) for i in range(n) for j in range(n)])
    dev = (Y * acb_mat(n, 1, g)) * (-1) + (I5 - Y * JX) * acb_mat(n, 1, discs)       # K - c
    ok = True
    K = []
    for i in range(n):
        e = dev[i, 0]
        ok &= bool(abs(e.real) < arb(rr[i])) and bool(abs(e.imag) < arb(rr[i]))
        K.append(c[i] + e)
    return ok, K, c


def certify_one(v):
    rr = [radius(z) for z in v]
    ok, K, c = krawczyk_box(v, rr)
    if not ok:
        return KRAW_FAIL, 0.0
    uni = True
    for i in range(d - 1):
        s = 1 / K[i].conjugate() - c[i]
        uni &= bool(abs(s.real) < arb(rr[i])) and bool(abs(s.imag) < arb(rr[i]))
    if uni:
        return UNIMOD, 0.0
    best = 0.0
    for i in range(d - 1):
        m = abs(K[i])
        if bool(m.upper() < 1) or bool(m.lower() > 1):
            dist = abs(m - 1).lower()
            best = max(best, float(dist.mid()) if dist.is_finite() else 0.0)
    if best > 0:
        return NONUNIMOD, best
    return UNDECIDED, 0.0


def disjointness(C, rad):
    """Pairs of boxes: shown disjoint in float64 with margin 1e-9, otherwise in exact rationals."""
    N = len(C)
    assert np.abs(C).max() < 1e3 and rad.max() < 1e-7
    P = np.concatenate([C.real, C.imag], 1)
    Rr = np.concatenate([rad, rad], 1)
    order = np.argsort(C[:, 0].real, kind="stable")
    key0 = C[order, 0].real
    hi = np.searchsorted(key0, key0 + 1e-6, side="right")
    npairs = nexact = nfail = 0
    for a in range(N):
        b0, b1 = a + 1, hi[a]
        if b1 <= b0:
            continue
        i = order[a]
        js = order[b0:b1]
        npairs += len(js)
        sep = np.abs(P[js] - P[i]) > (Rr[js] + Rr[i] + 1e-9)
        for j in js[~sep.any(1)]:
            nexact += 1
            ok = any(abs(Fraction(float(P[i, t])) - Fraction(float(P[j, t]))) > Fraction(float(Rr[i, t])) + Fraction(float(Rr[j, t]))
                     for t in range(2 * (d - 1)))
            nfail += (not ok)
    return npairs, nexact, nfail


def load_stored(path):
    """200-bit midpoints of the second program: 48 vectors, six coordinates 're im' strings (x_0 = 1 first)."""
    mids = json.load(open(path))["mids"]

    def parts(s):                                    # '[a +/- r] [b +/- r]' or '1.0 0' -> (a, b) as strings
        toks, out, skip = s.replace("[", " ").replace("]", " ").split(), [], False
        for t in toks:
            if skip:
                skip = False
            elif t == "+/-":
                skip = True
            else:
                out.append(t)
        assert len(out) == 2, s
        return out[0], out[1]
    return [[parts(row[k]) for k in range(1, d)] for row in mids]


def certify_all(C, stored_path=None):
    t0 = time.time()
    N = len(C)
    print(f"certifying {N} candidate roots; prec={ctx.prec} bits, box half-width 2^-{R_EXP}*max(1,ceil|c|)", flush=True)
    res = [certify_one(v) for v in C]
    status = np.array([s for s, _ in res], dtype=np.int8)
    dist = np.array([k for _, k in res])
    rad = np.array([[radius(z) for z in row] for row in C])
    cert = int((status != KRAW_FAIL).sum())
    print(f"Krawczyk: {cert}/{N} boxes contain exactly one root; {time.time()-t0:.0f}s", flush=True)
    good = status != KRAW_FAIL
    npairs, nexact, nfail = disjointness(C[good], rad[good])
    print(f"Disjointness of the {cert} boxes: window pairs examined {npairs}, exact-rational fallbacks {nexact}, "
          f"pairs NOT shown disjoint {nfail}", flush=True)
    nu = int((status == UNIMOD).sum())
    nn = int((status == NONUNIMOD).sum())
    nund = int((status == UNDECIDED).sum())
    match_ok = None
    if stored_path:
        pts = load_stored(stored_path)
        F = np.array([[complex(float(a), float(b)) for a, b in p] for p in pts])
        used = {}
        for s, (p, f) in enumerate(zip(pts, F)):
            i = int(np.argmin(np.abs(C - f).max(1)))
            ok = True
            for m, (a, b) in enumerate(p):
                r = arb(rad[i, m])
                ok &= bool(abs(arb(a) - arb(float(C[i, m].real))) < r) and bool(abs(arb(b) - arb(float(C[i, m].imag))) < r)
            if ok:
                used[i] = s
        uni_idx = set(np.nonzero(status == UNIMOD)[0].tolist())
        match_ok = (set(used) == uni_idx and len(used) == len(pts))
        print(f"Stored 48 vectors: {len(used)} lie strictly inside distinct certified boxes; "
              f"boxes hit equal the certified unimodular boxes: {set(used) == uni_idx}", flush=True)
    mind = float(dist[status == NONUNIMOD].min()) if nn else float("nan")
    print(f"smallest (over the {nn} non-unimodular roots) of the certified max_j | |x_j| - 1 | : {mind:.4f}", flush=True)
    print(f"COUNTS: found={N} certified={cert} unimodular={nu} certified_non_unimodular={nn} undecided={nund} "
          f"krawczyk_failed={N-cert} boxes_pairwise_disjoint={nfail == 0} stored48_match={match_ok}; total time {time.time()-t0:.0f}s", flush=True)
    good_all = (N == TARGET and cert == N and nu == 48 and nn == 108 and nund == 0 and nfail == 0 and match_ok in (True, None))
    return status, dist, good_all


if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    stored = os.path.join(HERE, "fourier6.json")
    if mode == "find":
        seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        if len(sys.argv) > 4:
            stored = sys.argv[4]
        C, starts = find_roots(seed)
        print(f"FINAL distinct roots (rounded 1e-6 keys): {len(C)} after {starts} starts", flush=True)
    elif mode == "verify":
        if len(sys.argv) > 3:
            stored = sys.argv[3]
        C = np.load(out)["x1_to_x5"].astype(complex)
    else:
        raise SystemExit(__doc__)
    status, dist, good = certify_all(C, stored)
    if mode == "find":
        np.savez_compressed(out, x1_to_x5=C, status=status, nonunimodular_distance=dist.astype(np.float32),
                            note=np.array("status: 1 unimodular (sigma test), 2 certified non-unimodular, 0 undecided, -1 Krawczyk failed. "
                                          "x_0 = 1; box half-width 2^-30*max(1,ceil|c|) per real/imag part; midpoints complex128"))
    print("OK" if good else "FAIL: expected 156 certified roots, 48 unimodular, 108 non-unimodular, boxes disjoint, 48 stored vectors matched")
    sys.exit(0 if good else 1)
