# Independent re-verification scripts (workstream A), structure-paper statements of workstream B/C

All scripts are numerical checks in double precision (not proofs) except `check_quartic_sos.py`, which is exact
arithmetic over Q(sqrt3) for one concrete functional. Run each with `nice -n 5 python3 <script>`; logs in `logs/`.
Each script ends by printing `OK` or raises.

| script | claim checked | range | result | runtime |
|---|---|---|---|---|
| `check_sixphase.py` | z_j unimodular, sum z_j = sqrt6 implies abs(sum z_j^3) <= 7 sqrt6/3 = 5.7154760665; equality at 3 x (1+i sqrt5)/sqrt6 and 3 x conjugate | 4,000 SLSQP random starts (3,998 feasible), about 300,000 exactly feasible random points, extremal configuration in 50-digit mpmath | largest value found 5.7154760665 (gap to bound -4e-15, i.e. attained); 445 starts reach the bound; other local maxima 5.2303, 4.9240, 4.3732; random feasible points at most 5.6120; extremal configuration feasible and equal to the bound to 1e-50. Matches source (Theorem 12.3) and report | 41 s |
| `check_hadamard_identities.py` | identities V*V = 18I + M*M/3 (all H), Fourier condition eq:fourier27 and B o K = 24I - K (non-Tao H), cap norm(M)^2 <= 18, tr((M*M)^2) <= 648 with equality iff rank 2, rank >= 2, cube rank two iff Fourier/transposed/Tao | 60 Tadej-Zyczkowski F6(a,b), 60 of the report's family H(z), their transposes, 30 random equivalents, Tao S6 (+20 equivalents), Dita D6, 700 numerically found Hadamard matrices (Gauss-Newton from random starts, defect < 1e-11; 127 of them cube rank 1 with Tao's equivalence invariant, 573 cube rank 6), 100 random equivalents of the generic ones | Max violations: V*V identity 5e-14 on every family including Tao; eq:fourier27 and B o K identity <= 6e-14 on every non-Tao family; on Tao S6 they FAIL as expected and are not claimed (fourier27 violation 3.0, BK violation 6.0, norm(M)^2 = 36, tr = 1296, M all ones). Largest norm(M)^2 over non-Tao matrices 18.0000 (Fourier family, equality) and 17.998 (generic); tr = 648 exactly on the cube-rank-2 families. Cube ranks: F6, transpose, H(z): 2; Tao: 1; Dita D6: 6 (norm(M)^2 = 6); generic non-Tao: 6. No discrepancy | 10 s |
| `check_gap72.py` | Lemma lem:energyid, Steps 1-4 of A.3, rational comparisons, E > 1/72, min E >= 0.0385, total-variation and distinguishing bounds | 200,000 Haar unit vectors; 200,000 targeted states satisfying the premises s <= 1/72, abs(a)^2 <= 1/12; exact Fractions; 200 BFGS minimizations | Energy identity error 1.6e-15 (also its Parseval sub-identities and sum abs(q_r)^2 = 3s); all premise-free step inequalities hold; on premise states the conclusions n_h < 9/200 (max 0.0425), n_i n_j > 3999/20000 (min 0.2029), abs(m)^2 > (31/50)^2 (min 0.4054), abs(R)^2 < (83/200)^2 (max 0.1074), abs(t) > 41/200 (min 0.3575), E > 1681/120000 all hold; exact fractions confirmed; min E over 200 starts 0.0387627564 = (4 - sqrt6)/40, all 200 starts reach it; min over Haar samples 0.0677; total variation: min over samples of max_b TV = 0.1675 > 0.0481125, success >= 0.5838 > 0.524056, some outcome deviates by >= 0.106 > 1/36; at minimizers max_b TV >= 0.1150, deviation >= 0.0575. No discrepancy | 26 s |
| `check_phase_ball.py` | phase-ball radius s* = sqrt6 arccos(1/sqrt6)/(4 pi) = 0.2242139: no orthogonal or MU pair in one ball below s*; MU pair at s*; proof ingredients | s* in 40 digits and chain of inequalities; 175,000 random/antipodal pairs; SLSQP minimization of abs(S) with 300 starts at 6 radii; witness in 40 digits; convexity of cos(sqrt u) on a 2,000,001-point grid; 200,000 Jensen tests | s* = 0.22421389884043780; witness squared overlap 1/6 (error 1e-41); minimum of abs(S) equals 6cos(4 pi s/sqrt6) to 4e-8 and exceeds sqrt6 for s < s*; at s* it equals sqrt6 (to 1e-8), and at s* + 1e-3 it is 2.4214 < sqrt6, so the radius is sharp; f'' >= 0.0253 on (0, pi]. No discrepancy | 125 s |
| `check_quartic_sos.py` | Proposition prop:quartic: pseudomoment matrix PSD of exact rank 63, L(E_hom) = 0, L(N^2) = 1 | exact over Q(sqrt3), one concrete functional (`quartic_L_moments.json`, 1,365 moments, built by `build_quartic_functional.py`) | 1,404 equations M c_l = 0 hold exactly; L(N^2) = 1 and L(E_hom) = 0 exactly; exact LDL^T has 63 strictly positive pivots and an exactly zero 15x15 Schur block; exact rank of the 18 quadratics is 15 and rank M + 15 = 78, so kernel M = span of the deviation quadratics. The source does not print its 342 moments, so this is an independent reconstruction (693 nonzero moments), not a check of that file; the source's moments, its sparsity (342) and its claim of rank 63 over Q(sqrt3) remain unverified directly, but our functional shows the claimed properties are attainable with exactly rank 63 | 12 s (builder 35 s, float SDP heuristic plus exact solve) |

