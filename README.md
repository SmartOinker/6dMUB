# Mutually unbiased bases in dimension six: codebase behind the report

Caltech x SAIR Mathathon, Problem 124. This repository holds the scripts, certificates, data and logs behind the
report: degree-six sum-of-squares energy certificates for the two product MUB triples in C^6, the vector-to-basis
bounds and their check against explicit four-basis sets, the hide-and-seek detection simulation, the rerun of the
2008-table near-miss certificate, and the conditional dimension-ten result. Every claim of the report is mapped to the check that
re-verifies it, with the exact command and expected output, in `docs/verification_matrix.md`; `verify_all.sh` runs all fast checks
in one go (log: `docs/verify_all.log`, 41 steps; steps S42 to S44, added in the final revision for `lean_structure/`, `openai_check/full_audit/` and the dimension-ten orbits and exact bases (`d10/check_orbits_exact.py`), are logged in `docs/verify_final_steps.log`). `docs/verification_ledger.md` is a short pointer to the matrix. Upstream sources and commit
hashes are in `docs/UPSTREAM.md`.

    ./verify_all.sh 2>&1 | tee docs/verify_all.log     # about 11 minutes on 2 cores; works on a copy of the repository; exit status 0 = all passed

## Directory map

| path | content |
|---|---|
| `verify_all.sh` | runs every fast check in sequence on a temporary copy of the repository, prints the claim ids each check supports, exits non-zero on any failure |
| `cert/` | degree-six SOS energy certificates (Gram matrices `Q_T0_*.npy`, `Q_T1_*.npy`), Arb checker `verify.py`, `verify_sets.py`, search script `build.py` (not part of the proof) |
| `checks/` | `check1.py` (energy identity, witness, minimum), `check2.py` (cube-rank counts, game numerics), `check3.py` (second triple, thresholds), `sos.py` (moment relaxations, degree 4 and 6); logs `check2.log`, `sos6.log`, `sos6_tight.log`. Audit checks written separately from the programs they check: `check_cert_pointwise.py` (second implementation of the Gram-matrix identity), `check_report_arithmetic.py` (recomputes derived numbers and compares stored results with the report), `check_bridge_theorem.py`, `check_minimiser.py`, `check_sqrt_lemma.py`, `check_gap72.py`, `check_hadamard_identities.py`, `check_sixphase.py`, `check_quartic_sos.py` (with `build_quartic_functional.py`), `check_phase_ball.py`, `check_fourier6_graph.py`, `check_d10_float.py`; see `checks/README_checks.md` |
| `hide_seek/` | Qiskit/Aer simulation `hide_seek.py`, `fig.py`, data `hide_seek.json`, `RESULTS.md` (with a dated update), figures `fig3*.png`; `finite_sample.py` (finite-sample detection theorem: shot counts, exact enumeration, Monte Carlo; log `finite_sample.log`); `check_purity_witness.py` (log `check_purity_witness.log`) |
| `hide_seek/rehearsal_fake_backend/` | hardware kit rehearsed on a fake-backend noise model only; not evidence (see its README) |
| `near_misses/` | rerun of the 2008-table near-miss interval certificate; `indep.py` (own 60-digit evaluation); `check_table.py` (recomputes the 35-row table and the 52,000-start counts of the report from the raw search output), `check_visibility_records.py`; `repo/` is the needed subset of the earlier team repository, kept in its original layout because the scripts use paths relative to it: `results/constellations/` (`table/` the 36 raw runs `t_*.jsonl.gz`, 2,000 starts per shape, seed 2026; `big/` the two 50,000-start runs; `sym/`, `extra/`, `evidence.json`, `certified/`, `nearmiss/`, `yale_examples_check.json`), `results/fourier/` and `src/fourier/` (the first Fourier program and its output), `results/openai_check/{REBUILD.md,rebuild.json}` (the first partial rebuild: seed cover, stage-A shard 0 with 764 records, two stage-C batches) and `src/openai_check/fourier_cell.py` (a heuristic search of the saved records, not run), `results/openmathos/` (an independent re-implementation of the search run on another platform: 6.5 million starts, none converged), `results/visibility/` and `src/visibility/` (how the explicit four-basis sets were found), `src/constellations/` (search, certificate, evidence, examples check) |
| `d6_fourier/` | dimension-six Fourier pair {I, F_6}: `certify_d6_roots.py` (156 cyclic 6-roots: search and Arb certification, data `cyclic6_roots.npz`), `certify_graph.py` (orthogonality graph of the 48 unimodular roots in ball arithmetic), `check_partial_bases.py` (partial fourth bases {5,5,b,c}), `fourier6.py` and its outputs (`fourier6.json`, `fourier6_vecs.npy`), general SOS checker `sos_general.py`, `run_fourier6_certs.py` (builds the 16 certificates, about 30 min), `verify_fourier6_certs.py` (re-checks all 16 in about 20 s: "all 16 certified, minimum 0.0234999999946"), logs and the 16 Gram matrices |
| `d10/` | dimension-ten checks: `check_d10.py` (Krawczyk, orthogonality graph, cliques, margins), `margin_arb.py` (margin in Arb), `search.py`, `search_match.py`, `energy10.py`, data and logs |
| `d10/roots_full/` | regenerated and certified list of all 34,940 cyclic 10-roots: `find_roots.py` (heuristic search), `certify_roots.py` (Arb certification: 3,040 unimodular, 31,900 not, none undecided), data and logs; its README states what is and is not proved |
| `openai_check/` | second, independent rerun (by a separate agent, pinned upstream revision) of the record checker of the OpenAI proof, the 26-corruption mutation test (`mutate.py`, `mutations_rerun.json`: 17 detected, same verdict for all 26) and the partial rebuild (`build_rebuild.sh`, `cmp_records.py`, `rebuild_rerun.json`). It needs the upstream repository (80 MB, not shipped), so it is not part of `verify_all.sh`; see its README |
| `supplementary/` | the structure paper and the certificate audit document (see its README) |
| `lean_structure/` | the structure Lean project (E > 1/72 and the structure declarations): sources, build log, axiom log, `check_logs.py` |
| `openai_check/full_audit/` | full native rerun of the OpenAI pipeline and re-certification of the Root records: drivers, logs of every invocation, checkers, repeat-run log |
| `lakefile.toml`, `lean-toolchain`, `lake-manifest.json`, `MUB6Bridge/`, `lean/` | Lean 4 project `MUB6Bridge`: four files (`BridgeLemma.lean`, `FiniteSample.lean`, `Bases.lean`, `Corollaries.lean`), 45 declarations; built locally with Lean v4.35.0 and Mathlib v4.35.0, no `sorry`, standard axioms only; the competition's automated build has not been run on it by us. Lean-verified: the square-root cap inequality; the vector-to-basis theorem as inequalities about orthonormal bases of C^6 with the game score defined by its formula (`bridge_bias`, `bridge_game`); the numerical corollaries as implications from an assumed energy bound (`corollary_T0`, `corollary_T1`); `gameScore_le`; the identity X^2 = 15 + 6(N-1)T (`pearson_eq_collision`, `pearson_total`); four elementary variance steps; the arithmetic of all five shot counts (`shots_*`). NOT Lean-verified: the energy bounds, the meaning of the score as an optimal success probability, every probability statement, the purity witness, dimension ten. `lean/README.md` lists the declarations and the differences from the report, `lean/BUILD_LOG.txt` is the build log. Not run by `verify_all.sh` |
| `docs/` | `verification_matrix.md` (claim-by-claim matrix), `verify_all.log`, `verification_ledger.md` (pointer), `adversarial_review.md`, `UPSTREAM.md` |
| `report/`, `slides/` | the report source and the slides with speaker notes |
| `tools/` | helper client for the Open Math OS platform API (the key is read from an environment variable and is not stored) |

