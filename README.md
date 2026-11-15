# Mutually unbiased bases in dimension six: codebase behind the report

Caltech x SAIR Mathathon, Problem 124. This repository holds the scripts, certificates, data and logs behind the
report: degree-six sum-of-squares energy certificates for the two product MUB triples in C^6, the vector-to-basis
bounds and their check against explicit four-basis sets, the hide-and-seek detection simulation, the rerun of the
2008-table near-miss certificate, and the conditional dimension-ten result. The status of every result is in
`docs/verification_ledger.md`. Upstream sources and commit hashes are in `docs/UPSTREAM.md`.

## Directory map

| path | content |
|---|---|
| `cert/` | degree-six SOS energy certificates (Gram matrices `Q_T0_*.npy`, `Q_T1_*.npy`), Arb checker `verify.py`, `verify_sets.py`, search script `build.py` (not part of the proof) |
| `checks/` | `check1.py` (energy identity, witness, minimum), `check2.py` (cube-rank counts, game numerics), `check3.py` (second triple, thresholds), `sos.py` (moment relaxations, degree 4 and 6); logs `check2.log`, `sos6.log`, `sos6_tight.log` |
| `hide_seek/` | Qiskit/Aer simulation `hide_seek.py`, `fig.py`, data `hide_seek.json`, `RESULTS.md`, figures `fig3*.png` |
| `hide_seek/rehearsal_fake_backend/` | hardware kit rehearsed on a fake-backend noise model only; not evidence (see its README) |
| `near_misses/` | rerun of the 2008-table near-miss interval certificate; `indep.py` (own 60-digit evaluation); `repo/` is the needed subset of the earlier team repository, kept in its original layout because the scripts use paths relative to it |
| `d6_fourier/` | dimension-six Fourier pair {I, F_6}: `fourier6.py` and its outputs, general SOS checker `sos_general.py`, `run_fourier6_certs.py` (results to be added) |
| `d10/` | dimension-ten checks: `check_d10.py` (Krawczyk, orthogonality graph, cliques, margins), `search.py`, `search_match.py`, `energy10.py`, data and logs |
| `supplementary/` | working documents of workstreams B and C (see its README) |
| `docs/` | `verification_ledger.md`, `UPSTREAM.md` |
| `report/`, `slides/`, `lean_drafts/`, `tools/` | placeholders |

## Install

    pip install python-flint cvxpy mpmath numpy scipy qiskit qiskit-aer

(`matplotlib` is also needed for `hide_seek/fig.py`.) Runtimes below are wall-clock on a 2-core cloud container,
measured on 15 Nov 2026 with one core busy with another job.

## Reproduce

Each command is run from the directory named in its heading.

### Energy certificates and four-basis bounds (`cert/`)

Trusts: python-flint (Arb ball arithmetic) and the checker itself; numpy only loads the files and supplies a
floating Cholesky factor whose error is then bounded in balls. `build.py` (cvxpy) only searches for the matrices.

    python3 verify.py 0.0385 Q_T0_gamma0.0385.npy T0
    # 2.2 s. Expected last line:
    # CERTIFIED (T0):  E(psi) >= 0.0385 - S  >  0.038499999998  for every unit psi      (S <= 2.189e-12)

    python3 verify.py 0.0235 Q_T1_gamma0.0235.npy T1
    # 1.0 s. Expected last line:
    # CERTIFIED (T1):  E(psi) >= 0.0235 - S  >  0.023499999997  for every unit psi      (S <= 2.807e-12)

    python3 verify_sets.py ../near_misses/repo/results/visibility/bases_d6_delta.npy ../near_misses/repo/results/visibility/bases_d6_P4.npy
    # 0.25 s. Expected lines:
    #   exact set has worst-case bias delta <= 0.030223872                (bases_d6_delta.npy)
    #   exact set has game score P_4 >= 0.7038883627, i.e. shortfall <= 2.357825e-04   (bases_d6_P4.npy)
    # T0: any 4 bases containing it:  delta >= sqrt(g/18) > 0.046248 ;  game shortfall >= c*g/72 > 3.302291e-04
    # T1: any 4 bases containing it:  delta >= sqrt(g/18) > 0.036132 ;  game shortfall >= c*g/72 > 2.015684e-04

The bias and game bounds also rely on the square-root inequality, proved by hand in the report.

### Product-triple checks (`checks/`)

