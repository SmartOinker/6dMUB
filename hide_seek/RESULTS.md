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
  closed-form minimum-energy state of xinrui.pdf eq. (20). Outcomes in the unused level are discarded.
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
