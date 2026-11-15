#!/usr/bin/env python3
"""Orthogonality graph of the 48 unimodular cyclic 6-roots in ball arithmetic (Arb via python-flint).

Input: `cyclic6_roots.npz` (midpoints of the 156 roots, produced and certified by certify_d6_roots.py).
Steps (all enclosures are 300-bit balls; no floating-point decision is used below):
  1. For each of the 48 roots with status "unimodular": polish by Newton at 300 bits, then a Krawczyk test
     on a box of half-width 1e-40 (any approximate inverse is allowed; rigor does not depend on it) proves a
     unique root of g(x) = 0 in the box, and the sigma test (1/conj(K) inside the box) proves |x_j| = 1.
     The enclosure K of the root (radius about 1e-78: the Krawczyk image of a 1e-40 box is about 1e-40 times smaller) is used below.
  2. For all 1128 pairs (u, v): enclosure of <u, v> = sum conj(u_k) v_k.
        "certified not orthogonal": the enclosure excludes 0,
        "possibly orthogonal":      the enclosure contains 0.
     Enclosures can never prove EXACT orthogonality.  The possibly-orthogonal graph therefore contains the
     true orthogonality graph (a superset); this is the safe direction for the report's use, because a
     missing edge would be the only way to lose a candidate basis, and no true edge can be missing.
  3. Maximal cliques of the possibly-orthogonal graph (own Bron-Kerbosch), their sizes, the edges they
     cover, and the number of six-cliques through each vertex.
  4. For each six-clique B: the triple {I, F_6, B} is "mutually unbiased up to the enclosure width":
     the enclosures of |x_j|^2 - 1 (unbiased to I), of |sum_j x_j w^(-jk)|^2 - 6 (unbiased to F_6) and of
     <b_i, b_j> (i != j, orthogonality inside B) all contain 0 and have radius below 1e-70.
  5. For the 120 pairs of the 16 bases: the largest, over the 36 overlaps, of the certified lower bound of
     | |<u,v>|^2 - 6 | (unnormalised; 6 means unbiased); a positive lower bound means "certified to differ
     from the unbiased value" for some overlap, so the two bases are not mutually unbiased.
Usage: python3 -I certify_graph.py [cyclic6_roots.npz]      exit 0 iff the expected counts hold.
"""
import itertools, os, sys

import numpy as np
from flint import acb, acb_mat, arb, ctx

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import certify_d6_roots as cr          # noqa: E402  (shared definitions of the system g_k; sets ctx.prec = 128)

ctx.prec = 300
d = 6
R = arb("1e-40")


def enclose(v):
    """v: complex128 midpoints (5,).  Returns (K, ok): list of 6 acb (x_0 = 1 first), ok = unique root and unimodular."""
    p = [acb(1)] + [cr.exact_acb(z) for z in v]
    for _ in range(6):                                    # Newton at 300 bits on the midpoints
        g, ix = cr.gfun(p)
        J = acb_mat(5, 5, [e for row in cr.jac(p, ix) for e in row])
        dx = J.solve(acb_mat(5, 1, g))
        p = [acb(1)] + [acb((p[i + 1] - dx[i, 0]).real.mid(), (p[i + 1] - dx[i, 0]).imag.mid()) for i in range(5)]
    g, ix = cr.gfun(p)
    Jc = acb_mat(5, 5, [e for row in cr.jac(p, ix) for e in row])
    Y = Jc.inv()
    disc = acb(arb(0, R.upper()), arb(0, R.upper()))
    X = [acb(1)] + [p[i + 1] + disc for i in range(5)]
    gX, ixX = cr.gfun(X)
    JX = acb_mat(5, 5, [e for row in cr.jac(X, ixX) for e in row])
    I5 = acb_mat(5, 5, [acb(1) if i == j else acb(0) for i in range(5) for j in range(5)])
    dev = (Y * acb_mat(5, 1, g)) * (-1) + (I5 - Y * JX) * acb_mat(5, 1, [disc] * 5)
    ok = all(bool(abs(dev[i, 0].real) < R) and bool(abs(dev[i, 0].imag) < R) for i in range(5))
    K = [acb(1)] + [p[i + 1] + dev[i, 0] for i in range(5)]
    uni = all(bool(abs((1 / K[i].conjugate() - p[i]).real) < R) and bool(abs((1 / K[i].conjugate() - p[i]).imag) < R)
              for i in range(1, 6))
    return K, ok and uni


def load_unimodular(path):
    z = np.load(path)
    C, st = z["x1_to_x5"].astype(complex), z["status"]
    idx = np.nonzero(st == 1)[0]
    vecs, allok = [], True
    for i in idx:
        K, ok = enclose(C[i])
        vecs.append(K)
        allok &= ok
    return vecs, allok


def inner(u, v):
    return sum((u[k].conjugate() * v[k] for k in range(d)), acb(0))


def pair_data(vecs):
    n = len(vecs)
    ip = [[None] * n for _ in range(n)]
    for a in range(n):
        for b in range(a, n):
            ip[a][b] = inner(vecs[a], vecs[b])
            ip[b][a] = ip[a][b].conjugate()
    return ip


def bron_kerbosch(adj, n):
    out = []

    def bk(Rr, P, X):
        if not P and not X:
            out.append(tuple(sorted(Rr)))
            return
        piv = max(P | X, key=lambda u: len(adj[u] & P))
        for v in list(P - adj[piv]):
            bk(Rr | {v}, P & adj[v], X & adj[v])
            P = P - {v}
            X = X | {v}
    bk(set(), set(range(n)), set())
    return out


