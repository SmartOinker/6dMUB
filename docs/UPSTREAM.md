# Upstream sources

| source | revision | what this repository takes from it |
|---|---|---|
| earlier team repository `mub6-problem124` (delivered as a git bundle, not public) | HEAD 2688d198ab28f3fcaf0b4cefa183ea544562ae80 | `near_misses/repo/` (constellation search, near-miss certificate `certify.py`, `polished.jsonl`, `certificate.json`, mutation-test record) and the explicit four-basis sets `near_misses/repo/results/visibility/bases_d6_delta.npy`, `bases_d6_P4.npy`, `sim.json`. Added later from the same repository (staged copy, same relative layout): `results/constellations/{table,sym,big,extra}` (the 36 table runs are stored gzip-compressed here, content unchanged), `yale_examples_check.json`, `results/fourier/`, `src/fourier/`, `src/constellations/{check_yale_examples,evidence,sym_search}.py`, `table_run.sh`, `src/visibility/{t1_t2_checks,t3_optimise,t7_assemble,t7_delta}.py`, and `results/openmathos/` (notes and JSON of an independent re-implementation of the constellation search run on another platform, copied unedited) |
| team Lean/audit repository (link in the report title block) | 1033fb082aa0a82ffa4708411370434dc7d9fc23 | workstream B baseline: structure theory and Lean proof of the 1/72 energy gap (`supplementary/workstream_B_structure_paper.pdf`) |
| same | 4360b1a5bc0211dfd8ebfc6b650c500a29dca384 | workstream C audit code and evidence: native rerun, 27,188 root records, sharp phase-ball radius (`supplementary/workstream_C_audit.pdf`) |
| same | c9e269511be6e7b6a8e5e908668af236209d15f8 | workstream C worked-check source |
| dimension-ten working folder `mub10` | none: not under version control, so no commit hash exists | the list of 3,040 unimodular cyclic 10-roots (`data/exact/bu10hp_unimod.txt`) and `data/exact/d10_analysis.json`, read by `d10/check_d10.py` and `d10/energy10.py`; the derived files used here are copied into `d10/` (`vecs.npy`, `bases.json`, `energy10.json`, logs) |

Nothing from the team Lean/audit repository was rebuilt or rerun for this repository.
