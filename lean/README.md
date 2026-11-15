# Lean 4 project `MUB6Bridge` (repository root: `lakefile.toml`, `lean-toolchain`, `lake-manifest.json`, `MUB6Bridge/`)

Status: **builds** with Lean v4.35.0 and Mathlib tag v4.35.0 (revision 56a005855ea17e0b0958f73ec801ae140b0a1679),
no `sorry`, no `native_decide`, no axioms beyond `propext`, `Classical.choice`, `Quot.sound`
(`#print axioms` for every declaration is at the end of each file; output in `BUILD_LOG.txt`).

How it was built: locally by workstream A, from Mathlib sources (the Mathlib binary cache was not reachable from the
event workspace, so the files import only the Mathlib modules they need instead of `import Mathlib`). With the
cache available, `lake exe cache get && lake build` from the repository root should take a few minutes.
`BUILD_LOG.txt` is the log of a full rebuild of the project files; `BUILD_LOG_agent.txt` is the log of the helper
agent that repaired the proof scripts (statements were frozen before the repair and compared afterwards).

## Declarations, the claim each supports, and the differences

| declaration (namespace `MUB6Bridge`) | claim in the report | difference between the Lean statement and the report |
|---|---|---|
| `cstar`, `cstar_pos`, `cstar_eq` | the constant c* = 3 sqrt6/(sqrt6+1)^2 = (21 sqrt6 - 36)/25 | none |
| `sqrt_le_quadratic_cap` | Lemma "A quadratic cap on the square root" (the inequality on [0,1]) | the "equality exactly at p = 1/6 and p = 1" part is not formalized |
| `bias_bound` | Theorem "From a vector to a basis", part (a) | stated for 18 real numbers with sum of squared deviations at least gamma |
| `pair_sum_bound` | the pair-sum inequality in the proof of part (b) | stated for a 6 x 6 real array with entries in [0,1] and total 6 |
| `game_bound` | part (b) for the three pairs (triple basis, fourth basis) | array form |
| `energy`, `pairSum`, `gameScore` (file `Bases.lean`) | definitions: energy of a vector against three orthonormal bases of C^6; sum of the 36 overlap moduli of two bases; score of the four-basis game | the game score is DEFINED by the formula 1/2 + (1/72) x (average of the pair sums over the six pairs); that this formula is the optimal success probability of the random-access code is cited in the report, not formalized |
| `sq_overlap_le_one`, `sq_overlap_row_sum`, `sq_overlap_total`, `pairSum_le` | squared overlaps lie in [0,1]; Parseval; the 36 squared overlaps sum to 6; any pair of bases has pair sum at most 6 sqrt6 | none |
| `bridge_bias` | Theorem "From a vector to a basis", part (a), for orthonormal bases of C^6 | none (bases are orthonormal bases of `EuclideanSpace ℂ (Fin 6)`; the three bases are not assumed mutually unbiased, as in the report) |
| `bridge_three_pairs`, `bridge_game` | Theorem "From a vector to a basis", part (b), for orthonormal bases of C^6 | none beyond the definition of `gameScore` above |
| `numbers_T0`, `numbers_T1` | Corollary "Numbers for the two product triples" | uses the certified values rounded down, 0.03849999999 and 0.02349999999 |
| `pearson_eq_collision` | the identity X^2 = 15 + 6(N-1)T (per setting: 5 + 6(N-1)(C - 1/6)) | counts are real numbers summing to N; N not 0 or 1 |
| `zeta1_le_second_moment`, `second_moment_le` | the bound zeta_1 <= eps/6 + eps^(3/2) in the proof of the finite-sample theorem | eps^(3/2) is written eps * sqrt(eps); the second lemma does not need the hypothesis that the probabilities sum to 1 |
| `shots_T0` | Corollary "No pure state passes for white noise": N = 1,936, t = 0.38751 give bounds 5% and 0.1% | arithmetic only |

Not formalized: every probability statement (the variance of the collision statistic, Cantelli's inequality), hence
the finite-sample theorem as a whole; the purity witness; the energy certificates; the dimension-ten theorem.
`Bases.lean` carries the vector-to-basis theorem from arrays to orthonormal bases of C^6 and is part of the built
project (it needs `Mathlib.Analysis.InnerProductSpace.PiL2`).

The analytic bound E > 1/72 is formalized in a different Lean project (workstream B, team Lean repository), which
was not rebuilt here.
