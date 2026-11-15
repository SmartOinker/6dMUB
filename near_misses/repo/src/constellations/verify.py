#!/usr/bin/env python3
"""High-precision examination of a candidate constellation or near-miss (mpmath).

Given a shape and phases (as written by search.py / sym_search.py), this script
  1. re-evaluates the misfit at high precision,
  2. minimises the misfit by damped Gauss-Newton (Levenberg-Marquardt) at high precision
     until the gradient J^T r is below 10^-(digits-15),
  3. reports the limiting misfit, the gradient norm, the Brierley-Weigert function F
     (arXiv:0808.1614, normalised vectors, threshold 1e-7) at that point, and the smallest
     eigenvalues of the Hessian of (1/2)|r|^2 (double precision, finite differences).

Reading the output:
  * misfit -> 0 (to working precision): a numerical SOLUTION (a candidate constellation).
  * misfit -> a positive number with gradient -> 0 and positive-definite Hessian: a strict
    LOCAL MINIMUM of the misfit that is not a solution. The misfit cannot vanish near it.
Neither outcome is a proof; see the report for what is and is not claimed.
"""
import argparse
import json
import sys

import mpmath as mp
import numpy as np

import search as S


def mp_setup(groups, x, digits):
    mp.mp.dps = digits
    gid, m, same, cross = S.layout(groups)
    return gid, m, same, cross, [mp.mpf(str(t)) if not isinstance(t, mp.mpf) else t for t in x]


def mp_vectors(x, m):
    V = [[mp.mpc(1)] * 6 for _ in range(m)]
    for i in range(1, m):
        for k in range(1, 6):
            V[i][k] = mp.expj(x[(i - 1) * 5 + (k - 1)])
    return V


def mp_res_jac(x, m, same, cross, want_jac=True):
    V = mp_vectors(x, m)
    nvar = 5 * (m - 1)
    s6 = mp.sqrt(6)
    r, rows = [], []

    def terms(i, j):
        return [mp.conj(V[i][k]) * V[j][k] for k in range(6)]

    def dG(i, j, T):
        row = [mp.mpc(0)] * nvar
        for k in range(1, 6):
            if j > 0:
                row[(j - 1) * 5 + (k - 1)] += 1j * T[k]
            if i > 0:
                row[(i - 1) * 5 + (k - 1)] += -1j * T[k]
        return row

    re_rows, im_rows = [], []
    for i, j in zip(*same):
        T = terms(i, j)
        g = mp.fsum(T)
        r.append(g.real)
        if want_jac:
            d = dG(i, j, T)
            re_rows.append([z.real for z in d])
            im_rows.append([z.imag for z in d])
    for i, j in zip(*same):
        r.append(mp.fsum(terms(i, j)).imag)
    cr_rows = []
    for i, j in zip(*cross):
        T = terms(i, j)
        g = mp.fsum(T)
        r.append((abs(g) ** 2 - 6) / (2 * s6))
        if want_jac:
            d = dG(i, j, T)
            cr_rows.append([(2 * (mp.conj(g) * z).real) / (2 * s6) for z in d])
    if not want_jac:
        return mp.matrix(r), None
    return mp.matrix(r), mp.matrix(re_rows + im_rows + cr_rows)


def bw_F(x, m, same, cross):
    """Brierley-Weigert objective: sum over pairs of (|<psi|psi'>| - chi)^2 with normalised
    vectors, chi = 0 inside a group and 1/sqrt(6) across groups (each pair counted once;
    the terms against the standard basis vanish identically in this parametrisation)."""
    V = mp_vectors(x, m)
    F = mp.mpf(0)
    for i, j in zip(*same):
        F += (abs(mp.fsum(mp.conj(V[i][k]) * V[j][k] for k in range(6))) / 6) ** 2
    for i, j in zip(*cross):
        F += (abs(mp.fsum(mp.conj(V[i][k]) * V[j][k] for k in range(6))) / 6
              - 1 / mp.sqrt(6)) ** 2
    return F


def polish(groups, x, digits=50, maxit=200, verbose=False):
    gid, m, same, cross, x = mp_setup(groups, x, digits)
    x = mp.matrix(x)
    lam = mp.mpf("1e-3")
    r, J = mp_res_jac(x, m, same, cross)
    cost = mp.fsum(t * t for t in r)
    gtol = mp.mpf(10) ** (-(digits - 15))
    for it in range(maxit):
        g = J.T * r
        gn = mp.norm(g)
        if verbose:
            print(f"  it {it}: misfit {mp.nstr(mp.sqrt(cost), 20)} grad {mp.nstr(gn, 5)}",
                  file=sys.stderr)
        if gn < gtol:
            break
        A = J.T * J
        while True:
            try:
                step = mp.lu_solve(A + lam * mp.eye(A.rows), -g)
            except ZeroDivisionError:
                lam *= 10
                continue
            xn = x + step
            rn, _ = mp_res_jac(xn, m, same, cross, want_jac=False)
            cn = mp.fsum(t * t for t in rn)
            if cn <= cost:
                x, cost = xn, cn
                r, J = mp_res_jac(x, m, same, cross)
                lam = max(lam / 10, mp.mpf(10) ** (-digits))
                break
            lam *= 10
            if lam > 1e30:
                return x, mp.sqrt(cost), gn, it, (m, same, cross)
    return x, mp.sqrt(cost), mp.norm(J.T * r), it, (m, same, cross)


def hessian_eigs(groups, x):
    """Eigenvalues of the Hessian of (1/2)|r|^2 in double precision (central differences
    of the analytic gradient)."""
    gid, m, same, cross = S.layout(groups)
    x = np.array([float(t) for t in x])

    def grad(y):
        return S.jacobian(y, m, same, cross).T @ S.residuals(y, m, same, cross)

    h = 1e-6
    H = np.array([(grad(x + h * e) - grad(x - h * e)) / (2 * h) for e in np.eye(len(x))])
    return np.linalg.eigvalsh((H + H.T) / 2)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("file", help="JSONL written by search.py or sym_search.py")
    ap.add_argument("--kind", default="solution", choices=["solution", "nearmiss"])
    ap.add_argument("--index", type=int, default=0, help="which record of that kind")
    ap.add_argument("--digits", type=int, default=50)
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    recs = [json.loads(l) for l in open(a.file)]
    rec = [r for r in recs if r.get("kind") == a.kind][a.index]
    groups = rec["groups"]
    x, misfit, gn, its, (m, same, cross) = polish(groups, rec["phases"], a.digits, verbose=True)
    ev = hessian_eigs(groups, x)
    out = dict(groups=groups, source=a.file, kind=a.kind, index=a.index, digits=a.digits,
               iterations=its, misfit=mp.nstr(misfit, 30), grad_norm=mp.nstr(gn, 5),
               bw_F=mp.nstr(bw_F(x, m, same, cross), 20),
               hessian_min_eigs=[float(t) for t in ev[:4]],
               phases=[mp.nstr(t, 40) for t in x])
    print(json.dumps({k: v for k, v in out.items() if k != "phases"}, indent=1))
    if a.out:
        with open(a.out, "a") as fh:
            fh.write(json.dumps(out) + "\n")
