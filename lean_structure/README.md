# Verified MUB proof integration: 394 public theorems

This snapshot contains 46 modules and 89 private theorem helpers. It retains all 387 public results from the frozen baseline and adds seven statements in one module. Counts are proof declarations, not discoveries or priority claims.

## New actual Fourier and two-dimensional frame obstructions

`MUBNormalizerObstructions` defines the actual primitive cubic root and three-point unnormalized Fourier transform, proves its Parseval identity, and proves that no unit-modulus complex triple w makes every entry of F(1+w) have squared modulus 6. Parseval forces zero real part of sum(w), while the zeroth coefficient then has squared modulus at least 9.

For an actual 2-by-3 complex matrix of three vectors, it constructs the actual Gram and frame operators and proves the squared Frobenius identity for VV*-(3/2)I2. Unit columns with pairwise squared inner products 1/6 would give that nonnegative square the value -1/2, a contradiction. No Fourier-energy, rank, spectral or Welch bound is assumed.

These formally verified arithmetic facts support the separately written fixed-ray common-normalizer argument. The spectral and gauge reduction into these coordinates, the four coherent T1 equivalences, the projective normalizer group-order restrictions, and global symmetry existence remain outside Lean. The package does not formalize the complete new normalizer classification.

## Retained actual differential and two-dimensional local seed chart

`MUBSeedDifferential` defines the actual equation F(theta,phi)=sum z_j exp(i theta_j)+sum w_j exp(i phi_j), where z and w are consecutive unit ratios of u,v, on the explicitly defined mean-zero subspace of R6. It proves genuine strict real Frechet differentiation, identifies the derivative with the verified coefficient matrix, and derives bounded surjectivity. The squared coordinate Euclidean bound is <=(2/3)|eta|²; no differently scaled Pi operator norm is claimed.

Exact unit-modulus and product-one preservation is proved for the perturbed ratios. The explicit reconstruction u(theta)=(u0,u1 exp(i theta0),u2 exp(i(theta0+theta1))) has exactly those ratios. F=0 is proved equivalent to actual unitarity of the reconstructed Hankel block; unitarity away from the base point is not assumed.

`MUBSeedLocalChart` gives the actual domain an explicit linear equivalence with R4, derives actual derivative kernel dimension2, and instantiates Mathlib strict IFT into an open partial homeomorphism with first coordinate exactly F. Its inverse exhausts the full nearby seed zero set using a two-dimensional kernel. This is an actual structured-family chart, not a generic rank or chart hypothesis. It does not exhaust arbitrary MUB triples or prove global seed topology.

## New actual Vandermonde restriction and cube-rank dichotomy

`MUBSunDiscriminant` proves the actual ratio Vandermonde norm identity27-18q-q²+8Re(gamma³). Opposite correlations give q²+18q<=27, hence q<=6sqrt(3)-9<3/2. Equality in the quadratic bound is equivalent to both actual Vandermondes vanishing; no attaining point or priority claim is supplied here.

The actual cube Gram determinant is (18-12q)²(6q)⁴. For q!=0 the actual cube determinant is nonzero and its matrix rank is6. For q=0 the actual residual vanishes and the previously formal residual-to-rank theorem yields rank2. Thus the actual block cube rank is exactly2 or6; a rank4 stratum cannot occur in this structural family. No characteristic polynomial or desired rank is assumed.

## Retained uniform projected ratio-angle coefficient theorem

`MUBUniformSubmersion` constructs the actual real 2-by-6 matrix L whose columns are real/imaginary parts of the mean-subtracted ratio coefficients i(z_j-gamma(u)/3), for z_j=u_(j+1)conjugate(u_j), and similarly v. From unit u,v and actual Hankel-block unitarity, it derives the actual Gram, characteristic polynomial (X-(3-q))(X-(3+q/3)), and uniform quadratic lower bound (3/2)||a||². Cancellation, parameter range, Gram pattern and nonsingularity are derived, not assumed.

It proves the projected coefficients act on the mean-zero angle domain as the corresponding uncentered complex ratio variation. The actual right inverse K=Lᵀ(LLᵀ)^(-1) satisfies LK=I, lands in both mean-zero triples, and obeys sum(Ky)_i² <=(2/3)sum y_j². The final theorem gives every output an explicit bounded preimage in that domain. This uses the inherited Euclidean metric on the two mean-zero subspaces of R³, not an unweighted dephased phase-coordinate metric.

