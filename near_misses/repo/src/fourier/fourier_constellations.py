#!/usr/bin/env python3
"""Which constellations {5,5,b,c} exist when the second basis is the Fourier basis?

Input: the 48 vectors unbiased to the standard and Fourier bases (results/fourier/results.json,
certified by fourier_case.py). Any vector of a third or fourth group of a constellation whose
first two groups are the standard and Fourier bases is one of these 48, so the question is a
finite one: is there an orthonormal set B of size b and an orthonormal set C of size c among
the 48 with every vector of B unbiased to every vector of C?

The pairwise values |<u,v>|^2 (unnormalised: orthogonal = 0, unbiased = 6) take nine well
separated values, so double precision decides each pair; the certified enclosures of
fourier_case.py back the "not unbiased" decisions on which the non-existence statements rest.
"""
import collections
import json
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, "..", "..", "results", "fourier")
r = json.load(open(os.path.join(R, "results.json")))
ph = np.array([[float(t) for t in row] for row in r["vectors_phases_p1_to_p5_30digits"]])
V = np.hstack([np.ones((48, 1)), np.exp(1j * ph)])
G = np.abs(V.conj() @ V.T) ** 2
iu = np.triu_indices(48, 1)
values = sorted(collections.Counter(np.round(G[iu], 6)).items())
orth = np.isclose(G, 0, atol=1e-9)
unb = np.isclose(G, 6, atol=1e-9)
gap_to_6 = float(np.min(np.abs(G[iu][~unb[iu]] - 6)))  # separation of non-unbiased pairs


def orth_sets(k):
    res = []

    def rec(cur, start):
        if len(cur) == k:
            res.append(tuple(cur))
            return
        for i in range(start, 48):
            if all(orth[i, j] for j in cur):
                rec(cur + [i], i + 1)
    rec([], 0)
    return res


sets = {k: orth_sets(k) for k in range(1, 6)}


def exists(b, c):
    for B in sets[b]:
        cand = [i for i in range(48) if all(unb[i, j] for j in B)]

        def rec(cur, pool):
            if len(cur) == c:
                return cur
            for idx, i in enumerate(pool):
                if all(orth[i, j] for j in cur):
                    out = rec(cur + [i], pool[idx + 1:])
                    if out:
                        return out
            return None
        C = rec([], cand)
        if C:
            return dict(B=list(B), C=C)
    return None


table = {}
for b in range(1, 6):
    for c in range(1, b + 1):
        w = exists(b, c)
        table[f"5,5,{b},{c}"] = dict(exists=bool(w), witness=w)
out = dict(pairwise_values_unnormalised=[[float(v), int(n)] for v, n in values],
           orthogonal_pairs=int(orth[iu].sum()), unbiased_pairs=int(unb[iu].sum()),
           min_distance_from_6_of_non_unbiased_pairs=gap_to_6,
           orthonormal_sets_by_size={k: len(v) for k, v in sets.items()}, constellations=table)
json.dump(out, open(os.path.join(R, "fourier_constellations.json"), "w"), indent=1)
print(json.dumps({k: v["exists"] for k, v in table.items()}))
print("pairwise |<u,v>|^2 values:", values)
print("min distance from 6 among non-unbiased pairs:", gap_to_6)
