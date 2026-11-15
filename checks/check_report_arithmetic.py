"""Independent recomputation of the arithmetic and of the stored-data summaries quoted in the report and slides.

Written by the verification audit, separately from the programs that produced the numbers.  It recomputes from
first principles (mpmath at 50 digits, exact Fractions, scipy for noncentral chi-square) every derived number
that is not itself the output of a heavy computation, and it re-reads the stored result files (JSON, JSONL, logs) and
compares them with the numbers printed in the report.  It does NOT re-run any Monte Carlo, simulation or search.
Each section prints one line; any mismatch raises AssertionError.  Prints OK at the end.
Run:  python3 checks/check_report_arithmetic.py   (about 5 s)
Claim ids (docs/verification_matrix.md) are given in brackets.
"""
import json, math, os, re, glob
from fractions import Fraction as Fr
import numpy as np
import mpmath as mp
from scipy.stats import chi2, ncx2, norm
from scipy.optimize import brentq
mp.mp.dps = 50
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
P = lambda *a: os.path.join(ROOT, *a)
s6 = mp.sqrt(6)
def close(x, y, rel=0, ab=0): assert abs(mp.mpf(x) - mp.mpf(y)) <= ab + rel*abs(mp.mpf(y)), (x, y)

# ---- [bridge constants] c*, closed forms, limiting constant
c = 3*s6/(s6 + 1)**2; close(c, (21*s6 - 36)/25, ab=mp.mpf(10)**-45); close(c, 0.617571, ab=1e-6)
a = 1/s6; cP = lambda Pm: 1/(2*a*(mp.sqrt(Pm) + a)**2); close(cP(1), c, ab=mp.mpf(10)**-45)
close(cP(mp.mpf(1)/6), 3*s6/4, ab=mp.mpf(10)**-45); close(3*s6/4, 1.8371, ab=1e-4); assert 2.9 < (3*s6/4)/c < 3.0
# equality at p = 1/6 and p = 1 and slack positive elsewhere (grid), exact form (s-a)^2 [1/(2a) - c (s+a)^2] >= 0
f = lambda p: 1/s6 + (s6/2)*(p - mp.mpf(1)/6) - c*(p - mp.mpf(1)/6)**2 - mp.sqrt(p)
close(f(mp.mpf(1)/6), 0, ab=mp.mpf(10)**-45); close(f(1), 0, ab=mp.mpf(10)**-45)
assert all(f(mp.mpf(k)/997) > -mp.mpf(10)**-45 for k in range(1, 998))
print("[C-lemma] c* = 3 sqrt6/(sqrt6+1)^2 = (21 sqrt6 - 36)/25 = %s; c(1/6) -> 3 sqrt6/4 = %s; equality at p = 1/6, 1; slack >= 0 on 997 rationals" % (mp.nstr(c, 8), mp.nstr(3*s6/4, 6)))

# ---- [bridge numbers] Corollary: bias and game bounds from gamma
for name, g, bias_r, game_r in (("T0", mp.mpf("0.038499999998"), "0.046248", "3.302291e-4"), ("T1", mp.mpf("0.023499999997"), "0.036132", "2.015684e-4")):
    b = mp.sqrt(g/18); gl = c*g/72
    assert b > mp.mpf(bias_r) and gl > mp.mpf(game_r), (name, b, gl)
    close(b, mp.mpf(bias_r), ab=1e-6); close(gl, mp.mpf(game_r), rel=1e-5)
    print("[C-bridge-numbers] %s: sqrt(g/18) = %s > %s ; c g/72 = %s > %s" % (name, mp.nstr(b, 7), bias_r, mp.nstr(gl, 7), game_r))
