#!/usr/bin/env bash
# verify_all.sh: run every fast check of the repository in sequence and fail if any of them fails.
#
# Usage, from the repository root:   nice -n 5 ./verify_all.sh            (log: ./verify_all.sh 2>&1 | tee docs/verify_all.log)
# Runtime: about 11 minutes on a 2-core machine (the slowest steps are checks/check2.py, about 2.5 minutes, and
# checks/check_fourier6_graph.py, about 1 minute).  Exit status: 0 if every step passed, 1 otherwise.
#
# Safety: the repository is copied (without .git) into a temporary directory and every step runs in the copy, so the
# stored results (hide_seek/hide_seek.json, d6_fourier/fourier6*.json, near_misses/.../certificate.json, d10/*.npy, ...)
# are never overwritten.  The copy is deleted at the end (set KEEP=1 to keep it).
#
# NOT run here (too slow, or needs software/data that is not in the repository), see docs/verification_matrix.md:
#   hide_seek/hide_seek.py (Qiskit, Monte Carlo, overwrites hide_seek.json), hide_seek/fig.py (matplotlib, figures only),
#   d6_fourier/run_fourier6_certs.py (about 30 min: it re-solves the 16 SDPs; the checker verify_fourier6_certs.py IS run),
#   near_misses/repo/src/fourier/fourier_case.py (the FIRST Fourier program, about 4 min, hard-coded output path; rerun by hand on a copy,
#   its results.json agreed with the shipped one except timings), near_misses/repo/src/constellations/evidence.py (about 4 min, rerun by hand:
#   evidence.json identical), near_misses/repo/src/constellations/search.py and table_run.sh (the 35-shape search, about 1 hour; seven shapes and the triple rerun by hand),
#   the Lean build of the project at the repository root (`lake build`, see lean/README.md and docs/verification_matrix.md),
#   d10/search_match.py (183 s, 1.2 million starts) and d10/search.py, d10/energy10.py (long; needs the original paths),
#   d10/roots_full/find_roots.py (heuristic search, about 100 s; the certifier certify_roots.py IS run),
#   checks/build_quartic_functional.py (35 s, regenerates the exact functional; the checker check_quartic_sos.py IS run),
#   cert/build.py (SDP search, not part of the proof), the openai_check/ scripts (need the OpenAI repository and its
#   saved run, 80 MB, not shipped; openai_check/ is in progress), lean_drafts/ (unbuilt draft, not a verification).
# The step "stored records" checks the stored logs and JSON files against the report numbers without re-running them.

set -u -o pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/mub_verify.XXXXXX")"
cleanup() { if [ "${KEEP:-0}" != "1" ]; then rm -rf "$WORK"; else echo "kept working copy: $WORK"; fi; }
trap cleanup EXIT
echo "verify_all.sh  $(date -u +%Y-%m-%dT%H:%M:%SZ)  host: $(uname -sm), $(nproc) cores, python $(python3 -c 'import sys;print(sys.version.split()[0])')"
python3 -c "import flint, numpy, scipy, mpmath, cvxpy; print('python-flint', flint.__version__, '| numpy', numpy.__version__, '| scipy', scipy.__version__, '| mpmath', mpmath.__version__, '| cvxpy', cvxpy.__version__)"
mkdir -p "$WORK/repo"
(cd "$ROOT" && tar --exclude=.git --exclude=__pycache__ -cf - .) | (cd "$WORK/repo" && tar -xf -)
cd "$WORK/repo" || exit 2
R="$WORK/repo"

NPASS=0; NFAIL=0; FAILED=""
# step ID "claims" "description" WORKDIR "pattern1|||pattern2|||..." command...
step() {
  local id="$1" claims="$2" desc="$3" dir="$4" pats="$5"; shift 5
  local out="$WORK/$id.out" t0 t1 rc=0 miss=""
  echo
  echo "=== $id  supports: $claims"
  echo "    $desc"
  echo "    command: (cd ${dir#"$R"/} && $*)"
  t0=$(date +%s)
  (cd "$dir" && "$@") > "$out" 2>&1 || rc=$?
  t1=$(date +%s)
  local IFS_OLD="$IFS" p
  IFS=$'\n'; for p in $(printf '%s' "$pats" | sed 's/|||/\n/g'); do
    if [ -n "$p" ]; then
      if grep -Eq -- "$p" "$out"; then grep -E -m1 -- "$p" "$out" | cut -c1-230 | sed 's/^/    expected line found: /'
      else miss="$miss [$p]"; fi
    fi
  done; IFS="$IFS_OLD"
  if [ "$rc" -eq 0 ] && [ -z "$miss" ]; then echo "    PASS  ($((t1 - t0)) s)"; NPASS=$((NPASS + 1))
  else
    echo "    FAIL  (exit code $rc, missing expected lines:${miss:- none})  ($((t1 - t0)) s)"; echo "    ---- last 25 lines of output ----"; tail -n 25 "$out" | cut -c1-230 | sed 's/^/    | /'
    NFAIL=$((NFAIL + 1)); FAILED="$FAILED $id"
  fi
}

