"""Find cyclic 10-roots numerically (heuristic search; nothing here is a proof - see certify_roots.py).

Coordinates: x in (C*)^10, x_0 = 1, g_k(x) = sum_j x_{j+k}/x_j = 0 (k=1..9)  (z_j = x_{j+1}/x_j gives cyclic 10-roots).
Method: damped Newton from random starts, in x-coordinates (log-normal moduli) and in log-coordinates (trust region),
then closure of every newly found root under the symmetry group of order 1600:
  dilation j -> a*j (a in {1,3,7,9}), inversion x -> 1/x, complex conjugation, cyclic shift (renormalised x_0 = 1),
  modulation x_j -> w^(m j) x_j (w = exp(2 pi i/10)).
Each symmetry is verified numerically on found roots (residual of the image) before the closure is used.
Usage: python3 find_roots.py TIME_LIMIT_SECONDS SEED out.npy [TARGET=34940]
"""
import numpy as np, sys, time, itertools
d = 10; TARGET = 34940
W = np.exp(2j * np.pi / d)

def G(Xv):
    B = Xv.shape[0]
    x = np.concatenate([np.ones((B, 1), complex), Xv], 1); ix = 1 / x
    r = np.empty((B, d - 1), complex); J = np.empty((B, d - 1, d - 1), complex)
    for k in range(1, d):
        xk = np.roll(x, -k, 1); t = xk * ix
        r[:, k - 1] = t.sum(1)
        J[:, k - 1, :] = (np.roll(ix, k, 1) - t * ix)[:, 1:]
    return r, J

def newton_x(Xv, iters=60):
    with np.errstate(all='ignore'):
        r, J = G(Xv); f = np.abs(r).max(1)
        for _ in range(iters):
            dx = np.linalg.solve(J, -r[:, :, None])[:, :, 0]
            step = np.ones(len(Xv)); best = Xv.copy(); bf = f.copy()
            for _ in range(6):
                Xn = Xv + step[:, None] * dx
                rn, _ = G(Xn); fn = np.abs(rn).max(1)
                ok = np.isfinite(fn) & (fn < bf)
                best = np.where(ok[:, None], Xn, best); bf = np.where(ok, fn, bf)
                step = np.where(ok, step, step / 2)
                if ok.all(): break
            Xv = best; r, J = G(Xv); f = np.abs(r).max(1)
    return Xv, f

def newton_log(U, iters=80):
    with np.errstate(all='ignore'):
        for _ in range(iters):
            X = np.exp(U); r, J = G(X); Jl = J * X[:, None, :]
            dx = np.linalg.solve(Jl, -r[:, :, None])[:, :, 0]
            s = np.minimum(1, 0.5 / np.maximum(np.abs(dx).max(1), 1e-300))
            U = U + s[:, None] * dx; U = np.where(np.isfinite(U), U, 0)
        X = np.exp(U); r, _ = G(X)
    return X, np.abs(r).max(1)

def resid(Xv):
    with np.errstate(all='ignore'):
        r, _ = G(Xv)
    return np.abs(r).max(1)

# ---- symmetry group: list of (a, inv, conj, s, m) ----
UNITS = [1, 3, 7, 9]
def image(x, a, inv, cj, s, m):
    """x: (B,10) with x_0=1 -> image (B,10) with x_0=1."""
    y = x[:, (a * np.arange(d)) % d]
    if inv: y = 1 / y
    if cj: y = y.conj()
    y = np.roll(y, -s, 1); y = y / y[:, :1]
    return y * W ** (m * np.arange(d))
GROUP = list(itertools.product(UNITS, [0, 1], [0, 1], range(d), range(d)))
assert len(GROUP) == 1600

def orbit(x):  # x: (9,) -> (1600,9)
    x10 = np.concatenate([[1], x])[None]
    return np.array([image(x10, *g)[0, 1:] for g in GROUP])

def key(X, dec=6):
    a = np.round(np.concatenate([X.real, X.imag], 1), dec) + 0.0
    return [tuple(v) for v in a]

def verify_symmetries(X):
    """each single generator, applied to polished roots, must give residual < 1e-9"""
    x10 = np.concatenate([np.ones((len(X), 1), complex), X], 1)
    gens = {"dilation3": (3,0,0,0,0), "dilation9(reversal)": (9,0,0,0,0), "inversion": (1,1,0,0,0), "conjugation": (1,0,1,0,0),
            "shift": (1,0,0,1,0), "modulation": (1,0,0,0,1)}
    for name, g in gens.items():
        r = resid(image(x10, *g)[:, 1:]).max()
        print(f"symmetry check {name}: max residual of images = {r:.2e}", flush=True)
        assert r < 1e-9, name

if __name__ == "__main__":
    tl, seed, out = float(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    if len(sys.argv) > 4: TARGET = int(sys.argv[4])
    rng = np.random.default_rng(seed); t0 = time.time()
    roots = []; known = set(); starts = 0; batch = 4000; it = 0; checked = False
    log = open(out + ".growth.log", "a")
    while time.time() - t0 < tl and len(roots) < TARGET:
        it += 1
        import os; sig = rng.choice([float(s) for s in os.environ.get("SIGS","0.4,0.7,1.0").split(",")])
        if it % 2:
            X0 = np.exp(rng.normal(0, sig, (batch, 9)) + 1j * rng.uniform(0, 2 * np.pi, (batch, 9)))
            X, f = newton_x(X0)
        else:
            X, f = newton_log(rng.normal(0, sig, (batch, 9)) + 1j * rng.uniform(0, 2 * np.pi, (batch, 9)))
        starts += batch
        good = X[f < 1e-9]
        if len(good):
            good, f2 = newton_x(good, 4); good = good[f2 < 1e-12]
        if len(good) and not checked:
            verify_symmetries(good[:50]); checked = True
        ks = key(good); new = [v for v, k in zip(good, ks) if k not in known]
        for v in new:
            if tuple(key(v[None])[0]) in known: continue
            orb = orbit(v)
            r = resid(orb); orb = orb[r < 1e-9]
            for o, k in zip(orb, key(orb)):
                if k not in known: known.add(k); roots.append(o)
        msg = f"starts {starts} converged {len(good)} distinct_roots {len(roots)} t={time.time()-t0:.0f}s"
        print(msg, flush=True); log.write(msg + "\n"); log.flush()
        if it % 5 == 0: np.save(out, np.array(roots))
    np.save(out, np.array(roots))
    print(f"FINAL distinct roots (rounded 1e-6 keys): {len(roots)} after {starts} starts, {time.time()-t0:.0f}s", flush=True)
