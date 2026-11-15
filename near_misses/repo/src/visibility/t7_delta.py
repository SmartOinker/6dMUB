"""Task 7: minimise delta = max over pairs,i,j of | |<e_i|f_j>|^2 - 1/d |  over n bases (first = identity).
Stage 1: p-norm surrogate (1/p) log sum |c|^p, p = 2,4,8,16,32,64 (L-BFGS, analytic gradient).
Stage 2: SLSQP epigraph polish: min t s.t. -t <= c_k <= t (true max, all d^2*npairs entries).
Usage: python t7_delta.py d n nrand tmax seed tag [fixed_triple]"""
import sys, json, time, numpy as np
from itertools import combinations
from scipy.optimize import minimize
from common import *

def setup(d, n, fixed):
    nf = len(fixed); nfree = n - 1 - nf; npar = make_index(d)[1]
    return nf, nfree, npar

def build(x, d, n, fixed, npar):
    Bs = [np.eye(d, dtype=complex)] + [f for f in fixed]; caches = [None] * (1 + len(fixed))
    for k in range(n - 1 - len(fixed)):
        U, c = unitary_and_cache(x[k * npar:(k + 1) * npar], d); Bs.append(U); caches.append(c)
    return Bs, caches

def devs(Bs, d):
    return np.concatenate([(np.abs(Bs[a].conj().T @ Bs[b]) ** 2 - 1 / d).ravel() for a, b in combinations(range(len(Bs)), 2)])

def delta_true(Bs, d): return np.abs(devs(Bs, d)).max()

def make_pnorm(d, n, fixed, p):
    npar = make_index(d)[1]; nf = len(fixed)
    def fg(x):
        Bs, caches = build(x, d, n, fixed, npar)
        G = [np.zeros((d, d), complex) for _ in range(n)]; S = 0.0; vs = []
        # adaptive scale c0 = current max |c| avoids under/overflow as delta -> 0:  F = log c0 + (1/p) log sum (|c|/c0)^p
        raw = [(a, b, Bs[a].conj().T @ Bs[b]) for a, b in combinations(range(n), 2)]
        c0 = max(max((np.abs(np.abs(m) ** 2 - 1 / d)).max() for _, _, m in raw), 1e-250)
        for a, b, m in raw:
            c = (np.abs(m) ** 2 - 1 / d) / c0
            S += (np.abs(c) ** p).sum(); vs.append((a, b, m, c))
        for a, b, m, c in vs:
            v = np.abs(c) ** (p - 1) * np.sign(c) / S / c0
            G[b] += Bs[a] @ (v * m); G[a] += Bs[b] @ (v * m.conj()).T
        g = np.concatenate([grad_x_from_G(G[k], caches[k], d) for k in range(1 + nf, n)])
        return np.log(c0) + np.log(S) / p, g
    return fg

def slsqp_polish(x, d, n, fixed, maxiter=200):
    npar = make_index(d)[1]; nf = len(fixed); nx = len(x)
    prs = list(combinations(range(n), 2))
    def cons(z):
        Bs, _ = build(z[:-1], d, n, fixed, npar); c = devs(Bs, d); t = z[-1]
        return np.concatenate([t - c, t + c])
    def jac(z):
        Bs, caches = build(z[:-1], d, n, fixed, npar); J = np.zeros((2 * len(prs) * d * d, nx + 1))
        r = 0; Jc = np.zeros((len(prs) * d * d, nx))
        for a, b in prs:
            m = Bs[a].conj().T @ Bs[b]
            for i in range(d):
                for j in range(d):
                    G = [None] * n
                    gx = np.zeros(nx)
                    for k, vec, col in ((b, Bs[a][:, i] * m[i, j], j), (a, Bs[b][:, j] * np.conj(m[i, j]), i)):
                        if k >= 1 + nf:
                            Gk = np.zeros((d, d), complex); Gk[:, col] = vec
                            gx[(k - 1 - nf) * npar:(k - nf) * npar] += grad_x_from_G(Gk, caches[k], d)
                    Jc[r] = gx; r += 1
        J[:len(Jc), :nx] = -Jc; J[:len(Jc), -1] = 1; J[len(Jc):, :nx] = Jc; J[len(Jc):, -1] = 1
        return J
    t0 = np.abs(devs(build(x, d, n, fixed, npar)[0], d)).max()
    z0 = np.concatenate([x, [t0]])
    r = minimize(lambda z: z[-1], z0, jac=lambda z: np.eye(len(z))[-1], method='SLSQP',
                 constraints=[dict(type='ineq', fun=cons, jac=jac)], options=dict(maxiter=maxiter, ftol=1e-15))
    return r.x[:-1]

def optimise(x0, d, n, fixed, ps=(2, 4, 8, 16, 32, 64), gate=None):
    x = x0
    if gate is not None:       # calibration mode: cheap p=2 pre-screen; abandon runs that are not converging to an exact MUB set
        x = minimize(make_pnorm(d, n, fixed, 2), x, jac=True, method='L-BFGS-B', options=dict(maxiter=800, ftol=1e-15, gtol=1e-12)).x
        Bs, _ = build(x, d, n, fixed, make_index(d)[1]); dp = delta_true(Bs, d)
        if dp > gate: return dp, x, dp
        ps = ps[1:]
    for p in ps:
        fg = make_pnorm(d, n, fixed, p)
        x = minimize(fg, x, jac=True, method='L-BFGS-B', options=dict(maxiter=800, ftol=1e-15, gtol=1e-12)).x
    Bs, _ = build(x, d, n, fixed, make_index(d)[1]); dp = delta_true(Bs, d)
    best = (dp, x)
    if gate is not None and dp > gate: return dp, x, dp    # calibration mode: skip slow polish for clearly non-MUB runs
    for rnd in range(3):                     # SLSQP polish, a few restarts
        try: xs = slsqp_polish(best[1], d, n, fixed)
        except Exception as e: break
        Bs, _ = build(xs, d, n, fixed, make_index(d)[1]); dd = delta_true(Bs, d)
        if dd < best[0] - 1e-13: best = (dd, xs)
        else: break
    return best[0], best[1], dp