## Install

    pip install python-flint cvxpy mpmath numpy scipy qiskit qiskit-aer

(`matplotlib` is also needed for `hide_seek/fig.py`; `sympy` and `networkx` are used by some audit checks. `qiskit` is needed only for `hide_seek/hide_seek.py`, which `verify_all.sh` does not run.) Runtimes below are wall-clock on a 2-core cloud container,
measured on 15 Nov 2026 with other jobs running on the same machine.

## Reproduce

Each command is run from the directory named in its heading.

### Energy certificates and four-basis bounds (`cert/`)

Trusts: python-flint (Arb ball arithmetic) and the checker itself; numpy only loads the files and supplies a
floating Cholesky factor whose error is then bounded in balls. `build.py` (cvxpy) only searches for the matrices.

    python3 verify.py 0.0385 Q_T0_gamma0.0385.npy T0
    # 1 to 2 s. Expected last lines (the bound is rounded DOWN to 11 decimals; S is printed with %.3e; ||R||_F is printed rounded up):
    # (3) residual bound S <= 2.189e-12
    # (2) ||Q - tau I - L L^T||_F <= 9.5511e-15  (tau = 1e-05; rounded up)
    # CERTIFIED (T0):  E(psi) >= 0.0385 - S  >  0.03849999999  for every unit psi

    python3 verify.py 0.0235 Q_T1_gamma0.0235.npy T1
    # 1 s. Expected last lines:
    # (3) residual bound S <= 2.807e-12
    # (2) ||Q - tau I - L L^T||_F <= 7.8320e-15  (tau = 1e-05; rounded up)
    # CERTIFIED (T1):  E(psi) >= 0.0235 - S  >  0.02349999999  for every unit psi

    python3 verify_sets.py ../near_misses/repo/results/visibility/bases_d6_delta.npy ../near_misses/repo/results/visibility/bases_d6_P4.npy
    # 0.3 s. Directed rounding: upper bounds rounded up, lower bounds rounded down. Expected lines:
    #   exact set has worst-case bias delta <= 0.030223873   (rounded up)                          (bases_d6_delta.npy)
    #   exact set has game score P_4 >= 0.7035060582 (rounded down), i.e. shortfall <= 0.0006180870 (rounded up)
    #   exact set has worst-case bias delta <= 0.040598666   (rounded up)                          (bases_d6_P4.npy)
    #   exact set has game score P_4 >= 0.7038883627 (rounded down), i.e. shortfall <= 0.0002357826 (rounded up)
    # T0: any 4 bases containing it:  delta >= sqrt(g/18) > 0.046248 ;  game shortfall >= c*g/72 > 0.0003302291   (both rounded down)
    # T1: any 4 bases containing it:  delta >= sqrt(g/18) > 0.036132 ;  game shortfall >= c*g/72 > 0.0002015684   (both rounded down)

