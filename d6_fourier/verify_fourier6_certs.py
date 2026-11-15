"""VERIFY ONLY (no SDP solver needed): re-check the stored Gram matrices Q_fourier6_triple*.npy.
Certify E >= gamma for each of the 16 triples {I, F_6, B}.  The third-basis vectors are re-certified here (Krawczyk + sigma test)
from the stored midpoints, and enter the checker as balls."""
import json, re, sys, time, numpy as np
from flint import arb, acb, acb_mat, ctx
import sos_general as sg
ctx.prec = 200; d = 6
D = json.load(open("fourier6.json")); R = arb("1e-30"); disc0 = acb(arb(0, R.upper()), arb(0, R.upper()))
def G(v): return [sum((v[(j+k) % d]/v[j] for j in range(d)), acb(0)) for k in range(1, d)]
def J(v): return [[1/v[(m-k) % d] - v[(m+k) % d]/(v[m]*v[m]) for m in range(1, d)] for k in range(1, d)]
encl = []
for row in D["mids"]:
    p = [acb(1)] + [acb(*[arb(t) for t in re.findall(r"\[[^\]]+\]|\S+", s)]) for s in row[1:]]
    Jf = np.array([[complex(float(e.real.mid()), float(e.imag.mid())) for e in rr] for rr in J(p)]); Yf = np.linalg.inv(Jf)
    Y = acb_mat(5, 5, [acb(float(z.real), float(z.imag)) for z in Yf.ravel()]); X = [acb(1)] + [p[i] + disc0 for i in range(1, d)]
    I5 = acb_mat(5, 5, [acb(1) if i == j else acb(0) for i in range(5) for j in range(5)])
    dev = (Y*acb_mat(5, 1, G(p)))*(-1) + (I5 - Y*acb_mat(5, 5, [e for rr in J(X) for e in rr]))*acb_mat(5, 1, [disc0]*5)
    assert all((abs(dev[i,0].real) < R) and (abs(dev[i,0].imag) < R) for i in range(5))
    K = [acb(1)] + [p[i+1] + dev[i,0] for i in range(5)]
    assert all((abs((1/K[i].conjugate() - p[i]).real) < R) and (abs((1/K[i].conjugate() - p[i]).imag) < R) for i in range(1, d))
    encl.append(K)
s6 = arb(6).sqrt(); w6 = acb(arb(1)/2, arb(3).sqrt()/2)
std = [[acb(1) if i == j else acb(0) for i in range(6)] for j in range(6)]
fou = [[w6**((j*k) % 6)/s6 for j in range(6)] for k in range(6)]
fl = np.load("fourier6_vecs.npy"); F6 = np.exp(2j*np.pi*np.outer(np.arange(d), np.arange(d))/d)/np.sqrt(d)
res = []; t0 = time.time()
for bi, o in enumerate(D["energy"]):
    Bx = o["basis"]; em = o["Emin"]; gamma = {0.0387628: "0.0385", 0.0238354: "0.0235", 0.0326759: "0.0324"}[round(em, 7)]
    vf = [np.eye(d)[:, j] for j in range(d)] + [F6[:, j] for j in range(d)] + [fl[k]/np.sqrt(d) for k in Bx]
    Q = np.load(f"Q_fourier6_triple{bi:02d}_gamma{gamma}.npy"); gstar = float("nan")
    va = std + fou + [[c/s6 for c in encl[k]] for k in Bx]
    bound, S, fro = sg.verify(va, gamma, Q)
    res.append(dict(triple=bi, basis=Bx, numerical_min=em, relaxation_value=gstar, gamma=gamma, certified_lower_bound=bound, residual=S, psd_defect=fro))
    print(f"triple {bi:2d}: numerical min {em:.7f}; CERTIFIED E > {int(bound*1e10 - 1e-3)/1e10:.10f} (rounded down)   [{time.time()-t0:.0f}s]", flush=True)
    json.dump(res, open("fourier6_verified.json", "w"), indent=1)
print("minimum certified bound over the 16 triples:", min(r["certified_lower_bound"] for r in res))
