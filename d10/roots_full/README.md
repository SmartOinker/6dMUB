# Cyclic 10-roots: regenerated and certified list (workstream A re-verification)

Purpose: make reproducible the step "the other 31,900 roots of the cyclic 10-roots system are not unimodular"
used in the conditional theorem (no four MUBs of C^10 contain I and F_10).

## What running the two scripts proves
System: x in (C*)^10, x_0 = 1, g_k(x) = sum_j x_{j+k}/x_j = 0 (k = 1..9) (equivalent to cyclic 10-roots via z_j = x_{j+1}/x_j).

`certify_roots.py` (Arb, 128 bits, box half-width 2^-30*max(1,ceil|c|) <= 5.8e-8 per real/imag part, centred at the stored complex128 midpoints) proves:
1. Each of the 34,940 boxes contains exactly one root (Krawczyk, certified strict inclusion).
2. The 34,940 boxes are pairwise disjoint (sort by Re x_1, window test in float64 with margin, exact rational fallback; argument in the docstring; no fallback was needed). Hence **at least 34,940 distinct roots**, all nonsingular.
3. **Exactly 3,040 of them are unimodular** (|x_j| = 1 for all j), by the fixed-point argument for sigma(x) = 1/conj(x) (sigma maps roots to roots; sigma(K) inside the box forces sigma(root) = root).
4. **The other 31,900 are certified NOT unimodular**: for each, some |x_j| enclosure excludes 1.
5. The 3,040 unimodular boxes coincide with the stored list `upstream_mub10/data/exact/bu10hp_unimod.txt`: every stored point (40 digits) lies strictly inside one of the certified unimodular boxes, the 3,040 boxes hit are distinct, and no other box is unimodular. (Combined with `../check_d10.py`, which certifies each stored point is within 1e-30 of a unique root, this matches them rigorously.)

Final numbers: found 34,940; certified 34,940; unimodular 3,040; certified non-unimodular 31,900; undecided 0; Krawczyk failures 0.

## What is NOT proved
- That there are no further roots. "34,940 is all of them" still rests on hypothesis (H) (cited upper bound 34,940 on the number of solutions of cyclic-10, Faugere via Fuhr-Rzeszotnik). Without (H) only BKK (cited mixed volume 35,940, not recomputed here) leaves up to 1,000 unaccounted isolated roots; positive-dimensional components are also not excluded by this computation.
- `find_roots.py` is heuristic (not part of the proof); only the certificates in `certify_roots.py` count. The numerical symmetry checks there are sanity checks, not proofs.
- The 34,940 total was reached in the search without prior knowledge of the orbit structure, and the figure matches (H) exactly; this is consistent with, but is not a proof of, completeness.

## Files
- `find_roots.py`: random Newton (x- and log-coordinates), closure under the symmetry group of order 1600 (dilations by units 1,3,7,9; inversion; conjugation; shift; modulation), each generator checked numerically first (residuals ~1e-15).
- `certify_roots.py`: the certifier. `cyclic10_roots.npz` (1.8 MB): midpoints `x1_to_x9` (complex128; x_0 = 1), status codes (1 unimodular, 2 non-unimodular, 0 undecided, -1 failed), max K deviation, index of matching stored point.
- `run.log`, `growth_run1_sigma0.4-1.log`, `growth_run2_sigma2-4.log`: logs (count against starts).

## Commands (from this folder; 2 shared cores)
    SIGS=2.0,3.0,4.0 nice -n 10 python3 find_roots.py 900 2 roots_found.npy      # ~100 s: 34,940 roots after 56,000 starts
    nice -n 10 python3 certify_roots.py roots_found.npy cyclic10_roots.npz ../upstream_mub10/data/exact/bu10hp_unimod.txt 2   # ~35 s
Re-verification from the shipped data only: `python3 certify_roots.py cyclic10_roots.npz out.npz ../upstream_mub10/data/exact/bu10hp_unimod.txt 2` (~35 s).

## Search log notes
- Run 1 (default sigmas 0.4/0.7/1.0, seed 1) stalled at 33,940 roots for 100k+ starts (later 34,340): moderate starting radii miss some orbits.
- Run 2 (sigmas 2/3/4, seed 2) found 34,740 after the first batch and 34,940 after 56,000 starts (99 s). Root count is after closure under the group (1,600 images per newly found root), keys rounded to 1e-6; the certifier independently proves distinctness.
- Total wall time for everything here is well inside the 60-minute box.