# ---------------------------------------------------------------------------------------------------- certificates
step S01 "C4 C5 C23 C25" "degree-six interval certificate, canonical triple T0 (Arb checker)" "$R/cert" \
  "CERTIFIED \(T0\):  E\(psi\) >= 0.0385 - S  >  0.03849999999|||residual bound S <= 2.189e-12|||\|\|Q - tau I - L L\^T\|\|_F <= 9.55" \
  nice -n 5 python3 verify.py 0.0385 Q_T0_gamma0.0385.npy T0
step S02 "C4 C5 C25" "degree-six interval certificate, second product triple T1 (Arb checker)" "$R/cert" \
  "CERTIFIED \(T1\):  E\(psi\) >= 0.0235 - S  >  0.02349999999|||residual bound S <= 2.807e-12|||\|\|Q - tau I - L L\^T\|\|_F <= 7.83" \
  nice -n 5 python3 verify.py 0.0235 Q_T1_gamma0.0235.npy T1
step S03 "C32 C33 C35" "bias and game bounds for any fourth basis, and the two explicit four-basis sets (Arb; upper bounds rounded up, lower bounds rounded down)" "$R/cert" \
  "exact set has worst-case bias delta <= 0.030223873   \(rounded up\)|||shortfall <= 0.0002357826 \(rounded up\)|||exact set has worst-case bias delta <= 0.040598666|||shortfall <= 0.0006180870 \(rounded up\)|||T0: any 4 bases containing it:  delta >= sqrt\(g/18\) > 0.046248 ;  game shortfall >= c\*g/72 > 0.0003302291   \(both rounded down\)|||T1: any 4 bases containing it:  delta >= sqrt\(g/18\) > 0.036132 ;  game shortfall >= c\*g/72 > 0.0002015684   \(both rounded down\)" \
  nice -n 5 python3 verify_sets.py ../near_misses/repo/results/visibility/bases_d6_delta.npy ../near_misses/repo/results/visibility/bases_d6_P4.npy
step S04 "C25 C36" "second implementation: pointwise test of the stored Gram matrices (numpy, no monomial expansion, no Arb)" "$R/checks" \
  "T0 \(Q_T0_gamma0.0385\): max .*min eigenvalue of Q|||Fourier-pair triples by certified level: \{'0.0324': 12, '0.0235': 2, '0.0385': 2\}|||^OK" \
  nice -n 5 python3 check_cert_pointwise.py
step S05 "C13 C36 C38" "Fourier pair: the 16 stored Gram matrices re-checked in Arb (third-basis vectors re-certified inside)" "$R/d6_fourier" \
  "minimum certified bound over the 16 triples: 0.0234999999946|||triple 15: numerical min 0.0326759; CERTIFIED E > 0.0323999999" \
  nice -n 5 python3 verify_fourier6_certs.py
step S06 "C29" "degree-six moment relaxation (SCS, tolerance 2e-4): 0.0383285692" "$R/checks" \
  "relaxation optimum = 0.0383285692" nice -n 5 python3 sos.py 6 SCS 2e-4
step S07 "C29" "degree-six moment relaxation (SCS, tolerance 1e-5): 0.0386693296" "$R/checks" \
  "relaxation optimum = 0.0386693296" nice -n 5 python3 sos.py 6 SCS 1e-5

# ---------------------------------------------------------------------------------------------------- bridge, game, detection
step S08 "C30 C31" "square-root lemma: 1.8 million random squared overlaps plus a grid of 2,000,001 points" "$R/checks" \
  "random points tested: 1800000|||grid points tested: 2000001|||OK: no violation" nice -n 5 python3 check_sqrt_lemma.py