assert 18*mp.mpf("0.030223872")**2 < mp.mpf("0.016443") < 0.016444 and mp.sqrt(mp.mpf("0.016443")/18) > mp.mpf("0.030223872")
assert mp.sqrt(mp.mpf("0.0234999")/18) > mp.mpf("0.036132") > mp.mpf("0.030224")          # Fourier-pair corollary
assert c*mp.mpf("0.0323999")/72 > mp.mpf("2.779e-4") > mp.mpf("2.358e-4")
assert mp.mpf("3.302e-4") > mp.mpf("2.358e-4") and mp.mpf("0.046248") > mp.mpf("0.030224")
assert mp.mpf("2.015e-4") < mp.mpf("2.358e-4")                                            # T1 game comparison inconclusive
print("[C-design] threshold 18 x 0.030223872^2 = %s (<= 0.016443); Fourier-pair game bound c*0.0323999/72 = %s > 2.779e-4" % (mp.nstr(18*mp.mpf("0.030223872")**2, 7), mp.nstr(c*mp.mpf("0.0323999")/72, 5)))
print("[C-design] 3.302/2.358e-4 etc: best explicit game-loss search value ratio 1.506e-3 / 3.302e-4 = %.2f (report: about 4.6)" % (1.506e-3/3.302e-4)); assert 4.5 < 1.506e-3/3.302e-4 < 4.65

# ---- [game] rounds and noise thresholds
mu = mp.mpf(1)/2 + s6/12; close(mu, 0.7041241, ab=1e-7)
Dl = mp.mpf("2.357825e-4"); n = 25*mu*(1 - mu)/Dl**2; assert 9.36e7 < n < 9.38e7
r1, r2 = Dl/mp.mpf("20.3"), Dl/mp.mpf("11.6"); assert abs(r1 - mp.mpf("1.16e-5")) < 5e-8 and abs(r2 - mp.mpf("2.03e-5")) < 5e-8
G = json.load(open(P("hide_seek/hide_seek.json")))["game"]
assert abs(G["rounds_5sigma"] - float(n)) < 2e4 and abs(G["rate_where_noise_loss_equals_gap_separate"] - 1.16e-5) < 5e-8 and abs(G["rate_where_noise_loss_equals_gap_fused"] - 2.03e-5) < 5e-8
print("[C-game] mu = %s; rounds 25 mu(1-mu)/Delta^2 = %s (stored %.3e); noise thresholds %s and %s (stored %.3e, %.3e)" % (mp.nstr(mu, 8), mp.nstr(n, 4), G["rounds_5sigma"], mp.nstr(r1, 4), mp.nstr(r2, 4), G["rate_where_noise_loss_equals_gap_separate"], G["rate_where_noise_loss_equals_gap_fused"]))

# ---- [finite-sample] shot counts of the finite-sample theorem, recomputed with exact rationals
def sqrt_fr(x, digits=40): return Fr(math.isqrt(int(x*10**(2*digits))), 10**digits)
def miss_prob(g, N):
    V = Fr(4, N)*g*(Fr(1, 6) + sqrt_fr(g)) + Fr(3, 2*N*(N - 1)); return V/(V + g*g/4)
def false_alarm(g, N): return 1/(1 + Fr(3, 10)*g*g*N*(N - 1))
def smallest_N(g, beta):
    lo, hi = 2, 2
    while miss_prob(g, hi) > beta: hi *= 2
    while lo < hi:
        mid = (lo + hi)//2
        if miss_prob(g, mid) <= beta: hi = mid
        else: lo = mid + 1
    return lo
exp = {("0.038499999998", Fr(5, 100)): 2892, ("0.038499999998", Fr(1, 100)): 14957, ("0.0234999", Fr(5, 100)): 4189, ("0.0234999", Fr(1, 100)): 21617}
for (gs, beta), want in exp.items():
    g = Fr(gs); N = smallest_N(g, beta); assert N == want, (gs, beta, N, want)
    assert miss_prob(g, N) <= beta < miss_prob(g, N - 1)
    print("[C-finite] gamma = %s: smallest N with miss <= %s is %d; false alarm there = %.3e" % (gs, float(beta), N, float(false_alarm(g, N))))
assert float(false_alarm(Fr("0.038499999998"), 2892)) < 2.7e-4 and float(false_alarm(Fr("0.038499999998"), 14957)) < 1.1e-5
fa = float(false_alarm(Fr("0.038499999998"), 14957)); assert abs(fa - 1.01e-5) < 5e-8, fa           # report says 1.1e-5: see matrix (disagreement)
print("[C-finite] N = 14,957: false alarm bound = %.4e (the report text says 1.1e-5; the exact value is 1.01e-5, so the report's statement 'at most 1.1e-5' is true but loose)" % fa)
assert 3*239 == 717 and 3*2892 == 8676
# uniform variance 5/(6N(N-1)) and Cantelli constant 3/10 (algebra)
N = Fr(2892); var_u = 3*Fr(2, 1)/(N*(N - 1))*Fr(5, 36); assert var_u == Fr(5, 6)/(N*(N - 1))
g = Fr("0.038499999998"); assert (g*g/4)/var_u == Fr(3, 10)*g*g*N*(N - 1)