The bias and game bounds also rely on the square-root inequality, proved by hand in the report.

### Product-triple checks (`checks/`)

Trusts: numpy/scipy floating point; these are numerical checks, not proofs.

    python3 check1.py      # 64 s. Expected: "min E over 400 starts: 0.038762756430420514 ..."; Lemma 3.1 error 8.9e-16; witness E diff -6.9e-17
    python3 check2.py      # 141 s. Output identical to check2.log; "clique counts sizes 0..5: [1, 30, 135, 120, 60, 12]"
    python3 check3.py      # 59 s. Expected: "T1 (...) min E = 0.023835355278249426"; "c = 0.6175713839378697"
    python3 sos.py 4       # 18 s. Expected: "relaxation optimum = -0.0000000207"; "numerical rank (>1e-7) 63"
    python3 sos.py 6 SCS 2e-4    # 22 s. Expected: "relaxation optimum = 0.0383285692" (matches sos6.log)
    python3 sos.py 6 SCS 1e-5    # 53 s. Expected: "relaxation optimum = 0.0386693296" (matches sos6_tight.log)
    # Numerical only: SCS is a first-order solver and these digits depend on the solver build. On a second machine (scs 3.3.2) the same
    # commands gave 0.0377947174 and 0.0377028616, so steps S06/S07 of verify_all.sh can fail there; no claim of the report depends on them
    # (the certified bound is checked in ball arithmetic by cert/verify.py).

