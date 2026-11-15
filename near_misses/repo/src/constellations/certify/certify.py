#!/usr/bin/env python3
"""Interval-arithmetic certificate that polished near-miss points of the constellation
misfit  f(x) = |r(x)|^2 / 2  are strict local minima with f > 0  (python-flint / Arb balls).

Conventions (identical to ../search.py): m vectors v_i = exp(i*phase) in C^6, first entry 1,
v_0 = (1,..,1); unknowns = phases 1..5 of vectors 1..m-1 (variable index 5*(i-1)+(k-1)).
For a pair (i<j):  theta_k = p_jk - p_ik (k=0..5, theta_0 = 0),  G_ij = sum_k exp(i theta_k).
  same group :  rows Re G = sum cos th_k ,  Im G = sum sin th_k
  cross group:  row (|G|^2-6)/(2 sqrt6) = (1/sqrt6) sum_{k<l} cos(th_k - th_l)
Each row r_a depends on the phases only through theta, so with a = d r/d theta, B = d2 r/d theta2
the Hessian of f is  H = sum_rows  s_u s_w (a_k a_l + r B_kl)  with s = +1 for v_j, -1 for v_i.
Tests: T1 Krawczyk, T2 positivity, T3 Gershgorin positive-definiteness in an approximate
eigenbasis, T4 exclusion radius, T5 Brierley-Weigert F.   Exit code 1 if any test fails.
"""
import json, sys, os, itertools, time
import numpy as np
from flint import arb, arb_mat, ctx

PREC = 256
ctx.prec = PREC
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
POLISHED = os.path.join(ROOT, "results/constellations/nearmiss/polished.jsonl")
OUT = os.path.join(ROOT, "results/constellations/certified/certificate.json")


def layout(groups):
    gid = [k for k, g in enumerate(groups) for _ in range(g)]
    m = len(gid)
    same, cross = [], []
    for i in range(m):
        for j in range(i + 1, m):
            (same if gid[i] == gid[j] else cross).append((i, j))
    return m, same, cross


def inv_sqrt6():
    return 1 / arb(6).sqrt()


def evaluate(x, groups, want_J=False, want_H=False):
    """x: list of arb (length 5(m-1)), balls allowed.  Returns (r, J or None, H or None):
    r list of arb rows ordered [Re same..., Im same..., cross...] (same order as search.py)."""
    m, same, cross = layout(groups)
    n = 5 * (m - 1)
    assert len(x) == n
    zero = arb(0)
    P = [[zero] * 6] + [[zero] + [x[5 * (i - 1) + k] for k in range(5)] for i in range(1, m)]
    c6 = inv_sqrt6()
    nrow = 2 * len(same) + len(cross)
    r = [None] * nrow
    J = arb_mat(nrow, n) if want_J else None
    Hm = [[zero] * n for _ in range(n)] if want_H else None

    def var(i, k):  # variable index of phase k (1..5) of vector i (>=1), else None
        return None if (i == 0 or k == 0) else 5 * (i - 1) + (k - 1)

    def accumulate(row, i, j, rv, a, B):
        # a[k], B[k][l]: derivatives w.r.t. theta (k,l in 1..5); chain rule to variables
        vs = []
        for k in range(1, 6):
            if i >= 1: vs.append((var(i, k), -1, k))
            if j >= 1: vs.append((var(j, k), +1, k))
        if want_J:
            for (u, s, k) in vs:
                J[row, u] = J[row, u] + (a[k] if s > 0 else -a[k])
        if want_H:
            for (u, su, k) in vs:
                for (w, sw, l) in vs:
                    t = a[k] * a[l] + rv * B[k][l]
                    Hm[u][w] = Hm[u][w] + (t if su * sw > 0 else -t)

    ns = len(same)
    for idx, (i, j) in enumerate(same):
        th = [P[j][k] - P[i][k] for k in range(6)]
        cs = [t.cos() for t in th]
        sn = [t.sin() for t in th]
        rre = sum(cs, zero)
        rim = sum(sn, zero)
        r[idx] = rre
        r[ns + idx] = rim
        if want_J or want_H:
            a1 = [None] + [-sn[k] for k in range(1, 6)]
            B1 = [[None] * 6 for _ in range(6)]
            a2 = [None] + [cs[k] for k in range(1, 6)]
            B2 = [[None] * 6 for _ in range(6)]
            for k in range(1, 6):
                for l in range(1, 6):
                    B1[k][l] = -cs[k] if k == l else zero
                    B2[k][l] = -sn[k] if k == l else zero
            accumulate(idx, i, j, rre, a1, B1)
            accumulate(ns + idx, i, j, rim, a2, B2)
    for idx, (i, j) in enumerate(cross):
        row = 2 * ns + idx
        th = [P[j][k] - P[i][k] for k in range(6)]
        C = [[None] * 6 for _ in range(6)]
        S = [[None] * 6 for _ in range(6)]
        for k in range(6):
            for l in range(6):
                if k != l:
                    d = th[k] - th[l]
                    C[k][l] = d.cos()
                    S[k][l] = d.sin()
        tot = zero
        for k in range(6):
            for l in range(k + 1, 6):
                tot = tot + C[k][l]
        rv = tot * c6
        r[row] = rv
        if want_J or want_H:
            a = [None] * 6
            B = [[None] * 6 for _ in range(6)]
            for k in range(1, 6):
                sa, sb = zero, zero
                for l in range(6):
                    if l != k:
                        sa = sa + S[k][l]
                        sb = sb + C[k][l]
                a[k] = -sa * c6
                for l in range(1, 6):
                    B[k][l] = (-sb * c6) if k == l else C[k][l] * c6
            accumulate(row, i, j, rv, a, B)
    H = arb_mat(n, n, [Hm[u][w] for u in range(n) for w in range(n)]) if want_H else None
    return r, J, H