# ---- [large-sample shots] noncentral chi-square rule, from E and the false-alarm rate
def shots(E, alpha, power, df=15, d=6):
    thr = chi2.isf(alpha, df); return brentq(lambda n_: ncx2.sf(thr, df, d*n_*E) - power, 1, 1e8)
a5 = norm.sf(5)
H = json.load(open(P("hide_seek/hide_seek.json")))
vals = (shots(0.0385, 1e-3, 0.99), shots(0.0385, a5, 0.5), shots(0.0385, a5, 0.99))
assert [math.ceil(v) for v in vals] == [239, 198, 369], vals
C = H["certified"]; assert abs(C["shots_per_setting_alpha1em3_99pct"] - vals[0]) < 1e-2 and abs(C["shots_per_setting_5sigma_50pct"] - vals[1]) < 1e-2 and abs(C["shots_per_setting_5sigma_99pct"] - vals[2]) < 1e-2
print("[C-239] E = 0.0385: %.2f, %.2f, %.2f shots per setting -> 239, 198, 369 (the original RESULTS.md table says 368: it is the unrounded 368.07)" % vals)
tot = {}
for row in H["d6"]["scan"]:
    if row["rate"] in (0.0, 0.0001, 0.001, 0.01, 0.1):
        t = 3*shots(row["E"], a5, 0.5); tot[row["rate"]] = round(t); assert abs(t - 3*row["shots_per_setting_5sigma_50pct"]) < 0.05
assert tot == {0.0: 589, 0.0001: 589, 0.001: 594, 0.01: 646, 0.1: 1500}, tot
print("[C-noise-scan] total shots at 5 sigma, 50%% detection, recomputed from the stored energies: %s" % tot)
# model-vs-simulation entries quoted in the text
for N_, pred in ((50, 0.108), (100, 0.481), (126, 0.682), (239, 0.990)):
    thr = chi2.isf(1e-3, 15); assert abs(ncx2.sf(thr, 15, 6*N_*0.0385) - pred) < 6e-4, (N_, ncx2.sf(thr, 15, 6*N_*0.0385))
print("[C-239] noncentral chi-square predictions 0.108, 0.481, 0.682, 0.990 at N = 50, 100, 126, 239 recomputed")

# ---- [d10 energies] stored numerical minima and the shot figure of Section 7
E10 = json.load(open(P("d10/energy10.json"))); e14 = [o for o in E10 if o["orbit"] == 14][0]["Emin"]; emin = min(o["Emin"] for o in E10)
assert abs(e14 - 0.0202) < 5e-5 and abs(emin - 0.0022) < 5e-5 and [o["orbit"] for o in E10 if o["Emin"] == emin] == [8]
low = sorted(o["orbit"] for o in E10 if o["frac"] < 0.06); assert low == [1, 7, 12] and all(0.02 <= o["frac"] <= 0.05 for o in E10 if o["orbit"] in low)
n14 = shots(e14, 1e-3, 0.99, df=27, d=10); n8 = shots(emin, 1e-3, 0.99, df=27, d=10)
assert 320 < n14 < 330 and 2800 < n8 < 3200 and abs(math.sqrt(e14/30) - 0.026) < 5e-4
print("[C-d10-energy] orbit 14: E = %.4f -> %.0f shots per setting; orbit 8: E = %.4f -> %.0f shots; orbits 1,7,12 reached by 2 to 5%% of starts" % (e14, n14, emin, n8))

# ---- [percentages]
assert abs(0.0385/((4 - math.sqrt(6))/40) - 0.993) < 5e-4 and abs(0.0235/0.0238354 - 0.986) < 5e-4 and abs(1 - 0.0385/((4 - math.sqrt(6))/40) - 0.007) < 5e-4
assert abs((4 - math.sqrt(6))/40 - 0.0387627564) < 1e-10 and abs(1/72 - 0.013889) < 1e-6
print("[C-ladder] 0.0385/0.0387628 = %.4f; 0.0235/0.0238354 = %.4f; (4-sqrt6)/40 = %.10f; 1/72 = %.6f" % (0.0385/((4 - math.sqrt(6))/40), 0.0235/0.0238354, (4 - math.sqrt(6))/40, 1/72))