Audit checks, written separately from the programs they check (each prints `OK` as its last line; the claim ids they support
are in `docs/verification_matrix.md`; commands and expected lines for all of them are in the matrix):

    python3 check_cert_pointwise.py       # 2 s. Second implementation: the Gram-matrix identity at 4,000 random points for T0, T1 and the 16 Fourier-pair triples
    python3 check_report_arithmetic.py    # 5 s. Recomputes derived numbers (bridge numbers, shot counts N = 1936/5142/3007/7687, 239/198/369, noise totals) and compares stored results with the report
    python3 check_sqrt_lemma.py           # 4 s. Square-root lemma on 1.8 million points and a grid of 2,000,001
    python3 check_bridge_theorem.py       # 32 s. Vector-to-basis theorem on random bases, stored four-basis sets, dimension-four control
    python3 check_minimiser.py            # 6 s. Closed-form minimiser (50 digits) and 60 own minimisations on T0 and T1
    python3 check_gap72.py                # 18 s. Steps of the proof of E > 1/72
    python3 check_hadamard_identities.py  # 10 s. Cubic cap and cube ranks on six families
    python3 check_seed_geometry.py        # 2 s. Structure paper Sec. 13: cube-Gram spectrum on the seed, operator inequality (numerical; 8 PASS, 1 NOT CHECKED)
    python3 check_sixphase.py             # 54 s. Six-phase bound: maximum 5.7154760665 = 7 sqrt6/3
    python3 check_quartic_sos.py          # 15 s. Exact degree-four functional over Q(sqrt3): 1,404 equations, rank 63
    python3 check_phase_ball.py           # 61 s. Phase-ball radius 0.2242139
    python3 check_fourier6_graph.py       # about 70 s. Fourier funnel 156 -> 48 -> 16 -> 0 in floating point, own code

### Hide and seek (`hide_seek/`)

Trusts: Qiskit/Aer and the chi-square approximation. A simulation; it turns the certified bound into shot counts.

    python3 finite_sample.py
    # 24 s. Finite-sample theorem (no approximation): N = 1936 (95% detection, 0.1% false alarm), 5142 (99%), 3007 and 7687 for gamma = 0.0234999;
    # exact enumeration for N = 2, 3, 4; Monte Carlo at N = 1936 with no missed detection and no false alarm in 20,000 runs. Log: finite_sample.log.
    python3 check_purity_witness.py
    # Purity witness on 100,000 random states; last line OK. Log: check_purity_witness.log.
    python3 hide_seek.py . ../near_misses/repo/results/visibility/bases_d6_P4.npy ../near_misses/repo/results/visibility/sim.json
    # not re-run in this session (needs Qiskit, Monte Carlo, long); output hide_seek.json included. Overwrites hide_seek.json.
    # Key numbers (RESULTS.md): 239 shots per setting (large-sample approximation, optimistic below N = 100); 589 total at 5 sigma; 1,500 at 10% gate error.
    python3 fig.py .
    # 1.6 s (tested on a copy). Writes fig3_hide_seek.png, fig3a_hide_seek.png, fig3b_hide_seek.png from hide_seek.json.

### Near-miss certificate (`near_misses/`)