## Further audit scripts (added with `docs/verification_matrix.md` and `verify_all.sh`)

Written separately from the programs they check; each prints `OK` as its last line. Claim ids refer to `docs/verification_matrix.md`.

| script | claim checked | runtime |
|---|---|---|
| `check_cert_pointwise.py` | second implementation of the degree-six identity for T0, T1 and the 16 Fourier-pair Gram matrices, at 4,000 random points (C25, C36) | 2 s |
| `check_report_arithmetic.py` | recomputation of derived numbers (bridge numbers, finite-sample shot counts N = 1936 / 5142 / 3007 / 7687 and 2892, 239 / 198 / 369, noise totals, game rounds) and comparison of stored results with the report (C9, C12, C32, C35, C40, C43, C47 to C52, C60, C61) | 2 s |
| `check_bridge_theorem.py` | vector-to-basis theorem on 5,000 Haar bases, stored four-basis sets via the polar factor, dimension-four control (C31, C33, C34, C46) | 33 s |
| `check_minimiser.py` | closed-form minimiser in 50 digits and own minimisations on T0 and T1 (C27, C28) | 6 s |
| `check_sqrt_lemma.py` | square-root lemma on 1.8 million points and a grid (C30) | 2 s |
| `check_fourier6_graph.py` | Fourier funnel 156 -> 48 -> 16 -> 0 in floating point, own Newton search and graph code (C14, C15, C16, C37). The ball-arithmetic counterparts are `../d6_fourier/certify_d6_roots.py`, `certify_graph.py` and `check_partial_bases.py` (C14, C15, C16, C53) | 34 s |
| `check_d10_float.py` | dimension ten in float64: unimodularity, 57,680 edges, clique sizes, 1,136 bases, margin 4.17807 (C56, C57) | 1 s |

## Where the other checks live

The scripts that check the Fourier pair in ball arithmetic are in `../d6_fourier/` (`certify_d6_roots.py`, `certify_graph.py`,
`check_partial_bases.py`), those that check the 2008-table numbers against the raw search output are in `../near_misses/`
(`check_table.py`, `check_visibility_records.py`). The scripts in this folder are numerical (double precision) unless a row says exact.
Measured runtimes in the tables above are from different sessions on a shared 2-core machine; the authoritative recent ones are in
`../docs/verify_all.log`. Expected-output lines are in `../verify_all.sh` and `../docs/verification_matrix.md`.

## Notes
- `build_quartic_functional.py` uses a floating-point SDP (Clarabel) only to choose a strictly interior point
  (minimum eigenvalue 2.5e-3 on the 63-dimensional complement of the kernel) and then solves the linear constraints exactly over
  Q(sqrt3) (rational rounding of 320 free moments at denominator 10^9). Correctness rests entirely on the exact
  verification in `check_quartic_sos.py`.
- Trust base of the exact check: Python Fractions, sympy (for the exact projectors) and the hand-written Q(sqrt3) arithmetic.
