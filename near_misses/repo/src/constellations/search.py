#!/usr/bin/env python3
"""Numerical search for mutually unbiased (MU) constellations {5, g1, g2, ...} in C^6.

Definitions
-----------
A constellation {5, g1, g2, g3}_6 is the standard basis of C^6 (five of its vectors fix the
sixth) together with further groups of g1, g2, g3 unit vectors such that
  * vectors in the same group are orthogonal, and
  * vectors in different groups (and every vector vs. the standard basis) are unbiased:
    |<u, v>|^2 = 1/6.

A vector unbiased to the standard basis has all entries of modulus 1/sqrt(6). We drop the
1/sqrt(6) and fix the global phase, so each vector is (1, e^{i p1}, ..., e^{i p5}).
With this scaling:  orthogonal  <=>  <u,v> = 0,   unbiased  <=>  |<u,v>|^2 = 6.
Multiplying every vector by one diagonal unitary keeps all conditions, so the first vector of
the first group is fixed to (1,1,1,1,1,1).

Method
------
Nonlinear least squares (Levenberg-Marquardt / trust region, SciPy) from random starting
phases. A start "converges" if the residual norm falls below --tol. This is a SEARCH: a
converged start is a candidate solution that must be confirmed separately (verify.py);
failure to converge proves nothing.

Output: one JSON line per converged start (phases, residual, singular values of the Jacobian)
plus a summary line with the distribution of final residuals.
"""
import argparse
import json
import sys
import time

import numpy as np
from scipy.optimize import least_squares

SQRT6 = np.sqrt(6.0)


def layout(groups):
    """Index bookkeeping: group id of each vector, same-group pairs, cross-group pairs."""
    gid = np.concatenate([np.full(g, k) for k, g in enumerate(groups)])
    m = len(gid)
    iu, ju = np.triu_indices(m, 1)
    same = gid[iu] == gid[ju]
    return gid, m, (iu[same], ju[same]), (iu[~same], ju[~same])


def vectors(x, m):
    """Free phases x (length 5*(m-1)) -> m x 6 array of unit-modulus entries."""
    ph = np.zeros((m, 6))
    ph[1:, 1:] = np.asarray(x).reshape(m - 1, 5)
    return np.exp(1j * ph)


def residuals(x, m, same, cross):
    V = vectors(x, m)
    G = V.conj() @ V.T  # G[i, j] = <v_i, v_j> (unnormalised)
    gs = G[same]
    gc = G[cross]
    return np.concatenate([gs.real, gs.imag, (np.abs(gc) ** 2 - 6.0) / (2 * SQRT6)])


def bw_objective(x, m, same, cross):
    """Brierley-Weigert objective F (arXiv:0808.1614): normalised vectors, each pair once,
    (|<u,v>| - chi)^2 with chi = 0 inside a group and 1/sqrt(6) across groups. Their
    criterion for "found" was F < 1e-7."""
    V = vectors(x, m)
    G = np.abs(V.conj() @ V.T) / 6.0
    return float((G[same] ** 2).sum() + ((G[cross] - 1 / SQRT6) ** 2).sum())


def jacobian(x, m, same, cross):
    V = vectors(x, m)
    nvar = 5 * (m - 1)

    def dG(i, j):
        # derivative of G_ij with respect to every free phase; rows = pairs, cols = variables
        T = V[i].conj() * V[j]  # (npairs, 6): the six terms of each inner product
        D = np.zeros((len(i), m, 6), dtype=complex)
        r = np.arange(len(i))
        D[r, j, :] += 1j * T
        D[r, i, :] += -1j * T
        return D[:, 1:, 1:].reshape(len(i), nvar)

    Ds = dG(*same)
    Dc = dG(*cross)
    gc = (V.conj() @ V.T)[cross]
    Jc = (2 * (gc.conj()[:, None] * Dc).real) / (2 * SQRT6)
    return np.vstack([Ds.real, Ds.imag, Jc])


def load_seeds(path, seed_groups):
    """Read solutions of shape seed_groups from a JSONL file written by this script."""
    seeds = []
    with open(path) as fh:
        for line in fh:
            rec = json.loads(line)
            if rec.get("kind") == "solution" and rec["groups"] == list(seed_groups):
                seeds.append(np.array(rec["phases"]))
    return seeds


def grow_start(seed_x, seed_groups, groups, rng, noise):
    """Starting point for shape `groups` built from a solution of the smaller shape
    `seed_groups` (componentwise <=; trailing groups may be new): keep the seed's vectors
    (plus optional noise) and append random vectors to the groups that grow."""
    ms = sum(seed_groups)
    ph = np.zeros((ms, 5))
    ph[1:] = seed_x.reshape(ms - 1, 5)
    out, pos = [], 0
    sg = list(seed_groups) + [0] * (len(groups) - len(seed_groups))
    for g_old, g_new in zip(sg, groups):
        block = ph[pos:pos + g_old] + noise * rng.standard_normal((g_old, 5))
        pos += g_old
        extra = rng.uniform(-np.pi, np.pi, (g_new - g_old, 5))
        out.append(np.vstack([block, extra]))
    full = np.vstack(out)
    full[0] = 0.0  # gauge: first vector of the first group is (1,...,1)
    return full[1:].ravel()


