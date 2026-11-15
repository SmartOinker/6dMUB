# Full native rerun of the 2026 pipeline and re-certification of the Root records

Evidence for claim C11 of `docs/verification_matrix.md` (report Section 3, paragraph "Full native rerun").

| what | where |
|---|---|
| drivers of the native run and of the replay | `src/full_run.py`, `src/replay_from_fine.py`, `src/build_native.sh` |
| output of every child invocation of the native run (100 invocations), command records | `results/fresh/`, `results/fresh-driver.log` |
| accounting check of the complete run (stage counts, batch roots, ordered failures, fallback operands, final partition; the 8 principal files against the released SHA-256 values) | `src/check_fresh.py`, result `results/fresh-checked.json` |
| independent check of the Root inequalities in 128-bit Arb ball arithmetic (27,189 records read, 27,188 distinct Roots, 1,143 in the transposed orientation) and its negative controls | `src/verify_roots.py`, `src/check_root_negative_controls.py`, results `results/roots-certified.json`, `results/root-negative-controls.json` |
| environment of the native run (AMD EPYC, GCC 14.2, flags) | `results/environment.json`, `results/abi-probe.txt` |
| the published sources that were compiled (Apache 2.0, copyright OpenAI, see `upstream/LICENSE`) | `upstream/` |
| repeat of the accounting check and of the Root re-certification on a second machine, 15 Nov 2026 | `RERUN_LOG.txt`, `results_rerun/` |

Quick check of the stored results (no download, 1 s): `python3 check_recorded_evidence.py` (step S43 of `verify_all.sh`).

Repeat the checks themselves (80 MB download, about 10 minutes):

```
./fetch_upstream_git.sh                 # pinned OpenAI saved run, 308 files, compared with results/upstream-manifest.json
python3 src/restore_recorded_data.py    # puts the byte-identical data files next to the logs of the run (hash-checked)
python3 src/check_fresh.py
OPENBLAS_NUM_THREADS=1 python3 src/verify_roots.py      # needs python-flint 0.9.0
python3 src/check_root_negative_controls.py
```

Repeat the native run (x86-64 Linux, GCC, about 4.4 hours of summed process time on four workers):
`bash src/build_native.sh && MUB6_FRESH_DIR=results/fresh2 python3 src/full_run.py && python3 src/check_fresh.py`.
The native run was done once. Exit status 1 of a stage-C batch means "records left for the fallback stage" (15 of the 88 batches); the run ends with no unresolved record.

Limits: both programs and the original were written with AI assistance, so this is not an independent human review; byte agreement does not rule out a shared source-level error and proves none of the analytic covering lemmas.
