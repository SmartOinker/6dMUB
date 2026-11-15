# Structure Lean project (E > 1/72 and the structure-theory declarations)

A Lake project separate from the root project `MUB6Bridge`: 46 modules, 394 public theorems, Lean v4.35.0, Mathlib at
`56a005855ea17e0b0958f73ec801ae140b0a1679` (same as the root project). See `README.md` for what each module proves and what remains written.

* Rebuild: `lake exe cache get && lake build` in this directory, then `lake env lean AuditAll.lean` for the axioms.
* Stored records: `logs/build-final.log` (3,350 jobs, completed successfully), `logs/axioms-all.log` (394 theorems, axioms `propext`, `Classical.choice`, `Quot.sound` only), `logs/environment.txt`, `hash-manifest.json`.
* `python3 check_logs.py` checks the records against the sources without Lean (step S42 of `verify_all.sh`).
* A build of the repository root does not compile this project. The stored build was made on one machine (macOS, arm64); it was not repeated on a second machine before the deadline.
* Local user paths were removed from `integration-provenance.json` and `verification.json`; nothing else was changed.