def run(groups, starts, seed, tol, out, max_nfev, report_every, keep=0,
        seed_file="", seed_groups=None, noise=0.0):
    gid, m, same, cross = layout(groups)
    nvar = 5 * (m - 1)
    nres = 2 * len(same[0]) + len(cross[0])
    method = "lm" if nres >= nvar else "trf"
    rng = np.random.default_rng(seed)
    seeds = load_seeds(seed_file, seed_groups) if seed_file else []
    if seed_file and not seeds:
        raise SystemExit(f"no seed solutions of shape {seed_groups} in {seed_file}")
    finals, best = [], []
    nconv = 0
    n_bw = 0  # starts that meet the 2008 criterion F < 1e-7
    t0 = time.time()
    fh = open(out, "a") if out else sys.stdout
    head = dict(kind="header", groups=groups, nvar=nvar, nres=nres, method=method,
                seed=seed, starts=starts, tol=tol, seed_file=seed_file,
                seed_groups=seed_groups, n_seeds=len(seeds), noise=noise)
    fh.write(json.dumps(head) + "\n")
    fh.flush()
    for s in range(starts):
        if seeds:
            x0 = grow_start(seeds[rng.integers(len(seeds))], seed_groups, groups, rng, noise)
        else:
            x0 = rng.uniform(-np.pi, np.pi, nvar)
        try:
            sol = least_squares(residuals, x0, jac=jacobian, args=(m, same, cross),
                                method=method, xtol=1e-15, ftol=1e-15, gtol=1e-15,
                                max_nfev=max_nfev)
        except Exception as e:  # keep the search alive
            print("start", s, "failed:", e, file=sys.stderr)
            continue
        rn = float(np.linalg.norm(sol.fun))
        finals.append(rn)
        n_bw += bw_objective(sol.x, m, same, cross) < 1e-7
        if rn < tol:
            nconv += 1
            sv = np.linalg.svd(jacobian(sol.x, m, same, cross), compute_uv=False)
            rec = dict(kind="solution", groups=groups, seed=seed, start=s, resnorm=rn,
                       phases=np.angle(np.exp(1j * sol.x)).tolist(),
                       rank=int((sv > 1e-8).sum()), nvar=nvar,
                       smallest_sv=sv[-6:].tolist())
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
        elif keep:
            # near-miss bookkeeping: gradient norm ~ 0 with residual > 0 means a genuine
            # local minimum of the misfit, not a slowly converging solution
            best.append((rn, s, float(sol.optimality), int(sol.status),
                         np.angle(np.exp(1j * sol.x)).tolist()))
            best.sort(key=lambda t: t[0])
            del best[keep:]
        if report_every and (s + 1) % report_every == 0:
            f = np.array(finals)
            print(f"[{groups}] {s+1}/{starts} starts, {nconv} converged, "
                  f"best residual {f.min():.3e}, {time.time()-t0:.0f}s", file=sys.stderr)
    for rn, s, opt, status, ph in best:
        fh.write(json.dumps(dict(kind="nearmiss", groups=groups, seed=seed, start=s,
                                 resnorm=rn, grad_norm=opt, status=status, phases=ph)) + "\n")
    f = np.array(finals)
    q = np.quantile(f, [0, 0.01, 0.1, 0.5]) if len(f) else [float("nan")] * 4
    summ = dict(kind="summary", groups=groups, seed=seed, starts=len(f), converged=nconv,
                bw_found=int(n_bw), best_resnorm=float(q[0]), q01=float(q[1]),
                q10=float(q[2]), median=float(q[3]), seconds=round(time.time() - t0, 1),
                seed_groups=seed_groups)
    fh.write(json.dumps(summ) + "\n")
    fh.flush()
    if out:
        fh.close()
    return summ


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--groups", type=int, nargs="+", required=True,
                    help="sizes of the groups beyond the standard basis, e.g. 3 3 3")
    ap.add_argument("--starts", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tol", type=float, default=1e-11,
                    help="residual norm below which a start counts as converged")
    ap.add_argument("--max-nfev", type=int, default=400)
    ap.add_argument("--out", type=str, default="")
    ap.add_argument("--report-every", type=int, default=0)
    ap.add_argument("--keep", type=int, default=0, help="also save the K best near-misses")
    ap.add_argument("--seed-file", type=str, default="",
                    help="JSONL of solutions of a smaller shape to grow from")
    ap.add_argument("--seed-groups", type=int, nargs="+", default=None,
                    help="shape of the seed solutions, e.g. 4 3 1")
    ap.add_argument("--noise", type=float, default=0.0,
                    help="std of Gaussian noise added to seed phases")
    a = ap.parse_args()
    s = run(a.groups, a.starts, a.seed, a.tol, a.out, a.max_nfev, a.report_every,
            keep=a.keep, seed_file=a.seed_file, seed_groups=a.seed_groups, noise=a.noise)
    print(json.dumps(s), file=sys.stderr)
