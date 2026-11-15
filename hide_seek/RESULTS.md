# Hide and seek: can a pure state look like white noise to three local MUB measurements?

Code: `hide_seek.py` (simulation), `fig.py` (figure). Data: `hide_seek.json`. Figure: `fig3_hide_seek.png` (panels also as `fig3a_`, `fig3b_`).
Conventions follow `src/visibility/t5_sim.py`: circuits transpiled to {cx, u}; depolarising error r on cx and r/10 on u;
exact outcome probabilities from Aer's density-matrix method; shot noise by multinomial sampling; fixed seeds.
A simulator repeats linear algebra and proves nothing. Its role is to turn the certified energy bound into shots and gate-error requirements.

## Setup
- Hider: prepares the pure state hardest to tell from white noise. Referee: N shots in each of the three settings, then
  Pearson's chi-square test for uniformity (3(d-1) degrees of freedom, false-alarm rate 0.1%).
- The test statistic is shifted by d*N*E, where E = sum over outcomes of (p - 1/d)^2. So E is the detectability per shot,
  and the minimum-energy state is the best hider.
- d = 6: one qubit plus a qutrit stored in two qubits (level 11 unused). Settings: the canonical product triple. Hider: the
  closed-form minimum-energy state of the structure paper (first version) eq. (20). Outcomes in the unused level are discarded.
- d = 4: two qubits, settings ZZ, XX, YY. Hider: (1, 1, i, -i)/2, which is exactly uniform in all three.

## Results
| claim | value | how supported |
|---|---|---|
| d=6 measurement circuits need no gate between qubit and qutrit | cx per setting: [0, 3, 3] (inside the qutrit's two qubits) | transpiled circuits |
| d=6 preparation plus measurement | cx per setting: [4, 7, 7] | transpiled circuits |
| noiseless circuits reproduce the exact probabilities | max deviation 5.3e-16 (d=6), 2.2e-16 (d=4) | simulation |
| per-shot sampling agrees with the exact probabilities | worst cell 1.8 sigma (no noise), 1.9 sigma (1% gate error), 200,000 shots per setting | simulation |
| referee's false-alarm rate on exactly uniform data (target 0.001; N = 10, 30, 100, 1000) | d=6: 0.00094, 0.00085, 0.00100, 0.00093; d=4: 0.00057, 0.00080, 0.00108, 0.00097 | Monte Carlo, 200,000 trials each |
| d=6 best hider: energy, largest single-outcome bias | 0.0387628, 0.0575 | exact formula |
| d=4 hider: energy | 9.9e-32 at every noise level tried | exact formula and simulation |
| d=4 hider is never caught | detection rate stays at the false-alarm rate up to 1,000 shots per setting | Monte Carlo, 20,000 trials per point |
| any pure state against the canonical triple: shots per setting for 99% detection at 0.1% false alarm | 239 | certified E >= 0.0385 plus chi-square approximation |
| same, at 5 sigma false alarm: 50% / 99% detection | 198 / 368 per setting | certified E >= 0.0385 plus chi-square approximation |
| guessing game, for comparison | 9.37e+07 rounds at 5 sigma; gate noise costs more than the gap beyond 1.16e-05 (2.03e-05 fused) | recomputed from bases_d6_P4.npy and sim.json |

## Noise scan, d = 6 best hider
| two-qubit error rate | E | largest bias | discarded fraction | total shots, 5 sigma (50% detection) |
|---|---|---|---|---|
| 0 | 0.03876 | 0.0575 | 0.0000 | 589 |
| 0.0001 | 0.03873 | 0.0575 | 0.0001 | 589 |
| 0.001 | 0.03841 | 0.0574 | 0.0014 | 594 |
| 0.01 | 0.03534 | 0.0562 | 0.0133 | 646 |
| 0.1 | 0.01521 | 0.0450 | 0.1069 | 1500 |

## Limits
- The certified floor is for pure states and the canonical product triple. Noise acts on the hider's side: a mixed state can hide,
  and the maximally mixed state hides perfectly. The scan shows how much gate noise the best pure hider needs before it does.
- Depolarising noise is unbiased. Real devices have biased readout, which fakes non-uniformity; an experiment needs a calibration
  run on white noise.
- Detection probabilities use the large-N chi-square form for the certified curve; the simulated points are Monte Carlo.
- The game comparison is between two different claims. The game is about every set of four bases; hide and seek is about one triple.

## Update, 15 November 2026

The text above is kept as written. Four things have changed since it was written.

1. **A finite-sample theorem now exists.** `finite_sample.py` (log: `finite_sample.log`) proves and checks a collision-statistic test with Cantelli bounds
   that uses no large-sample approximation. For the canonical triple (certified E > 0.0384999) the smallest N for which some threshold meets both
   error bounds is N = 1,936 (t = 0.38751; detection at least 95%, false alarm at most 0.1%) and N = 5,142 (t = 0.14579; detection at least 99%,
   false alarm at most 0.1%). For the second product triple and the 16 Fourier-pair triples (E > 0.0234999) the numbers are N = 3,007 (t = 0.40853)
   and N = 7,687 (t = 0.15978). With the unoptimised threshold t = 1/2 the same bounds need N = 2,892 and N = 14,957 for the canonical triple.
   The variance formula is checked exactly by enumeration for N = 2, 3, 4, and the Monte Carlo at N = 1,936 had no missed detection and no false alarm
   in 20,000 runs each. `checks/check_report_arithmetic.py` recomputes all of these shot counts and thresholds independently.
2. **The 239 / 198 / 369 shot counts are a large-sample approximation, not a theorem.** They come from a noncentral chi-square model of Pearson's
   statistic and are slightly optimistic below about N = 100 (model 0.108 against simulation 0.098 at N = 50). For a guaranteed detection use the
   finite-sample numbers of item 1. The 239 shots remain the practical figure.
3. **Correction to the table above.** The row "5 sigma false alarm: 50% / 99% detection" reads 198 / 368. The unrounded value is 368.07, so the correct
   rounded-up figure is **369** shots per setting (198: 197.54; 239: 238.79; all rounded up).
4. **The dimension-four control was run further than stated above.** The sentence "never caught up to 1,000 shots per setting" holds, and the stored
   data in `hide_seek.json` (and the report) extend it to 5,000 shots per setting.

Also new: `check_purity_witness.py` (log `check_purity_witness.log`) tests the purity witness (uniform statistics force the largest eigenvalue of the
state to be at most 0.8232) on 100,000 random states. The exact bound is 0.82308. `hide_seek.py` was not re-run for this update (it needs Qiskit and
a Monte Carlo run); the stored output `hide_seek.json` is unchanged.