step S09 "C9 C12 C26 C28 C32 C35 C38 C40 C43 C45 C47 C48 C49 C50 C51 C52 C57 C60 C61" "independent recomputation of derived numbers and of stored-result summaries (mpmath, Fractions, scipy)" "$R/checks" \
  "smallest N with miss <= 0.05 is 2892|||smallest N = 1936; feasible t in|||smallest N = 7687; feasible t in|||bound at E\(rho\) = 0: sqrt\(5/6\)|||238.79, 197.54, 368.07 shots per setting -> 239, 198, 369|||\{0.0: 589, 0.0001: 589, 0.001: 594, 0.01: 646, 0.1: 1500\}|||all rational comparisons of Appendix A.3 hold exactly|||17 of 26 detected|||18 shapes have a nonzero 2008 rate|||^OK" \
  nice -n 5 python3 check_report_arithmetic.py
step S10 "C39 C40 C41 C43 C44" "finite-sample theorem: exact enumeration N = 2,3,4, variance bound, shot counts, Monte Carlo at N = 1936, chi-square comparison" "$R/hide_seek" \
  "N = 1936 shots per setting, threshold 0.38751\*gamma: miss <= 0.05000, false alarm <= 9.984e-04|||N = 5142 shots per setting, threshold 0.14579\*gamma|||N = 3007 shots per setting, threshold 0.40853\*gamma|||N = 7687 shots per setting, threshold 0.15978\*gamma|||with the fixed threshold gamma/2: N = 2892|||missed detections \(T < 0.38751\*gamma\): 0 of 20000|||^OK" \
  nice -n 5 python3 finite_sample.py

# ---------------------------------------------------------------------------------------------------- near-misses, 2008 table
step S11 "C51" "2008 near-misses: independent 60-digit evaluation (mpmath, no shared code with the certificate)" "$R/near_misses" \
  "shape \[4, 4, 1\]: misfit = 0.00102497683851953369499|||shape \[5, 3, 1\]: misfit = 0.0007327886563036878044317|||20 perturbed restarts returning to the same misfit: 20/20" \
  nice -n 5 python3 indep.py
step S12 "C51" "2008 near-misses: Arb interval certificate rerun (on a copy: the script overwrites certificate.json)" "$R/near_misses/repo" \
  "441 overall: True|||531 overall: True|||432 overall: True|||442 overall: True" \
  nice -n 5 python3 src/constellations/certify/certify.py
step S13 "C51" "regenerated certificate.json equals the original one in every field except run times" "$R/near_misses" \
  "differences other than timing: 0" python3 - <<'PY'
import json
a = json.load(open("repo/results/constellations/certified/certificate.json")); b = json.load(open("cert_original.json")); d = []
def cmp(x, y, p=""):
    if isinstance(x, dict) and isinstance(y, dict):
        for k in set(x) | set(y):
            if k not in x or k not in y: d.append(p + "/" + k)
            else: cmp(x[k], y[k], p + "/" + k)
    elif isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
        for i, (u, v) in enumerate(zip(x, y)): cmp(u, v, p + "[%d]" % i)
    elif x != y: d.append(p)
cmp(a, b); other = [p for p in d if not p.endswith("/seconds")]
print("differences other than timing:", len(other), "; timing fields differing:", len(d) - len(other))
assert not other
PY

# ---------------------------------------------------------------------------------------------------- structure theory
step S14 "C18 C31" "cube-rank enumeration (1,395 systems), game numerics, sqrt-inequality summed form" "$R/checks" \
  "clique counts sizes 0..5: \[1, 30, 135, 120, 60, 12\]|||k = 3 systems: 1215 nullity histogram: \{0: 1160, 1: 54, 3: 1\}|||P_4 deficit \(average over 6 pairs\) = 0.00150636" \
  nice -n 5 python3 check2.py
step S15 "C23 C27" "energy identity, witness minimiser, 400 BFGS minimisations on T0" "$R/checks" \
  "min E over 400 starts: 0.0387627564304205|||distinct local minima values: \[0.0387628\]|||witness: x\+y\+z = 1.0" nice -n 5 python3 check1.py
step S16 "C28" "second product triple: numerical minimum 0.0238354, thresholds" "$R/checks" \
  "T1 \(third basis \|0_y>B2, \|1_y>B3\) min E = 0.0238353|||c = 0.6175713839378697" nice -n 5 python3 check3.py
step S17 "C21 C29" "degree-four moment relaxation: optimum about 0, numerical rank 63" "$R/checks" \
  "relaxation optimum = -0.0000000207|||numerical rank \(>1e-7\) 63" nice -n 5 python3 sos.py 4