Trusts: numpy/scipy floating point; these are numerical checks, not proofs.

    python3 check1.py      # 64 s. Expected: "min E over 400 starts: 0.038762756430420514 ..."; Lemma 3.1 error 8.9e-16; witness E diff -6.9e-17
    python3 check2.py      # 141 s. Output identical to check2.log; "clique counts sizes 0..5: [1, 30, 135, 120, 60, 12]"
    python3 check3.py      # 59 s. Expected: "T1 (...) min E = 0.023835355278249426"; "c = 0.6175713839378697"
    python3 sos.py 4       # 18 s. Expected: "relaxation optimum = -0.0000000207"; "numerical rank (>1e-7) 63"
    python3 sos.py 6 SCS 2e-4    # not re-run in this session, log included (sos6.log): optimum 0.0383285692, 18.5 s solve
    python3 sos.py 6 SCS 1e-5    # not re-run in this session, log included (sos6_tight.log): optimum 0.0386693296, 43 s solve

### Hide and seek (`hide_seek/`)

Trusts: Qiskit/Aer and the chi-square approximation. A simulation; it turns the certified bound into shot counts.

    python3 hide_seek.py . ../near_misses/repo/results/visibility/bases_d6_P4.npy ../near_misses/repo/results/visibility/sim.json
    # not re-run in this session (Monte Carlo, long); output hide_seek.json included. Overwrites hide_seek.json.
    # Key numbers (RESULTS.md): 239 shots per setting; 589 total at 5 sigma; 1,500 at 10% gate error.
    python3 fig.py .
    # 1.6 s (tested on a copy). Writes fig3_hide_seek.png, fig3a_hide_seek.png, fig3b_hide_seek.png from hide_seek.json.

### Near-miss certificate (`near_misses/`)

Trusts: python-flint/Arb and `certify.py` (its r, J, H are validated against `search.py` numerically, not rigorously;
see `repo/results/constellations/certified/CERT.md`). `indep.py` trusts mpmath at 60 digits.

    python3 indep.py
    # 3.8 s. Expected: "shape [4, 4, 1]: misfit = 0.00102497683851953369499" and
    #                  "shape [5, 3, 1]: misfit = 0.0007327886563036878044317"; "20/20" restarts for each.

    cd repo && python3 src/constellations/certify/certify.py
    # 1.8 s. Expected: "441 overall: True ...", "531 overall: True ..." (also 432, 442 pass T1-T4).
    # Matches certify_rerun.log. NOTE: overwrites repo/results/constellations/certified/certificate.json
    # (only the timing fields change); run on a copy to keep the stored file.

### Dimension-six Fourier pair (`d6_fourier/`)

Trusts: python-flint/Arb (Krawczyk test of the 48 vectors, SOS checker in `sos_general.py`).

    python3 fourier6.py              # not re-run in this session; outputs fourier6.json, fourier6_vecs.npy included
    python3 run_fourier6_certs.py    # about 1 min per triple, 16 triples; not re-run in this session, results to be added

### Dimension ten (`d10/`)

Trusts: python-flint/Arb for `check_d10.py`; numpy/scipy for the searches and energy minima. The final theorem is
conditional on the completeness of the cited list of 34,940 cyclic 10-roots, which nothing here checks.

The scripts were not edited after the move and contain absolute paths: `search_match.py` and `energy10.py` read
`/home/claude/work/d10/vecs.npy`, `check_d10.py` writes `vecs.npy` and `bases.json` there, and `energy10.py` reads
the `mub10` working folder at `/mnt/user-data/uploads/mathathon/mub10`. To run them elsewhere, provide those paths,
for example `mkdir -p /home/claude/work && ln -s "$PWD" /home/claude/work/d10` from inside `d10/`, and a copy of
the `mub10` folder (see `docs/UPSTREAM.md`).

    python3 check_d10.py <mub10 folder>    # not re-run in this session. Expected: 3040/3040 certified, 57,680 pairs,
                                           # "10-cliques: 1136; identical to the stored list of bases: True", margin 4.17807
    python3 search_match.py 60 2026        # not re-run in this session, log included (search_match.log, 183 s):
                                           # "starts 1200000, converged 1199148, end points not on the certified list: 0"
    python3 energy10.py                    # not re-run in this session; output energy10.json included

## What is not checked here

The Lean build of workstream B, the native rerun of workstream C, and the completeness of the 34,940 cyclic 10-roots.
See the "Not verified" section of `docs/verification_ledger.md`.
