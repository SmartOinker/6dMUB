#!/usr/bin/env bash
# verify_all.sh: run every fast check of the repository in sequence and fail if any of them fails.
#
# Usage, from the repository root:   nice -n 5 ./verify_all.sh            (log: ./verify_all.sh 2>&1 | tee docs/verify_all.log)
# Runtime: about 10 to 11 minutes on a 2-core machine (the slowest steps are checks/check2.py, about 2.5 minutes, and
# checks/check_fourier6_graph.py, about 1 minute).  Exit status: 0 if every step passed, 1 otherwise.
#
# Safety: the repository is copied (without .git) into a temporary directory and every step runs in the copy, so the
# stored results (hide_seek/hide_seek.json, d6_fourier/fourier6*.json, near_misses/.../certificate.json, d10/*.npy, ...)
# are never overwritten.  The copy is deleted at the end (set KEEP=1 to keep it).
#
# NOT run here (too slow, or needs software/data that is not in the repository), see docs/verification_matrix.md:
#   hide_seek/hide_seek.py (Qiskit, Monte Carlo, overwrites hide_seek.json), hide_seek/fig.py (matplotlib, figures only),
#   d6_fourier/run_fourier6_certs.py (about 30 min: it re-solves the 16 SDPs; the checker verify_fourier6_certs.py IS run),
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
step S01 "C4 C5 C26 C28" "degree-six interval certificate, canonical triple T0 (Arb checker)" "$R/cert" \
  "CERTIFIED \(T0\):  E\(psi\) >= 0.0385 - S  >  0.038499999998|||residual bound S <= 2.189e-12|||<= 9.550e-15" \
  nice -n 5 python3 verify.py 0.0385 Q_T0_gamma0.0385.npy T0
step S02 "C4 C5 C26 C28" "degree-six interval certificate, second product triple T1 (Arb checker)" "$R/cert" \
  "CERTIFIED \(T1\):  E\(psi\) >= 0.0235 - S  >  0.023499999997|||residual bound S <= 2.807e-12" \
  nice -n 5 python3 verify.py 0.0235 Q_T1_gamma0.0235.npy T1
step S03 "C34 C35 C37 C38 C39" "bias and game bounds for any fourth basis, and the two explicit four-basis sets (Arb)" "$R/cert" \
  "exact set has worst-case bias delta <= 0.030223872|||shortfall <= 2.357825e-04|||T0: any 4 bases containing it:  delta >= sqrt\(g/18\) > 0.046248 ;  game shortfall >= c\*g/72 > 3.302291e-04|||T1: any 4 bases containing it:  delta >= sqrt\(g/18\) > 0.036132 ;  game shortfall >= c\*g/72 > 2.015684e-04" \
  nice -n 5 python3 verify_sets.py ../near_misses/repo/results/visibility/bases_d6_delta.npy ../near_misses/repo/results/visibility/bases_d6_P4.npy
step S04 "C4 C5 C28 C41" "second implementation: pointwise test of the stored Gram matrices (numpy, no monomial expansion, no Arb)" "$R/checks" \
  "T0 \(Q_T0_gamma0.0385\): max .*min eigenvalue of Q|||Fourier-pair triples by certified level: \{'0.0324': 12, '0.0235': 2, '0.0385': 2\}|||^OK" \
  nice -n 5 python3 check_cert_pointwise.py
step S05 "C14 C41 C42" "Fourier pair: the 16 stored Gram matrices re-checked in Arb (third-basis vectors re-certified inside)" "$R/d6_fourier" \
  "minimum certified bound over the 16 triples: 0.0234999999946|||triple 15: numerical min 0.0326759; degree-6 relaxation nan; CERTIFIED E >= 0.0324000000" \
  nice -n 5 python3 verify_fourier6_certs.py
step S06 "C32" "degree-six moment relaxation (SCS, tolerance 2e-4): 0.0383285692" "$R/checks" \
  "relaxation optimum = 0.0383285692" nice -n 5 python3 sos.py 6 SCS 2e-4
step S07 "C32" "degree-six moment relaxation (SCS, tolerance 1e-5): 0.0386693296" "$R/checks" \
  "relaxation optimum = 0.0386693296" nice -n 5 python3 sos.py 6 SCS 1e-5

# ---------------------------------------------------------------------------------------------------- bridge, game, detection
step S08 "C33" "square-root lemma: 1.8 million random squared overlaps plus a grid of 2,000,001 points" "$R/checks" \
  "random points tested: 1800000|||grid points tested: 2000001|||OK: no violation" nice -n 5 python3 check_sqrt_lemma.py