step S18 "C21" "degree-four obstruction: exact check over Q(sqrt3) of an independently built functional (rank 63, L(E)=0, L(N^2)=1)" "$R/checks" \
  "M c_l = 0 verified exactly: 1404 equations|||63 strictly positive pivots, remaining Schur block 15x15 exactly zero: True|||^OK" nice -n 5 python3 check_quartic_sos.py
step S19 "C18 C19" "Hadamard identities, cubic cap, cube ranks on Fourier-family, Tao, Dita and 700 numerical Hadamard matrices" "$R/checks" \
  "^OK" nice -n 5 python3 check_hadamard_identities.py
step S20 "C20" "six-phase bound: constrained maximisation from 4,000 starts, extremal configuration in 50 digits" "$R/checks" \
  "largest \|sum z\^3\| found      : 5.7154760665|||starts reaching the bound within 1e-6: 445|||^OK" nice -n 5 python3 check_sixphase.py
step S21 "C23" "analytic gap E > 1/72: every step inequality of Appendix A.3 on 200,000 states, exact fractions, total variation" "$R/checks" \
  "min E                                                       3.876276e-02|||^OK" nice -n 5 python3 check_gap72.py
step S22 "C12" "sharp phase-ball radius: 0.2242139, sharpness, convexity, Jensen step" "$R/checks" \
  "s\* \(40 digits\) = 0.2242138988404377963946674|||^OK" nice -n 5 python3 check_phase_ball.py

# ---------------------------------------------------------------------------------------------------- dimension six Fourier pair, dimension ten
step S23 "C13 C14 C15 C37" "Fourier pair: second program fourier6.py rerun (48 vectors, 300 pairs, 16 bases, minima) on a copy" "$R/d6_fourier" \
  "Krawczyk \+ unimodularity: 48/48 certified within 1e-30|||orthogonal pairs: 300|||candidate third bases \(6-cliques\): 16|||distinct minima: \[0.023835 0.032676 0.038763\]" \
  nice -n 5 python3 fourier6.py
step S24 "C13 C15 C37" "rerun output equals the stored fourier6.json and fourier6_vecs.npy (originals read from the repository)" "$R/d6_fourier" \
  "identical to the stored files: True" python3 - "$ROOT" <<'PY'
import json, sys, numpy as np
root = sys.argv[1] + "/d6_fourier/"
a = json.load(open("fourier6.json")); b = json.load(open(root + "fourier6.json"))
ja = json.dumps(a, sort_keys=True); jb = json.dumps(b, sort_keys=True)
va = np.load("fourier6_vecs.npy"); vb = np.load(root + "fourier6_vecs.npy")
ok = (ja == jb) and va.shape == vb.shape and np.abs(va - vb).max() < 1e-12
print("rerun fourier6.json and fourier6_vecs.npy identical to the stored files:", ok)
assert ok
PY
step S25 "C14 C15 C16 C37" "Fourier funnel 156 -> 48 -> 16 -> 0 re-derived in floating point with own code (graph, 120 pairs, own Newton search for 156 roots, minima)" "$R/checks" \
  "156 distinct cyclic 6-roots found \(classical count 156\), 48 unimodular|||16 six-cliques, largest clique 6; they cover 228 of 300 edges|||\[12, 2, 2\] triples|||^OK" nice -n 5 python3 check_fourier6_graph.py
step S26 "C56 C57" "dimension ten: re-certification of the 3,040 vectors, 57,680 pairs, 1,136 cliques, margin (Arb, own Krawczyk code)" "$R/d10" \
  "Krawczyk: 3040/3040 unique roots within 1e-30|||pairs with \|<u,v>\| < 1e-6: 57680|||10-cliques: 1136; identical to the stored list of bases: True|||4.17807" \
  nice -n 5 python3 check_d10.py "$R/d10/upstream_mub10"
step S27 "C57" "dimension ten margin in Arb with every coordinate widened to 1e-15 (1,272,177 pairs)" "$R/d10" \
  "distinct \(u,v\) pairs 1272177|||certified lower bound on margin: \[4.178074647" nice -n 5 python3 margin_arb.py
step S28 "C55" "dimension ten: all 34,940 cyclic 10-roots, boxes pairwise disjoint, 3,040 unimodular, 31,900 not, match with the stored list (Arb)" "$R/d10/roots_full" \
  "COUNTS: found=34940 certified=34940 unimodular=3040 certified_non_unimodular=31900 undecided=0 krawczyk_failed=0|||equal to matched set: True" \
  nice -n 5 python3 certify_roots.py cyclic10_roots.npz "$WORK/roots_out.npz" ../upstream_mub10/data/exact/bu10hp_unimod.txt 2