def build(path):
    """Returns dict with vecs, ip (enclosures), orth_possible (bool matrix), certified_nonorth (bool matrix)."""
    vecs, ok = load_unimodular(path)
    n = len(vecs)
    ip = pair_data(vecs)
    possible = np.zeros((n, n), bool)
    nonorth = np.zeros((n, n), bool)
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            if ip[a][b].contains(0):
                possible[a, b] = True
            else:
                nonorth[a, b] = True
    return dict(vecs=vecs, ok=ok, ip=ip, orth_possible=possible, nonorth=nonorth)


def main(path):
    D = build(path)
    vecs, ip, poss, non = D["vecs"], D["ip"], D["orth_possible"], D["nonorth"]
    n = len(vecs)
    good = True

    def check(cond, msg):
        nonlocal good
        print(("ok  " if cond else "FAIL"), msg)
        good &= bool(cond)

    print(f"{n} unimodular roots re-enclosed (300 bits, Krawczyk box 1e-40, sigma test): all certified = {D['ok']}")
    check(n == 48 and D["ok"], "48 vectors, each Krawczyk-certified (unique root in its box) and unimodular")
    maxrad = max(float(max(e.real.rad(), e.imag.rad())) for K in vecs for e in K)
    print(f"largest radius of a coordinate enclosure: {maxrad:.2e}")

    npairs = n * (n - 1) // 2
    pp = int(np.triu(poss, 1).sum())
    pn = int(np.triu(non, 1).sum())
    print(f"pairs: {npairs}; possibly orthogonal (enclosure contains 0): {pp}; certified not orthogonal: {pn}")
    check(pp == 300 and pn == 828, "300 possibly-orthogonal pairs, 828 certified non-orthogonal")
    lo = min(float(ip[a][b].abs_lower().mid()) for a in range(n) for b in range(a + 1, n) if non[a, b])
    hi = max(float(abs(ip[a][b]).upper()) for a in range(n) for b in range(a + 1, n) if poss[a, b])
    radmax = max(float(max(ip[a][b].real.rad(), ip[a][b].imag.rad())) for a in range(n) for b in range(a + 1, n) if poss[a, b])
    print(f"smallest certified lower bound of |<u,v>| over the non-orthogonal pairs: {lo:.4f} (unnormalised, norm^2 = 6)")
    print(f"largest |<u,v>| upper end over the possibly-orthogonal pairs: {hi:.2e}; largest enclosure radius there: {radmax:.2e}")
    check(lo > 0.9 and hi < 1e-70, "separation: non-orthogonal pairs have |<u,v>| >= 0.9, possibly-orthogonal ones are enclosed in a ball of radius < 1e-70 around 0")
    print("NOTE: enclosures cannot prove exact orthogonality; the possibly-orthogonal graph is a superset of the true graph.")

    adj = [set(np.nonzero(poss[i])[0].tolist()) for i in range(n)]
    cl = bron_kerbosch(adj, n)
    by = {}
    for c in cl:
        by[len(c)] = by.get(len(c), 0) + 1
    print("maximal cliques by size:", dict(sorted(by.items())))
    six = [c for c in cl if len(c) == 6]
    cover = set()
    for c in six:
        cover |= {frozenset(p) for p in itertools.combinations(c, 2)}
    through = [sum(1 for c in six if v in c) for v in range(n)]
    print(f"six-cliques: {len(six)}; edges covered: {len(cover)}; vertices per clique count: {sorted(set(through))}")
    check(len(six) == 16 and len(cover) == 228 and set(through) == {2}, "16 six-cliques cover 228 of the 300 pairs; each vertex lies in exactly two of them")
    check(max(by) == 6, "no clique larger than six")

    # (4) triples {I, F_6, B}
    wk = [[(acb(0, 1) * (-2 * arb.pi() * j * k / 6)).exp() for k in range(6)] for j in range(6)]  # exp(-2 pi i jk/6)
    worst = 0.0
    all_in = True
    for c in six:
        for v in c:
            u = vecs[v]
            for j in range(6):
                e = abs(u[j]) ** 2 - 1
                all_in &= e.contains(0)
                worst = max(worst, float(e.rad()))
            for k in range(6):
                X = sum((u[j] * wk[j][k] for j in range(6)), acb(0))
                e = abs(X) ** 2 - 6
                all_in &= e.contains(0)
                worst = max(worst, float(e.rad()))
        for a, b in itertools.combinations(c, 2):
            e = ip[a][b]
            all_in &= e.contains(0)
            worst = max(worst, float(max(e.real.rad(), e.imag.rad())))
    print(f"triples {{I, F_6, B}}: every required value (|x_j|^2 = 1, |DFT|^2 = 6, <b_i, b_j> = 0) enclosed with 0 inside; largest radius {worst:.2e}")
    check(all_in and worst < 1e-70, "all 16 triples {I, F_6, B} are mutually unbiased / orthonormal up to the enclosure width (< 1e-70)")

    # (5) pairs of bases
    mind = None
    for A, B in itertools.combinations(six, 2):
        best = max(float((abs(ip[a][b]) ** 2 - 6).abs_lower().mid()) for a in A for b in B)
        mind = best if mind is None else min(mind, best)
    print(f"120 pairs of bases: smallest over pairs of the largest certified lower bound of | |<u,v>|^2 - 6 | : {mind:.6f} (unnormalised; = {mind/36:.6f} in probability units)")
    check(len(list(itertools.combinations(six, 2))) == 120 and mind > 5.99, "for each of the 120 pairs of bases some overlap is certified to differ from the unbiased value (by at least 6.0 unnormalised, i.e. 1/6 in probability)")

    print("OK" if good else "FAIL")
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "cyclic6_roots.npz")))