The analytic differentiation and local ratio-equation/actual-block bridge are now formal in the new modules above. The composed physical Sun A†B transition and registration bridge remain written. There is no claim that this package formalizes a global Jacobian or unrestricted MUB exclusion.

## Retained actual block cube invariants and finite gluing controls

`MUBSunCubeGram` defines the actual unregistered 6-by-6 Hankel-block matrix with unit ternary vectors u,v. From its actual unitarity C†C=6I, it derives gamma(v)=-gamma(u), the Newton cancellation, the full entrywise-cube Gram pattern and the range 0<=q<=3/2, where q=|gamma(u)|². No desired Gram, range or residual inequality is assumed.

`MUBSunCubeSpectrum` gives an explicit parity reindexing and actual 3-by-3 characteristic-polynomial calculation. The actual cube Gram characteristic polynomial is (X-(18-12q))²(X-6q)⁴; factors coincide at q=1.

The actual phase-scale deficit is identified with the literal cube of C/sqrt(6). Its value is q(2-q)/108; the actual Frobenius residual energy is 2592q(3-q²). The zero equivalences, sharp maxima 1/108 and 5184, equality iff q=1, unit entries, and an explicit q=1 block witness are formal. The composed physical Sun seed-to-block calculation and arbitrary registration-gauge invariance remain written; the witness is not claimed to be the previously registered full Sun triple.

`MUBSeedGluing` checks the actual S3xS3 face set and six explicit edge moves: 36 faces, 108 edge orbits, 54 corner orbits, Euler characteristic -18 and actual edge-path connectivity. Its finite statements do not identify the continuous seed with a surface or prove genus 10; that analytic/topological bridge remains written.

## Retained crossing algebra and mixed-projector transport

`MUBLocalGermAlgebra` proves ideal invariance under an actual invertible coefficient matrix over any commutative ring. It verifies the explicit mixed 4-by-4 matrix determinant -4+2sqrt(3), including nonvanishing. If a matrix of real formal power series has this constant coefficient matrix, its determinant is a unit and it preserves the generated ideal. The derivative origin of the matrix and the analytic coordinate charts remain outside Lean.

`MUBCoordinateProductIdeal` proves from actual polynomial supports that disjoint coordinate-ideal products equal their intersection. A coefficientwise argument identifies coordinate ideals with actual ring-homomorphism kernels. Over any integral domain, the four-generator ideal (X0X2,X0X3,X1X2,X1X3) is therefore the intersection of two prime coordinate ideals and is itself radical, with a reduced polynomial quotient. This does not formalize the corresponding reducedness for power-series or analytic rings, nor identify the actual MUB analytic germ.

`MUBMixedTransport` derives the overlap and factorization of three actual repetition-frame projectors, their partial trace and trace, and the centered norm identity with factor 1/36. The algebraic identities assume no unitarity. Only the centered formulas require the actual B unitary and flatness conditions. No target factorization or residual identity is a hypothesis.

## Retained actual small Gram certificates

`MUBFourLineForms` checks the 10 antipodal representatives, their actual tight-frame entries, and the actual characteristic polynomials of all 8 normalized four-line Gram forms, with 1/1/6 multiplicities. Normalization of arbitrary four classes into these forms remains written.

`MUBBalancedSmallTables` defines actual rational Gram and centering matrices, verifies five inverses, checks all 80 sign extensions and 62 positive Schur cases, and derives the actual cubic trace bound <25/2. A separate theorem bounds a five-value square-root sum using nonnegativity and equality of the first three power sums with these actual trace moments. This is an explicit conditional bridge; the actual matrix/eigenvalue correspondence remains written.

`MUBMatchingGram` verifies an actual balanced sign witness, its Gram matrix, the polynomial null-projector identities for all 64 signed matching forms, an arbitrary rational vector kernel characterization, and the exact imbalance alternatives 0,24,32,56,64. Classification of all optimizing Gram matrices into the matching form remains written.

Those 22 retained statements use kernel-checked finite reduction, exact polynomial arithmetic and ordinary real inequalities. No desired trace or nuclear bound is a premise. The full centered nuclear maximum, regular-Hadamard distance >7/2, physical distance >21, analytic crossing-germ classification and global MUB exclusion are not formalized by them.

## Actual balanced-phase Gram separation

