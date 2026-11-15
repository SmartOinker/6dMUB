"""Task 3: maximise P_4 (or mean D^2) over n bases, first fixed to identity.
Usage: python t3_optimise.py d n kind(P|D) n_random n_seeded seed tag
Smoothing |m| -> sqrt(|m|^2+delta^2) with continuation delta=1e-2..1e-8, then exact evaluation."""
import sys, json, time, numpy as np
from scipy.optimize import minimize
from common import *

def run(d, n, kind, x0):
    x = x0
    for delta in (1e-2, 1e-3, 1e-4, 1e-6, 1e-8) if kind == 'P' else (0,):
        fg = make_fg(d, n, kind, delta)
        r = minimize(fg, x, jac=True, method='L-BFGS-B', options=dict(maxiter=1500, maxfun=3000, ftol=1e-15, gtol=1e-10))
        x = r.x
    Bs = bases_from_x(x, d, n)
    return x, Bs

def score(Bs, kind):
    return P_n(Bs) if kind == 'P' else D2_n(Bs)

if __name__ == '__main__':
    d, n, kind = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    nr, ns, seed, tag = int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), sys.argv[7]
    tmax = float(sys.argv[8]) if len(sys.argv) > 8 else 420
    rng = np.random.default_rng(seed)
    npar = make_index(d)[1]
    t0 = time.time(); results = []; best = (-1, None)
    def starts():
        for i in range(nr + ns):
            if i < nr:
                x0 = np.concatenate([x_from_unitary(haar(d, rng), d) for _ in range(n - 1)]); kindstart = 'random'
            else:
                M = mubs_d6() if d == 6 else mubs_prime(d)
                xs = [x_from_unitary(M[k], d) for k in range(1, 3)] + [x_from_unitary(haar(d, rng), d)]
                x0 = np.concatenate(xs[:n - 1]); kindstart = 'seeded3MUB'
            yield kindstart, x0
    for ks, x0 in starts():
        if time.time() - t0 > tmax: break
        x, Bs = run(d, n, kind, x0)
        v = score(Bs, kind)
        results.append((ks, v))
        if v > best[0]: best = (v, Bs)
    vals = np.array([v for _, v in results])
    ks = np.array([k for k, _ in results])
    summ = dict(d=d, n=n, kind=kind, seed=seed, n_runs=len(results), best=float(best[0]),
                best_random=float(vals[ks == 'random'].max()) if (ks == 'random').any() else None,
                best_seeded=float(vals[ks == 'seeded3MUB'].max()) if (ks == 'seeded3MUB').any() else None,
                top10=[float(v) for v in np.sort(vals)[::-1][:10]], elapsed=time.time() - t0)
    Bs = best[1]
    if kind == 'P':
        summ['pairwise_P'] = pairs_P(Bs); summ['P_n'] = P_n(Bs); summ['D2_of_this_set'] = D2_n(Bs)
        summ['mub_bound'] = P_bound(d); summ['gap_to_bound'] = P_bound(d) - P_n(Bs)
    else:
        summ['pairwise_D2'] = [D2_pair(Bs[a], Bs[b]) for a in range(n) for b in range(a + 1, n)]
        summ['D2_n'] = D2_n(Bs); summ['P_of_this_set'] = P_n(Bs)
    np.save(f"{OUT}/bases_{tag}.npy", np.array(Bs))
    summ['bases_re'] = [B.real.tolist() for B in Bs]   # JSON dump with repr-level (17 digit) floats
    summ['bases_im'] = [B.imag.tolist() for B in Bs]
    json.dump(summ, open(f"{OUT}/opt_{tag}.json", 'w'))
    print({k: v for k, v in summ.items() if not k.startswith('bases')})
