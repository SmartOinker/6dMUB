#!/usr/bin/env python3
"""Independent numerical check of the three constellation examples in arXiv:2611.06917,
Supplementary Material Sec. 5, Eqs. (A.147)-(A.154): {5,3,3,3}, {5,4,3,1}, {5,5,2,2}.

For each example we build the vectors from the paper's formulas, confirm every entry has
modulus 1, and evaluate our misfit (see search.py). For {5,5,2,2} the paper gives a rational
box of radius 1e-6 that is stated to contain exactly one solution; we start from the box
centre, polish with verify.polish, and report how far the polished point is from the centre.
This is a floating-point / multiprecision check, not a proof.
"""
import json
import mpmath as mp
import numpy as np
import search as S
import verify as Vf

mp.mp.dps = 40
w = mp.expj(2 * mp.pi / 3)
L = [mp.mpc(1), mp.mpc(1), w, mp.conj(w), w, mp.conj(w)]
one = [mp.mpc(1)] * 6


def Lp(v, t):
    return [L[k] ** t * v[k] for k in range(6)]


def to_x(groups_vecs):
    """list of groups (lists of 6-vectors) -> shape, free phases in the search.py gauge."""
    vecs = [v for g in groups_vecs for v in g]
    mods = max(abs(abs(z) - 1) for v in vecs for z in v)
    vecs = [[z / v[0] for z in v] for v in vecs]
    assert all(abs(z - 1) < mp.mpf(10) ** -30 for z in vecs[0]), "first vector must be all ones"
    x = [mp.arg(v[k]) for v in vecs[1:] for k in range(1, 6)]
    return [len(g) for g in groups_vecs], x, mods


def misfit(shape, x):
    gid, m, same, cross = S.layout(shape)
    r, _ = Vf.mp_res_jac(x, m, same, cross, want_jac=False)
    return mp.sqrt(mp.fsum(t * t for t in r))


out = {}
# ---- {5,3,3,3}, Eq. (A.149)
a = (1 + 1j * mp.sqrt(15)) / 4
b = [1, mp.conj(w), 1, a, w, a]
c = [1, mp.conj(w), mp.conj(a), w, mp.conj(a), 1]
shape, x, mods = to_x([[one, Lp(one, 1), Lp(one, 2)], [b, Lp(b, 1), Lp(b, 2)],
                       [c, Lp(c, 1), Lp(c, 2)]])
out["5333"] = dict(shape=shape, max_modulus_error=mp.nstr(mods, 5), misfit=mp.nstr(misfit(shape, x), 5))

# ---- {5,4,3,1}, Eqs. (A.150)-(A.151), T = Q = 1
R = mp.sqrt((mp.sqrt(5) - 1) / 2)
kappa = mp.sqrt(3) * R ** 3
eta = (R - 1 + 1j * R ** 2) / (2 * R ** 2)
Y = lambda t: 2 * R * mp.im(t)
F = lambda t: -(Y(t) + 1) * (2 * Y(t) - 1) / kappa + 1j * Y(t)
G = lambda t: (1 - 1j) * t / R * mp.conj(t + eta) / (t + eta)
res431 = []
for beta in mp.polyroots([1, 0, 0, -(R ** 2 / 4) * (-1 + 1j * R ** 3)], maxsteps=200, extraprec=200):
    d, e, p, q = F(beta), F(mp.conj(w) * beta), G(beta), G(mp.conj(w) * beta)
    h = [1, -1, 1, 1, -1, -1]
    bb = [1, -1j, w, 1, -1j * w, -1j]
    cc = [1, e, p, p * q, 1j * p * mp.conj(d * e), d * p * q]
    shape, x, mods = to_x([[one, h, Lp(h, 2), Lp(one, 1)], [bb, Lp(bb, 1), Lp(bb, 2)], [cc]])
    res431.append(dict(max_modulus_error=mp.nstr(mods, 5), misfit=mp.nstr(misfit(shape, x), 5)))
out["5431"] = dict(shape=shape, per_cube_root=res431)

# ---- {5,5,2,2}, Eqs. (A.152)-(A.154)
mvec = [88191, -12383399, -17366867, -6227352, -15603052, -1112587,
        34985264, 13037208, 17392983, 1296019, -22919921, 7181585]


def build522(t):
    u = [(1 + 1j * tj) / (1 - 1j * tj) for tj in t]
    T, Q = u[0], u[1]
    bv = [mp.mpc(1)] + u[2:7]
    cv = [mp.mpc(1)] + u[7:12]
    h = [1, -1, T, Q, -T, -Q]
    J = lambda v: [mp.conj(v[1]), -mp.conj(v[0]), T * mp.conj(w) * mp.conj(v[4]),
                   Q * w * mp.conj(v[5]), -T * mp.conj(w) * mp.conj(v[2]),
                   -Q * w * mp.conj(v[3])]
    return to_x([[one, h, Lp(h, 1), Lp(h, 2), Lp(one, 2)], [bv, J(bv)], [cv, J(cv)]])


t0 = [mp.mpf(k) / 10 ** 7 for k in mvec]
shape, x0, mods = build522(t0)
m0 = misfit(shape, x0)
xp, mis, gn, its, _ = Vf.polish(shape, x0, digits=40)
shift = max(abs(mp.mpf(xp[i]) - x0[i]) for i in range(len(x0)))
gid, m, same, cross = S.layout(shape)
sv = np.linalg.svd(S.jacobian(np.array([float(t) for t in xp]), m, same, cross), compute_uv=False)
out["5522"] = dict(shape=shape, max_modulus_error=mp.nstr(mods, 5),
                   misfit_at_box_centre=mp.nstr(m0, 5), misfit_after_polish=mp.nstr(mis, 5),
                   max_phase_shift_from_box_centre=mp.nstr(shift, 5),
                   smallest_singular_values=[float(s) for s in sv[-3:]], nvar=len(x0))
print(json.dumps(out, indent=1))
json.dump(out, open("../../results/constellations/yale_examples_check.json", "w"), indent=1)