step S09 "C10 C13 C29 C35 C36 C39 C44 C46 C47 C49 C50 C51 C53 C55 C56 C64 C66 C68" "independent recomputation of derived numbers and of stored-result summaries (mpmath, Fractions, scipy)" "$R/checks" \
  "smallest N with miss <= 0.05 is 2892|||smallest N with miss <= 0.01 is 14957|||238.79, 197.54, 368.07 shots per setting -> 239, 198, 369|||\{0.0: 589, 0.0001: 589, 0.001: 594, 0.01: 646, 0.1: 1500\}|||all rational comparisons of Appendix A.3 hold exactly|||17 of 26 detected|||18 shapes have a nonzero 2008 rate|||^OK" \
  nice -n 5 python3 check_report_arithmetic.py
step S10 "C43 C44 C45 C46" "finite-sample theorem: exact enumeration N = 2,3,4, variance bound, shot counts, Monte Carlo at N = 2892, chi-square comparison" "$R/hide_seek" \
  "needs N = 2892 shots per setting|||needs N = 14957 shots per setting|||needs N = 4189 shots per setting|||needs N = 21617 shots per setting|||missed detections \(T < gamma/2\): 0 of 20000|||^OK" \
  nice -n 5 python3 finite_sample.py

# ---------------------------------------------------------------------------------------------------- near-misses, 2008 table
step S11 "C54 C55" "2008 near-misses: independent 60-digit evaluation (mpmath, no shared code with the certificate)" "$R/near_misses" \
  "shape \[4, 4, 1\]: misfit = 0.00102497683851953369499|||shape \[5, 3, 1\]: misfit = 0.0007327886563036878044317|||20 perturbed restarts returning to the same misfit: 20/20" \
  nice -n 5 python3 indep.py
step S12 "C54 C55" "2008 near-misses: Arb interval certificate rerun (on a copy: the script overwrites certificate.json)" "$R/near_misses/repo" \
  "441 overall: True|||531 overall: True|||432 overall: True|||442 overall: True" \
  nice -n 5 python3 src/constellations/certify/certify.py
step S13 "C54 C55" "regenerated certificate.json equals the original one in every field except run times" "$R/near_misses" \
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
step S14 "C19 C36 C37" "cube-rank enumeration (1,395 systems), game numerics, sqrt-inequality summed form" "$R/checks" \
  "clique counts sizes 0..5: \[1, 30, 135, 120, 60, 12\]|||k = 3 systems: 1215 nullity histogram: \{0: 1160, 1: 54, 3: 1\}|||P_4 deficit \(average over 6 pairs\) = 0.00150636" \
  nice -n 5 python3 check2.py
step S15 "C25 C29 C30" "energy identity, witness minimiser, 400 BFGS minimisations on T0" "$R/checks" \
  "min E over 400 starts: 0.0387627564304205|||distinct local minima values: \[0.0387628\]|||witness: x\+y\+z = 1.0" nice -n 5 python3 check1.py
step S16 "C31" "second product triple: numerical minimum 0.0238354, thresholds" "$R/checks" \
  "T1 \(third basis \|0_y>B2, \|1_y>B3\) min E = 0.0238353|||c = 0.6175713839378697" nice -n 5 python3 check3.py
step S17 "C22 C32" "degree-four moment relaxation: optimum about 0, numerical rank 63" "$R/checks" \
  "relaxation optimum = -0.0000000207|||numerical rank \(>1e-7\) 63" nice -n 5 python3 sos.py 4
step S18 "C22" "degree-four obstruction: exact check over Q(sqrt3) of an independently built functional (rank 63, L(E)=0, L(N^2)=1)" "$R/checks" \
  "M c_l = 0 verified exactly: 1404 equations|||63 strictly positive pivots, remaining Schur block 15x15 exactly zero: True|||^OK" nice -n 5 python3 check_quartic_sos.py
step S19 "C19 C20" "Hadamard identities, cubic cap, cube ranks on Fourier-family, Tao, Dita and 700 numerical Hadamard matrices" "$R/checks" \
  "^OK" nice -n 5 python3 check_hadamard_identities.py
step S20 "C21" "six-phase bound: constrained maximisation from 4,000 starts, extremal configuration in 50 digits" "$R/checks" \
  "largest \|sum z\^3\| found      : 5.7154760665|||starts reaching the bound within 1e-6: 445|||^OK" nice -n 5 python3 check_sixphase.py
