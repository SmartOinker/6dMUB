#!/usr/bin/env python3
"""Reads the stored record of the optimisation that produced the explicit four-basis sets
(repo/results/visibility/results.json, written by repo/src/visibility/t3_optimise.py and t7_*.py) and checks the
numbers the report quotes about it.  Nothing is re-optimised here; this is a check of a stored record against the
report, in floating point, and against the stored matrices (bases_d6_*.npy, evaluated with numpy).

Checked: 72 starts for the bias optimisation, 700 starts for the game optimisation, best bias 0.030224,
best game score 0.7038883627 (shortfall 2.3578e-4 against the MUB value 0.7041241452), and the structure of the
P_4 set (three pairs at the MUB value, three pairs biased).
Usage: python3 -I check_visibility_records.py
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
V = os.path.join(HERE, "repo", "results", "visibility")
r = json.load(open(os.path.join(V, "results.json")))
ok = True


def chk(cond, msg):
    global ok
    print(("ok  " if cond else "FAIL"), msg)
    ok &= bool(cond)


wb, op = r["worst_case_bias"], r["optimisation"]
chk(wb["n_starts"] == 72, f"bias optimisation: {wb['n_starts']} starts recorded (report: 72)")
chk(op["n_runs_d6_P"] == 700, f"game optimisation: {op['n_runs_d6_P']} runs recorded (report: 700)")
chk(abs(wb["best_delta"] - 0.030224) < 5e-7, f"best bias {wb['best_delta']:.9f} (report 0.030224)")
chk(abs(op["d6_P4_best"] - 0.7038883627) < 5e-11, f"best game score {op['d6_P4_best']:.10f} (report 0.7038883627)")
chk(abs(op["gap_to_MUB"] - 2.357825e-4) < 5e-10, f"shortfall {op['gap_to_MUB']:.6e} (report 2.357825e-4)")
pw = np.array(op["d6_pairwise_P"])
chk((np.abs(pw[:3] - op["d6_MUB_value_exact"]) < 1e-9).all() and (pw[3:] < op["d6_MUB_value_exact"] - 4e-4).all(),
    "P_4 set: three pairs reach the MUB value (to 1e-9, i.e. unbiased only numerically), three pairs fall short by about 4.7e-4")

# the stored matrices: unitary, and the bias of the delta set recomputed from them
for name, want in (("bases_d6_delta.npy", 0.030224), ("bases_d6_P4.npy", None)):
    B = np.load(os.path.join(V, name))
    n, d = B.shape[0], B.shape[1]
    unit = max(np.abs(b.conj().T @ b - np.eye(d)).max() for b in B)
    dev = max(np.abs(np.abs(B[a].conj().T @ B[b]) ** 2 - 1 / d).max() for a in range(n) for b in range(a + 1, n))
    print(f"    {name}: {n} bases in dimension {d}; unitarity defect {unit:.2e}; largest deviation of an overlap from 1/6: {dev:.9f}")
    if want:
        chk(abs(dev - want) < 5e-7, f"{name}: bias recomputed from the stored matrices {dev:.9f} (report 0.030224)")
print("OK" if ok else "FAIL")
sys.exit(0 if ok else 1)