Trusts: python-flint/Arb and `certify.py` (its r, J, H are validated against `search.py` numerically, not rigorously;
see `repo/results/constellations/certified/CERT.md`). `indep.py` trusts mpmath at 60 digits.

    python3 -I check_table.py ../report/report.tex
    # 1 s. Recomputes the 35-row table of the report (2,000 starts per shape, seed 2026), the 389 and 695 of 52,000, the level counts,
    # 4.99e-3, the {5,3,3,3} run and the explicit examples from the raw search output in repo/results/constellations/ (the 36 table files
    # are stored gzip-compressed). Last line: "OK: every column of the 35-row table and the quoted figures agree with the raw data".
    python3 -I check_visibility_records.py   # 0.3 s. The stored record behind the explicit four-basis sets: 72 and 700 starts, best values.

    python3 indep.py
    # 5 s. Expected: "shape [4, 4, 1]: misfit = 0.00102497683851953369499" and
    #                  "shape [5, 3, 1]: misfit = 0.0007327886563036878044317"; "20/20" restarts for each.

    cd repo/src/constellations && python3 -I -c 'import sys,runpy; sys.path.insert(0,"."); runpy.run_path("check_yale_examples.py", run_name="__main__")'
    # 2 s. The three explicit constellation examples of the third 2026 preprint ({5,3,3,3}, {5,4,3,1}, {5,5,2,2}) in 40-digit arithmetic:
    # misfits 2.8352e-40, at most 4.6909e-40, and 2.2221e-7 at the centre of the rational box / 3.5639e-30 after polishing.
    # It writes ../../results/constellations/yale_examples_check.json (identical content; run on a copy to keep the stored file).

    cd repo && python3 src/constellations/certify/certify.py
    # 3 s. Expected: "441 overall: True ...", "531 overall: True ..." (also 432, 442 pass T1-T4).
    # Matches certify_rerun.log. NOTE: overwrites repo/results/constellations/certified/certificate.json
    # (only the timing fields change); run on a copy to keep the stored file.

### Dimension-six Fourier pair (`d6_fourier/`)

Trusts: python-flint/Arb (Krawczyk test of the 48 vectors, SOS checker in `sos_general.py`).

The certified funnel 156 -> 48 -> 16 -> 0 (run with `python3 -I`; data file `cyclic6_roots.npz` holds the 156 midpoints):

    python3 -I certify_d6_roots.py find cyclic6_roots_new.npz 1   # 2 s. Heuristic search (symmetry group of order 288), then Arb certification.
                                     # Expected: "COUNTS: found=156 certified=156 unimodular=48 certified_non_unimodular=108 undecided=0
                                     # krawczyk_failed=0 boxes_pairwise_disjoint=True stored48_match=True" and "OK". Adapted from d10/roots_full.
    python3 -I certify_d6_roots.py verify cyclic6_roots.npz       # 0.5 s. The same certification from the shipped midpoints only.
    python3 -I certify_graph.py      # 0.5 s. 48 vectors re-enclosed (300 bits); 300 possibly-orthogonal pairs, 828 certified non-orthogonal;
                                     # maximal cliques {2: 72, 6: 16}; 16 six-cliques cover 228 pairs, two per vertex; the 16 triples {I, F_6, B}
                                     # unbiased up to the enclosure width; 120 pairs of bases certified apart (defect 6.0 unnormalised). Last line OK.
                                     # Enclosures cannot prove exact orthogonality: the possibly-orthogonal graph is a superset of the true one.
    python3 -I check_partial_bases.py   # 1 s. From the same enclosures: besides {5,5,b} only {5,5,1,1} and {5,5,2,1} are possible, so no
                                     # partial fourth basis larger than {5,5,2,1}; equal to near_misses/repo/results/fourier/fourier_constellations.json.

The FIRST Fourier program (4,000 starts, 320-bit Krawczyk, 156 roots by `cyclic6.py`, mixed volume) is in `near_misses/repo/src/fourier/`;
run on a copy with the hard-coded output folder changed, it reproduced `near_misses/repo/results/fourier/results.json` apart from timings (4 min).

    python3 fourier6.py              # 28 s. Expected: 48/48 Krawczyk-certified, 300 orthogonal pairs, 16 six-cliques, minima [0.023835 0.032676 0.038763];
                                     # rewrites fourier6.json and fourier6_vecs.npy with identical content (verify_all.sh runs it on a copy)
    python3 verify_fourier6_certs.py # 20 s. Re-checks the 16 stored Gram matrices in Arb. Expected: all 16 certified, minimum 0.0234999999946
                                     # (0.02349999999466995); the bounds per triple are in fourier6_verified.json and verify_fourier6.log
    python3 run_fourier6_certs.py    # about 30 minutes: re-solves the 16 SDPs and rebuilds the matrices; log fourier6_certs.log; not re-run in this session

### Dimension ten (`d10/`)