step S29 "C31 C33 C46" "bridge theorem: 5,000 Haar bases and 20 loss minimisations per triple, stored sets via polar factor, d=4 control" "$R/checks" \
  "^OK" nice -n 5 python3 check_bridge_theorem.py
step S30 "C27 C28" "closed-form minimiser psi* (50 digits) and own BFGS minima on T0 and T1" "$R/checks" \
  "E\(psi_\*\) = 0.0387627564304|||^OK" nice -n 5 python3 check_minimiser.py
step S31 "C56 C57" "dimension ten in float64 with own code: unimodularity, 57,680 edges, clique sizes, 1,136 bases, margin" "$R/checks" \
  "maximal cliques by size: \{2: 17700, 10: 1136\}|||^OK" nice -n 5 python3 check_d10_float.py

step S32 "C42" "purity witness: E(rho) <= tr rho^2 - 1/6 and lambda_max bound on 100,000 random states" "$R/hide_seek" \
  "bound at E = 0: 0.8230848|||^OK" nice -n 5 python3 check_purity_witness.py


# ---------------------------------------------------------------------------------------------------- added: closing the reproducibility gaps
# (Fourier pair: certified 156 -> 48 -> 16 -> 0 in ball arithmetic; 2008 table recomputed from the shipped raw search output)
step S33 "C14" "cyclic 6-roots: heuristic search (symmetry closure, group of order 288), then Arb certification of 156 roots: 48 unimodular, 108 not, boxes disjoint, 48 stored vectors matched" "$R/d6_fourier" \
  "COUNTS: found=156 certified=156 unimodular=48 certified_non_unimodular=108 undecided=0 krawczyk_failed=0 boxes_pairwise_disjoint=True stored48_match=True|||^OK" \
  nice -n 5 python3 -I certify_d6_roots.py find "$WORK/cyclic6_roots_new.npz" 1
step S34 "C14" "same certification from the shipped midpoints only (cyclic6_roots.npz)" "$R/d6_fourier" \
  "COUNTS: found=156 certified=156 unimodular=48 certified_non_unimodular=108 undecided=0|||^OK" \
  nice -n 5 python3 -I certify_d6_roots.py verify cyclic6_roots.npz
step S35 "C15 C16 C36" "orthogonality graph of the 48 vectors in ball arithmetic: 300 possibly-orthogonal pairs, 16 six-cliques covering 228, triples {I,F6,B} unbiased up to enclosure width, 120 pairs of bases certified apart" "$R/d6_fourier" \
  "possibly orthogonal \(enclosure contains 0\): 300; certified not orthogonal: 828|||maximal cliques by size: \{2: 72, 6: 16\}|||six-cliques: 16; edges covered: 228; vertices per clique count: \[2\]|||120 pairs of bases: smallest over pairs|||^OK" \
  nice -n 5 python3 -I certify_graph.py
step S36 "C53" "partial fourth bases {5,5,b,c} at the Fourier pair re-derived from the ball enclosures: only {5,5,1,1} and {5,5,2,1}; compared with the earlier program's json" "$R/d6_fourier" \
  "orthonormal sets \(cliques of the possibly-orthogonal graph\) by size: \{1: 48, 2: 300, 3: 316, 4: 240, 5: 96, 6: 16\}|||possible with c >= 1: \[\(1, 1\), \(2, 1\)\]|||constellations equal: True|||^OK" \
  nice -n 5 python3 -I check_partial_bases.py
step S37 "C53" "earlier program fourier_constellations.py rerun on a copy (reads the stored 48 vectors); output equal to the stored fourier_constellations.json" "$R/near_misses/repo/src/fourier" \
  "\"5,5,2,1\": true, \"5,5,2,2\": false|||min distance from 6 among non-unbiased pairs: 0.4307|||fourier_constellations.json identical to the stored file: True" \
  bash -c 'mkdir -p "$0/results/fourier" && cp ../../results/fourier/results.json "$0/results/fourier/" && mkdir -p "$0/src/fourier" && cp *.py "$0/src/fourier/" && (cd "$0/src/fourier" && nice -n 5 python3 -I fourier_constellations.py) && cmp "$0/results/fourier/fourier_constellations.json" ../../results/fourier/fourier_constellations.json && echo "fourier_constellations.json identical to the stored file: True"' "$WORK/fc"
