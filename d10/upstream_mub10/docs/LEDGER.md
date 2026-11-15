# MUB-10 claims ledger (orchestrator; updated 2026-11-14 21:50 PT)

Status words: PROVED (pen and paper), CA (computer-assisted, with what it rests on), NUM (numerical evidence),
CITED, OPEN. "Checked by" lists independent re-verifications; a claim with none is unconfirmed.

## A. Unconditional bounds
- A1. 3 <= N(10) <= 11, N(10) != 10. CITED (tensor product; Wootters-Fields; Weiner arXiv:0902.0635).
  Weiner does not exclude 9 (reading helper, via a summarising reader: verify wording in the PDF before citing).

## B. Fourier pair {I, F_10}  (exact lead; data in exact/data, code in exact/code)
- B1. Vectors unbiased to I and F_10 (x_0 = 1) = unimodular solutions of sum_j x_{j+s}/x_j = 0, s=1..9. PROVED (standard).
- B2. 34,940 distinct nonsingular solutions found, each Krawczyk-certified in Arb, boxes pairwise disjoint; 49 orbits.
  CA. Completeness rests on the published count 34,940 (Faugere 2001; Fuhr-Rzeszotnik table). Checked by: [rootcheck helper: pending]
  [Open Math OS session A, independent PHCpack/msolve route: pending].
- B3. Exactly 3,040 are unimodular (fixed-point argument for x -> 1/conj(x)), 31,900 certified not. 10 orbits
  (800, 400x4, 200x3, 20x2). CA, rests on B2. Checked by: [rootcheck helper: pending]. NUM cross-check: 1M-start phase
  search finds the same 3,040, each hit >= 105 times; Open Math OS session B independent count: pending.
- B4. Every orthonormal basis unbiased to I and F_10 is one of at most 1,136 ten-subsets (10-cliques of the
  possibly-orthogonal graph, 57,680 edges). CA, rests on B3. That all 1,136 ARE bases: NUM (zeros to 1e-40; intervals cannot
  prove exact zero). 19 orbits; 16 are product bases incl. eigenbases of XZ^{+-1}, XZ^{+-3}; 1,120 are neither product nor Weyl.
  Checked by: [basischeck helper: pending].
- B5. No listed vector is unbiased to any of the 1,136 candidate bases => every MU triple {I, F_10, B} is strongly unextendible;
  no 4 MUBs contain {I, F_10}. Min pair defect 4.178. CA, rests on B2-B4. Checked by: [basischeck helper: pending].
  Contains as a special case the uncertified claim of arXiv:1611.08962 for the Heisenberg-Weyl triple in d = 10.
- B6. Affine Fourier family, 4 random parameter points: 1480/1680/1840/1760 vectors, 148/168/184/176 bases, no MU pair,
  no extending vector. NUM, no completeness claim.
- Calibration: d=6: 156 roots, 48 vectors, 16 bases, no MU pair. d=7: 924 roots, 532 vectors, 146 bases, 6 forming the complete set.

## C. Constellations {9,a,b,c}_10 (theory lead; theory/certs, theory/candidates)
- C1. Krawczyk existence certificates (Arb) for 64 of 165 three-group shapes (counting sub-shapes of certified ones). CA.
  Maximal certified: (9,1), (8,3,1), (8,2,2), (7,5), (7,4,2), (7,3,3), (6,6,1), (6,5,2), (6,4,3), (5,5,4) [no symmetry];
  (5,5,5) [D5 orbits, 3-parameter family], (6,6,2), (6,4,4), (9,2,2) [D2 symmetry]. Largest s = a+b+c certified: 15.
  Checked by: certcheck helper (Sonnet), own vectors + own Krawczyk at 400 bits: (5,5,4), (5,5,5), (9,2,2) CONFIRMED;
  100-digit direct check of all pair conditions, max violation < 1e-95. Wording fixes: radius is about the polished centre,
  not the stored float64 point; uniqueness only within the frozen slice; (9,2,2) first group is a full basis of 10.
- C2. Counting conventions. Ours: unknowns 9(s-1), real equations 2*(orth pairs) + (cross pairs). Brierley-Weigert: p=(d-1)(s-1),
  c = s(s-1)/2, critical at s = 2(d-1) = 18. Under BW, (5,5,5) and (9,2,2) are UNDERdetermined. Do not say "overdetermined"
  without naming the count. BW expect {9,x,y,z}_10 with x+y+z = 18 unlikely except three MUBs (reading helper; verify in PDF).