def grad(x, groups):
    """g = J^T r (ball)."""
    r, J, _ = evaluate(x, groups, want_J=True)
    return list(J.transpose() * arb_mat(len(r), 1, r))  # list of n arb


def sum_sq_enclosure(r):
    """Enclosure of sum r_a^2 over the box (each term squared via |.| bounds, so >=0)."""
    lo, hi = arb(0), arb(0)
    for ra in r:
        l, u = ra.abs_lower(), ra.abs_upper()
        lo += l * l
        hi += u * u
    return lo, hi


def bw_F(x, groups):
    """Brierley-Weigert F enclosure."""
    m, same, cross = layout(groups)
    r, _, _ = evaluate(x, groups)
    ns = len(same)
    F = arb(0)
    for idx in range(ns):
        g2 = r[idx] ** 2 + r[ns + idx] ** 2          # |G|^2 (rows are Re G, Im G)
        F += g2 / 36
    for idx in range(len(cross)):
        g2 = 6 + 2 * arb(6).sqrt() * r[2 * ns + idx]  # |G|^2 = 6 + 2 sqrt6 * row
        g = g2.sqrt()
        F += (g / 6 - inv_sqrt6()) ** 2
    return F


# ---------------------------------------------------------------- helpers
def dec_lo(a, d=25):
    """Decimal string provably <= a.lower()."""
    v = a.lower()
    s = v.str(d, radius=False)
    for _ in range(5):
        if arb(s) <= v and (arb(s) <= v) is True:
            return s
        v2 = v - abs(v) * arb(10) ** (-(d - 2)) - arb(10) ** (-200)
        s = v2.str(d, radius=False)
        v = v2
    return s


def dec_hi(a, d=25):
    v = a.upper()
    s = v.str(d, radius=False)
    for _ in range(5):
        if bool(arb(s) >= v):
            return s
        v = v + abs(v) * arb(10) ** (-(d - 2)) + arb(10) ** (-200)
        s = v.str(d, radius=False)
    return s


def interval_str(a, d=25):
    return [dec_lo(a, d), dec_hi(a, d)]


def inf_norm_upper(M):
    n, mm = M.nrows(), M.ncols()
    best = arb(0)
    for i in range(n):
        s = arb(0)
        for j in range(mm):
            s += M[i, j].abs_upper()
        best = s if (s > best) else best
    return best.upper()


def to_f(a):
    return float(a)


