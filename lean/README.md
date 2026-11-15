# Lean 4 project `MUB6Bridge` (repository root: `lakefile.toml`, `lean-toolchain`, `lake-manifest.json`, `MUB6Bridge/`)

Status: **builds** with Lean v4.35.0 and Mathlib tag v4.35.0 (revision 56a005855ea17e0b0958f73ec801ae140b0a1679),
no `sorry`, no `native_decide`, no axioms beyond `propext`, `Classical.choice`, `Quot.sound`
(`#print axioms` for every declaration is at the end of each file; output in `BUILD_LOG.txt`).

How it was built: locally by workstream A, from Mathlib sources (the Mathlib binary cache was not reachable from the
event workspace, so the files import only the Mathlib modules they need instead of `import Mathlib`). With the
cache available, `lake exe cache get && lake build` from the repository root should take a few minutes.
`BUILD_LOG.txt` is the log of a rebuild of all four project files (45 `#print axioms` lines); `BUILD_LOG_agent.txt` is the log of the helper
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
| `bridge_bias` | Theorem "From a vector to a basis", part (a), for orthonormal bases of C^6 | the Lean statement is: for every vector of the fourth basis there is a vector of the triple whose squared overlap with it deviates from 1/6 by at least sqrt(gamma/18). The word "bias" (largest deviation over all pairs of the four bases) is not defined in Lean; the statement implies the report's bound on it. Bases are orthonormal bases of `EuclideanSpace ℂ (Fin 6)`; the three bases are not assumed mutually unbiased, as in the report |
| `bridge_three_pairs`, `bridge_game` | Theorem "From a vector to a basis", part (b), for orthonormal bases of C^6 | none beyond the definition of `gameScore` above |
| `numbers_T0`, `numbers_T1` | the arithmetic of Corollary "Numbers for the two product triples" | arithmetic only: two inequalities between real numbers, with the certified values rounded down, 0.03849999999 and 0.02349999999 |
| `gameLoss`, `gameScore_le`, `gameLoss_nonneg` (file `Corollaries.lean`) | definition of the game loss, 1/2 + sqrt6/12 minus the game score; no four orthonormal bases score more than 1/2 + sqrt6/12 | none beyond the definition of `gameScore` |
| `corollary_of`, `corollary_T0`, `corollary_T1` | Corollary "Numbers for the two product triples", as an implication about bases | CONDITIONAL: the hypothesis "every unit vector has energy at least 0.03849999999 (0.02349999999) against the three bases" is an assumption of the Lean theorem. That the two product triples satisfy it is the output of the interval-arithmetic checker `cert/verify.py`, not a Lean fact. Conclusion: for each vector of the fourth basis some squared overlap deviates by more than 0.046248 (0.036132), and the game loss exceeds 3.302e-4 (2.015e-4) |
| `pearson_eq_collision`, `pearson_total` | the identity X^2 = 15 + 6(N-1)T (per setting: 5 + 6(N-1)(C - 1/6); `pearson_total` sums the three settings) | counts are real numbers summing to N in each setting; N not 0 or 1 |
| `zeta1_le_second_moment`, `second_moment_le`, `zeta2_le`, `three_halves_le` | four elementary steps of the variance bound in the proof of the finite-sample theorem: sum p^3 - (sum p^2)^2 <= sum p (p-1/6)^2 <= eps/6 + eps^(3/2); theta(1-theta) <= 1/4; a^(3/2)+b^(3/2)+c^(3/2) <= (a+b+c)^(3/2) | x^(3/2) is written x * sqrt(x); the quantities zeta_1, zeta_2 are NOT defined in Lean as covariances: the lemmas are inequalities between the algebraic expressions that the report's proof identifies with them. `second_moment_le` does not need the hypothesis that the probabilities sum to 1 |
| `shots_T0` (file `FiniteSample.lean`); `missBound`, `faBound`, `shots_of`, `shots_T0_95`, `shots_T0_99`, `shots_T0_half`, `shots_T1_95`, `shots_T1_99` (file `Corollaries.lean`) | the arithmetic of all five shot counts of Corollary "No pure state passes for white noise": (gamma, N, t) = (0.0384999, 1936, 0.38751), (0.0384999, 5142, 0.14579), (0.0384999, 2892, 1/2), (0.0234999, 3007, 0.40853), (0.0234999, 7687, 0.15978) | arithmetic only: `missBound` and `faBound` are the two closed-form expressions of the theorem; that they bound probabilities is not formalized. Minimality of each N is not formalized (it is computed by `hide_seek/finite_sample.py`) |

In one sentence. Lean-verified: the cap inequality, and the vector-to-basis theorem as inequalities about orthonormal
bases of C^6 with the game score defined by its formula, and the numerical corollaries as implications from an
assumed energy bound. Not Lean-verified: that the formula is the optimal success probability of the random-access
code (cited), the equality cases of the lemma, the energy bounds themselves (interval arithmetic, outside Lean), and
every probability statement.

Not formalized: every probability statement (the variance of the collision statistic, Cantelli's inequality), hence
the finite-sample theorem as a whole; the purity witness; the energy certificates; the dimension-ten theorem.
`Bases.lean` carries the vector-to-basis theorem from arrays to orthonormal bases of C^6 and is part of the built
project (it needs `Mathlib.Analysis.InnerProductSpace.PiL2`).

The analytic bound E > 1/72 is formalized in a different Lean project (workstream B, team Lean repository), which
was not rebuilt here.
