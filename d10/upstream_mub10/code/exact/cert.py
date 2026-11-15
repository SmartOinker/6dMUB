"""Krawczyk certification (python-flint / Arb ball arithmetic) of cyclic d-roots in x-coordinates
   g_k(x) = sum_j x_{j+k}/x_j, k=1..d-1, x_0 = 1, unknowns x_1..x_{d-1}.
For each approximate root m: box X = m + [-r,r]+i[-r,r] per coordinate (r relative),
K = m - Y g(m) + (I - Y J(X))(X - m);  K inside interior(X)  =>  unique root in X, and it lies in K.
Unimodularity:   sigma(K) subset X with sigma(x) = 1/conj(x)  => root is unimodular (sigma maps roots to roots).
Non-unimodular:  some |K_j| enclosure excludes 1.
Usage: python3 cert.py d roots.npy out_prefix [prec_bits] [refine_iters] [rel_radius]
Outputs out_prefix_cert.json (status per root) and, for unimodular roots, out_prefix_unimod.txt with midpoints
(high precision) and radii.
"""
import numpy as np, sys, json, time
from flint import acb, arb, acb_mat, ctx

d = int(sys.argv[1]); S = np.load(sys.argv[2]); out = sys.argv[3]
prec = int(sys.argv[4]) if len(sys.argv) > 4 else 106
refine = int(sys.argv[5]) if len(sys.argv) > 5 else 0
relr = float(sys.argv[6]) if len(sys.argv) > 6 else 1e-9
ctx.prec = prec
n = d - 1

def full(xs):
    return [acb(1)] + list(xs)

def g_and_J(xs):
    x = full(xs); ix = [1 / v for v in x]
    g = []; J = []
    for k in range(1, d):
        g.append(sum((x[(j + k) % d] * ix[j] for j in range(d)), acb(0)))
        J.append([ix[(m - k) % d] - x[(m + k) % d] * ix[m] * ix[m] for m in range(1, d)])
    return g, J

def certify(v):
    xs = [acb(complex(c).real, complex(c).imag) for c in v]
    for _ in range(refine):
        g, J = g_and_J(xs)
        dx = acb_mat(J).solve(acb_mat([[c] for c in g]))
        xs = [(xs[i] - dx[i, 0]).mid() for i in range(n)]
    g, J = g_and_J(xs)
    Y = acb_mat(J).mid().inv().mid() if True else None
    rad = [relr * max(1.0, abs(complex(c.mid()))) for c in xs]
    X = [acb(arb(c.real.mid(), rad[i]), arb(c.imag.mid(), rad[i])) for i, c in enumerate(xs)]
    _, JX = g_and_J(X)
    I = acb_mat([[1 if i == j else 0 for j in range(n)] for i in range(n)])
    gm = acb_mat([[c] for c in g])
    D = acb_mat([[X[i] - xs[i]] for i in range(n)])
    K = acb_mat([[c] for c in xs]) - Y * gm + (I - Y * acb_mat(JX)) * D
    K = [K[i, 0] for i in range(n)]
    ok = all(X[i].contains_interior(K[i]) for i in range(n))
    if not ok:
        return dict(ok=False), xs, K
    # unimodularity
    sK = [1 / c.conjugate() for c in K]
    if all(X[i].contains(sK[i]) for i in range(n)):
        um = "unimodular"
    elif any((abs(c).lower() > 1) or (abs(c).upper() < 1) for c in K):
        um = "not_unimodular"
    else:
        um = "undecided"
    krad = max(float(max(c.real.rad(), c.imag.rad())) for c in K)
    return dict(ok=True, unimod=um, box_rad=max(rad), K_rad=krad), xs, K

if __name__ == "__main__":
    t0 = time.time(); res = []; uni_lines = []
    for i, v in enumerate(S):
        r, xs, K = certify(v)
        r["i"] = i; res.append(r)
        if r.get("unimod") == "unimodular":
            uni_lines.append(f"{i} " + " ".join(f"{c.real.mid().str(40, radius=False)} {c.imag.mid().str(40, radius=False)}" for c in xs)
                             + f" Krad={r['K_rad']:.3e}")
        if i % 2000 == 0:
            print(f"{i}/{len(S)} {time.time()-t0:.0f}s", flush=True)
    from collections import Counter
    c = Counter((r["ok"], r.get("unimod")) for r in res)
    print("summary:", dict(c), f"{time.time()-t0:.0f}s")
    json.dump(dict(d=d, prec=prec, refine=refine, relr=relr, summary={str(k): v for k, v in c.items()}, roots=res),
              open(out + "_cert.json", "w"))
    open(out + "_unimod.txt", "w").write("\n".join(uni_lines) + "\n")
