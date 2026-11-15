# Verification ledger

One row per result. Workstream A: this repository (certificates, bridge inequalities, hide and seek, near-misses,
dimension ten, mutation test). Workstream B: structure theory and Lean. Workstream C: explanatory audit.
"Re-run 15 Nov" means the command was executed again while this repository was assembled (see README.md for
outputs and runtimes).

Status vocabulary: proved / Lean-checked as reported / interval-certified / computed / numerical only / cited /
conditional / unproved.

Setup: T0 is the canonical product triple U_r = A_r (x) B_r; T1 the second product triple (third basis
|0_y> (x) DF, |1_y> (x) D^2 F; arXiv:2410.23997 eq. 7.19). E(psi) = sum over the 18 outcomes of (p - 1/6)^2.

| # | result | workstream | what was run | outcome | status | path |
|---|---|---|---|---|---|---|
| 1 | E >= 0.0385 for every unit psi, triple T0 | A | Arb interval checker `verify.py` on the 364x364 Gram matrix (re-run 15 Nov) | PD Gram (Cholesky defect 9.6e-15 against tau = 1e-5), residual S <= 2.2e-12; E > 0.038499999998 | interval-certified | `cert/verify.py`, `cert/Q_T0_gamma0.0385.npy` |
| 2 | E >= 0.0235 for every unit psi, triple T1 | A | same checker (re-run 15 Nov) | residual S <= 2.8e-12; E > 0.023499999997 | interval-certified | `cert/verify.py`, `cert/Q_T1_gamma0.0235.npy` |
| 3 | energy identity (Lemma 3.1), witness state, minimum on T0 | A, checking B | 2,000 random states; witness evaluated; 400 minimisations (re-run 15 Nov) | identity error 8.9e-16; witness E = (4 - sqrt6)/40 to 7e-17; all 400 starts reach 0.0387628 | numerical only (exact minimum is cited prior work, Zenodo doi 10.5281/zenodo.20670933) | `checks/check1.py` |
| 4 | numerical minimum on T1 = 0.0238354 | A | 300 BFGS starts (re-run 15 Nov) | 0.023835355 | numerical only | `checks/check3.py` |
| 5 | square-root inequality sqrt p <= 1/sqrt6 + (sqrt6/2)(p - 1/6) - c (p - 1/6)^2 on [0,1], c = 3 sqrt6/(sqrt6+1)^2 | A | algebraic proof; 1.8M random distributions (earlier session) | no violation | proved (numerical check agrees) | proof in report; the 1.8M-sample script is not in this repository. `checks/check2.py` checks a related summed form on 200,000 distributions (min slack 2.9e-5) |
| 6 | bias and game bounds for any fourth basis | A | from rows 1, 2, 5; printed by `verify_sets.py` (re-run 15 Nov) | T0: bias > 0.046248, game loss > 3.302e-4. T1: bias > 0.036132, game loss > 2.015e-4 | proved (conditional only on rows 1, 2, which are interval-certified) | `cert/verify_sets.py` |
| 7 | explicit four-basis sets | A | Arb interval evaluation with polar-factor correction (re-run 15 Nov) | `bases_d6_delta.npy`: bias <= 0.030223872; `bases_d6_P4.npy`: game loss <= 2.357825e-4 | interval-certified | `cert/verify_sets.py`, `near_misses/repo/results/visibility/bases_d6_*.npy` |
| 8 | design lesson: best four bases are not a completion of a perfect local triple | A | comparison of rows 6 and 7 | holds for T0 on both measures and for T1 on bias; T1 game comparison inconclusive (2.015e-4 < 2.358e-4) | proved where stated | as rows 6, 7 |
| 9 | hide and seek: 239 shots per setting (99% detection, 0.1% false alarm); 589 total at 5 sigma; 1,500 at 10% gate error | A | Qiskit/Aer simulation and chi-square formula (not re-run 15 Nov; output data included) | as stated | computed (asymptotic chi-square plus Monte Carlo; not a finite-sample theorem) | `hide_seek/hide_seek.py`, `hide_seek/hide_seek.json`, `hide_seek/RESULTS.md` |
| 10 | 2008-table near-misses {5,4,4,1} and {5,5,3,1} | A | certificate `certify.py` rerun (re-run 15 Nov) + own 60-digit evaluation `indep.py` (re-run 15 Nov) | all tests pass; misfits 1.02497683851953e-3 and 7.32788656303688e-4 | interval-certified (one strict local minimum each) | `near_misses/repo/src/constellations/certify/certify.py`, `near_misses/indep.py`, `near_misses/repo/results/constellations/certified/` |
| 11 | {5,3,3,3} found once in 20,000 starts | A | record read | one hit in the stored log | computed (record read only, not re-run) | `near_misses/repo/results/constellations/extra/random_333_seed11_20000starts.jsonl` |
| 12 | E > 1/72 on T0, analytic | B | proof read; Lean build NOT run by us | as reported | Lean-checked as reported (workstream B, revision 1033fb08) | `supplementary/xinrui2.pdf` |
| 13 | cube-rank counts [1,30,135,120,60,12] and 1,395 systems | B, reproduced by A | own enumeration (re-run 15 Nov, output identical to log) | counts match; k=1: 60, k=2: 120 = 112 + 8, k=3: 1215 = 1160 + 54 + 1 | computed (exact enumeration, floating rank) | `checks/check2.py`, `checks/check2.log` |
| 14 | degree-four SOS optimum 0, pseudomoment rank 63 | B, reproduced by A | own SDP (re-run 15 Nov) | optimum -2.1e-8, numerical rank 63 | numerical only (B's exact statement: as reported) | `checks/sos.py` (`python3 sos.py 4`) |
| 15 | degree-six SOS relaxation reaches 99% of the minimum | A | own SDP, SCS at eps 2e-4 and 1e-5 (logs) | 0.0383286 and 0.0386693 | numerical only (row 1 is the rigorous version) | `checks/sos.py`, `checks/sos6.log`, `checks/sos6_tight.log` |
| 16 | dimension ten: 3,040/3,040 vectors Krawczyk-certified unimodular roots; 57,680 possibly-orthogonal pairs; 1,136 ten-cliques; margin 4.17807 (0.0418 in probability) | A | own Krawczyk code and clique enumeration (earlier session; not re-run 15 Nov) | as stated | interval-certified for the listed vectors | `d10/check_d10.py` |
| 17 | no four MUBs contain {I, F_10} | A | rows 16 + hypothesis (H) that the cited list of 34,940 cyclic 10-roots is complete | follows from (H) | conditional (H NOT verified) | `d10/` |
| 18 | independent search: 1.2M starts, 1,199,148 converged, 0 off the list | A | batched Levenberg-Marquardt (log; not re-run 15 Nov) | all 3,040 hit, worst match 1.1e-9 | numerical only (evidence for H, not a proof) | `d10/search_match.py`, `d10/search_match.log`, `d10/search_1p2M.log` |
| 19 | sharp phase-ball radius s* = sqrt6 arccos(1/sqrt6)/(4 pi) = 0.2242139 | C | proof read; numerics agree to 5 digits | as reported | proved (proof read) | `supplementary/fanghao.pdf` |
| 20 | full native rerun of the 2026 pipeline, 27,188 root records re-certified in 128-bit Arb | C | NOT re-run: reported by workstream C, commit 4360b1a5 | as reported | cited (reported by workstream C) | `supplementary/fanghao.pdf` |
| 21 | checker mutation test, 17 of 26 mutations detected | A | record read only | 17/26 | computed (record read only) | `near_misses/repo/results/openai_check/mutations.json`, `NOTES.md` |
| 22 | universal step (residual-product vanishing on all compatible triples) | B | none | open | unproved | `supplementary/xinrui2.pdf` |
| 23 | dimension-six Fourier pair {I, F_6}: 16 third bases, numerical minima 0.0326759 / 0.0238354 / 0.0387628 | A | `fourier6.py` done; certificates `run_fourier6_certs.py` in progress, results not yet in this repository | pending | numerical only | `d6_fourier/` |

## Not verified

- Lean build of workstream B (including the 1/72 bound, row 12): not run by us.
- Full native rerun and the 27,188 root records of workstream C (row 20): not re-run; reported by workstream C.
- Completeness of the cited list of 34,940 cyclic 10-roots, hypothesis (H) (row 17): not verified.
- Mutation test 17 of 26 (row 21) and {5,3,3,3} once in 20,000 (row 11): records read, not re-run.
- Certificates for the 16 Fourier-pair triples in dimension six (row 23): not finished at the time of writing.
- The 1.8M-sample check of the square-root inequality (row 5): script not included here (the inequality itself is proved).
