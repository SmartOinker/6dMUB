# Upstream sources

| source | revision | what this repository takes from it |
|---|---|---|
| earlier team repository `mub6-problem124` (delivered as a git bundle, not public) | HEAD 2688d198ab28f3fcaf0b4cefa183ea544562ae80 | `near_misses/repo/` (constellation search, near-miss certificate `certify.py`, `polished.jsonl`, `certificate.json`, mutation-test record) and the explicit four-basis sets `near_misses/repo/results/visibility/bases_d6_delta.npy`, `bases_d6_P4.npy`, `sim.json` |
| team Lean/audit repository (link in the report title block) | 1033fb082aa0a82ffa4708411370434dc7d9fc23 | workstream B baseline: structure theory and Lean proof of the 1/72 energy gap (`supplementary/xinrui2.pdf`) |
| same | 4360b1a5bc0211dfd8ebfc6b650c500a29dca384 | workstream C audit code and evidence: native rerun, 27,188 root records, sharp phase-ball radius (`supplementary/fanghao.pdf`) |
| same | c9e269511be6e7b6a8e5e908668af236209d15f8 | workstream C worked-check source |
| dimension-ten working folder `mub10` | none: not under version control, so no commit hash exists | the list of 3,040 unimodular cyclic 10-roots (`data/exact/bu10hp_unimod.txt`) and `data/exact/d10_analysis.json`, read by `d10/check_d10.py` and `d10/energy10.py`; the derived files used here are copied into `d10/` (`vecs.npy`, `bases.json`, `energy10.json`, logs) |

Nothing from the team Lean/audit repository was rebuilt or rerun for this repository.
