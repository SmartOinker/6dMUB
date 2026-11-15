#!/usr/bin/env python3
"""Recompute the 35-row table of constellations {5,a,b,c} of the report from the raw search output
shipped in this repository, and compare every column with the LaTeX table of the report.

What is checked (all from `repo/results/constellations/`, no search is re-run here):
  * table/t_abc.jsonl.gz (35 shapes + the triple {5,5,5} as t_55): per shape the header (seed, starts),
    the summary (converged = starts with misfit < 1e-11, bw_found = starts with F_BW < 1e-7, best misfit)
    and the number of "solution" records.  Columns "ours, 2008 crit." and "ours, strict" are
    100*bw_found/starts and 100*converged/starts rounded to two decimals; "min. misfit" is the best end
    misfit with three significant digits ("<1e-14" when it is below 1e-14 and some start converged).
  * the figures "389 of 52,000" and "695 of 52,000" (50,000 starts of big/ at seeds 101, 102 plus the
    2,000 starts of the table at seed 2026), and "none of the 52,000" strict;
  * the level counts of the 6,000-start run (seed 77) in evidence.json against the report text;
  * the long-run value 4.99e-3 for {5,4,3,2} and the 20,000-start search for {5,3,3,3}
    (extra/random_432_seed11_6000starts.jsonl, extra/random_333_seed11_20000starts.jsonl);
  * yale_examples_check.json (output of src/constellations/check_yale_examples.py) against the
    paragraph on the three explicit constellation examples.
The report table is parsed from the LaTeX file given as argument (default ../report/report.tex).
The 2008 column is quoted from the 2008 paper (literature); no raw data of it exist, it is only parsed.
This is bookkeeping on stored floating-point search output, not a certificate.

Usage:  python3 -I check_table.py [report.tex] [repo_dir]
Exit code 0 iff no mismatch (a mismatch list is printed in any case).
"""
import gzip, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "report", "report.tex")
REPO = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "repo")
RC = os.path.join(REPO, "results", "constellations")
mismatches, notes = [], []


def mism(msg):
    mismatches.append(msg)
    print("MISMATCH:", msg)