step S21 "C25 C26" "analytic gap E > 1/72: every step inequality of Appendix A.3 on 200,000 states, exact fractions, total variation" "$R/checks" \
  "min E                                                       3.876276e-02|||^OK" nice -n 5 python3 check_gap72.py
step S22 "C13" "sharp phase-ball radius: 0.2242139, sharpness, convexity, Jensen step" "$R/checks" \
  "s\* = 0.22421389884043780|||^OK" nice -n 5 python3 check_phase_ball.py

# ---------------------------------------------------------------------------------------------------- dimension six Fourier pair, dimension ten
step S23 "C14 C15 C16 C17 C40" "Fourier pair: second program fourier6.py rerun (48 vectors, 300 pairs, 16 bases, minima) on a copy" "$R/d6_fourier" \
  "Krawczyk \+ unimodularity: 48/48 certified within 1e-30|||orthogonal pairs: 300|||candidate third bases \(6-cliques\): 16|||distinct minima: \[0.023835 0.032676 0.038763\]" \
  nice -n 5 python3 fourier6.py
step S24 "C14 C16 C17 C40" "rerun output equals the stored fourier6.json and fourier6_vecs.npy (originals read from the repository)" "$R/d6_fourier" \
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
step S25 "C15 C16 C17 C40" "Fourier funnel 156 -> 48 -> 16 -> 0 re-derived in floating point with own code (graph, 120 pairs, own Newton search for 156 roots, minima)" "$R/checks" \
  "156 distinct cyclic 6-roots found \(classical count 156\), 48 unimodular|||16 six-cliques, largest clique 6; they cover 228 of 300 edges|||\[12, 2, 2\] triples|||^OK" nice -n 5 python3 check_fourier6_graph.py
step S26 "C61 C62" "dimension ten: re-certification of the 3,040 vectors, 57,680 pairs, 1,136 cliques, margin (Arb, own Krawczyk code)" "$R/d10" \
  "Krawczyk: 3040/3040 unique roots within 1e-30|||pairs with \|<u,v>\| < 1e-6: 57680|||10-cliques: 1136; identical to the stored list of bases: True|||4.17807" \
  nice -n 5 python3 check_d10.py "$R/d10/upstream_mub10"
step S27 "C62" "dimension ten margin in Arb with every coordinate widened to 1e-15 (1,272,177 pairs)" "$R/d10" \
  "distinct \(u,v\) pairs 1272177|||certified lower bound on margin: \[4.178074647" nice -n 5 python3 margin_arb.py
step S28 "C60" "dimension ten: all 34,940 cyclic 10-roots, boxes pairwise disjoint, 3,040 unimodular, 31,900 not, match with the stored list (Arb)" "$R/d10/roots_full" \
  "COUNTS: found=34940 certified=34940 unimodular=3040 certified_non_unimodular=31900 undecided=0 krawczyk_failed=0|||equal to matched set: True" \
  nice -n 5 python3 certify_roots.py cyclic10_roots.npz "$WORK/roots_out.npz" ../upstream_mub10/data/exact/bu10hp_unimod.txt 2

step S29 "C34 C36 C37 C48" "bridge theorem: 5,000 Haar bases and 20 loss minimisations per triple, stored sets via polar factor, d=4 control" "$R/checks" \
  "^OK" nice -n 5 python3 check_bridge_theorem.py
step S30 "C29 C30 C31 C40" "closed-form minimiser psi* (50 digits) and own BFGS minima on T0 and T1" "$R/checks" \
  "E\(psi_\*\) = 0.0387627564304|||^OK" nice -n 5 python3 check_minimiser.py
step S31 "C58 C61 C62" "dimension ten in float64 with own code: unimodularity, 57,680 edges, clique sizes, 1,136 bases, margin" "$R/checks" \
  "maximal cliques by size: \{2: 17700, 10: 1136\}|||^OK" nice -n 5 python3 check_d10_float.py

echo
echo "=== SUMMARY: $NPASS steps passed, $NFAIL failed.${FAILED:+ Failed steps:$FAILED}"
echo "Not re-run here (stored logs only): hide_seek/hide_seek.py, d6_fourier/run_fourier6_certs.py, d10/search_match.py, d10/energy10.py, openai_check/*, near_misses 20,000-start search."
[ "$NFAIL" -eq 0 ]
