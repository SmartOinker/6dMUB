"""Independent re-derivation (double precision) of the dimension-six Fourier-pair funnel 156 -> 48 -> 16 -> 0.

Uses only the stored 48 enclosure midpoints d6_fourier/fourier6_vecs.npy (written by d6_fourier/fourier6.py) for the graph
part and none of the Arb code.  Not a proof (floating point, thresholds), a cross-check of the counts in the report:
  1. the 48 vectors have unimodular entries and are unbiased to F_6;
  2. orthogonality graph: 300 edges, 16 cliques of size 6 and none larger, the 16 cliques cover 228 of the 300 edges,
     every vertex lies in exactly two cliques;
  3. for each of the 120 pairs of the 16 bases some overlap differs from the unbiased value (smallest such defect printed);
  4. an own random-start Newton search for the cyclic 6-roots (x_0 = 1, g_k = sum_j x_{j+k}/x_j = 0): counts the distinct
     complex solutions found (the classical count is 156) and how many are unimodular (48);
  5. numerical minima of the energy on the 16 triples: 12 / 2 / 2 triples at 0.0326759 / 0.0238354 / 0.0387628 (40 BFGS starts each).
Prints OK or raises.  Run from anywhere (about 10 s).
"""
import itertools, os, json
import numpy as np
from scipy.optimize import minimize
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
d = 6
V = np.load(os.path.join(ROOT, "d6_fourier/fourier6_vecs.npy")); assert V.shape == (48, 6)
F6 = np.exp(2j*np.pi*np.outer(np.arange(d), np.arange(d))/d)
assert np.abs(np.abs(V) - 1).max() < 1e-12 and np.abs(np.abs(V @ F6.conj().T)**2 - 6).max() < 1e-9      # unimodular, unbiased to F_6
assert len({tuple(np.round(v, 6)) for v in V}) == 48
print("1. 48 distinct vectors: unimodular (max defect %.1e) and |F v|^2 = 6 (max defect %.1e)" % (np.abs(np.abs(V) - 1).max(), np.abs(np.abs(V @ F6.conj().T)**2 - 6).max()))

G = np.abs(V.conj() @ V.T); np.fill_diagonal(G, 6)
orth = G < 1e-9; edges = [(i, j) for i in range(48) for j in range(i + 1, 48) if orth[i, j]]
others = G[~orth & ~np.eye(48, dtype=bool)]
assert len(edges) == 300 and others.min() > 0.1
adj = [set(np.nonzero(orth[i])[0].tolist()) for i in range(48)]
cl = set(); big = 0
def bk(R, P, X):
    global big
    if not P and not X:
        big = max(big, len(R))
        if len(R) >= d: cl.update(itertools.combinations(sorted(R), d))
        return
    u = max(P | X, key=lambda w: len(adj[w] & P))
    for v in list(P - adj[u]):
        bk(R | {v}, P & adj[v], X & adj[v]); P.remove(v); X.add(v)
bk(set(), set(range(48)), set())
bases = sorted(cl); assert len(bases) == 16 and big == 6
cov = {e for b in bases for e in itertools.combinations(b, 2)}; deg = np.bincount([v for b in bases for v in b], minlength=48)
assert len(cov) == 228 and (deg == 2).all()
print("2. graph: %d edges (smallest non-orthogonal |<u,v>| = %.4f); %d six-cliques, largest clique %d; they cover %d of 300 edges; every vertex lies in %d cliques" % (len(edges), others.min(), len(bases), big, len(cov), deg[0]))
worst = 1e9
for a, b in itertools.combinations(range(16), 2):
    M = np.abs(V[list(bases[a])].conj() @ V[list(bases[b])].T)**2          # unimodular scaling: unbiased means 6
    worst = min(worst, np.abs(M - 6).max())
assert worst > 0.1
print("3. 120 pairs of candidate bases: in every pair some squared overlap differs from the unbiased value 6 by at least %.4f (unimodular scaling), so no two are mutually unbiased (floating point)" % worst)

# 4. own Newton search for cyclic 6-roots
rng = np.random.default_rng(6)
def gj(X):
    x = np.concatenate([np.ones((len(X), 1), complex), X], 1); ix = 1/x
    r = np.empty((len(X), 5), complex); J = np.empty((len(X), 5, 5), complex)
    for k in range(1, 6):
        t = np.roll(x, -k, 1)*ix; r[:, k - 1] = t.sum(1); J[:, k - 1, :] = (np.roll(ix, k, 1) - t*ix)[:, 1:]
    return r, J
roots = []
with np.errstate(all="ignore"):
    for batch in range(60):
        X = np.exp(rng.normal(0, 0.8, size=(4000, 5)) + 1j*rng.uniform(0, 2*np.pi, size=(4000, 5)))
        for it in range(80):
            r, J = gj(X)
            try: dx = np.linalg.solve(J, -r[:, :, None])[:, :, 0]
            except np.linalg.LinAlgError: break
            nrm = np.abs(dx).max(1, keepdims=True); dx = np.where(nrm > 1.0, dx/nrm, dx)      # damped step
            X = X + dx
        r, J = gj(X); ok = np.isfinite(r).all(1) & (np.abs(r).max(1) < 1e-11) & (np.abs(X) < 1e6).all(1) & (np.abs(X) > 1e-6).all(1)
        roots.append(X[ok])
R = np.concatenate(roots); keys = {}
for x in R:
    k = tuple(np.round(np.concatenate([x.real, x.imag]), 5)); keys[k] = x
pts = np.array(list(keys.values())); uni = (np.abs(np.abs(pts) - 1) < 1e-8).all(1)
print("4. own Newton search (240,000 starts): %d distinct cyclic 6-roots found (classical count 156), %d unimodular (report: 48)" % (len(pts), uni.sum()))
assert len(pts) == 156 and uni.sum() == 48

# 5. numerical energy minima of the 16 triples
Dd = json.load(open(os.path.join(ROOT, "d6_fourier/fourier6.json")))
I6 = np.eye(6); F = F6/np.sqrt(6); levels = []
for Bx in bases:
    Bm = V[list(Bx)].T/np.sqrt(6); M = np.concatenate([u.conj().T for u in (I6, F, Bm)])
    def f(xx):
        psi = xx[:6] + 1j*xx[6:]; n2 = (abs(psi)**2).sum(); a = M @ psi; p = abs(a)**2/n2; e = p - 1/6
        gc = 2*(M.conj().T @ (2*e*a))/n2 - 2*(2*e*p).sum()*psi/n2
        return (e**2).sum(), np.concatenate([gc.real, gc.imag])
    levels.append(min(minimize(f, rng.normal(size=12), jac=True, method="BFGS").fun for _ in range(40)))
cnt = {k: sum(1 for L in levels if abs(L - k) < 2e-6) for k in (0.0326759, 0.0238354, 0.0387628)}
assert cnt == {0.0326759: 12, 0.0238354: 2, 0.0387628: 2}, (cnt, sorted(levels))
assert sorted(round(o["Emin"], 7) for o in Dd["energy"]) == sorted(round(L, 7) for L in levels)
print("5. numerical energy minima over the 16 triples (own BFGS, 40 starts each): %s triples at 0.0326759 / 0.0238354 / 0.0387628, identical to the stored list" % list(cnt.values()))
print("OK")
