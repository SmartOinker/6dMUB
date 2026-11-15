"""Biunimodular vectors for F_d: batched Levenberg-Marquardt on the (d-1)-phase system
   A_s(x) = sum_j x_j conj(x_{j+s}) = 0,  s = 1..floor(d/2)   (x_0 = 1, |x_j| = 1).
Usage: python3 bu.py d nstarts seed out.npy
"""
import numpy as np, sys, time

def residual_jac(P, d):
    B = P.shape[0]
    ph = np.concatenate([np.zeros((B, 1)), P], axis=1)
    x = np.exp(1j * ph)                       # (B,d)
    rs, Js = [], []
    for s in range(1, d // 2 + 1):
        xs = np.roll(x, -s, axis=1)           # x_{j+s}
        t = x * xs.conj()                      # x_j conj x_{j+s}
        A = t.sum(1)
        # dA/dp_k = i x_k conj x_{k+s} - i x_{k-s} conj x_k = i t_k - i t_{k-s}
        dA = 1j * t - 1j * np.roll(t, s, axis=1)
        dA = dA[:, 1:]
        if 2 * s == d:
            rs.append(A.real[:, None]); Js.append(dA.real[:, None, :])
        else:
            rs += [A.real[:, None], A.imag[:, None]]
            Js += [dA.real[:, None, :], dA.imag[:, None, :]]
    return np.concatenate(rs, 1), np.concatenate(Js, 1)

def solve(P, d, iters=200, tol=1e-13):
    B, n = P.shape
    lam = np.full(B, 1e-2)
    r, J = residual_jac(P, d)
    f = (r * r).sum(1)
    I = np.eye(n)
    for it in range(iters):
        JT = J.transpose(0, 2, 1)
        H = JT @ J + lam[:, None, None] * I
        g = (JT @ r[:, :, None])[:, :, 0]
        dP = -np.linalg.solve(H, g[:, :, None])[:, :, 0]
        Pn = P + dP
        rn, Jn = residual_jac(Pn, d)
        fn = (rn * rn).sum(1)
        acc = fn < f
        P = np.where(acc[:, None], Pn, P); r = np.where(acc[:, None], rn, r)
        J = np.where(acc[:, None, None], Jn, J); f = np.where(acc, fn, f)
        lam = np.where(acc, np.maximum(lam / 5, 1e-15), lam * 4)
        if (np.sqrt(f) < tol).mean() > 0.999 and it > 30:
            break
    # final pure Newton polish
    for _ in range(3):
        r, J = residual_jac(P, d)
        try:
            dP = -np.linalg.solve(J, r[:, :, None])[:, :, 0]
        except np.linalg.LinAlgError:
            break
        Pn = P + dP; rn, _ = residual_jac(Pn, d)
        ok = (rn * rn).sum(1) <= (r * r).sum(1)
        P = np.where(ok[:, None], Pn, P)
    r, J = residual_jac(P, d)
    return np.mod(P, 2 * np.pi), np.sqrt((r * r).sum(1)), J

def dedupe(P, d, decimals=7):
    x = np.exp(1j * np.concatenate([np.zeros((len(P), 1)), P], 1))
    keys = {}
    for i, v in enumerate(x):
        k = tuple(np.round(np.concatenate([v.real, v.imag]), decimals) + 0.0)
        keys.setdefault(k, i)
    return np.array(sorted(keys.values()))

def run(d, nstarts, seed, batch=20000):
    rng = np.random.default_rng(seed)
    sols, hits = [], []
    done = 0
    while done < nstarts:
        b = min(batch, nstarts - done)
        P0 = rng.uniform(0, 2 * np.pi, (b, d - 1))
        P, res, J = solve(P0, d)
        conv = res < 1e-11
        sols.append(P[conv]); done += b
    P = np.concatenate(sols)
    return P

if __name__ == "__main__":
    d, n, seed, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    t = time.time()
    P = run(d, n, seed)
    x = np.exp(1j * np.concatenate([np.zeros((len(P), 1)), P], 1))
    idx = dedupe(P, d)
    # hit counts
    keyof = lambda v: tuple(np.round(np.concatenate([v.real, v.imag]), 7) + 0.0)
    from collections import Counter
    cnt = Counter(keyof(v) for v in x)
    U = P[idx]
    h = np.array([cnt[keyof(x[i])] for i in idx])
    np.save(out, U); np.save(out.replace('.npy', '_hits.npy'), h)
    print(f"d={d} starts={n} converged={len(P)} distinct={len(U)} minhits={h.min() if len(h) else 0} time={time.time()-t:.1f}s")