def star_seed(d, rng):
    F = np.exp(2j * np.pi * np.outer(np.arange(d), np.arange(d)) / d) / np.sqrt(d)
    D = lambda: np.diag(np.exp(2j * np.pi * rng.random(d)))
    P = lambda: np.eye(d)[rng.permutation(d)]
    return D() @ F @ D() @ P()

def classify(Bs, d, tol=1e-6):
    n = len(Bs); prs = list(combinations(range(n), 2))
    dm = {pr: np.abs(np.abs(Bs[pr[0]].conj().T @ Bs[pr[1]]) ** 2 - 1 / d).max() for pr in prs}
    zero = [pr for pr in prs if dm[pr] < tol]
    if len(zero) == 0: return 'spread (no exactly unbiased pair)', dm
    for tri in combinations(range(n), 3):
        if all(p in zero for p in combinations(tri, 2)): return 'triangle (contains exact MUB triple)', dm
    for c in range(n):
        if sum(1 for pr in zero if c in pr) >= n - 1: return 'star (one basis unbiased to all others)', dm
    return f'partial ({len(zero)} exactly unbiased pairs, no star/triangle)', dm

if __name__ == '__main__':
    d, n, nrand, tmax, seed, tag = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
    fixed_triple = len(sys.argv) > 7 and sys.argv[7] == 'fixed'
    calib = len(sys.argv) > 7 and sys.argv[7] == 'calib'   # p-norm stages only, polish only runs already < 1e-3
    rng = np.random.default_rng(seed); t0 = time.time()
    fixed = mubs_d6()[1:3] if fixed_triple else []
    nfree = n - 1 - len(fixed)
    X = lambda U: x_from_unitary(U, d)
    starts = []
    if fixed_triple:
        starts = [('random4th', X(haar(d, rng))) for _ in range(nrand)]
    else:
        for _ in range(nrand): starts.append(('random', np.concatenate([X(haar(d, rng)) for _ in range(n - 1)])))
        if d == 6 and n == 4:
            for f in ('bases_d6_P4.npy', 'bases_d6_D2.npy'):
                B = np.load(f"{OUT}/{f}")
                for s in (0, 0.02, 0.05):
                    xs = np.concatenate([X(B[k]) for k in range(1, 4)])
                    starts.append((f'saved_{f[9:-4]}_pert{s}', xs + s * rng.standard_normal(len(xs))))
            M = mubs_d6()
            for _ in range(nrand // 3): starts.append(('3MUB+random', np.concatenate([X(M[1]), X(M[2]), X(haar(d, rng))])))
            for _ in range(nrand // 3): starts.append(('star_seed', np.concatenate([X(star_seed(d, rng)) for _ in range(3)])))
        # interleave so the time cap does not drop whole categories
        rng.shuffle(starts) if False else None
        order = np.random.default_rng(seed + 1).permutation(len(starts)); starts = [starts[i] for i in order]
    res = []; best = (9, None, None)
    for kind, x0 in starts:
        if time.time() - t0 > tmax: break
        dl, x, dp = optimise(x0, d, n, fixed, gate=1e-3 if calib else None)
        res.append((kind, dl, dp))
        if dl < best[0]: best = (dl, x, kind)
    dl, x, kind = best
    Bs, _ = build(x, d, n, fixed, make_index(d)[1])
    cls, dm = classify(Bs, d); allc = np.abs(devs(Bs, d)); dd = allc.max()
    out = dict(d=d, n=n, tag=tag, fixed_triple=fixed_triple, n_starts_run=len(res), n_starts_planned=len(starts), best_delta=float(dd),
               best_start_kind=kind, pair_max=[float(dm[p]) for p in combinations(range(n), 2)],
               n_active_within_1em6=int((allc > dd - 1e-6).sum()), n_overlaps=int(len(allc)), n_starts_below_1em9=int(sum(1 for r in res if r[1] < 1e-9)), structure=cls,
               pnorm_only_delta_of_best=None, P_n=float(P_n(Bs)), D2_n=float(D2_n(Bs)),
               delta_by_kind={k: float(min(v for kk, v, _ in res if kk.split('_pert')[0] == k.split('_pert')[0])) for k in set(r[0] for r in res)},
               top10=sorted(float(r[1]) for r in res)[:10], elapsed=time.time() - t0,
               note='numerical upper bound on the minimum: explicit bases achieve this delta; nothing proves a lower bound')
    np.save(f"{OUT}/bases_{tag}.npy", np.array(Bs))
    out['bases_re'] = [B.real.tolist() for B in Bs]; out['bases_im'] = [B.imag.tolist() for B in Bs]
    json.dump(out, open(f"{OUT}/delta_{tag}.json", 'w'))
    print({k: v for k, v in out.items() if not k.startswith('bases')})