The retained balanced-row subtype has exactly 20 Boolean six-vectors with three plus and three minus signs. Kernel-evaluated finite proofs give their zero sums and pair dot products in {-6,-2,2,6}. For any six such rows, the constructed complex matrix is exactly

    S=(J+i sqrt(5) H)/sqrt(6).

The phase formula, unit entries, row sums sqrt(6), and actual Gram entries are derived. The main theorem proves

    ||SS*−6I||_F² >=160/3.

A direct corollary proves SS* !=6I for these actual matrices. No desired Gram/coherence inequality is assumed, and the proof uses no external finite checker or native evaluation. The scalar spectral-envelope module separately proves the exact q-majorant factorization, q(x)>=sqrt(x) for x>=0, and kappa>2. Its e²>7/5 conversion has the displayed scalar Gram-error inequality as an explicit premise; the corresponding matrix-norm comparison is not formalized.

The exhaustive 177100-case Procrustes bound, regular-Hadamard distance>7/2, physical tensor distance>21, and complex-component classification remain written/exact results outside this Lean integration.

## Retained direct trace result

`MUBDensityTrace.canonical_density_trace_deficit` proves 1−Re tr(R³)>1/144 from Hermiticity, purity one and actual canonical uniform expectations. No positivity or spectral-decomposition premise is assumed. The numerical 1/5184 anchor specialization remains a written consequence, not an extra theorem.

## Actual measurement-to-density bridge

MUBMeasurementProjectors constructs actual canonical projectors in the C=D²F coefficient coordinates of the existing Born theorem. It proves positivity, trace-one idempotence, agreement with Born probabilities and canonical relabeling, the full cross-basis Gram table, completeness and centered Gram values. No generic overlap premise replaces the calculation. The first canonical measurement is not assumed coordinate-diagonal.

MUBMeasurementBessel derives the exact square identity ||R−Z||²=||R||²−E(R) and actual Bessel bound. Hermitian coefficients and the uniform-density distance comparison are derived, not assumed.

MUBDensityGap connects this with the prior formal canonical Born gap. A Hermitian R with all actual canonical expectations equal to 1/6 has squared Frobenius distance >1/72 from every normalized pure state. Trace one follows from completeness. Adding tr(R²)=1 gives:

    (143/144) I − R  positive definite,
    Q − R²/144      positive semidefinite, Q=R²−R³,
    ker(Q−R²/144) = ker R,
    u†(Q−R²/144)u > 0 iff R u != 0.

Every vector/anchor in the actual coefficient space is covered. Positivity or idempotency of R, trace one, the cubic bound, and a Bessel inequality are not hypotheses. Purity one and uniformity in this specific canonical triple are essential. This is a derived formal refinement of the known canonical gap, not a new unrestricted MUB exclusion or priority claim. The prior sharp optimum is not substituted for the verified conservative 1/72.

## Retained scope

The baseline retains the actual phase-tensor and tetrahedral quartet equivalences, anchored projector/principal-minor identities, the 3+2+1 polynomial envelope, physical partial-trace transport, residual/cap bounds, and generic Mathlib IFT local-exhaustion interface. The concrete Sun IFT/minor instantiation and full six-phase sharp proof remain written, outside Lean. The cube cap still assumes Fourier vanishing. The two upstream adapters and full upstream certificate closure remain separate. Universal three-edge purity-product vanishing and unrestricted quartet exclusion remain unproved.

## Reproduction

Run `bash verify.sh` with Lean 4.35.0 and Mathlib revision `56a005855ea17e0b0958f73ec801ae140b0a1679`. Local symlinks reuse a prepared cache; a fresh archive needs the pinned environment. Verification builds all 46 modules, directly re-elaborates the new module, checks every public theorem's transitive axioms and prints key signatures/definitions. The 45 baseline sources preserve historical direct-check evidence and are rebuilt here.

Only `propext`, `Classical.choice` and `Quot.sound` are allowed. Private helpers are kernel checked and audited transitively. Placeholders, native_decide and custom axioms are forbidden. New modules are warning-free; unchanged baseline style warnings remain.

All 46 local proof hashes are mandatory. Original workspace paths are optional corroboration. The portability tests verify absent-path behavior and rejection of altered baseline/new proof files; they do not repeat Lean builds in temporary fixtures. See verification.json, hash-manifest.json, integration-provenance.json, portability-check.json and logs/. The frozen 387 release is unchanged.
