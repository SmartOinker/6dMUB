#!/usr/bin/env python3
"""Check the stored evidence of the full native rerun and of the Root re-certification (no data download needed).

It reads the result files of the original run (results/) and of the repeat on a second machine (results_rerun/)
and checks the numbers quoted in the report: 100 child invocations, 8 principal files byte-identical to the
released ones, no unresolved record at the end; 27,189 Root records read, 27,188 distinct Roots certified at
128 bits, 1,143 in the transposed orientation; the per-invocation logs are present.
To repeat the checks themselves (about 10 minutes, 80 MB download):
  ./fetch_upstream_git.sh && python3 src/restore_recorded_data.py && python3 src/check_fresh.py
  OPENBLAS_NUM_THREADS=1 python3 src/verify_roots.py && python3 src/check_root_negative_controls.py
The native run itself (src/full_run.py, about 4.4 hours of process time) is not repeated by this script.
"""
import json, pathlib, sys
D = pathlib.Path(__file__).resolve().parent
ok = True
def check(name, cond, detail=""):
    global ok
    print(("[PASS] " if cond else "[FAIL] ") + name + (": " + str(detail) if detail != "" else ""))
    ok = ok and bool(cond)
for tag, R in (("original run", D / "results"), ("repeat on a second machine", D / "results_rerun")):
    f = json.loads((R / "fresh-checked.json").read_text())
    check(f"{tag}: accounting check of the full native run passes", f["result"] == "PASS" and f["children"] == 100 and f["final_unresolved"] == 0,
          f"children {f['children']}, centers {f['centers']}, batches {f['batches']}, initial unresolved {f['initial_unresolved']}, fallback {f['fallback']}, final unresolved {f['final_unresolved']}")
    pf = f["principal_files_match_released_sha256"]
    check(f"{tag}: principal files byte-identical to the released ones", len(pf) == 8 and all(pf.values()), ", ".join(sorted(pf)))
    r = json.loads((R / "roots-certified.json").read_text())
    check(f"{tag}: Root records re-certified in Arb", r["result"] == "PASS" and r["precision_bits"] == 128 and r["records_read"] == 27189
          and r["unique_roots_checked"] == 27188 and r["transposed_orientation_certificates"] == 1143,
          f"read {r['records_read']}, distinct certified {r['unique_roots_checked']}, transposed {r['transposed_orientation_certificates']}, {r['precision_bits']} bits, python-flint {r['python_flint']}, {r['seconds']:.0f} s")
    n = json.loads((R / "root-negative-controls.json").read_text())
    check(f"{tag}: negative controls of the Root checker", n.get("result", "").startswith("PASS"), n.get("scope", "")[:110])
drv = [l.split() for l in (D / "results/fresh-driver.log").read_text().splitlines() if len(l.split()) == 3]
# Exit status 1 is the pipeline's documented signal "this stage-C batch left unresolved records" (they go to the fallback stage).
n1 = sum(x[1] == "1" for x in drv)
check("driver log: 100 child invocations, exit statuses 0 or 1 (1 = batch with records sent to the fallback), run completed",
      len(drv) == 100 and all(x[1] in ("0", "1") for x in drv) and all(x[0].startswith("C") for x in drv if x[1] == "1")
      and "complete native pipeline with zero final unresolved records" in (D / "results/fresh-driver.log").read_text(),
      f"{len(drv)} invocations, {n1} stage-C batches with status 1, {sum(float(x[2]) for x in drv):.0f} s summed")
logs = list((D / "results/fresh").glob("*"))
check("per-invocation output files of the native run are present", len(logs) >= 200, f"{len(logs)} files in results/fresh")
man = json.loads((D / "results/upstream-manifest.json").read_text())
check("pinned upstream manifest", man["commit"] == "4eaee87548250b2682affda7d05d947c05554bae" and len(man["files"]) == 308, f"{len(man['files'])} files, {sum(x['bytes'] for x in man['files'])} bytes")
print("OK" if ok else "FAILED"); sys.exit(0 if ok else 1)
