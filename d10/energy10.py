"""Numerical minimum of E(psi) = sum over 30 outcomes of (p - 1/10)^2 for triples {I, F_10, B} in dimension ten.
One representative B per basis orbit. Numerical upper bounds on the true minima (random-start L-BFGS)."""
import os; HERE = os.path.dirname(os.path.abspath(__file__)) + os.sep   # data files live next to this script
import json, numpy as np, time
from scipy.optimize import minimize
from scipy.stats import chi2, ncx2
from scipy.optimize import brentq
U = "/mnt/user-data/uploads/mathathon/mub10"
A = json.load(open(U + "/data/exact/d10_analysis.json"))
V = np.load(HERE+"vecs.npy") / np.sqrt(10)          # 3040 x 10, unit vectors (rows)
d = 10
F = np.exp(2j*np.pi*np.outer(np.arange(d), np.arange(d))/d)/np.sqrt(d)
I = np.eye(d)
rng = np.random.default_rng(5)
def Emin(Bm, starts):
    Us = [I, F, Bm]
    for a in range(3):
        for b in range(a+1, 3):
            assert np.allclose(abs(Us[a].conj().T @ Us[b])**2, 1/d, atol=1e-10)
    M = np.concatenate([u.conj().T for u in Us])                        # 30 x 10
    def f(x):
        psi = x[:d] + 1j*x[d:]; n2 = (abs(psi)**2).sum()
        a = M @ psi; p = abs(a)**2/n2; e = p - 1/d
        val = (e**2).sum()
        gp = 2*e                                                       # dval/dp
        # p = |a|^2/n2 ; gradient wrt psi (complex): 2 * (M^H (gp*a))/n2 - 2*sum(gp*p) psi/n2
        gc = 2*(M.conj().T @ (gp*a))/n2 - 2*(gp*p).sum()*psi/n2
        return val, np.concatenate([gc.real, gc.imag])
    vals = []
    for _ in range(starts):
        r = minimize(f, rng.normal(size=2*d), jac=True, method="L-BFGS-B", options={"maxiter": 2000, "ftol": 1e-16, "gtol": 1e-12})
        vals.append(r.fun)
    vals = np.array(vals)
    return vals.min(), float(np.mean(vals < vals.min() + 1e-8))
out = []; t0 = time.time()
for o, rep in enumerate(A["basis_orbit_reps"]):
    Bm = V[A["bases"][rep]].T                                           # columns
    e, frac = Emin(Bm, 150)
    out.append((o, A["basis_orbit_sizes"][o], e, frac))
    print(f"basis orbit {o:2d} (size {A['basis_orbit_sizes'][o]:3d}): min E = {e:.6f}   reached by {100*frac:.0f}% of starts   [{time.time()-t0:.0f}s]", flush=True)
es = np.array([x[2] for x in out])
print("smallest over the 19 classes: %.6f (orbit %d); largest: %.6f" % (es.min(), int(es.argmin()), es.max()))
for name, E in (("Heisenberg-Weyl product triple (orbit 14)", out[14][2]), ("hardest class", es.min())):
    df = 3*(d-1); thr = chi2.isf(1e-3, df)
    N = brentq(lambda n: ncx2.sf(thr, df, d*n*E) - 0.99, 1, 1e9)
    print(f"{name}: E = {E:.5f}; some outcome off by >= {np.sqrt(E/30):.4f}; hide-and-seek: {N:.0f} shots per setting for 99% at 0.1% false alarm")
json.dump([dict(orbit=o, size=s, Emin=e, frac=fr) for o, s, e, fr in out], open("energy10.json", "w"), indent=1)