- C3. Minimal open shapes (our count): (9,3,1), (8,4,1), (8,3,2), (7,5,1), (7,4,3), (6,5,3). OPEN; CPU job on the PC.
  Best (7,5,1) end point misfit 6.7e-6, full-rank local minimum (NUM).
- C4. Exclusion lemma: no zero within rho of x0 where (H^2/4) rho^4 + 2 g rho = m0^2, H = 2(2d-1)/sqrt(d) * sqrt(k(G-1)). PROVED
  (theory/exclusion.md; not yet independently checked). Local only.

## D. Random-start search, four MUBs and ladders (numerics lead code; GPU lead runs)
- D1. Code gates (CPU): d=6 near-misses reproduced to 10 digits; d=5 (4,4,4) 52.7%/start; d=7 (6,6,6) 0.44-0.46%/start. NUM.
- D2. HW triple + 1 vector, d=10: 0/13,891, best misfit 1.4580913946; tensor triple same value. NUM (CPU).
  The theory lead's 2.475 and Open Math OS session B's 2.474828697 (HW triple, 4496 of 6000 starts, Jacobian rank 9) use all 10
  vectors of each fixed basis (20 residuals); the numerics lead's 1.458 uses 9 per basis (18 residuals). Likely explanation of the
  difference; confirm by evaluating one end point under both conventions (referee item). Either way these are landscape numbers:
  B5 is the rigorous statement for the HW triple.
- D3. GPU: benchmark, controls d=8,9,11, (9,9,9) main, ladder (9,9,k): pending.

## E. To resolve / referee list
- 34,940 count: independent confirmation (Open Math OS A).
- D2 discrepancy.
- Verify BW and Weiner wording from PDFs.
- "At most 1,136" vs "exactly 1,136" bases: exact orthogonality would need algebraic numbers (roots of unity? check whether the
  3,040 vectors have closed forms).

## Updates
- 21:46 PT. basischeck helper (Sonnet, own code; networkx cliques; float64 with a stated 1e-13 bound on Gram entries, margins >= 0.0089):
  B4 CONFIRMED given the list of 3,040: 57,680 possibly-orthogonal pairs (largest 1.8e-15), smallest non-orthogonal |<u,v>| = 0.0089515,
  1,136 ten-cliques and none larger, identical to the lead's list. B5 CONFIRMED given the list: min over (B, v) of max defect 4.17807;
  min over basis pairs 4.17807. Orbit note: 19 basis orbits only if the Fourier transform is included as a symmetry; 34 under shift,
  modulation, dilation, conjugation alone. XZ eigenbasis is among the cliques. Helper's own d=6 calibration: 48 vectors, 16 bases, no MU pair.
  Not covered: completeness of the 3,040 list (rootcheck helper and Open Math OS A).
- 21:49 PT. rootcheck helper (Sonnet, own code, python-flint): B2 CONFIRMED: 34,940/34,940 rows Krawczyk-certified (arb 192 bits,
  centres polished at 256 bits), existence radius 1e-50, uniqueness radii 5.8e-6..0.67, polydiscs pairwise disjoint (KD-tree; margin
  factor >= 7.8), all roots simple; x -> z bijective (34,940 distinct z). B3 CONFIRMED: 3,040 unimodular by the fixed-point test,
  31,900 certified off the torus, none undecided (nearest non-unimodular ||x|-1| = 0.38). Lemma E_s(x*) = conj(E_{10-s}(x)) proved by
  hand. Orbits under the order-1600 group: unimodular 10 orbits {20:2, 200:3, 400:4, 800:1}; others 39 orbits. Own n=6 calibration:
  156 roots, 48 unimodular. Minor: disjointness test in float64 with 1e-12 slack.
- Completeness logic (orchestrator): we hold 34,940 distinct simple roots. If the published 34,940 counts with multiplicity or
  without, there is no room for another root either way. Unconditionally, Bernstein's bound (mixed volume 35,940, reported by
  Open Math OS A from PHCpack; exact combinatorial quantity) leaves room for at most 1,000 further roots. A mod-p Groebner degree is
  NOT a rigorous upper bound (roots can go to infinity p-adically), so only a rational Groebner basis or a certified count closes it.