def read_jsonl(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def sig3(x):
    return float("%.2e" % x)


def num(s):
    """'$8.89\\times10^{-2}$' -> 0.0889 ; '$<10^{-14}$' -> '<1e-14'."""
    s = s.strip().strip("$").strip()
    if s.startswith("<"):
        return "<1e-14"
    m = re.match(r"([0-9.]+)\\times10\^\{(-?\d+)\}", s)
    return float(m.group(1)) * 10 ** int(m.group(2)) if m else float(s)


# ------------------------------------------------------------------ parse the report
tex = open(REPORT, encoding="utf-8").read()
i0 = tex.index(r"\label{tab:const}")
body = tex[i0:tex.index(r"\end{longtable}", i0)]
row_re = re.compile(r"\$\\\{5,(\d),(\d),(\d)\\\}\$\s*&\s*([0-9.]+)\s*&\s*([0-9.]+)\s*&\s*([0-9.]+)\s*&\s*(\$[^&]*?\$)\s*&\s*([^\\]*?(?:\\cite\{CWT\})?)\\\\")
rows = []
for m in row_re.finditer(body):
    a, b, c = int(m.group(1)), int(m.group(2)), int(m.group(3))
    rows.append(dict(g=(a, b, c), r2008=float(m.group(4)), ours=float(m.group(5)), strict=float(m.group(6)),
                     mis=num(m.group(7)), status=m.group(8).strip()))
print(f"report table: {len(rows)} rows parsed from {REPORT}")
if len(rows) != 35:
    mism(f"expected 35 rows in the report table, parsed {len(rows)}")

# summary table (six rows) of the main text
# (the summary table was removed from the main text in review cycle 4; the check runs only if it is present)
j0 = tex.find(r"\label{tab:constsum}")
sbody = tex[tex.rindex(r"\begin{tabular}", 0, j0):j0] if j0 >= 0 else ""
srows = []
for m in re.finditer(r"\$\\\{5,(\d),(\d),(\d)\\\}\$\s*&\s*([0-9.]+)\s*&\s*([0-9.]+)\s*&\s*([0-9.]+)\s*&\s*(\$[^&]*?\$)\s*&", sbody):
    srows.append(dict(g=tuple(int(m.group(k)) for k in (1, 2, 3)), r2008=float(m.group(4)), ours=float(m.group(5)),
                      strict=float(m.group(6)), mis=num(m.group(7))))
print(f"report summary table (tab:constsum): {len(srows)} rows")

# ------------------------------------------------------------------ recompute from raw data
data = {}
for r in rows:
    fn = os.path.join(RC, "table", "t_%d%d%d.jsonl.gz" % r["g"])
    recs = read_jsonl(fn)
    hdr = [d for d in recs if d["kind"] == "header"]
    summ = [d for d in recs if d["kind"] == "summary"]
    sol = [d for d in recs if d["kind"] == "solution"]
    assert len(hdr) == 1 and len(summ) == 1, fn
    h, s = hdr[0], summ[0]
    data[r["g"]] = dict(seed=h["seed"], starts=h["starts"], tol=h["tol"], run=s["starts"], conv=s["converged"],
                        bw=s["bw_found"], best=s["best_resnorm"], nsol=len(sol), groups=h["groups"])
    d = data[r["g"]]
    if d["groups"] != list(r["g"]):
        mism(f"{r['g']}: file header says groups {d['groups']}")
    if d["nsol"] != d["conv"]:
        mism(f"{r['g']}: {d['nsol']} solution records but summary says converged={d['conv']}")
    if d["run"] != d["starts"]:
        mism(f"{r['g']}: header starts {d['starts']} but {d['run']} starts completed")
    if d["bw"] < d["conv"]:
        mism(f"{r['g']}: bw_found {d['bw']} < converged {d['conv']}")

seeds = {d["seed"] for d in data.values()}
starts = {d["starts"] for d in data.values()}
tols = {d["tol"] for d in data.values()}
print(f"seeds used by the 35 table runs: {sorted(seeds)}; starts per shape: {sorted(starts)}; strict tolerance: {sorted(tols)}")
if starts != {2000}:
    mism(f"report says 2,000 starts per shape, data has {sorted(starts)}")
if len(seeds) != 1:
    mism(f"report says one fixed seed, data has seeds {sorted(seeds)}")
# the strict criterion in the report is mu < 1e-11
if tols != {1e-11}:
    mism(f"report strict criterion mu < 1e-11, data tolerance {sorted(tols)}")

# the {5,5,5} triple, shipped as t_55
t55 = read_jsonl(os.path.join(RC, "table", "t_55.jsonl.gz"))
s55 = [d for d in t55 if d["kind"] == "summary"][0]
print(f"extra file t_55 (the MU triple {{5,5,5}}, not a row of the table): {s55['converged']} of {s55['starts']} starts converged")

# ------------------------------------------------------------------ compare row by row
print("\nshape      2008 | ours(2008 crit) rep/data | strict rep/data | min misfit rep/data | status")
for r in rows:
    d = data[r["g"]]
    n = d["starts"]
    ours = round(d["bw"] * 10000 / n) / 100
    strict = round(d["conv"] * 10000 / n) / 100
    if d["best"] < 1e-14 and d["conv"] > 0:
        mis = "<1e-14"
    else:
        mis = sig3(d["best"])
    ok_o = abs(ours - r["ours"]) < 5e-3
    ok_s = abs(strict - r["strict"]) < 5e-3
    ok_m = (mis == r["mis"]) if isinstance(mis, str) or isinstance(r["mis"], str) else abs(mis - r["mis"]) <= 1e-9 * abs(mis) + 1e-12
    shape = "{5,%d,%d,%d}" % r["g"]
    print(f"{shape:10s} {r['r2008']:6.2f} | {r['ours']:6.2f} / {ours:6.2f} ({d['bw']:4d}) {'ok ' if ok_o else 'XX '}| "
          f"{r['strict']:6.2f} / {strict:6.2f} ({d['conv']:4d}) {'ok ' if ok_s else 'XX '}| "
          f"{r['mis']} / {mis} {'ok ' if ok_m else 'XX '}| {r['status']}")
    if not ok_o:
        mism(f"{shape} ours (2008 criterion): report {r['ours']:.2f}, data {ours:.2f} ({d['bw']}/{n})")
    if not ok_s:
        mism(f"{shape} strict: report {r['strict']:.2f}, data {strict:.2f} ({d['conv']}/{n})")
    if not ok_m:
        mism(f"{shape} min misfit: report {r['mis']}, data {mis} (best_resnorm {d['best']!r})")
    # status consistency with the data
    st = r["status"]
    if st.startswith("exists (sub-shape)") and not (d["conv"] > 0 and d["best"] < 1e-14):
        mism(f"{shape} labelled sub-shape found with misfit <1e-14, data best {d['best']!r}, converged {d['conv']}")
    if (st.startswith("empty") or st.startswith("undecided")) and d["conv"] > 0:
        mism(f"{shape} labelled {st} but {d['conv']} starts converged")

# summary table rows
for sr in srows:
    r = next(x for x in rows if x["g"] == sr["g"])
    for k in ("r2008", "ours", "strict", "mis"):
        if sr[k] != r[k]:
            mism(f"tab:constsum row {sr['g']} column {k}: {sr[k]} but appendix table {r[k]}")
print(f"tab:constsum rows checked against the appendix table: {len(srows)}")

# counts of statuses
cnt = {"sub": 0, "cwt_exists": 0, "empty": 0, "undecided": 0, "near": 0}
for r in rows:
    st = r["status"]
    if st.startswith("exists (sub-shape)"):
        cnt["sub"] += 1
    elif st.startswith("exists"):
        cnt["cwt_exists"] += 1
    elif st.startswith("empty"):
        cnt["empty"] += 1
    elif st.startswith("undecided (near-miss)"):
        cnt["near"] += 1
    elif st.startswith("undecided"):
        cnt["undecided"] += 1
nz = sum(1 for r in rows if r["r2008"] > 0)
print(f"status counts: {cnt}; shapes with a nonzero 2008 rate: {nz}")
if (cnt["sub"], cnt["cwt_exists"], cnt["empty"], cnt["undecided"] + cnt["near"], cnt["near"]) != (14, 3, 5, 13, 2):
    mism(f"status counts differ from 14 + 3 + 5 + 13 (2 near-misses): {cnt}")
if nz != 18:
    mism(f"report says 18 shapes with a nonzero 2008 rate, table has {nz}")
found_here = sum(1 for g, d in data.items() if d["conv"] > 0)
print(f"shapes with at least one strictly converged start in the data: {found_here} "
      f"(14 sub-shapes + {{5,4,3,1}} and {{5,5,2,2}}; {{5,3,3,3}} is not found in 2,000 starts)")
if found_here != 16:
    mism(f"expected 16 shapes found strictly in the 2,000-start runs, data has {found_here}")

# ------------------------------------------------------------------ 52,000 starts
print("\nFinding 1: the 52,000-start counts")
txt = re.sub(r"\\,|\{,\}", "", tex)
m389 = re.search(r"\$([0-9.]+)\\%\$\s*\((\d+) of (\d+) starts\)\s*and\s*\$([0-9.]+)\\%\$\s*\((\d+) of (\d+)\)", txt)
rep = dict(p441=float(m389.group(1)), k441=int(m389.group(2)), n441=int(m389.group(3)),
           p531=float(m389.group(4)), k531=int(m389.group(5)), n531=int(m389.group(6)))
tot = {}
for g, big in (((4, 4, 1), "big_441_seed101.jsonl"), ((5, 3, 1), "big_531_seed102.jsonl")):
    recs = read_jsonl(os.path.join(RC, "big", big))
    s = [d for d in recs if d["kind"] == "summary"][0]
    h = [d for d in recs if d["kind"] == "header"][0]
    t = data[g]
    tot[g] = dict(bw=s["bw_found"] + t["bw"], conv=s["converged"] + t["conv"], n=s["starts"] + t["starts"],
                  parts=f"big seed {h['seed']}: {s['bw_found']} of {s['starts']}; table seed {t['seed']}: {t['bw']} of {t['starts']}",
                  convparts=f"strict {s['converged']} + {t['conv']}")
    print(f"  {g}: {tot[g]['parts']} -> {tot[g]['bw']} of {tot[g]['n']} ({100*tot[g]['bw']/tot[g]['n']:.3f}%); {tot[g]['convparts']}")
for g, k, n, p in (((4, 4, 1), rep["k441"], rep["n441"], rep["p441"]), ((5, 3, 1), rep["k531"], rep["n531"], rep["p531"])):
    t = tot[g]
    if (t["bw"], t["n"]) != (k, n):
        mism(f"{g}: report {k} of {n}, data {t['bw']} of {t['n']}")
    if abs(round(100 * t["bw"] / t["n"], 2) - p) > 5e-3:
        mism(f"{g}: report {p}%, data {100*t['bw']/t['n']:.2f}%")
    if t["conv"] != 0:
        mism(f"{g}: report says none of {n} starts converged strictly, data has {t['conv']}")
print(f"  report: {rep}")

# ------------------------------------------------------------------ levels (evidence.json, seed 77)
print("\nFinding 1: level counts (evidence.json, 6,000 starts, seed 77)")
ev = json.load(open(os.path.join(RC, "evidence.json")))["c_levels_of_2008_hits"]
mm = re.search(r"the (\d+) hits for \$\\\{5,4,4,1\\\}\$ sit at three positive misfit levels\s*"
               r"\(\$\\mu\\approx([0-9.]+)\$,\s*\$([0-9.]+)\$,\s*\$([0-9.]+)\\times10\^\{-3\}\$\)"
               r"\s*and the (\d+) hits for \$\\\{5,5,3,1\\\}\$ at (\w+)\s*levels from \$([0-9.]+)\\times10\^\{-4\}\$ to \$([0-9.]+)\\times10\^\{-3\}\$", tex)
e441, e531 = ev["441"], ev["531"]
lv441 = [l for l, c in e441["misfit_levels"]]
lv531 = [l for l, c in e531["misfit_levels"]]
print(f"  441: hits {e441['hits_2008_criterion']}, levels {e441['misfit_levels']} (starts {e441['starts']}, seed {e441['seed']})")
print(f"  531: hits {e531['hits_2008_criterion']}, levels {e531['misfit_levels']} (starts {e531['starts']}, seed {e531['seed']})")
if not mm:
    mism("could not parse the level sentence of Finding 1 in the report")
else:
    r441 = [float(mm.group(k)) * 1e-3 for k in (2, 3, 4)]
    if int(mm.group(1)) != e441["hits_2008_criterion"] or int(mm.group(5)) != e531["hits_2008_criterion"]:
        mism(f"hit counts: report {mm.group(1)}/{mm.group(5)}, data {e441['hits_2008_criterion']}/{e531['hits_2008_criterion']}")
    if len(lv441) != 3 or any(abs(a - b) > 6e-7 for a, b in zip(sorted(r441), sorted(lv441))):
        mism(f"levels for {{5,4,4,1}}: report {r441}, data {lv441}")
    words = {"three": 3, "eight": 8}
    if words.get(mm.group(6)) != len(lv531):
        mism(f"{{5,5,3,1}} number of levels: report {mm.group(6)}, data {len(lv531)}")
    lo, hi = float(mm.group(7)) * 1e-4, float(mm.group(8)) * 1e-3
    if abs(min(lv531) - lo) > 6e-7 or abs(max(lv531) - hi) > 6e-7:
        mism(f"{{5,5,3,1}} level range: report {lo}..{hi}, data {min(lv531)}..{max(lv531)}")
    if (e441["seed"], e441["starts"], e531["seed"]) != (77, 6000, 77):
        mism("evidence.json is not the 6,000-start seed-77 run described in the report")
    if sum(c for l, c in e441["misfit_levels"]) != e441["hits_2008_criterion"] or sum(c for l, c in e531["misfit_levels"]) != e531["hits_2008_criterion"]:
        mism("level counts do not sum to the number of hits in evidence.json")

# ------------------------------------------------------------------ long runs
print("\nlong runs")
r432 = [d for d in read_jsonl(os.path.join(RC, "extra", "random_432_seed11_6000starts.jsonl")) if d["kind"] == "summary"][0]
mlong = re.search(r"\$([0-9.]+)\\times10\^\{-3\}\$ for \$\\\{5,4,3,2\\\}\$", tex)
print(f"  {{5,4,3,2}}: best misfit over {r432['starts']} starts (seed {r432['seed']}): {r432['best_resnorm']!r}; report {mlong.group(1)}e-3")
if abs(float(mlong.group(1)) * 1e-3 - sig3(r432["best_resnorm"])) > 1e-9:
    mism(f"{{5,4,3,2}} long run: report {mlong.group(1)}e-3, data {r432['best_resnorm']:.3e}")
r333 = read_jsonl(os.path.join(RC, "extra", "random_333_seed11_20000starts.jsonl"))
s333 = [d for d in r333 if d["kind"] == "summary"][0]
sol333 = [d for d in r333 if d["kind"] == "solution"]
print(f"  {{5,3,3,3}}: {s333['converged']} converged of {s333['starts']} (seed {s333['seed']}); solution at start "
      f"{sol333[0]['start']} residual {sol333[0]['resnorm']:.3e}; median end misfit {s333['median']:.3f}")
if (s333["converged"], s333["starts"], sol333[0]["start"]) != (1, 20000, 16374):
    mism(f"{{5,3,3,3}}: report 1 of 20,000 at start 16,374, data {s333['converged']} of {s333['starts']} at {sol333[0]['start']}")
if round(sol333[0]["resnorm"] / 1e-15, 1) != 2.5:
    mism(f"{{5,3,3,3}} residual: report 2.5e-15, data {sol333[0]['resnorm']:.3e}")
if round(s333["median"], 2) != 0.41:
    mism(f"{{5,3,3,3}} median end misfit: report 0.41, data {s333['median']:.4f}")
# seed 11 stated for the 333 run and seed 77 for the levels
if "seed 11" not in tex:
    mism("seed 11 not stated in the report")

# ------------------------------------------------------------------ independent re-implementation (other platform)
print("\nindependent re-implementation on another platform (results/openmathos/final_run.json, 6,535,041 starts, 0 converged)")
om = json.load(open(os.path.join(REPO, "results", "openmathos", "final_run.json")))
if om["total"]["converged"] != 0:
    mism(f"openmathos run: {om['total']['converged']} starts converged")
for name, rec in om["run_2"]["per_shape"].items():
    g = tuple(int(t) for t in re.findall(r"\d", name))[1:]
    mine = data[g]["best"]
    ok = rec["smallest_misfit"] <= mine * (1 + 1e-9)
    print(f"  {name}: smallest misfit over {rec['starts']} starts {rec['smallest_misfit']:.10e}; this table (2,000 starts) {mine:.10e}  {'ok' if ok else 'XX'}")
    if not ok or rec["converged"] != 0:
        mism(f"openmathos {name}: smallest misfit {rec['smallest_misfit']} not below the 2,000-start value {mine}")
oc = om["run_2"]["per_shape"]["{5,4,3,2}"]["smallest_misfit"]
if abs(oc - r432["best_resnorm"]) > 1e-10:
    mism(f"{{5,4,3,2}} long run: this repository {r432['best_resnorm']:.10e}, other platform {oc:.10e}")

# F_BW = mu^2/36 for the two further minima whose certificate was rerun (Proposition on near-misses, "Independent checks")
for g, rep in (((4, 3, 2), 6.9e-7), ((4, 4, 2), 1.56e-6)):
    mu = om["run_2"]["per_shape"]["{5,%d,%d,%d}" % g]["smallest_misfit"]
    fbw = mu * mu / 36
    ok = abs(fbw - rep) / rep < 0.01
    print(f"  F_BW ~ mu^2/36 for {{5,{g[0]},{g[1]},{g[2]}}}: {fbw:.3e} (report {rep:.2e}, above 1e-7)  {'ok' if ok else 'XX'}")
    if not ok or fbw < 1e-7:
        mism(f"F_BW for {g}: report {rep}, mu^2/36 = {fbw:.3e}")

# ------------------------------------------------------------------ explicit examples
print("\nexplicit constellation examples (yale_examples_check.json)")
y = json.load(open(os.path.join(RC, "yale_examples_check.json")))
f = lambda s: float(s)
m5333 = f(y["5333"]["misfit"])
m5431 = max(f(c["misfit"]) for c in y["5431"]["per_cube_root"])
c5522, p5522 = f(y["5522"]["misfit_at_box_centre"]), f(y["5522"]["misfit_after_polish"])
print(f"  {{5,3,3,3}} {m5333:.3e}; {{5,4,3,1}} largest over the three cube roots {m5431:.3e}; "
      f"{{5,5,2,2}} centre {c5522:.3e}, polished {p5522:.3e}")
claims = [("{5,3,3,3} about 3e-40", abs(m5333 - 3e-40) < 0.5e-40), ("{5,4,3,1} below 5e-40", m5431 < 5e-40),
          ("{5,5,2,2} centre 2.2e-7", round(c5522 / 1e-7, 1) == 2.2), ("{5,5,2,2} polished below 4e-30", p5522 <= 4e-30)]
for name, ok in claims:
    print("  ", "ok " if ok else "XX ", name)
    if not ok:
        mism("explicit examples: " + name)

# ------------------------------------------------------------------ what has no raw data
print("\nnumbers of the report section without raw data in this repository")
print("  - the 2008 column (10,000 starts of the 2008 paper): quoted from the literature, no data here")
print("  - the 'status' of each row beyond the data (exists / empty from the cited classification)")
print("  - the 6,000-start level run itself is stored only as the summary evidence.json "
      "(re-runnable with src/constellations/evidence.py part (c); see docs/verification_matrix.md)")

print()
if mismatches:
    print(f"{len(mismatches)} MISMATCH(ES):")
    for x in mismatches:
        print("  -", x)
    sys.exit(1)
print("OK: every column of the 35-row table and the quoted figures agree with the raw data")
