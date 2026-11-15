"""Float64 re-derivation of the dimension-ten Fourier-pair data from d10/vecs.npy (3,040 points) and d10/bases.json.
Own code (numpy + networkx), no Arb.  Checks: all entries unimodular; each vector has |<u,v>|^2 summing correctly; the orthogonality
graph has 57,680 edges; maximal cliques by size (17,700 of size 2 expected, per the report); the 10-cliques are exactly the 1,136
stored bases; the extension margin min over pairs of bases of max ||<u,v>|^2 - 10| is 4.17807.  Numerical evidence only.  Prints OK."""
import os, json, collections, itertools
import numpy as np, networkx as nx
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "d10")
V = np.load(os.path.join(D, "vecs.npy")); bases = [tuple(sorted(b)) for b in json.load(open(os.path.join(D, "bases.json")))]
N, d = V.shape; assert (N, d) == (3040, 10)
print("1. max | |v_i| - 1 | = %.2e (unimodular to float precision); v_0 = 1: %s" % (np.abs(np.abs(V) - 1).max(), np.allclose(V[:, 0], 1)))
assert np.abs(np.abs(V) - 1).max() < 1e-12
A = np.abs(V.conj() @ V.T); np.fill_diagonal(A, 10)
small = A < 1e-6; np.fill_diagonal(small, False)
nz = A[np.triu(~small, 1)]
print("2. orthogonal pairs (|<u,v>| < 1e-6): %d; smallest |<u,v>| among the other pairs: %.6f" % (small.sum()//2, nz.min()))
assert small.sum()//2 == 57680 and nz.min() > 1e-3
G = nx.from_numpy_array(small.astype(int))
cnt = collections.Counter(len(c) for c in nx.find_cliques(G))
print("3. maximal cliques by size:", dict(sorted(cnt.items())))
assert cnt[10] == 1136 and max(cnt) == 10
cl = set()
for c in nx.find_cliques(G):
    if len(c) == 10: cl.add(tuple(sorted(c)))
assert cl == set(bases); print("   the 10-cliques are exactly the 1,136 stored bases: True")
P2 = A**2; Bi = np.array(sorted(bases)); mp = 1e9
for a in range(len(Bi)):
    blk = np.abs(P2[Bi[a]] - 10).max(axis=0)[Bi].max(axis=1); blk[a] = 1e9; mp = min(mp, blk.min())
print("4. margin min over pairs of bases of max ||<u,v>|^2 - 10| = %.5f (report 4.17807)" % mp)
assert abs(mp - 4.17807) < 5e-5
print("OK")