# ---------------------------------------------------------------- validation vs search.py
def validate():
    sys.path.insert(0, os.path.join(ROOT, "src/constellations"))
    import importlib
    S = importlib.import_module("search")
    rng = np.random.default_rng(1)
    ok = True
    report = []
    for groups in ([4, 4, 1], [5, 3, 1], [4, 3, 2], [4, 4, 2]):
        gid, m, same, cross = S.layout(groups)
        n = 5 * (m - 1)
        x = rng.uniform(-3, 3, n)
        xa = [arb(float(v)) for v in x]
        r, J, H = evaluate(xa, groups, want_J=True, want_H=True)
        r_ref = S.residuals(x, m, same, cross)
        J_ref = S.jacobian(x, m, same, cross)
        er = np.max(np.abs(np.array([to_f(v) for v in r]) - r_ref))
        Jn = np.array([[to_f(J[a, b]) for b in range(n)] for a in range(J.nrows())])
        eJ = np.max(np.abs(Jn - J_ref))
        # Hessian vs central differences of the search.py gradient J^T r
        h = 1e-6
        gfun = lambda y: S.jacobian(y, m, same, cross).T @ S.residuals(y, m, same, cross)
        Hfd = np.zeros((n, n))
        for u in range(n):
            e = np.zeros(n); e[u] = h
            Hfd[:, u] = (gfun(x + e) - gfun(x - e)) / (2 * h)
        Hn = np.array([[to_f(H[a, b]) for b in range(n)] for a in range(n)])
        eH = np.max(np.abs(Hn - Hfd)) / np.max(np.abs(Hn))
        good = er < 1e-12 and eJ < 1e-12 and eH < 1e-6
        ok &= good
        report.append(dict(groups=groups, err_r=float(er), err_J=float(eJ), rel_err_H=float(eH), ok=bool(good)))
        print("validate", report[-1], flush=True)
    return ok, report


# ---------------------------------------------------------------- certification of one point
def box(c, rho):
    return [arb(ci, rho) for ci in c]   # ball with exact midpoint c_i, radius rho