- 21:50 PT. Exact lead resumed for phase 2: write-up, exact algebraic forms, classification of the triples {I,F_10,B}, plan for the
  affine family.
- 22:00 PT. Exact lead phase 2 (exact/THEOREM.md). (a) 96 of the 1,136 candidate bases proved to be bases EXACTLY (arithmetic in
  Q(zeta_20); entries zeta_20^a or zeta_20^a u^{+-1}, u = (-sqrt5 + 2i)/3; basis orbits 12-18), so 96 <= #bases <= 1,136. The other
  1,040 involve algebraic numbers of degree >= 8 (orbit 2: degree 8 and 16 by PSLQ, NUM); not exact. Not independently checked yet.
  (b) Triples {I,F_10,B}: 17 to 19 equivalence classes (triple-product invariant takes 17 values; 19 group orbits); 5 classes are
  product/Weyl (16 bases); 14 classes cover the 1,120 others, several giving isolated (defect 0) Hadamard matrices. NUM/CA mixed;
  novelty unknown (catalogue helper launched). (c) Affine-family extension: naive rigorous cover needs 1e10-1e12 boxes, infeasible;
  near-term target is a neighbourhood of the centre. (d) BKK does not exclude positive-dimensional components; finiteness for n = 10
  is part of the cited Groebner result.
- GPU lead report 21:46: env OK (torch 2.11 cu128), gates on preview code agree with CPU; (9,9,9) d=10 at 156 starts/s mixed vs 39 f64;
  d=7 (6,6,6) 0.40% f64 / 0.49% mixed per start. Queue re-prioritised at 21:51 (controls d=8,9,11; main; ladder; survey).
- 22:04 PT. Catalogue helper (Sonnet, web, via a summarising reader; helpers/catalogue_check.md). Known order-10 Hadamards: F10^(4),
  D10, X10, S10 (isolated, BH(10,5); McNulty-Weigert arXiv:1208.1057), N10A, G10; Bruzda arXiv:2204.11727 lists isolated non-Butson
  circulant matrices V10A/V10B/V10C with Haagerup-set sizes 109/134/251, which equal three of our sizes, so our isolated matrices are
  PROBABLY Bruzda's (inference; entries not compared). Fuhr-Rzeszotnik Sec. 10.3: 3,040 numerical, same orbit sizes as ours, no closed
  forms, says no complete list exists for n = 10. Not found in the literature searched: a list or count of MU triples containing
  {I,F_10}; the 1,136 bases; strong unextendibility with certificates; the number u = (-sqrt5+2i)/3 in this context. The count
  34,940 was found only in the Fuhr-Rzeszotnik table (helper could not open Faugere's paper). Before any novelty claim: compare
  entries with Bruzda's scripts, read review Secs 6.10 and 7.3, locate the primary source for 34,940.
- 22:12 PT. Sourcing of (H) = 34,940 (orchestrator web check). Steel's Magma timings page (2004): cyclic-10 MODULO A PRIME is
  zero-dimensional with quotient dimension 34,940; says only Faugere had computed it before. Parisse arXiv:1903.12427: Groebner basis
  of cyclic-10 over Q with Giac (2019); count not seen stated. A degree mod one prime is not a rigorous bound over Q. So (H) is
  "widely reproduced computation", weaker than "proved in print". Mitigations in progress: Open Math OS A asked for the degree over Q;
  general-pair lead asked for an exact deficiency count via face systems (Bernstein B).
- 22:00-22:10 PT. GPU lead (msgs 0003-0005): final-code gates pass on GPU; d6 (4,4,1) 1.0249768385190165e-03 and (5,3,1)
  7.327886563031523e-04 reproduced; independent misfit checker (own code, mpmath 40 digits) agrees to 1e-12 relative; HW triple + 1
  vector best 1.4580913946 (matches cloud). Method notes adopted: time-budgeted success rates are completion-biased, report
  [conv/(n+abandoned), conv/n]; d6 (4,3,1) has a genuine critical point at misfit 1.59e-11, so every d=10 end point < 1e-8 goes
  through 40-digit inspection. theory-overdet-1 at t=1184 s: 0 converged in all targets; (7,5,1) best 2.612e-06.
- 22:06 PT. Launched: general-pair lead (Opus; Bernstein saturation for unconditional completeness; other Hadamard pairs) and
  upper-bound scout (Opus; SDP / Delsarte / structural routes to N(10) <= 9, 45-minute feasibility).
