#!/usr/bin/env python3
"""Which partial fourth bases {5,5,b,c} exist at the Fourier pair {I, F_6}?  Re-derived from ball enclosures.

Every vector of a third or fourth group of a constellation whose first two groups are I and F_6 is one of
the 48 unimodular cyclic 6-roots (up to a phase), if the cited count of 156 cyclic 6-roots is used
(certify_d6_roots.py certifies 156 distinct roots, 48 unimodular, 108 not).  So the question is finite:
is there an orthonormal set B (size b) and an orthonormal set C (size c) among the 48 with every vector of B
unbiased to every vector of C ("unbiased": |<u,v>|^2 = 6 for norm^2 = 6)?

Method (independent of the earlier program d6 `fourier_constellations.py`, different data structures and
enumeration order; the only shared input are the Arb enclosures of the 48 vectors from certify_graph.py):
  * orthogonal-possible(u,v): enclosure of <u,v> contains 0           (superset of true orthogonality)
  * unbiased-possible(u,v):   enclosure of |<u,v>|^2 - 6 contains 0   (superset of true unbiasedness)
  * Enumerate B over cliques of the orthogonal-possible graph (networkx), the vectors unbiased-possible to
    all of B, and look for a c-clique among them.
Because both relations are supersets, "no such pair (B, C) exists" is a rigorous statement about the TRUE
relations (given the 48), while "(B, C) exists" is only established up to the enclosure width: enclosures
cannot prove exact orthogonality or exact unbiasedness.  Floating point is not used for any decision.
The result is compared with results/fourier/fourier_constellations.json of the earlier repository.

Usage: python3 -I check_partial_bases.py [cyclic6_roots.npz [fourier_constellations.json]]
"""
import json, os, sys

import networkx as nx
import numpy as np
from flint import arb

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import certify_graph as cg   # noqa: E402

npz = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "cyclic6_roots.npz")
ref = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "near_misses", "repo", "results", "fourier", "fourier_constellations.json")

D = cg.build(npz)
n = len(D["vecs"])
ip = D["ip"]
orth = D["orth_possible"]
unb = np.zeros((n, n), bool)
certified_not_unb = 0
for a in range(n):
    for b in range(n):
        if a != b:
            v = abs(ip[a][b]) ** 2 - 6
            unb[a, b] = v.contains(0)
            certified_not_unb += (not unb[a, b])
print(f"{n} vectors; possibly orthogonal pairs {int(np.triu(orth, 1).sum())}; possibly unbiased pairs {int(np.triu(unb, 1).sum())}; "
      f"certified not unbiased pairs {certified_not_unb // 2}")
assert not (orth & unb).any(), "a pair cannot be both possibly orthogonal and possibly unbiased"

Go = nx.Graph()
Go.add_nodes_from(range(n))
Go.add_edges_from((a, b) for a in range(n) for b in range(a + 1, n) if orth[a, b])
sets = {}
for cl in nx.enumerate_all_cliques(Go):          # all orthonormal sets (cliques), by increasing size
    sets.setdefault(len(cl), []).append(tuple(sorted(cl)))
sizes = {k: len(v) for k, v in sorted(sets.items())}
print("orthonormal sets (cliques of the possibly-orthogonal graph) by size:", sizes)

exists = {}
for b in range(1, 6):
    for c in range(1, b + 1):
        found = None
        for B in sets.get(b, []):
            pool = [v for v in range(n) if v not in B and all(unb[v, u] for u in B)]
            sub = Go.subgraph(pool)
            for cl in nx.enumerate_all_cliques(sub):
                if len(cl) == c:
                    found = (B, tuple(sorted(cl)))
                    break
            if found:
                break
        exists[(b, c)] = found

ok = True
print("\n{5,5,b,c} possible under the superset relations (b >= c >= 1):")
for (b, c), w in exists.items():
    print(f"  {{5,5,{b},{c}}}: {'possible, witness B=%s C=%s' % w if w else 'impossible (not even under the superset relations)'}")
largest = [k for k, w in exists.items() if w]
print("possible with c >= 1:", sorted(largest))
good = sorted(largest) == [(1, 1), (2, 1)]
print("RESULT: besides {5,5,b} (b <= 5, from the six-cliques), only {5,5,1,1} and {5,5,2,1} are possible;"
      " no partial fourth basis larger than {5,5,2,1}:", good)
ok &= good
ok &= (sizes.get(6) == 16 and 7 not in sizes)

# comparison with the earlier program's output
if os.path.exists(ref):
    r = json.load(open(ref))
    old = {tuple(int(t) for t in k.split(",")[2:]): v["exists"] for k, v in r["constellations"].items()}
    new = {k: bool(w) for k, w in exists.items()}
    same = old == new
    print(f"\nearlier fourier_constellations.json: constellations equal: {same}; orthogonal pairs {r['orthogonal_pairs']} vs {int(np.triu(orth, 1).sum())}; "
          f"unbiased pairs {r['unbiased_pairs']} vs {int(np.triu(unb, 1).sum())}; "
          f"orthonormal sets by size {r['orthonormal_sets_by_size']} vs {dict((k, v) for k, v in sizes.items() if k < 6)}")
    same_sets = {int(k): v for k, v in r["orthonormal_sets_by_size"].items()} == {k: v for k, v in sizes.items() if k < 6}
    print("  orthonormal-set counts equal:", same_sets)
    ok &= same and same_sets and r["orthogonal_pairs"] == int(np.triu(orth, 1).sum()) and r["unbiased_pairs"] == int(np.triu(unb, 1).sum())
else:
    print("earlier json not found:", ref)
print("OK" if ok else "FAIL")
sys.exit(0 if ok else 1)
