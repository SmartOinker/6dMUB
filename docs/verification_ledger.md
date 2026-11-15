# Verification ledger (superseded by the verification matrix)

This file used to hold a short table of results with their status. It had fallen behind the repository (for example it still said that the
certificates for the 16 Fourier-pair triples were not finished, that the dimension-ten root list was not in the repository, and that the
square-root lemma had no script), so its rows were removed instead of being patched.

The current, complete record is **`docs/verification_matrix.md`**: 70 rows (65 claims of the report plus five Lean rows), each with where it appears, its status tag, who produced it, the shipped
check that independently re-verifies it (script, exact command, expected output line, runtime), what was observed on 15 November 2026, and a
yes / partly / no verdict. `verify_all.sh` runs all fast checks, and `docs/verify_all.log` is the log of the run (41 steps); steps S42 and S43 of the final revision are logged in `docs/verify_final_steps.log`.

Summary of the verdicts at the time of writing: 70 rows; 32 independently re-verified, 27 partly, 11 not (literature cited and not re-verified,
or results without a script in this repository). The two largest items that were run once only are the build of the structure Lean project (`lean_structure/`, stored logs checked by step S42; the separate Lean project at the repository root, `MUB6Bridge`, four files and 45 declarations, built locally with Lean v4.35.0 and Mathlib v4.35.0 and with five rows C65 to C69; the competition's automated build has not been run on it by us. Not Lean-verified: the energy bounds, the score as an optimal success probability, every probability statement, the purity witness, dimension ten) and the full native rerun (`openai_check/full_audit/`, stored results checked by step S43; its accounting check and Root re-certification were repeated on a second machine). The statement E > 1/72 does not depend on the Lean build for its truth: it is independently
implied by the interval certificate E > 0.0384999 (`cert/verify.py`), and its proof steps are tested by `checks/check_gap72.py`.
Hypothesis (H), the cited count of 34,940 cyclic 10-roots, is not verified by anything here.

Status vocabulary used in the report: proved / Lean-checked (root project or structure project) / interval-certified / computed / numerical only / cited / conditional /
conjectured. Terminology of the matrix: "reproduced" means the same program gave the same output again; "independently
re-verified" means a second implementation or a certificate checker that shares no code with the producer.