# ---- [gap72] the rational comparisons of Appendix A.3 (exact)
assert Fr(9, 200)*(Fr(71, 200) - Fr(9, 200)) == Fr(279, 20000) and Fr(1, 6)*(Fr(71, 200) - Fr(1, 6)) == Fr(113, 3600)
assert min(Fr(279, 20000), Fr(113, 3600)) > Fr(1, 72)
assert (Fr(71, 200) - Fr(9, 200))*(1 - Fr(71, 200)) == Fr(3999, 20000)
assert 2*Fr(3999, 20000) - Fr(1, 72) > Fr(31, 50)**2 and Fr(1, 12) < Fr(29, 100)**2 and (1 - Fr(29, 100))/2 == Fr(71, 200)
assert 4*Fr(9, 200)*Fr(191, 200) == Fr(1719, 10000) and Fr(1719, 10000) < Fr(83, 200)**2
assert Fr(31, 50) - Fr(83, 200) == Fr(41, 200) and Fr(1, 3)*Fr(41, 200)**2 == Fr(1681, 120000) and Fr(1681, 120000) > Fr(1, 72)
assert Fr(1, 36)**2*18 == Fr(1, 72)                                   # E > 1/72 over 18 outcomes -> some |p - 1/6| > 1/36
assert abs(1/(12*mp.sqrt(3)) - mp.mpf("0.0481125")) < 1e-7 and abs(mp.mpf(1)/2 + 1/(24*mp.sqrt(3)) - mp.mpf("0.524056")) < 1e-6
assert abs(mp.sqrt(mp.mpf(1)/432) - 1/(12*mp.sqrt(3))) < mp.mpf(10)**-45
print("[C-gap72] all rational comparisons of Appendix A.3 hold exactly; 1/(12 sqrt3) = 0.0481125; 1/2 + 1/(24 sqrt3) = 0.524056")

# ---- [counts] combinatorial counts used in the text
from math import comb
assert comb(14, 3) == 364 and comb(17, 6) == 12376 and comb(15, 4) == 1365 and comb(14, 2) == 91 and comb(13, 2) == 78 and comb(16, 2) == 120
assert 60 + 120 + 1215 == 1395 and 1272 + 122 + 1 == 1395 and 112 + 8 == 120 and 1160 + 54 + 1 == 1215 and 6 + 92 + 24 == 122
assert 3040 + 31900 == 34940 and 35940 - 34940 == 1000 and 156 - 108 == 48 and 17 + 5 + 13 == 35 and comb(7, 3) == 35 and 14 + 3 == 17
assert 800 + 4*400 + 3*200 + 2*20 == 3040 and 1136*3040 == 3453440 and 12 + 2 + 2 == 16 and 50000*36 == 1800000 and 27189 - 1 == 27188
assert 1199148/1200000 < 1 and 389/52000 < 0.00749 and abs(389/52000 - 0.0075) < 5e-5 and abs(695/52000 - 0.0134) < 5e-5
assert 20*12 + 60*24 == 1680 and 20*13 + 60*23 == 1640 and 2*12 + 24 == 48 and 2*13 + 23 == 49 and 12 + 24 == 36 and 13 + 23 == 36 and comb(4, 2)*2 == 12 and comb(5, 2) + comb(3, 2) == 13
assert 5*(9 - 1) == 40 and 4 + 4 + 1 == 9 and 5 + 3 + 1 == 9 and abs(math.sqrt(1680) - 40.99) < 0.005 and abs(math.sqrt(1640) - 40.50) < 0.005
assert 2892 != 2893
print("[C-counts] binomials and sums quoted in the text hold (364, 12,376, 1,365, 78, 120, 1,395, 34,940, 3,040 orbit sizes, 17+5+13 = 35, ...)")

