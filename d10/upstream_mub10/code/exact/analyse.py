"""Orbits, orthogonality graph, bases, MU pairs of bases, extension counts.
Usage: python3 analyse.py d phases.npy outprefix
"""
import numpy as np, sys, json, itertools, networkx as nx
from collections import Counter

d = int(sys.argv[1]); P = np.load(sys.argv[2]); out = sys.argv[3]
N = len(P)
X = np.exp(1j * np.concatenate([np.zeros((N, 1)), P], 1))
w = np.exp(2j * np.pi / d)
Fm = np.array([[w ** (j * k) for k in range(d)] for j in range(d)]) / np.sqrt(d)

def norm(v):
    return v / v[0]

def key(v):
    return tuple(np.round(np.concatenate([v.real, v.imag]), 6) + 0.0)

index = {key(v): i for i, v in enumerate(X)}
units = [m for m in range(1, d) if np.gcd(m, d) == 1]
gens = [lambda v: norm(np.roll(v, -1)),
        lambda v: v * w ** np.arange(d),
        lambda v: v.conj()] + \
       [ (lambda m: (lambda v: v[(m * np.arange(d)) % d]))(m) for m in units if m != 1] + \
       [lambda v: norm(Fm @ v)]
orbit_of = -np.ones(N, int); orbits = []
for i in range(N):
    if orbit_of[i] >= 0: continue
    o = len(orbits); orbit_of[i] = o; stack = [i]; mem = [i]
    while stack:
        v = X[stack.pop()]
        for g in gens:
            k = key(g(v))
            if k not in index:
                raise SystemExit("image not in list: list not closed under symmetry")
            j = index[k]
            if orbit_of[j] < 0:
                orbit_of[j] = o; stack.append(j); mem.append(j)
    orbits.append(mem)
sizes = sorted(len(o) for o in orbits)
print("orbits:", len(orbits), "sizes:", Counter(sizes))

G = X.conj() @ X.T
A = np.abs(G)
ortho = (A < 1e-8); np.fill_diagonal(ortho, False)
amb = ((A >= 1e-8) & (A < 1e-3)).sum()
print("orthogonal pairs:", ortho.sum() // 2, " ambiguous |<u,v>| in [1e-8,1e-3):", amb // 2)
print("min |<u,v>| over non-orth pairs:", A[~ortho & ~np.eye(N, dtype=bool)].min())
Gr = nx.Graph(); Gr.add_nodes_from(range(N))
Gr.add_edges_from(zip(*np.nonzero(np.triu(ortho))))
deg = np.array([Gr.degree(i) for i in range(N)])
cl = list(nx.find_cliques(Gr))
csz = Counter(len(c) for c in cl)
print("maximal clique sizes:", dict(sorted(csz.items())))
bases = sorted(sorted(int(i) for i in c) for c in cl if len(c) == d)
print("bases (d-cliques):", len(bases))
# basis orbits: via orbit_of signature + group action on vector indices
def act(g, b):
    return tuple(sorted(index[key(g(X[i]))] for i in b))
bset = {tuple(b): k for k, b in enumerate(bases)}
borb = -np.ones(len(bases), int); bo = []
for k, b in enumerate(bases):
    if borb[k] >= 0: continue
    o = len(bo); borb[k] = o; stack = [tuple(b)]; mem = [k]
    while stack:
        bb = stack.pop()
        for g in gens:
            nb = act(g, bb)
            j = bset[nb]
            if borb[j] < 0:
                borb[j] = o; stack.append(nb); mem.append(j)
    bo.append(mem)
print("basis orbits:", len(bo), "sizes:", [len(o) for o in bo])
# MU pairs of bases
U = np.abs(np.abs(G) ** 2 - d)            # 0 iff unbiased
unb = U < 1e-8
mu_pairs = []
nearest = np.inf
for a, b in itertools.combinations(range(len(bases)), 2):
    sub = U[np.ix_(bases[a], bases[b])]
    m = sub.max()
    nearest = min(nearest, m)
    if m < 1e-8: mu_pairs.append((int(a), int(b)))
print("MU pairs of bases:", len(mu_pairs), " min over pairs of max_{u,v} ||<u,v>|^2-d|:", nearest)
# vectors unbiased to each basis
ext = [int(np.all(unb[:, b], axis=1).sum()) for b in bases]
print("per basis: #biunimodular vectors unbiased to whole basis:", Counter(ext))
# per basis, max number of mutually orthogonal vectors among those unbiased
res = dict(d=d, N=N, orbit_sizes=[len(o) for o in orbits], orbit_reps=[int(o[0]) for o in orbits],
           orbit_of=orbit_of.tolist(), n_ortho_pairs=int(ortho.sum() // 2), degree_counts=dict(Counter(deg.tolist())),
           maximal_clique_sizes={int(k): v for k, v in csz.items()}, bases=bases,
           basis_orbit_sizes=[len(o) for o in bo], basis_orbit_reps=[int(o[0]) for o in bo], basis_orbit=borb.tolist(),
           mu_basis_pairs=mu_pairs, min_pair_defect=float(nearest), ext_counts=ext)
for k, o in enumerate(bo):
    b = bases[o[0]]
    print(f" basis orbit {k}: size {len(o)}, vector orbits {sorted(Counter(orbit_of[b].tolist()).items())}, ext {ext[o[0]]}")
json.dump(res, open(out + "_analysis.json", "w"))
