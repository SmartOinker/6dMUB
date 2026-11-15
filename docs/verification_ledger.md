# Verification ledger (superseded by the verification matrix)

This file used to hold a short table of results with their status. It had fallen behind the repository (for example it still said that the
certificates for the 16 Fourier-pair triples were not finished, that the dimension-ten root list was not in the repository, and that the
square-root lemma had no script), so its rows were removed instead of being patched.

The current, complete record is **`docs/verification_matrix.md`**: 67 rows (64 claims of the report plus three Lean rows), each with where it appears, its status tag, who produced it, the shipped
check that independently re-verifies it (script, exact command, expected output line, runtime), what was observed on 15 November 2026, and a
yes / partly / no verdict. `verify_all.sh` runs all fast checks, and `docs/verify_all.log` is the log of the run (40 steps).

Summary of the verdicts at the time of writing: 67 rows; 30 independently re-verified, 24 partly, 13 not (literature cited and not re-verified,
results reported by a teammate, or results without a script in this repository). The two largest items that remain outside this repository are the Lean
build of workstream B (a separate Lean project at the repository root, `MUB6Bridge`, is built and has its own rows) and the full native rerun by workstream C. The statement E > 1/72 does not depend on the Lean build for its truth: it is independently
implied by the interval certificate E > 0.0384999 (`cert/verify.py`), and its proof steps are tested by `checks/check_gap72.py`.
Hypothesis (H), the cited count of 34,940 cyclic 10-roots, is not verified by anything here.

Status vocabulary used in the report: proved / Lean-checked as reported / interval-certified / computed / numerical only / cited / conditional /
conjectured / reported. Terminology of the matrix: "reproduced" means the same workstream or program gave the same output again; "independently
re-verified" means a second implementation or a certificate checker that shares no code with the producer.
