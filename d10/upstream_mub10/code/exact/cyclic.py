"""Complex cyclic d-roots in x-coordinates: x in (C*)^d, x_0 = 1,
   g_k(x) = sum_j x_{j+k}/x_j = 0, k = 1..d-1  (z_j = x_{j+1}/x_j gives the cyclic d-roots system).
Random damped Newton + closure under the symmetry group.
Usage: python3 cyclic.py d nstarts seed out.npy [existing.npy]
"""
import numpy as np, sys, time

def G(Xv, d):
    # Xv: (B,d-1) -> full x (B,d)
    B = Xv.shape[0]
    x = np.concatenate([np.ones((B, 1), complex), Xv], 1)
    ix = 1 / x
    r = np.empty((B, d - 1), complex); J = np.zeros((B, d - 1, d - 1), complex)
    for k in range(1, d):
        xk = np.roll(x, -k, 1)            # x_{j+k}
        t = xk * ix                        # x_{j+k}/x_j
        r[:, k - 1] = t.sum(1)
        # d/dx_m: term j=m-k (a=m): 1/x_{m-k};  term j=m (b=m): -x_{m+k}/x_m^2
        dm = np.roll(ix, k, 1) - xk * ix * ix
        J[:, k - 1, :] = dm[:, 1:]
    return r, J

def newton(Xv, d, iters=80):
    r, J = G(Xv, d); f = np.abs(r).max(1)
    for it in range(iters):
        try:
            dx = np.linalg.solve(J, -r[:, :, None])[:, :, 0]
        except np.linalg.LinAlgError:
            dx = np.linalg.lstsq(J[0], -r[0], rcond=None)[0][None] * 0  # unreachable in practice
        step = np.ones(len(Xv))
        best = Xv.copy(); bf = f.copy()
        for _ in range(6):
            Xn = Xv + step[:, None] * dx
            with np.errstate(all='ignore'):
                rn, _ = G(Xn, d)
                fn = np.abs(rn).max(1)
            ok = np.isfinite(fn) & (fn < bf)
            best = np.where(ok[:, None], Xn, best); bf = np.where(ok, fn, bf)
            step = np.where(ok, step, step / 2)
            if ok.all(): break
        moved = bf < f
        # where no improvement, take a random small kick to avoid stagnation
        Xv = np.where(moved[:, None], best, Xv)
        with np.errstate(all='ignore'):
            r, J = G(Xv, d)
        f = np.abs(r).max(1)
    return Xv, f

def key(Xv, dec=6):
    a = np.round(np.concatenate([Xv.real, Xv.imag], 1), dec) + 0.0
    return [tuple(v) for v in a]

def sym_images(Xv, d):
    """images of normalised x under generators; returns list of arrays (B,d-1)"""
    B = len(Xv); x = np.concatenate([np.ones((B, 1), complex), Xv], 1)
    w = np.exp(2j * np.pi / d); out = []
    s = np.roll(x, -1, 1); out.append(s / s[:, :1])                # shift
    out.append(x * w ** np.arange(d))                              # modulation
    out.append(1 / x)                                              # inversion (analytic conj)
    out.append(x.conj())                                           # complex conjugation
    for m in range(2, d):
        if np.gcd(m, d) == 1: out.append(x[:, (m * np.arange(d)) % d])
    return [o[:, 1:] for o in out]

def closure(S, d, tol=1e-9):
    """close a set of roots under the group; images are Newton-polished"""
    idx = {k: i for i, k in enumerate(key(S))}
    S = list(S); frontier = np.array(S)
    while len(frontier):
        new = []
        for img in sym_images(frontier, d):
            img, f = newton(img, d, iters=3)
            for v, k, ff in zip(img, key(img), f):
                if ff < tol and k not in idx:
                    idx[k] = len(S); S.append(v); new.append(v)
        frontier = np.array(new)
    return np.array(S)

if __name__ == "__main__":
    d, n, seed, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    rng = np.random.default_rng(seed); t0 = time.time()
    S = np.load(sys.argv[5]) if len(sys.argv) > 5 else np.zeros((0, d - 1), complex)
    known = set(key(S)) if len(S) else set()
    batch = 5000; done = 0; found = []
    while done < n:
        b = min(batch, n - done)
        X0 = np.exp(rng.normal(0, float(__import__("os").environ.get("SIG","0.7")), (b, d - 1)) + 1j * rng.uniform(0, 2 * np.pi, (b, d - 1)))
        Xv, f = newton(X0, d)
        good = Xv[f < 1e-10]
        for v, k in zip(good, key(good)):
            if k not in known:
                known.add(k); found.append(v)
        done += b
        print(f"starts {done}, converged {len(good)}/{b}, new distinct so far {len(found)}, {time.time()-t0:.0f}s", flush=True)
    S = np.concatenate([S, np.array(found).reshape(-1, d - 1)]) if found else S
    print("before closure:", len(S), flush=True)
    S = closure(S, d)
    print(f"after closure: {len(S)}  time {time.time()-t0:.0f}s")
    np.save(out, S)