# ---- [near-miss arithmetic] mu, F = mu^2/36, exclusion radii
mu1, mu2 = mp.mpf("1.02497683851953e-3"), mp.mpf("7.32788656303688e-4")
assert abs(mu1**2/36 - mp.mpf("2.918e-8")) < 1e-11 and abs(mu2**2/36 - mp.mpf("1.492e-8")) < 1e-11 and 3.4 < 1e-7/(mu1**2/36) < 3.5 and 6.6 < 1e-7/(mu2**2/36) < 6.8
assert abs(6*math.sqrt(1e-7) - 1.9e-3) < 2e-5
assert abs(mu1/mp.mpf("6.13") - mp.mpf("1.67e-4")) < 1e-6 and abs(mu2/mp.mpf("6.05") - mp.mpf("1.21e-4")) < 1e-6
assert abs(mu1/math.sqrt(1680) - 2.50e-5) < 1e-7 and abs(mu2/math.sqrt(1640) - 1.81e-5) < 1e-7
print("[C-nearmiss] F = mu^2/36 = %s, %s (below 1e-7 by factors %.2f, %.2f); exclusion radii mu/L = 1.67e-4, 1.21e-4; global-bound radii 2.50e-5, 1.81e-5" % (mp.nstr(mu1**2/36, 4), mp.nstr(mu2**2/36, 4), 1e-7/(mu1**2/36), 1e-7/(mu2**2/36)))

# ---- [phase ball] closed form and the numeric chain of the proof
s_star = s6*mp.acos(1/s6)/(4*mp.pi); close(s_star, 0.2242139, ab=1e-7)
assert s_star < s6/8 - 1/(4*mp.pi) < mp.mpf(5)/16 - mp.mpf(7)/88 < mp.mpf(1)/4 and Fr(5, 16) - Fr(7, 88) == Fr(41, 176)
al = mp.acos(1/s6); assert abs(abs(3*mp.exp(1j*al) + 3*mp.exp(-1j*al))/6 - 1/s6) < mp.mpf(10)**-45          # witness overlap
assert 6*mp.cos(4*mp.pi*s_star/s6) - s6 < mp.mpf(10)**-40                                                      # equality at s*
print("[C-phase] s* = %s; chain s* < sqrt6/8 - 1/(4 pi) < 41/176 < 1/4; witness overlap cos(alpha) = 1/sqrt6; 6 cos(4 pi s*/sqrt6) = sqrt6" % mp.nstr(s_star, 10))

# ---- [six-phase / cap numbers]
assert abs(7*s6/3 - mp.mpf("5.7154761")) < 1e-7 and abs((7*s6/3)**2 - mp.mpf(98)/3) < mp.mpf(10)**-45
assert Fr(153, 8) < Fr(98, 3) and 18*36 == 648 and 20*6 == 120
z = (1 + 1j*mp.sqrt(5))/s6; assert abs(abs(z) - 1) < mp.mpf(10)**-45 and abs(3*z + 3*z.conjugate() - s6) < mp.mpf(10)**-45 and abs(abs(3*z**3 + 3*z.conjugate()**3) - 7*s6/3) < mp.mpf(10)**-45
print("[C-sixphase] 7 sqrt6/3 = %s, squared = 98/3; extremal (3,3) point is feasible and attains the bound (50 digits)" % mp.nstr(7*s6/3, 10))

