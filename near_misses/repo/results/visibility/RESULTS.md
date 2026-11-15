# Visibility of a missing 4th MUB in C^6 (2-to-1 QRAC)

All optimisation numbers are numerical lower bounds on the optimum: the true optimum is at least this; nothing here proves an upper bound. Scripts in src/visibility (common.py, t1_t2_checks.py, t3_optimise.py, t5_sim.py, t4_stats_figs.py); fixed seeds.

| claim | value | how supported |
|---|---|---|
| P(E,F)=1/2+(1/2d^2) sum abs<e_i|f_j> | matches brute force, err < 7e-16 (d=3,6) | exact formula |
| d=5,7: any 4 of the d+1 MUBs give P_4 = 1/2+1/(2 sqrt d) | dev < 1.2e-16 | explicit construction (checked to 1e-12) |
| d=6: 3 MUBs (qubit x qutrit) reach P_3 bound | dev 0 | explicit construction (checked to 1e-12) |
| d=6 MUB value 1/2+1/(2 sqrt6) | 0.7041241452 | exact formula |
| d=6 best P_4 found (700 starts, random and 3-MUB seeded) | 0.7038883627 | numerical optimisation (lower bound only) |
| gap to MUB value | 2.358e-4 | numerical optimisation (lower bound only) |
| best set = 3 pairs at 0.7041241452 + 3 pairs at 0.70365258 | | numerical optimisation (lower bound only) |
| literature P_4 0.703888 | reproduced (diff < 1e-6) | cited |
| best mean D^2, d=6, n=4 | 0.9982917 | numerical optimisation (lower bound only) |
| literature D^2 0.99829 | reproduced | cited |
| optimiser finds MUB value, d=5 (200 starts) / d=7 (200 starts) | diff 3e-16 / 0 | numerical optimisation |
| N rounds for 3 sigma / 5 sigma (N=z^2 p(1-p)/Delta^2) | 3.4e7 / 9.4e7 | exact formula |
| N, both hypotheses z sigma from threshold | 1.3e8 / 3.7e8 | exact formula |
| depolarising budget eps=(P_MUB-p_best)/(P_MUB-1/d) | 4.4e-4 | exact formula |
| 3-qubit transpiled circuits, two-qubit gates (cx+u) | mean ~33 (max 38) separate prep/measure; 19 fused | simulation |
| noiseless Aer reproduces P_4 d=5,6,7 | to 1e-13 | simulation |
| 2-qubit depolarising rate at which noise deficit = d=6 gap | 1.2e-5 (separate), 2.0e-5 (fused) | simulation |
| shot noise 1 sigma at N=1e6 / 1e8 | 4.6e-4 / 4.6e-5 | simulation |

Notes
- D^2 is a property of the bases, not an observable game probability; its gap (1.7e-3) has no direct round-count.
- Shot noise: sampled from exact per-setting probabilities (multinomial over all 6 pairs x d^2 x 2 settings, then binomial); no per-shot circuits.
- Noise: Aer density-matrix, 200 fixed-seed sampled settings per d, exact probabilities; P_4(noisy) = exact P_4 minus mean paired deficit. Rates 1e-6..1e-2 (two-qubit; one-qubit 10x smaller). Deficit is about 20 x rate (separate) regardless of d.
- The 1e-4 and 1e-3 results: deficits 2e-3 and 2e-2, far above the gap.

## Worst-case bias delta = max |<e_i|f_j>|^2 - 1/6| (d=6, four bases)
Numerical upper bound on the minimum: explicit bases achieve this delta; nothing proves a lower bound. Code: t7_delta.py, t7_assemble.py. Bases: bases_d6_delta.npy/.json.

| claim | value | how supported |
|---|---|---|
| smallest delta found (72 starts: random, star, 3-MUB+random, saved sets) | 0.030224 | numerical optimisation (upper bound on min only) |
| six per-pair maxima | all 0.030224 (equal to 1e-14) | numerical optimisation |
| active overlaps (within 1e-6 of max) | 132 of 216 | numerical optimisation |
| structure | spread over all six pairs; no exactly unbiased pair | numerical optimisation |
| P_4, D^2 of that set | 0.703506, 0.995201 | exact formula |
| best delta with exact MUB triple fixed (40 starts) | 0.07983 (triangle-type) | numerical optimisation |
| calibration d=5 / d=7 random starts | 8.6e-16 (221/364 starts below 1e-9) / 1.4e-15 (16/2144) | numerical optimisation |
| shots, one setting, 1/6 vs 1/6 +- delta at 5 sigma | about 3.8e3 (about 545 for fixed-triple 0.0798) | exact formula |

The P_4-optimal and D^2-optimal sets are not delta-optimal. d=7 calibration succeeds in under 1% of random starts, so the d=6 minimum could be missed by a similarly small basin; 4 of 9 start families and random starts agree on 0.030224, one family stops at 0.030237 (a nearby local optimum).
