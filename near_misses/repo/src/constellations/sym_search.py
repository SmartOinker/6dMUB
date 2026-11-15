#!/usr/bin/env python3
"""Symmetric search for MU constellations {5, g1, g2, g3} in C^6.

Same equations as search.py, but the vectors are built from fewer free "generators":
each group consists of some full orbits {b, Lb, L^2 b} of the order-three diagonal unitary
    L = diag(1, 1, w, w^2, w, w^2),  w = exp(2 pi i / 3),
plus some single vectors. For a vector b with unit-modulus entries, <b, L b> = trace(L) = 0,
so an orbit is automatically orthonormal. All known examples of {5,3,3,3}, {5,4,3,1} and
{5,5,2,2} in arXiv:2611.06917 (SM Sec. 5) are built from such orbits, and every MUB triple in
C^6 has a symmetry of this type, which is why this ansatz is tried.

A solution found here is an ordinary solution of the full system (it is re-checked with the
full residual and can be passed to verify.py). A failure proves nothing.

Config syntax: one token per group, "<orbits>o<singles>s", e.g.  1o1s 1o0s 0o2s  = {5,4,3,2}.
"""
import argparse
import itertools
import json
import sys
import time

import numpy as np
from scipy.optimize import least_squares

import search as S

W_PH = 2 * np.pi / 3
L_PH = np.array([0, 0, 1, 2, 1, 2]) * W_PH  # phases of the diagonal of L


def build(config):
    """Return (groups, A, c): full phases (m x 6, flattened) = A @ y + c for generator phases y.
    The first generator is gauged to (1,...,1) and carries no variables."""
    rows = []  # (generator index, power of L)
    groups = []
    gen = 0
    for (no, ns) in config:
        for _ in range(no):
            rows += [(gen, 0), (gen, 1), (gen, 2)]
            gen += 1
        for _ in range(ns):
            rows.append((gen, 0))
            gen += 1
        groups.append(3 * no + ns)
    m = len(rows)
    ny = 5 * (gen - 1)
    A = np.zeros((m * 6, ny))
    c = np.zeros(m * 6)
    for r, (g, t) in enumerate(rows):
        c[r * 6:(r + 1) * 6] = t * L_PH
        if g > 0:
            for k in range(1, 6):
                A[r * 6 + k, (g - 1) * 5 + (k - 1)] = 1.0
    return groups, A, c, m


def full_x(y, A, c, m):
    ph = (A @ y + c).reshape(m, 6)
    return ph[1:, 1:].ravel()


def run(config, starts, seed, tol, max_nfev, keep, fh):
    groups, A, c, m = build(config)
    gid, m2, same, cross = S.layout(groups)
    assert m == m2
    # columns of A restricted to the free full variables (vectors 1.., entries 1..5)
    Ared = A.reshape(m, 6, -1)[1:, 1:, :].reshape(5 * (m - 1), -1)
    ny = A.shape[1]

    def res(y):
        return S.residuals(full_x(y, A, c, m), m, same, cross)

    def jac(y):
        return S.jacobian(full_x(y, A, c, m), m, same, cross) @ Ared

    nres = 2 * len(same[0]) + len(cross[0])
    method = "lm" if nres >= ny else "trf"
    rng = np.random.default_rng(seed)
    finals, best, nconv = [], [], 0
    t0 = time.time()
    for s in range(starts):
        y0 = rng.uniform(-np.pi, np.pi, ny)
        sol = least_squares(res, y0, jac=jac, method=method, xtol=1e-15, ftol=1e-15,
                            gtol=1e-15, max_nfev=max_nfev)
        rn = float(np.linalg.norm(sol.fun))
        finals.append(rn)
        x = full_x(sol.x, A, c, m)
        if rn < tol:
            nconv += 1
            sv_full = np.linalg.svd(S.jacobian(x, m, same, cross), compute_uv=False)
            sv_sym = np.linalg.svd(jac(sol.x), compute_uv=False)
            fh.write(json.dumps(dict(
                kind="solution", groups=groups, config=config, seed=seed, start=s, resnorm=rn,
                phases=np.angle(np.exp(1j * x)).tolist(), nvar=5 * (m - 1),
                rank=int((sv_full > 1e-8).sum()), sym_nvar=ny,
                sym_rank=int((sv_sym > 1e-8).sum()))) + "\n")
            fh.flush()
        elif keep:
            best.append((rn, s, float(sol.optimality), np.angle(np.exp(1j * x)).tolist()))
            best.sort(key=lambda t: t[0])
            del best[keep:]
    for rn, s, opt, ph in best:
        fh.write(json.dumps(dict(kind="nearmiss", groups=groups, config=config, seed=seed,
                                 start=s, resnorm=rn, grad_norm=opt, phases=ph)) + "\n")
    f = np.array(finals)
    summ = dict(kind="summary", groups=groups, config=config, seed=seed, starts=starts,
                converged=nconv, best_resnorm=float(f.min()),
                q10=float(np.quantile(f, 0.1)), sym_nvar=ny, nres=nres,
                seconds=round(time.time() - t0, 1))
    fh.write(json.dumps(summ) + "\n")
    fh.flush()
    return summ


def configs_for(shape):
    """All ways to split each group size into orbits and singles, with at least one orbit."""
    # a group of size 5 is a full basis (five orthonormal vectors fix the sixth), so it may
    # also be written as two full orbits (six vectors)
    opts = [[(k, g - 3 * k) for k in range(g // 3 + 1)] + ([(2, 0)] if g == 5 else [])
            for g in shape]
    for cfg in itertools.product(*opts):
        if sum(k for k, _ in cfg) >= 1:
            yield [list(t) for t in cfg]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--shape", type=int, nargs="+", required=True, help="e.g. 4 3 2")
    ap.add_argument("--starts", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tol", type=float, default=1e-11)
    ap.add_argument("--max-nfev", type=int, default=600)
    ap.add_argument("--keep", type=int, default=2)
    ap.add_argument("--out", type=str, required=True)
    a = ap.parse_args()
    with open(a.out, "a") as fh:
        for cfg in configs_for(a.shape):
            s = run(cfg, a.starts, a.seed, a.tol, a.max_nfev, a.keep, fh)
            print(json.dumps(s), file=sys.stderr)
