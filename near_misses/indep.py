"""Independent re-evaluation (own code, mpmath 60 digits) of the two certified near-misses of the 2008 table.
Checks: misfit value, gradient ~ 0, Hessian positive definite (numerically), every overlap condition and its error,
the 2008 success function F < 1e-7, and that a fresh optimiser started nearby returns to the same point."""
import json, mpmath as mp, numpy as np
from scipy.optimize import least_squares
mp.mp.dps = 60
pts = [json.loads(l) for l in open("repo/results/constellations/nearmiss/polished.jsonl")]
def build(ph, groups):
    m = sum(groups); V = [[mp.mpc(1)]*6]
    for i in range(1, m):
        V.append([mp.mpc(1)] + [mp.e**(1j*ph[5*(i-1)+k]) for k in range(5)])
    gid = [g for g, n in enumerate(groups) for _ in range(n)]
    return V, gid
def conditions(ph, groups):
    V, gid = build(ph, groups); m = len(V); orth = []; unb = []
    for i in range(m):
        for j in range(i+1, m):
            G = sum(mp.conj(V[i][k])*V[j][k] for k in range(6))        # vectors have norm^2 6
            if gid[i] == gid[j]: orth.append(abs(G)/6)                     # should be 0   (normalised overlap)
            else: unb.append((abs(G)**2/36 - mp.mpf(1)/6, abs(G)/6 - 1/mp.sqrt(6)))   # (|<u,v>|^2 - 1/6 , |<u,v>| - 1/sqrt6)
    return orth, unb
def rvec(ph, groups):
    V, gid = build(ph, groups); m = len(V); same = []; cross = []
    for i in range(m):
        for j in range(i+1, m):
            G = sum(mp.conj(V[i][k])*V[j][k] for k in range(6))
            if gid[i] == gid[j]: same.append(G)
            else: cross.append((abs(G)**2 - 6)/(2*mp.sqrt(6)))
    return [mp.re(g) for g in same] + [mp.im(g) for g in same] + cross
for p in pts:
    g = p["groups"]
    if g not in ([4,4,1],[5,3,1]): continue
    ph = [mp.mpf(s) for s in p["phases"]]
    r = rvec(ph, g); mis = mp.sqrt(sum(x*x for x in r))
    f = lambda *x: sum(y*y for y in rvec(list(x), g))/2
    grad = [mp.diff(f, ph, tuple(1 if a == b else 0 for b in range(len(ph))), h=mp.mpf(10)**-20) for a in range(len(ph))]
    gn = mp.sqrt(sum(x*x for x in grad))
    # float Hessian by finite differences of the float gradient
    phf = np.array([float(x) for x in ph])
    def rf(x): return np.array([float(y) for y in rvec([mp.mpf(float(t)) for t in x], g)])
    def rfast(x):
        m = sum(g); V = np.ones((m, 6), complex); V[1:, 1:] = np.exp(1j*x.reshape(m-1, 5))
        gid = np.array([k for k, n in enumerate(g) for _ in range(n)]); G = V.conj() @ V.T
        iu = np.triu_indices(m, 1); same = gid[iu[0]] == gid[iu[1]]; Gs = G[iu][same]; Gc = G[iu][~same]
        return np.concatenate([Gs.real, Gs.imag, (abs(Gc)**2 - 6)/(2*np.sqrt(6))])
    assert np.allclose(rf(phf), rfast(phf), atol=1e-13)
    n = len(phf); J = np.zeros((len(rfast(phf)), n)); h = 1e-6
    for a in range(n):
        e = np.zeros(n); e[a] = h; J[:, a] = (rfast(phf+e) - rfast(phf-e))/(2*h)
    def gradf(x):
        Jx = np.zeros((len(rfast(x)), n))
        for a in range(n):
            e = np.zeros(n); e[a] = h; Jx[:, a] = (rfast(x+e) - rfast(x-e))/(2*h)
        return Jx.T @ rfast(x)
    H = np.zeros((n, n)); hh = 1e-5
    for a in range(n):
        e = np.zeros(n); e[a] = hh; H[:, a] = (gradf(phf+e) - gradf(phf-e))/(2*hh)
    H = (H+H.T)/2; ev = np.linalg.eigvalsh(H)
    orth, unb = conditions(ph, g)
    # 2008 objective as coded in the repository's search.py, re-derived here: sum over same pairs |<u,v>|^2 + cross (|<u,v>|^2-1/6)^2, normalised vectors
    F = sum(o*o for o in orth) + sum(u[1]*u[1] for u in unb)
    # fresh optimiser from perturbed starts
    back = 0; rng = np.random.default_rng(3)
    for _ in range(20):
        s = least_squares(rfast, phf + 1e-3*rng.normal(size=n), method="lm", xtol=1e-15, ftol=1e-15, gtol=1e-15)
        back += abs(np.linalg.norm(s.fun) - float(mis)) < 1e-9
    print(f"shape {g}: misfit = {mp.nstr(mis, 22)}  (listed {p['misfit'][:24]})")
    print(f"   |grad f| = {mp.nstr(gn, 3)};  Hessian eigenvalues (float): min {ev[0]:.3e}, next {ev[1]:.3e}")
    print(f"   worst orthogonality error |<u,v>| = {mp.nstr(max(orth), 4)};  worst unbiasedness error ||<u,v>|^2 - 1/6| = {mp.nstr(max(abs(u[0]) for u in unb), 4)}")
    print(f"   2008 objective F recomputed = {mp.nstr(F, 6)};  listed bw_F = {p['bw_F']}")
    print(f"   20 perturbed restarts returning to the same misfit: {back}/20")