# ---- [stored data] near-miss levels, 2008 hits, 20,000-start run, mutation test, d10 logs
E = json.load(open(P("near_misses/repo/results/constellations/evidence.json")))["c_levels_of_2008_hits"]
assert sum(n_ for _, n_ in E["441"]["misfit_levels"]) == E["441"]["hits_2008_criterion"] == 53 and len(E["441"]["misfit_levels"]) == 3
assert sum(n_ for _, n_ in E["531"]["misfit_levels"]) == E["531"]["hits_2008_criterion"] == 69 and len(E["531"]["misfit_levels"]) == 8
assert E["441"]["seed"] == E["531"]["seed"] == 77 and E["441"]["starts"] == 6000
assert [x for x, _ in E["441"]["misfit_levels"]] == [0.001025, 0.0016412, 0.001744] and min(x for x, _ in E["531"]["misfit_levels"]) == 0.0007328 and max(x for x, _ in E["531"]["misfit_levels"]) == 0.0012579
print("[C-levels] 6,000 starts, seed 77: 53 hits at 3 levels (1.025e-3, 1.641e-3, 1.744e-3), 69 hits at 8 levels (7.328e-4 to 1.258e-3): stored evidence agrees")
recs = [json.loads(l) for l in open(P("near_misses/repo/results/constellations/extra/random_333_seed11_20000starts.jsonl"))]
sol = [r for r in recs if r.get("kind") == "solution"]; summ = [r for r in recs if r.get("kind") == "summary"][0]
assert len(sol) == 1 and sol[0]["start"] == 16374 and abs(sol[0]["resnorm"] - 2.5e-15) < 5e-16 and summ["starts"] == 20000 and summ["seed"] == 11 and summ["converged"] == 1
print("[C-333] stored record: %d solution in %d starts (seed %d) at start %d, residual %.2e; median end misfit in summary: %s" % (len(sol), summ["starts"], summ["seed"], sol[0]["start"], sol[0]["resnorm"], [k for k in summ if "median" in k]))
A = json.load(open(P("openai_check/mutations_rerun.json"))); B = json.load(open(P("near_misses/repo/results/openai_check/mutations.json")))
assert len(A) == len(B) == 26 and [x["id"] for x in A] == [x["id"] for x in B] and [x["detected"] for x in A] == [x["detected"] for x in B]
assert sum(x["detected"] for x in A) == 17 and sorted(x["id"] for x in A if not x["detected"]) == ["M05", "M06", "M09", "M13", "M14", "M16", "M20", "M22", "M26"]
print("[C-mutation] stored first run and stored rerun agree mutant by mutant: 17 of 26 detected; missed: M05 M06 M09 M13 M14 M16 M20 M22 M26")
sm = open(P("d10/search_match.log")).read(); assert "starts 1200000, converged 1199148, end points not on the certified list: 0" in sm and "min hits 132" in sm and "3040/3040" in sm
mg = open(P("d10/margin_arb.log")).read(); assert "distinct (u,v) pairs 1272177" in mg and "4.178074647" in mg
print("[C-d10-logs] search_match.log (1.2M starts, 1,199,148 converged, 0 off list, min hits 132) and margin_arb.log (1,272,177 pairs, margin 4.178074647) agree with the report")
fs = open(P("d6_fourier/verify_fourier6.log")).read(); assert "minimum certified bound over the 16 triples: 0.0234999999946" in fs
V6 = json.load(open(P("d6_fourier/fourier6_verified.json"))); assert len(V6) == 16 and max(r["residual"] for r in V6) < 5.8e-12 + 1e-14 and abs(min(r["certified_lower_bound"] for r in V6) - 0.0234999999946) < 1e-12
print("[C-fourier-certs] stored fourier6_verified.json: 16 entries, min certified bound %.13f, largest residual %.2e (report: at most 5.8e-12)" % (min(r["certified_lower_bound"] for r in V6), max(r["residual"] for r in V6)))

# ---- [tables] the 35-row table of the report against the counts quoted in the text (only if the report source is present)
rep = P("report/report.tex")
if os.path.exists(rep):
    tex = open(rep, encoding="utf-8").read(); body = tex[tex.index("label{tab:const}"):]; body = body[:body.index("\\end{longtable}")]
    rows = re.findall(r"\$\\\{5,(\d),(\d),(\d)\\\}\$ & ([\d.]+) & ([\d.]+) & ([\d.]+) & (.*?) & (.*?)\\\\", body)
    assert len(rows) == 35, len(rows)
    stat = {}
    for r in rows:
        k = "near-miss" if "near-miss" in r[7] else ("sub" if "sub-shape" in r[7] else ("exists" if r[7].startswith("exists") else ("empty" if "empty" in r[7] else "undecided")))
        stat[k] = stat.get(k, 0) + 1
    assert stat == {"sub": 14, "exists": 3, "empty": 5, "undecided": 11, "near-miss": 2}, stat
    assert sum(1 for r in rows if float(r[3]) > 0) == 18                        # 2008 paper: 18 of 35 shapes reported as found
    assert [r[3:6] for r in rows if r[:3] == ("4", "4", "1")] == [("0.74", "0.80", "0.00")] and [r[3:6] for r in rows if r[:3] == ("5", "3", "1")] == [("1.47", "1.20", "0.00")]
    print("[C-table35] appendix table: 35 rows = 14 sub-shapes + 3 CWT examples + 5 empty + 13 undecided (11 + 2 near-misses); 18 shapes have a nonzero 2008 rate")
else:
    print("[C-table35] report/report.tex not present: table parse skipped")
print("OK")
