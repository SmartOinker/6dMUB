"""Dimension six, Fourier pair {I, F_6}: the 48 unbiased vectors, certified enclosures, the 16 candidate third bases,
and numerical energy minima for the 16 triples {I, F_6, B}."""
import json, sys, itertools, numpy as np
from scipy.spatial import cKDTree
from scipy.optimize import minimize
from flint import arb, acb, acb_mat, ctx
ctx.prec = 200
d = 6; rng = np.random.default_rng(1)
W = np.exp(-2j*np.pi*np.outer(np.arange(d), np.arange(d))/d)
def resjac(th):
    x = np.concatenate([np.ones((th.shape[0],1)), np.exp(1j*th)], axis=1); X = x @ W.T
    return np.abs(X)**2 - d, -2*np.imag(np.conj(X)[:, :, None] * x[:, None, 1:] * W[None, :, 1:])
B = 6000; th = rng.uniform(0, 2*np.pi, size=(B, d-1)); lam = np.full(B, 1e-2); r, Jm = resjac(th); f = (r**2).sum(1)
for it in range(500):
    A = np.einsum('bki,bkj->bij', Jm, Jm) + lam[:, None, None]*np.eye(d-1)[None]
    step = -np.linalg.solve(A, np.einsum('bki,bk->bi', Jm, r)[..., None])[..., 0]
    r2, J2 = resjac(th + step); f2 = (r2**2).sum(1); acc = f2 < f
    th = np.where(acc[:, None], th + step, th); r = np.where(acc[:, None], r2, r); Jm = np.where(acc[:, None, None], J2, Jm)
    f = np.where(acc, f2, f); lam = np.clip(np.where(acc, lam*0.3, lam*4.0), 1e-12, 1e8)
x = np.exp(1j*th[f < 1e-20]); pts = np.concatenate([x.real, x.imag], axis=1)
keep = []
for i, p in enumerate(pts):
    if all(np.abs(p - pts[k]).max() > 1e-6 for k in keep): keep.append(i)
x = x[keep]; order = np.lexsort(np.round(np.angle(x), 8).T[::-1]); x = x[order]
print("distinct unbiased vectors found:", len(x))
# Newton polish in arb + Krawczyk (system g_k(x) = sum_j x_{j+k}/x_j, k = 1..5, x_0 = 1)
def G(v): return [sum((v[(j+k) % d]/v[j] for j in range(d)), acb(0)) for k in range(1, d)]
def J(v): return [[1/v[(m-k) % d] - v[(m+k) % d]/(v[m]*v[m]) for m in range(1, d)] for k in range(1, d)]
R = arb("1e-30"); disc0 = acb(arb(0, R.upper()), arb(0, R.upper())); encl = []; mids = []
for row in x:
    p = [acb(1)] + [acb(float(z.real), float(z.imag)) for z in row]
    for _ in range(8):                                   # Newton at 200 bits on midpoints
        Jm_ = acb_mat(d-1, d-1, [e for rr in J(p) for e in rr]); Gp = acb_mat(d-1, 1, G(p))
        dx = Jm_.solve(Gp)
        p = [acb(1)] + [acb(arb(float((p[i+1].real - dx[i,0].real).mid())*0 + (p[i+1].real - dx[i,0].real).mid()), arb((p[i+1].imag - dx[i,0].imag).mid())) for i in range(d-1)]
    Jf = np.array([[complex(float(e.real.mid()), float(e.imag.mid())) for e in rr] for rr in J(p)]); Yf = np.linalg.inv(Jf)
    Y = acb_mat(d-1, d-1, [acb(float(z.real), float(z.imag)) for z in Yf.ravel()])
    X = [acb(1)] + [p[i] + disc0 for i in range(1, d)]
    I5 = acb_mat(d-1, d-1, [acb(1) if i == j else acb(0) for i in range(d-1) for j in range(d-1)])
    dev = (Y*acb_mat(d-1, 1, G(p)))*(-1) + (I5 - Y*acb_mat(d-1, d-1, [e for rr in J(X) for e in rr]))*acb_mat(d-1, 1, [disc0]*(d-1))
    ok = all((abs(dev[i,0].real) < R) and (abs(dev[i,0].imag) < R) for i in range(d-1))
    K = [acb(1)] + [p[i+1] + dev[i,0] for i in range(d-1)]
    uni = all((abs((1/K[i].conjugate() - p[i]).real) < R) and (abs((1/K[i].conjugate() - p[i]).imag) < R) for i in range(1, d))
    assert ok and uni
    encl.append(K); mids.append([str(c.real.mid()) + " " + str(c.imag.mid()) for c in p])
print("Krawczyk + unimodularity: 48/48 certified within 1e-30" if len(encl) == 48 else "count %d" % len(encl))
fl = np.array([[complex(float(c.real.mid()), float(c.imag.mid())) for c in K] for K in encl])
A_ = np.abs(fl.conj() @ fl.T); np.fill_diagonal(A_, 6); small = A_ < 1e-9
print("orthogonal pairs:", int(np.triu(small, 1).sum()), "; smallest other overlap: %.4f" % A_[~small & ~np.eye(48, dtype=bool)].min())
adj = [set(np.nonzero(small[i])[0].tolist()) for i in range(48)]; cl = set()
def bk(Rr, P, Xx):
    if not P and not Xx:
        if len(Rr) >= d:
            for s in itertools.combinations(sorted(Rr), d): cl.add(s)
        return
    for v in list(P):
        bk(Rr | {v}, P & adj[v], Xx & adj[v]); P.remove(v); Xx.add(v)
bk(set(), set(range(48)), set()); bases = sorted(cl); print("candidate third bases (6-cliques):", len(bases))
F6 = np.conj(W).T/np.sqrt(d)*0 + np.exp(2j*np.pi*np.outer(np.arange(d), np.arange(d))/d)/np.sqrt(d)
out = []
for bi, Bx in enumerate(bases):
    Bm = fl[list(Bx)].T/np.sqrt(d); Us = [np.eye(d), F6, Bm]
    for a in range(3):
        for b in range(a+1, 3): assert np.allclose(abs(Us[a].conj().T @ Us[b])**2, 1/d, atol=1e-10)
    M = np.concatenate([u.conj().T for u in Us])
    def fE(xx):
        psi = xx[:d] + 1j*xx[d:]; n2 = (abs(psi)**2).sum(); a = M @ psi; p = abs(a)**2/n2; e = p - 1/d
        gc = 2*(M.conj().T @ (2*e*a))/n2 - 2*(2*e*p).sum()*psi/n2
        return (e**2).sum(), np.concatenate([gc.real, gc.imag])
    vals = np.array([minimize(fE, rng.normal(size=2*d), jac=True, method="L-BFGS-B", options={"maxiter": 3000, "ftol": 1e-16, "gtol": 1e-13}).fun for _ in range(300)])
    out.append(dict(basis=list(map(int, Bx)), Emin=float(vals.min()), frac=float(np.mean(vals < vals.min() + 1e-9))))
    print("triple %2d: numerical min E = %.7f (reached by %.0f%% of 300 starts)" % (bi, vals.min(), 100*out[-1]["frac"]), flush=True)
json.dump(dict(mids=mids, bases=[list(map(int, b)) for b in bases], energy=out), open("fourier6.json", "w"))
np.save("fourier6_vecs.npy", fl)
es = np.array([o["Emin"] for o in out]); print("distinct minima:", np.unique(np.round(es, 6)), " threshold to beat delta 0.030224:", 18*0.030224**2)