def certify(rec, groups):
    t0 = time.time()
    m, same, cross = layout(groups)
    n = 5 * (m - 1)
    ns, nc = len(same), len(cross)
    ctx.prec = PREC
    x0 = [arb(s) for s in rec["phases"]]
    c = [v.mid() for v in x0]             # exact binary centre (256-bit rounding of the decimals)
    cdev = max((abs(c[i] - x0[i]).upper() for i in range(n)), key=lambda v: float(v))  # |c-x0| (selection by float; fine, value only reported)
    out = dict(shape=groups, source_index=rec.get("index"), listed_misfit=rec["misfit"],
               n=n, precision_bits=PREC, x0_phases=rec["phases"],
               centre_minus_x0_max_abs_approx=cdev.str(5, radius=False), tests={}, rho_scan=[])
    # --- centre quantities
    r_c, J_c, H_c = evaluate(c, groups, want_J=True, want_H=True)
    g_c = list(J_c.transpose() * arb_mat(len(r_c), 1, r_c))
    # Hessian is symmetric in exact arithmetic; take Y = midpoint of ball inverse (any Y is fine for rigor)
    Yb = H_c.inv()
    Y = arb_mat(n, n, [Yb[i, j].mid() for i in range(n) for j in range(n)])
    Yg = Y * arb_mat(n, 1, g_c)
    b_inf = max(float(Yg[i, 0].abs_upper()) for i in range(n))
    out["max_abs_Y_g_c"] = f"{b_inf:.6e}"
    out["grad_norm_inf_at_c_le"] = f"{max(float(v.abs_upper()) for v in g_c):.4e}"
    I = arb_mat(n, n)
    for i in range(n): I[i, i] = arb(1)

    # float eigenbasis of H(c) (only a guess; verified below in ball arithmetic)
    Hf = np.array([[float(H_c[i, j].mid()) for j in range(n)] for i in range(n)])
    Hf = (Hf + Hf.T) / 2
    w, Qf = np.linalg.eigh(Hf)
    Q = arb_mat(n, n, [arb(float(Qf[i, j])) for i in range(n) for j in range(n)])  # exact conversion
    QT = Q.transpose()
    E = QT * Q - I
    E_inf = inf_norm_upper(E)
    out["Q_check"] = dict(eig_min_float=float(w[0]), eig_max_float=float(w[-1]),
                          norm_inf_QtQ_minus_I_le=f"{float(E_inf):.3e}", Q_nonsingular=bool(E_inf < 1))

    def krawczyk(rho):
        rho_u = rho.upper()
        X = box(c, rho_u)
        _, _, HX = evaluate(X, groups, want_H=True)
        M = I - Y * HX                                   # enclosure of I - Y H(x), x in X
        dx = arb_mat(n, 1, [arb(0, rho_u)] * n)
        Kd = -Yg + M * dx                                # K(X) - c
        worst = max(float(Kd[i, 0].abs_upper() / rho_u) for i in range(n))  # float only for reporting
        ok = all(bool(Kd[i, 0].abs_upper() < rho_u) for i in range(n))      # rigorous comparison
        return ok, worst, X, HX, float(inf_norm_upper(M))

    def gersh(HX):
        B = QT * HX * Q
        t = None
        for i in range(n):
            s = B[i, i].lower()
            for j in range(n):
                if j != i:
                    s = s - B[i, j].abs_upper()
            t = s if (t is None or s < t) else t
        return t     # arb: lower bound (ball) of min_i (diag_lo - offdiag_up)

    # --- scan powers of ten
    best_pass = None
    for e in range(6, 41):
        rho = arb(10) ** (-e)
        ok, worst, X, HX, qn = krawczyk(rho)
        entry = dict(rho=f"1e-{e}", T1_pass=bool(ok), max_ratio_K_over_rho=worst, norm_inf_I_minus_YHX=qn)
        if ok:
            t = gersh(HX)
            tl = t.lower()
            entry["T3_gershgorin_lower_bound_of_B"] = tl.str(12, radius=False)
            entry["T3_pass"] = bool(tl > 0) and bool(E_inf < 1)
            if best_pass is None and entry["T3_pass"]:
                best_pass = e
        out["rho_scan"].append(entry)
        if best_pass is not None and e >= best_pass + 3:
            break
    if best_pass is None:
        out["tests"] = dict(T1=False, T3=False, overall=False)
        out["seconds"] = time.time() - t0
        return out, False
    rho_big = arb(10) ** (-best_pass)

    # --- tight rho: smallest rho (searching down in factors ~0.7) that still passes
    rho_t = arb(2 * b_inf if b_inf > 0 else 1e-60)
    rho_t = arb(float(f"{float(rho_t):.1e}"))      # 2 significant digits
    for _ in range(60):
        ok, *_r = krawczyk(rho_t)
        if ok: break
        rho_t = rho_t * 2
    for _ in range(60):
        cand = rho_t * arb("0.9")
        ok, *_r = krawczyk(cand)
        if not ok: break
        rho_t = cand
    ok_t, worst_t, Xt, HXt, qn_t = krawczyk(rho_t)
    rho_t_u = rho_t.upper()
    out["rho_largest_pow10_T1_and_T3"] = f"1e-{best_pass}"
    out["rho_largest_pow10_T1_only"] = next((e_["rho"] for e_ in out["rho_scan"] if e_["T1_pass"]), None)
    out["rho_tight"] = rho_t_u.str(8, radius=False)
    out["tight_T1_pass"] = bool(ok_t)

    # --- T2 on the largest box and on the tight box (x* lies in both: unique zero of g in each)
    res = {}
    for name, rr in (("big", rho_big.upper()), ("tight", rho_t_u)):
        X = box(c, rr)
        r_X, _, H_X = evaluate(X, groups, want_H=True)
        lo, hi = sum_sq_enclosure(r_X)
        mis_lo = lo.sqrt().lower() if lo > 0 else arb(0)
        mis_hi = hi.sqrt().upper()
        res[name] = dict(rho=rr.str(8, radius=False), misfit_abs_r=[dec_lo(mis_lo, 30), dec_hi(mis_hi, 30)])
        res[name]["T2_pass"] = bool(mis_lo > 0)
        res[name]["f_half_sq"] = [dec_lo(lo / 2, 30), dec_hi(hi / 2, 30)]
        if name == "big":
            tG = gersh(H_X)
            res[name]["T3_gershgorin_lower_bound_B"] = dec_lo(tG, 12)
            lam_lo = tG.lower() / (1 + E_inf)
            res[name]["T3_lambda_min_H_lower_bound"] = dec_lo(lam_lo, 12)
            res[name]["T3_pass"] = bool(lam_lo > 0)
        else:
            mis_lo_t, mis_hi_t = mis_lo, mis_hi
            lo_t = lo
    out["enclosures"] = res

    # --- T4 exclusion radius
    L = (20 * ns + 60 * nc) ** 0.5
    Lb = arb(20 * ns + 60 * nc).sqrt()
    R_glob = mis_lo_t / Lb
    out["T4_L_global"] = float(Lb)
    out["T4_exclusion_radius_global_L"] = dec_lo(R_glob, 12)
    # (a) larger ball from interval Jacobian bound on box of half-width delta around c
    best_R, best_d = arb(0), None
    for kk in range(0, 60):
        delta = arb(10) ** (-arb(kk) / 8 - 2)    # 1e-2 ... down
        delta = arb(float(f"{float(delta):.3e}")).upper()
        X = box(c, delta)
        r_X, J_X, _ = evaluate(X, groups, want_J=True)
        nr = J_X.nrows()
        fro2 = arb(0)
        for a_ in range(nr):
            for b_ in range(n):
                v = J_X[a_, b_].abs_upper(); fro2 += v * v
        JTJ = J_X.transpose() * J_X
        n_inf = inf_norm_upper(JTJ)                      # ||J||_2^2 <= ||J^T J||_inf
        def exact_max(vals):   # vals are exact (.upper()) so '>' comparisons are exact
            best = None
            for v in vals:
                v = v.upper()
                best = v if (best is None or v > best) else best
            return best
        n1 = exact_max(sum((J_X[a_, b_].abs_upper() for a_ in range(nr)), arb(0)) for b_ in range(n))
        ninf = exact_max(sum((J_X[a_, b_].abs_upper() for b_ in range(n)), arb(0)) for a_ in range(nr))
        cands = [fro2.sqrt(), n_inf.sqrt(), (n1 * ninf).sqrt()]
        Lbox = min(cands, key=lambda v: float(v)).upper()
        R = mis_lo_t / Lbox
        if bool(R + rho_t_u <= delta) and float(R) > float(best_R):
            best_R, best_d = R, (delta, Lbox)
    if best_d:
        out["T4_exclusion_radius_box"] = dict(radius=dec_lo(best_R, 12), box_halfwidth=best_d[0].str(6, radius=False),
                                              L_box_upper=dec_hi(best_d[1], 8),
                                              note="R + rho_tight <= box half-width, |r(x)|>=|r(x*)|-L_box|x-x*| on segment")
        out["T4_exclusion_radius_best"] = dec_lo(best_R, 12) if float(best_R) > float(R_glob) else dec_lo(R_glob, 12)
    else:
        out["T4_exclusion_radius_best"] = dec_lo(R_glob, 12)

    # --- T5
    F = bw_F(Xt, groups)
    out["T5_F_enclosure"] = [dec_lo(F, 20), dec_hi(F, 20)]
    out["T5_F_lt_1e-7"] = bool(F < arb("1e-7"))
    t1 = bool(ok_t) and any(e_["T1_pass"] for e_ in out["rho_scan"])
    t2 = res["tight"]["T2_pass"] and res["big"]["T2_pass"]
    t3 = res["big"]["T3_pass"]
    out["tests"] = dict(T1=t1, T2=t2, T3=t3, T4=bool(R_glob > 0), T5_F_below_1em7=out["T5_F_lt_1e-7"])
    out["tests"]["overall"] = bool(t1 and t2 and t3 and R_glob > 0)
    out["seconds"] = round(time.time() - t0, 1)
    return out, out["tests"]["overall"]


