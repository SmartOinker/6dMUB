#!/usr/bin/env python3
"""Regenerates three small pieces of evidence quoted in the report (Section 6) and saves them
to results/constellations/evidence.json:
 (a) basin test: Levenberg-Marquardt from the Yale {5,3,3,3} example plus Gaussian noise;
 (b) family test: Jacobian ranks and a symmetry-invariant number for the saved solutions of
     {5,5,2,2}, {5,4,3,1} (random starts) and {5,3,3,3} (symmetric starts);
 (c) where the starts that meet the 2008 criterion F < 1e-7 end, for {5,4,4,1} and {5,5,3,1}.
"""
import collections, itertools, json, os
import numpy as np
from scipy.optimize import least_squares
import search as S

HERE = os.path.dirname(os.path.abspath(__file__))
EX = os.path.join(HERE, "..", "..", "results", "constellations", "extra")
out = {}

# ---- (a)
w = np.exp(2j * np.pi / 3); a = (1 + 1j * np.sqrt(15)) / 4
L = np.diag([1, 1, w, w.conjugate(), w, w.conjugate()])
one = np.ones(6, complex); b = np.array([1, w.conjugate(), 1, a, w, a])
c = np.array([1, w.conjugate(), a.conjugate(), w, a.conjugate(), 1])
V = np.array([one, L @ one, L @ L @ one, b, L @ b, L @ L @ b, c, L @ c, L @ L @ c])
gid, m, same, cross = S.layout([3, 3, 3])
x = np.angle((V / V[:, [0]])[1:, 1:]).ravel()
rng = np.random.default_rng(0)
basin = {}
for eps in [1e-3, 1e-2, 5e-2, 0.1, 0.2, 0.4]:
    ok = 0
    for t in range(20):
        sol = least_squares(S.residuals, x + eps * rng.standard_normal(len(x)), jac=S.jacobian,
                            args=(m, same, cross), method="lm", xtol=1e-15, ftol=1e-15,
                            gtol=1e-15, max_nfev=2000)
        ok += np.linalg.norm(sol.fun) < 1e-10
    basin[str(eps)] = f"{ok} of 20"
sv = np.linalg.svd(S.jacobian(x, m, same, cross), compute_uv=False)
out["a_basin_of_yale_5333"] = dict(converged_by_noise_std=basin, misfit_at_example=float(np.linalg.norm(S.residuals(x, m, same, cross))),
                                    smallest_singular_values=sv[-3:].tolist(), nvar=len(x))


# ---- (b)
def inv(groups, ph):
    gid, m, same, cross = S.layout(groups)
    Vv = S.vectors(np.array(ph), m); G = Vv.conj() @ Vv.T
    return float(sum((G[i, j] * G[j, k] * G[k, i]).real for i, j, k in itertools.combinations(range(m), 3)))


fam = {}
for fn, g in [("random_522_seed3_400starts.jsonl", [5, 2, 2]), ("random_431_seed3_300starts.jsonl", [4, 3, 1]),
              ("symmetric_333_seed1_300starts.jsonl", [3, 3, 3])]:
    vals, ranks = [], []
    for line in open(os.path.join(EX, fn)):
        r = json.loads(line)
        if r["kind"] == "solution" and r["groups"] == g:
            vals.append(inv(g, r["phases"])); ranks.append(r["rank"])
    vals = np.array(vals)
    fam["".join(map(str, g))] = dict(file=fn, solutions=len(vals), nvar=5 * (sum(g) - 1),
                                      jacobian_ranks=dict(collections.Counter(ranks)),
                                      distinct_invariant_values_6dp=int(len(np.unique(np.round(vals, 6)))),
                                      invariant_min=float(vals.min()), invariant_max=float(vals.max()))
out["b_families"] = fam

# ---- (c)
lev = {}
for g in ([4, 4, 1], [5, 3, 1]):
    gid, m, same, cross = S.layout(g); rng = np.random.default_rng(77); vals = []
    N = 6000
    for s in range(N):
        sol = least_squares(S.residuals, rng.uniform(-np.pi, np.pi, 5 * (m - 1)), jac=S.jacobian,
                            args=(m, same, cross), method="lm", xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=400)
        if S.bw_objective(sol.x, m, same, cross) < 1e-7:
            vals.append(float(np.linalg.norm(sol.fun)))
    cnt = collections.Counter(np.round(vals, 7))
    lev["".join(map(str, g))] = dict(starts=N, seed=77, hits_2008_criterion=len(vals),
                                      misfit_levels=[[float(k), int(v)] for k, v in sorted(cnt.items())])
out["c_levels_of_2008_hits"] = lev
json.dump(out, open(os.path.join(HERE, "..", "..", "results", "constellations", "evidence.json"), "w"), indent=1)
print(json.dumps(out, indent=1)[:2500])