Trusts: python-flint/Arb for `check_d10.py`, `margin_arb.py` and `roots_full/certify_roots.py`; numpy/scipy for the searches and energy
minima. The final theorem is conditional on the completeness of the cited list of 34,940 cyclic 10-roots (hypothesis H), which nothing
here checks. The scripts in `d10/` find their data files next to themselves (no absolute paths) except `energy10.py`, which reads the `mub10`
working folder at `/mnt/user-data/uploads/mathathon/mub10` (a copy is in `d10/upstream_mub10/`, see `docs/UPSTREAM.md`). Among the scripts copied
from the earlier team repository into `near_misses/repo/src/`, `fourier/fourier_case.py`, `fourier/bound_mv.py` and `visibility/common.py` write to
a hard-coded folder `/home/claude/mub6/results/...`; they were run on copies with that constant changed and are not part of `verify_all.sh`.

    cd roots_full
    python3 certify_roots.py cyclic10_roots.npz out.npz ../upstream_mub10/data/exact/bu10hp_unimod.txt 2
        # 18 to 25 s. Expected: "found=34940 certified=34940 unimodular=3040 certified_non_unimodular=31900 undecided=0 krawczyk_failed=0",
        # boxes pairwise disjoint, match with the stored list of 3,040 True. Writes out.npz.
    cd .. && python3 check_d10.py upstream_mub10
        # 8 s. Expected: 3040/3040 Krawczyk-certified, 57,680 pairs, "10-cliques: 1136; identical to the stored list of bases: True", margin 4.17807.
        # Overwrites vecs.npy and bases.json with identical content (run on a copy).
    python3 margin_arb.py              # 12 s. Expected: margin [4.178074647 +/- 3.79e-10] over 1,272,177 pairs
    python3 ../checks/check_d10_float.py   # 3 s. Float re-derivation: 57,680 edges, maximal cliques {2: 17700, 10: 1136}, margin 4.17807
    python3 search_match.py 60 2026    # not re-run in this session, log included (search_match.log, 183 s):
                                       # "starts 1200000, converged 1199148, end points not on the certified list: 0"
    python3 energy10.py                # not re-run in this session; output energy10.json included

### Second run of the OpenAI record checker (`openai_check/`)

In progress and not reproducible from this repository alone: the commands in `openai_check/README.md` need a sparse clone of the upstream
repository at the pinned revision (80 MB of saved records). The stored result `mutations_rerun.json` agrees mutant by mutant (17 of 26
detected) with the first run in `near_misses/repo/results/openai_check/mutations.json`; `checks/check_report_arithmetic.py` compares the two.
The full native rerun of the OpenAI pipeline (100 invocations, 8 principal files byte-identical) is in `openai_check/full_audit/`: logs of every invocation, the accounting checker and the 128-bit re-certification of the 27,188 Root records. The native run was done once (about 4.4 hours of process time); its accounting check and the Root re-certification were repeated on a second machine (`openai_check/full_audit/RERUN_LOG.txt`), and `verify_all.sh` step S43 checks the stored results.

## What is not checked here

A second native run of the OpenAI pipeline (see above: run once, checks repeated), a build of the structure Lean project by `verify_all.sh` itself (`lean_structure/` was built twice, on macOS and on Open Math OS; the stored build logs, axiom logs and source hashes of both builds are checked by step S42), the completeness of the 34,940 cyclic 10-roots (hypothesis H) and of the 156 cyclic 6-roots (cited
counts), the cited literature, the Qiskit simulations (`hide_seek.py`, not run in the last session), and a full rerun of the 35-shape search
(the raw output is shipped and recomputed by `near_misses/check_table.py`; seven of the 35 shapes and the triple {5,5,5} were rerun by hand with bit-identical output). The complete list, with what would be needed for each, is in the section "Claims without independent re-verification" of
`docs/verification_matrix.md`. The Lean project at the repository root (`MUB6Bridge`) is separate from the structure Lean project in `lean_structure/` (a build of the repository root does not compile it) and from the OpenAI Lean development, whose scope note and statement file we read at the pinned revision (hashes in `openai_check/README.md`) but did not rebuild; the competition's automated Lean build has not been run on `MUB6Bridge` by us.
