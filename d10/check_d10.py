"""Independent check of the dimension-ten Fourier-pair data (own code; reads only the list of 3,040 points and the
list of 1,136 index sets).  Steps:
  1. Krawczyk (Arb, complex polydiscs) for each stored point: a unique root of g_k(x) = sum_j x_{j+k}/x_j = 0, k=1..9
     (x_0 = 1) lies within R of it; sigma(x) = 1/conj(x) maps that root into the same disc => it is unimodular.
  2. Pairwise inner products: which pairs can be orthogonal (enclosure contains 0), smallest certified non-zero one.
  3. All 10-cliques of the possibly-orthogonal graph; compare with the stored list of bases.
  4. For every clique B and every vector v: max_u ||<u,v>|^2 - 10| ; minimum over (B, v).
What this does NOT check: that the 3,040 are ALL unimodular solutions (completeness)."""
import sys, json, time, itertools
import numpy as np
from flint import arb, acb, acb_mat, ctx
ctx.prec = 200
U = sys.argv[1]
d = 10
t0 = time.time()
rows = [l.split() for l in open(U + "/data/exact/bu10hp_unimod.txt")]
N = len(rows); assert N == 3040 and all(len(r) == 20 for r in rows)
R = arb("1e-30")
disc0 = acb(arb(0, R.upper()), arb(0, R.upper()))          # square of half-width R about 0
w = None


def G(x):                                                   # x: list of 10 acb, x[0] = 1
    return [sum((x[(j + k) % d] / x[j] for j in range(d)), acb(0)) for k in range(1, d)]


def J(x):
    M = [[None] * 9 for _ in range(9)]
    for k in range(1, d):
        for m in range(1, d):
            M[k - 1][m - 1] = 1 / x[(m - k) % d] - x[(m + k) % d] / (x[m] * x[m])
    return M


encl = []; fl = np.zeros((N, d), complex); worst_ratio = 0.0; nfail = 0; n_uni = 0
for idx, r in enumerate(rows):
    p = [acb(1)] + [acb(arb(r[1 + 2 * i]), arb(r[2 + 2 * i])) for i in range(9)]
    pf = np.array([complex(float(c.real.mid()), float(c.imag.mid())) for c in p])
    fl[idx] = pf
    Jf = np.array([[complex(float(e.real.mid()), float(e.imag.mid())) for e in row] for row in J(p)])
    Yf = np.linalg.inv(Jf)
    Y = acb_mat(9, 9, [acb(float(z.real), float(z.imag)) for z in Yf.ravel()])
    X = [acb(1)] + [p[i] + disc0 for i in range(1, d)]
    JX = acb_mat(9, 9, [e for row in J(X) for e in row])
    Gp = acb_mat(9, 1, G(p))
    I9 = acb_mat(9, 9, [acb(1) if i == j else acb(0) for i in range(9) for j in range(9)])
    dev = (Y * Gp) * (-1) + (I9 - Y * JX) * acb_mat(9, 1, [disc0] * 9)      # K - p
    ok = True; Kx = [acb(1)]
    for i in range(9):
        e = dev[i, 0]
        m = max(float(abs(e.real).upper()), float(abs(e.imag).upper()))
        worst_ratio = max(worst_ratio, m / float(R.upper()))
        ok &= (abs(e.real) < R) and (abs(e.imag) < R)       # arb '<' is certified
        Kx.append(p[i + 1] + e)
    if not ok:
        nfail += 1; encl.append(Kx); continue
    # sigma test: 1/conj(K_i) inside X_i for all i
    uni = True
    for i in range(1, d):
        s = 1 / Kx[i].conjugate() - p[i]
        uni &= (abs(s.real) < R) and (abs(s.imag) < R)
    n_uni += uni
    encl.append(Kx)
print(f"1. Krawczyk: {N - nfail}/{N} unique roots within 1e-30 of the stored points; "
      f"max |K - p|/R = {worst_ratio:.2e}; unimodular by the sigma test: {n_uni}/{N}   [{time.time()-t0:.0f}s]", flush=True)

# 2. inner products (float64 first; arb on the near-zero ones)
Gm = fl.conj() @ fl.T
A = np.abs(Gm); np.fill_diagonal(A, 10)
small = A < 1e-6
iu = np.triu_indices(N, 1)
print("   float64: pairs with |<u,v>| < 1e-6:", int(small[iu].sum()), "; smallest |<u,v>| among the others: %.7f" % A[iu][~small[iu]].min())
contains0 = 0; notzero = 0; maxrad = 0.0
for i, j in zip(*np.nonzero(np.triu(small, 1))):
    ip = sum((encl[i][k].conjugate() * encl[j][k] for k in range(d)), acb(0))
    if ip.contains(0):
        contains0 += 1; maxrad = max(maxrad, float(abs(ip).upper()))
    else:
        notzero += 1
print(f"2. Arb on those pairs: enclosure contains 0 for {contains0} (largest enclosure {maxrad:.1e}); certified non-zero: {notzero}")
# rigorous non-orthogonality of the rest: float error of a 10-term sum of unit-modulus products is < 1e-13
# 3. cliques
adj = [set(np.nonzero(small[i])[0].tolist()) for i in range(N)]
deg = np.array([len(a) for a in adj])
print("   degrees:", {int(k): int(v) for k, v in zip(*np.unique(deg, return_counts=True))})
cl10 = set(); maxsize = 0
def bk(Rr, P, Xx):
    global maxsize
    if not P and not Xx:
        maxsize = max(maxsize, len(Rr))
        if len(Rr) >= d:
            for s in itertools.combinations(sorted(Rr), d): cl10.add(s)
        return
    pivot = max(P | Xx, key=lambda u: len(adj[u] & P))
    for v in list(P - adj[pivot]):
        bk(Rr | {v}, P & adj[v], Xx & adj[v]); P.remove(v); Xx.add(v)
sys.setrecursionlimit(10000)
bk(set(), set(range(N)), set())
stored = set(tuple(sorted(b)) for b in json.load(open(U + "/data/exact/d10_analysis.json"))["bases"])
print(f"3. largest clique size {maxsize}; 10-cliques: {len(cl10)}; identical to the stored list of bases: {cl10 == stored}   [{time.time()-t0:.0f}s]", flush=True)
# 4. extension margins
P2 = A ** 2
Bl = sorted(cl10); best = 1e9; bestpair = 1e9
for B in Bl:
    dfc = np.abs(P2[list(B), :] - 10).max(axis=0)          # for each v: max over u in B
    best = min(best, dfc.min())
print(f"4. min over (basis B, vector v) of max_u ||<u,v>|^2 - 10| = {best:.5f}  (normalised probabilities: {best/100:.5f})")
Bi = np.array(Bl)
mp = 1e9
for a in range(len(Bl)):
    blk = np.abs(P2[np.ix_(Bi[a], np.arange(N))] - 10)      # 10 x N
    # pair defect with every other basis b: max over u in B_a, v in B_b
    m = blk.max(axis=0)[Bi].max(axis=1); m[a] = 1e9
    mp = min(mp, m.min())
print(f"   min over pairs of bases of max ||<u,v>|^2 - 10| = {mp:.5f}")
np.save(U + "/../d10_floats.npy", fl) if False else None
np.save("/home/claude/work/d10/vecs.npy", fl); json.dump([list(b) for b in Bl], open("/home/claude/work/d10/bases.json", "w"))
print(f"done in {time.time()-t0:.0f}s")