step S38 "C49 C50 C52" "2008 table: every column of the 35 rows, 389 and 695 of 52,000, level counts, 4.99e-3, {5,3,3,3} run, explicit examples, recomputed from the shipped raw search output and compared with the report" "$R/near_misses" \
  "35 rows parsed|||seeds used by the 35 table runs: \[2026\]; starts per shape: \[2000\]|||389 of 52000 \(0.748%\)|||695 of 52000 \(1.337%\)|||^OK: every column of the 35-row table" \
  nice -n 5 python3 -I check_table.py ../report/report.tex
step S39 "C17" "the three explicit constellation examples of the third 2026 preprint: check_yale_examples.py rerun on a copy; output equal to the stored yale_examples_check.json" "$R/near_misses/repo/src/constellations" \
  "\"misfit\": \"2.8352e-40\"|||\"misfit_after_polish\": \"3.5639e-30\"|||yale_examples_check.json identical to the stored file: True" \
  bash -c 'mkdir -p "$0/results/constellations" "$0/src" && cp -r ../constellations "$0/src/" && (cd "$0/src/constellations" && nice -n 5 python3 -I -c "import sys,runpy; sys.path.insert(0,\".\"); runpy.run_path(\"check_yale_examples.py\", run_name=\"__main__\")") && cmp "$0/results/constellations/yale_examples_check.json" ../../results/constellations/yale_examples_check.json && echo "yale_examples_check.json identical to the stored file: True"' "$WORK/yale"
step S40 "C34" "stored record of the optimisation behind the explicit four-basis sets: 72 and 700 starts, best values, stored matrices" "$R/near_misses" \
  "bias optimisation: 72 starts recorded|||game optimisation: 700 runs recorded|||^OK" \
  nice -n 5 python3 -I check_visibility_records.py
step S41 "C70" "structure paper, Section 13 (numerical only): cube-Gram spectrum on the seed, operator inequality on random admissible operators" "$R/checks" \
  "PASS\] seed third transition C is a phase Hadamard|||PASS\] 1 - tr rho\^3 > 1/144|||NOT CHECKED\] requires the 55-variable" \
  nice -n 5 python3 check_seed_geometry.py
step S42 "C24, C23" "structure Lean project (lean_structure/): stored logs of its two builds, axiom logs and source hashes checked against the sources (no Lean needed)" "$R/lean_structure" \
  "PASS\] source hashes match hash-manifest.json|||PASS\] build log reports success: Build completed successfully \(3350 jobs\)|||PASS\] axiom log: audited theorems: 394 theorems|||PASS\] axiom log: only standard axioms|||PASS\] second build: log reports success|||PASS\] second build: the Lean files built there have the manifest hashes|||^OK" \
  nice -n 5 python3 -I check_logs.py
step S43 "C11" "full native rerun and Root re-certification: stored results of the original run and of the repeat on a second machine" "$R/openai_check/full_audit" \
  "original run: principal files byte-identical|||repeat on a second machine: Root records re-certified in Arb: read 27189, distinct certified 27188, transposed 1143, 128 bits|||100 invocations|||^OK" \
  nice -n 5 python3 -I check_recorded_evidence.py
step S44 "C55-C61 (dimension ten)" "symmetry orbits of the 3,040 vectors (10) and 1,136 candidate bases (19); exact orthonormality of the 96 candidate bases with coordinates in Q(zeta_20)" "$R/d10" \
  "PASS\] vector orbits: 10 orbits|||PASS\] candidate-basis orbits: 19 orbits|||PASS\] exact pairwise orthogonality inside each candidate basis made of these vectors: 96 bases, 4320 pairs|||^OK" \
  nice -n 5 python3 -I check_orbits_exact.py
echo
echo "=== SUMMARY: $NPASS steps passed, $NFAIL failed.${FAILED:+ Failed steps:$FAILED}"
echo "Not re-run here (stored logs only): hide_seek/hide_seek.py, d6_fourier/run_fourier6_certs.py, d10/search_match.py, d10/energy10.py, openai_check/* (the native rerun; its stored results are checked in S43), near_misses 20,000-start and 35-shape searches, near_misses/repo/src/fourier/fourier_case.py, evidence.py, the Lean builds (stored logs of the structure project are checked in S42)."
[ "$NFAIL" -eq 0 ]