def main():
    ok_v, rep = validate()
    recs = [json.loads(l) for l in open(POLISHED)]
    todo = []
    pick = {(4, 4, 1): None, (5, 3, 1): None}
    for r in recs:
        g = tuple(r["groups"])
        if g in pick: todo.append(r)
    for r in recs:
        if r["groups"] == [4, 3, 2] and str(r["misfit"]).startswith("0.00498809725"): todo.append(r)
    for r in recs:
        if r["groups"] == [4, 4, 2]: todo.append(r)
    results, allok = [], ok_v
    only = sys.argv[1:]  # optional: restrict to shapes like 441
    for r in todo:
        tag = "".join(map(str, r["groups"]))
        if only and tag not in only: continue
        res, ok = certify(r, r["groups"])
        print(tag, "overall:", ok, json.dumps(res["tests"]), "rho:", res.get("rho_largest_pow10_T1_and_T3"),
              res.get("rho_tight"), "t=", res.get("seconds"), flush=True)
        results.append(res)
        allok &= ok
        json.dump(dict(validation=rep, validation_ok=ok_v, flint_precision_bits=PREC, points=results,
                       all_pass=bool(allok)), open(OUT, "w"), indent=1, default=lambda o: bool(o) if type(o).__name__ in ('bool','bool_') else str(o))
    sys.exit(0 if allok else 1)


if __name__ == "__main__":
    main()
