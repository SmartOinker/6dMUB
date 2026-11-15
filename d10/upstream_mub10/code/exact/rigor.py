"""Rigorous (Arb) pair tests on the certified biunimodular vectors.
NO[i,j]  = certified <x_i,x_j> != 0       (not orthogonal)
NU[i,j]  = certified |<x_i,x_j>|^2 != d    (not unbiased)
Then: every 10-clique of the 'possibly orthogonal' graph, and for each clique B and each vector v,
whether some u in B is certified not unbiased to v.  Also pairs of cliques.
Usage: python3 rigor.py d xfile analysis.json out_prefix
"""
import numpy as np, sys, json, time, itertools, networkx as nx
sys.argv_saved = list(sys.argv)
d = int(sys.argv[1]); xfile = sys.argv[2]; A = json.load(open(sys.argv[3])); out = sys.argv[4]
sys.argv = ["cert.py", str(d), xfile, "/tmp/unused", "256", "5", "1e-45"]
sys.path.insert(0, "/home/claude/mub10/exact/code")
import cert
from flint import acb, acb_mat, arb
S = np.load(xfile); N = len(S); t0 = time.time()
Ks = []
for v in S:
    r, xs, K = cert.certify(v)
    assert r["ok"] and r["unimod"] == "unimodular"
    Ks.append([acb(1)] + K)
print("certified", N, f"{time.time()-t0:.0f}s", flush=True)
M = acb_mat(Ks)                     # N x d
MH = acb_mat([[c.conjugate() for c in row] for row in Ks])
NO = np.zeros((N, N), bool); NU = np.zeros((N, N), bool); maxrad = 0.0
blk = 152
MT = M.transpose()
for a in range(0, N, blk):
    sub = acb_mat([[MH[i, j] for j in range(d)] for i in range(a, min(N, a + blk))])
    Gm = sub * MT
    for ii in range(Gm.nrows()):
        i = a + ii
        row = Gm.tolist()[ii] if False else None
        for j in range(N):
            gij = Gm[ii, j]
            ab = abs(gij)
            NO[i, j] = ab.lower() > 0
            q = ab * ab - d
            NU[i, j] = (q.lower() > 0) or (q.upper() < 0)
    print(f"rows {a+blk}/{N} {time.time()-t0:.0f}s", flush=True)
np.fill_diagonal(NO, True)
poss = ~NO
print("possibly-orthogonal pairs:", poss.sum() // 2)
numer = set(map(tuple, (np.array(A["bases"]))))
Gr = nx.Graph(); Gr.add_nodes_from(range(N)); Gr.add_edges_from(zip(*np.nonzero(np.triu(poss, 1))))
cl = [tuple(sorted(c)) for c in nx.find_cliques(Gr)]
big = [c for c in cl if len(c) >= d]
print("maximal cliques of size >= d:", len(big), "sizes", set(len(c) for c in big))
cliques10 = set()
for c in big:
    for s in itertools.combinations(c, d): cliques10.add(s)
print("10-cliques:", len(cliques10), " equal to numerical bases:", cliques10 == set(tuple(b) for b in A["bases"]))
# strong unextendibility: for each clique B, each v: exists u in B with NU[u,v]
bad = []
for B in cliques10:
    covered = NU[list(B), :].any(0)
    if not covered.all(): bad.append((B, np.nonzero(~covered)[0].tolist()))
print("cliques with a vector not certified-biased to it:", len(bad))
# pairs of cliques (implied by the above, but checked directly)
Bl = sorted(cliques10); mu_poss = 0
for a, b in itertools.combinations(range(len(Bl)), 2):
    if not NU[np.ix_(Bl[a], Bl[b])].any(): mu_poss += 1
print("pairs of cliques not certified non-MU:", mu_poss, f"{time.time()-t0:.0f}s")
json.dump(dict(N=N, possibly_orthogonal_pairs=int(poss.sum() // 2), n_10cliques=len(cliques10),
               equals_numerical=cliques10 == set(tuple(b) for b in A["bases"]), bad_cliques=len(bad),
               possibly_MU_clique_pairs=mu_poss), open(out + "_rigor.json", "w"))
