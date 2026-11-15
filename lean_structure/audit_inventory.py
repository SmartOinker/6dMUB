"""Audit all public theorem declarations in the forty-six integrated modules."""
import hashlib,json,re,sys
from datetime import datetime,timezone
from pathlib import Path
root=Path(__file__).resolve().parent
modules=["MUBIdentities","MUBGap","MUBQuantum","MUBQuantumFourier",
         "MUBQuantumMeasurements","MUBSpectral","MUBBridge","MUBResidual","MUBTensorFrame","MUBFieldObstruction","MUBOperationalTV","MUBCubeCounts",
         "MUBCubicGram","MUBGramCap","MUBPurityGap","MUBSquarefreePhysical","MUBCompatibility","MUBPhaseTensor","MUBPhaseTensorConverse","MUBResidualBounds","MUBQuantumTransport","MUBAnchoredPurity","MUBSixPhasePolynomial","MUBTetrahedral","MUBLocalExhaustion","MUBMeasurementProjectors","MUBMeasurementBessel","MUBDensityGap","MUBDensityTrace","MUBBalancedRows","MUBBalancedGram","MUBBalancedSpectralEnvelope","MUBBalancedSmallTables","MUBFourLineForms","MUBMatchingGram","MUBLocalGermAlgebra","MUBCoordinateProductIdeal","MUBMixedTransport","MUBSunCubeGram","MUBSunCubeSpectrum","MUBSeedGluing","MUBUniformSubmersion","MUBSeedDifferential","MUBSeedLocalChart","MUBSunDiscriminant","MUBNormalizerObstructions"]
names=[]; counts={}; hashes={}; private_helpers={}
for mod in modules:
    p=root/(mod+".lean"); text=p.read_text()
    namespace=re.search(r"^namespace (\w+)",text,re.M).group(1)
    declarations=re.findall(r"^theorem (\w+)",text,re.M)
    names.extend(namespace+"."+n for n in declarations)
    counts[mod]=len(declarations)
    hashes[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    helpers=re.findall(r"^private theorem (\w+)",text,re.M)
    if helpers: private_helpers[mod]=helpers
assert len(names)==len(set(names))
assert len(names)==394 and len(modules)==46
assert sum(map(len,private_helpers.values()))==89
if sys.argv[1]=="prepare":
    (root/"AuditAll.lean").write_text("module\npublic import MUBBridge\npublic import MUBResidual\npublic import MUBTensorFrame\npublic import MUBFieldObstruction\npublic import MUBOperationalTV\npublic import MUBCubeCounts\npublic import MUBCubicGram\npublic import MUBGramCap\npublic import MUBPurityGap\npublic import MUBSquarefreePhysical\npublic import MUBCompatibility\npublic import MUBPhaseTensor\npublic import MUBPhaseTensorConverse\npublic import MUBResidualBounds\npublic import MUBQuantumTransport\npublic import MUBAnchoredPurity\npublic import MUBSixPhasePolynomial\npublic import MUBTetrahedral\npublic import MUBLocalExhaustion\npublic import MUBMeasurementProjectors\npublic import MUBMeasurementBessel\npublic import MUBDensityGap\npublic import MUBDensityTrace\npublic import MUBBalancedGram\npublic import MUBBalancedSpectralEnvelope\npublic import MUBBalancedSmallTables\npublic import MUBFourLineForms\npublic import MUBMatchingGram\npublic import MUBLocalGermAlgebra\npublic import MUBCoordinateProductIdeal\npublic import MUBMixedTransport\npublic import MUBSunCubeSpectrum\npublic import MUBSeedGluing\npublic import MUBUniformSubmersion\npublic import MUBSeedLocalChart\npublic import MUBSunDiscriminant\npublic import MUBNormalizerObstructions\n\n"+
        "\n".join("#print axioms "+n for n in names)+
        "\n#check MUBNormalizerObstructions.actual_shared_chirp_obstruction\n"+
        "#check MUBNormalizerObstructions.actual_qubit_three_ray_obstruction\n"+
        "#check MUBNormalizerObstructions.actual_fourier_parseval\n"+
        "#check MUBNormalizerObstructions.actual_qubit_welch_identity\n"+
        "#print MUBNormalizerObstructions.fourier3\n"+
        "#print MUBNormalizerObstructions.qubitGram\n"+
        "#print MUBNormalizerObstructions.qubitFrame\n"+
        "#check MUBSeedDifferential.actual_seed_strict_submersion\n"+
        "#check MUBSeedDifferential.actual_seed_zero_iff_varied_block_unitary\n"+
        "#print MUBSeedDifferential.seedEquation\n"+
        "#print MUBSeedDifferential.angleDomain\n"+
        "#check MUBSeedLocalChart.angle_domain_finrank\n"+
        "#check MUBSeedLocalChart.actual_kernel_finrank\n"+
        "#check MUBSeedLocalChart.actual_eventual_zero_set_chart\n"+
        "#check MUBSunDiscriminant.actual_discriminant_slack\n"+
        "#check MUBSunDiscriminant.actual_parameter_stronger_bound\n"+
        "#check MUBSunDiscriminant.actual_cube_rank_dichotomy\n"+
        "#print MUBSunDiscriminant.vandermonde\n"+
        "#check MUBUniformSubmersion.actual_coefficient_gram\n"+
        "#check MUBUniformSubmersion.actual_coefficient_characteristic_polynomial\n"+
        "#check MUBUniformSubmersion.actual_uniform_lower_bound\n"+
        "#check MUBUniformSubmersion.coefficient_action_on_mean_zero\n"+
        "#check MUBUniformSubmersion.actual_bounded_mean_zero_preimage\n"+
        "#print MUBUniformSubmersion.coefficientMatrix\n"+
        "#print MUBUniformSubmersion.MeanZeroPair\n"+
        "#print MUBUniformSubmersion.canonicalRightInverse\n"+
        "#check MUBSunCubeGram.actual_cube_gram\n"+
        "#check MUBSunCubeGram.actual_parameter_range\n"+
        "#check MUBSunCubeGram.actual_normalization_identity\n"+
        "#check MUBSunCubeGram.actual_residual_energy\n"+
        "#check MUBSunCubeGram.actual_maximum_witness\n"+
        "#check MUBSunCubeSpectrum.actual_cube_characteristic_polynomial\n"+
        "#print MUBSunCubeGram.blockMatrix\n"+
        "#print MUBSunCubeGram.UnitTriple\n"+
        "#print MUBSeedGluing.step\n"+
        "#check MUBSeedGluing.actual_cell_counts\n"+
        "#check MUBSeedGluing.gluing_graph_connected\n"+
        "#check MUBLocalGermAlgebra.powerSeries_generators_eq\n"+
        "#print MUBLocalGermAlgebra.mixedMatrix\n"+
        "#check MUBCoordinateProductIdeal.actual_cross_intersection\n"+
        "#check MUBCoordinateProductIdeal.actual_cross_quotient_reduced\n"+
        "#print MUBCoordinateProductIdeal.crossIdeal\n"+
        "#check MUBMixedTransport.mixed_projector_factorization\n"+
        "#check MUBMixedTransport.centered_mixed_norm\n"+
        "#print MUBMixedTransport.mixedOperator\n"+
        "#check MUBBalancedSmallTables.actual_moment_majorant_bound\n"+
        "#check MUBBalancedSmallTables.sqrt_sum_lt_of_actual_moments\n"+
        "#print MUBBalancedSmallTables.moment\n"+
        "#print MUBBalancedSmallTables.extension\n"+
        "#print MUBBalancedSmallTables.centeringWeight\n"+
        "#print MUBBalancedSmallTables.schur\n"+
        "#check MUBFourLineForms.eight_gram_characteristic_polynomials\n"+
        "#check MUBMatchingGram.signed_kernel_characterization\n"+
        "#print MUBMatchingGram.nullPolynomial\n"+
        "#check MUBBalancedGram.balanced_gram_separation\n"+
        "#check MUBBalancedGram.balanced_matrix_not_hadamard\n"+
        "#print MUBBalancedRows.Row\n"+
        "#print MUBBalancedGram.phaseMatrix\n"+
        "#print MUBBalancedGram.gramDefect\n"+
        "#print MUBBalancedGram.frobeniusSq\n"+
        "#check MUBBalancedSpectralEnvelope.sqrt_majorant\n"+
        "#check MUBBalancedSpectralEnvelope.gram_error_scalar_gap\n"+
        "#check MUBDensityTrace.canonical_density_trace_deficit\n"+
        "#check MUBDensityGap.canonical_density_operator_gap\n"+
        "#check MUBDensityGap.canonical_density_cubic_operator_bound\n"+
        "#check MUBDensityGap.canonical_density_cubic_kernel\n"+
        "#check MUBDensityGap.canonical_density_cubic_strict\n"+
        "#check MUBMeasurementBessel.canonical_measurement_bessel\n"+
        "#print MUBMeasurementProjectors.canonicalProjector\n"+
        "#print MUBMeasurementProjectors.expectation\n"+
        "#print MUBMeasurementProjectors.pureState\n"+
        "#print MUBMeasurementBessel.reconstruction\n"+
        "#print MUBMeasurementBessel.energy\n"+
        "\n#check MUBBridge.canonical_probability_gap\n"+
        "#check MUBBridge.canonical_no_unbiased_state\n"+
        "#check MUBSquarefreePhysical.physical_cube_gram_cap\n"+
        "#check MUBCompatibility.coupled_equations_unitary\n"+
        "#check MUBCompatibility.coupled_flat_unitary\n"+
        "#check MUBPhaseTensorConverse.phase_tensor_equivalence\n"+
        "#print MUBPhaseTensor.UnitTensor\n"+
        "#print MUBPhaseTensor.AnchoredBoxes\n"+
        "#print MUBPhaseTensor.LineSums\n"+
        "#print MUBPhaseTensor.PhysicalRealization\n"+
        "#check MUBResidualBounds.residual_purity_lower_bound\n"+
        "#check MUBResidualBounds.residual_purity_upper_bound\n"+
        "#check MUBQuantumTransport.physical_partial_trace\n"+
        "#check MUBQuantumTransport.residual_energy_decomposition\n"+
        "#print MUBQuantumTransport.transport\n"+
        "#print MUBQuantumTransport.partialTrace12\n"+
        "#print MUBQuantumTransport.overlapSquare\n"+
        "#print MUBQuantumTransport.normalizedResidual\n"+
        "#print MUBQuantumTransport.normalizedGap\n"+
        "#print MUBQuantumTransport.tracelessOverlap\n"+
        "#check MUBAnchoredPurity.anchored_square_identity\n"+
        "#check MUBAnchoredPurity.anchored_distance_identity\n"+
        "#check MUBAnchoredPurity.anchored_defect_zero_iff\n"+
        "#check MUBAnchoredPurity.anchored_distance_weighted_bound\n"+
        "#check MUBAnchoredPurity.anchored_minor_identity\n"+
        "#check MUBAnchoredPurity.aggregate_minor_nonnegative_iff\n"+
        "#print MUBAnchoredPurity.anchorDefect\n"+
        "#print MUBAnchoredPurity.anchorProjection\n"+
        "#print MUBAnchoredPurity.anchoredMinorSum\n"+
        "#check MUBSixPhasePolynomial.positive_polynomial_certificate\n"+
        "#check MUBSixPhasePolynomial.rational_gap_identities\n"+
        "#check MUBSixPhasePolynomial.sharp_envelope_bound\n"+
        "#print MUBSixPhasePolynomial.polynomialP\n"+
        "#print MUBSixPhasePolynomial.polynomialQ\n"+
        "#print MUBSixPhasePolynomial.envelopeCenter\n"+
        "#print MUBSixPhasePolynomial.envelopeVariance\n"+
        "#print MUBSixPhasePolynomial.targetGap\n"+
        "#check MUBTetrahedral.tetrahedral_equivalence\n"+
        "#check MUBTetrahedral.physical_quartet_is_unbiased\n"+
        "#check MUBTetrahedral.fourth_face_conditions\n"+
        "#print MUBTetrahedral.Cocycle\n"+
        "#print MUBTetrahedral.TetrahedralConditions\n"+
        "#print MUBTetrahedral.PhysicalQuartet\n"+
        "#print MUBTetrahedral.UnbiasedQuartet\n"+
        "#check MUBLocalExhaustion.local_graph_exhaustion\n"+
        "#check MUBLocalExhaustion.local_property_transfer\n")
    print(f"Prepared full audit for {len(names)} theorem declarations.")
elif sys.argv[1]=="verify":
    log=(root/"logs/axioms-all.log").read_text()
    allowed={"propext","Classical.choice","Quot.sound"}
    records={}
    for n in names:
        m=re.search(re.escape("'"+n+"' depends on axioms: [")+r"([^\]]*)\]",log)
        if m:
            axioms={a.strip() for a in m.group(1).split(",") if a.strip()}
        else:
            assert "'"+n+"' does not depend on any axioms" in log,n
            axioms=set()
        assert axioms<=allowed,(n,axioms)
        records[n]=sorted(axioms)
    assert not re.search(r"\berror:|\bsorryAx\b",log)
    provenance=json.loads((root/"integration-provenance.json").read_text())
    # Local proof provenance is mandatory and independent of workspace paths.
    baseline_proofs={filename:digest
                     for filename,digest in provenance["base_source_sha256"].items()
                     if filename.startswith("MUB") and filename.endswith(".lean")}
    assert set(baseline_proofs).isdisjoint(provenance["added_sources"])
    assert set(baseline_proofs)|set(provenance["added_sources"])==set(hashes)
    for filename,digest in baseline_proofs.items():
        assert hashes[filename]==digest,("local baseline proof",filename)
    for filename,record in provenance["added_sources"].items():
        assert hashes[filename]==record["sha256"],("local added proof",filename)

    # Original locations are optional corroboration, never required archive inputs.
    base=Path(provenance["base_release"])
    original_baseline={"path":str(base),"status":"not_available","checked_files":0}
    if base.exists():
        assert base.is_dir(),("original baseline is not a directory",str(base))
        for filename,digest in provenance["base_source_sha256"].items():
            assert hashlib.sha256((base/filename).read_bytes()).hexdigest()==digest,(
                "original baseline changed",filename)
        original_baseline.update(status="verified_unchanged",
                                 checked_files=len(provenance["base_source_sha256"]))
    original_added={}
    for filename,record in provenance["added_sources"].items():
        source=Path(record["path"])
        status="not_available"
        if source.exists():
            assert hashlib.sha256(source.read_bytes()).hexdigest()==record["sha256"],(
                "original added source changed",filename)
            status="verified_unchanged"
        original_added[filename]={"path":str(source),"status":status}
    baseline_preserved=True if original_baseline["status"]=="verified_unchanged" else None
    result={"status":"PASS","lean_version":"4.35.0",
      "checked_at_utc":datetime.now(timezone.utc).isoformat(),
      "mathlib_commit":"56a005855ea17e0b0958f73ec801ae140b0a1679",
      "verification":"forty-six-module lake build; direct re-elaboration of the new actual Fourier and C2 frame obstruction module; every-public-theorem axiom audit; source provenance checks",
      "theorem_count":len(names),"module_counts":counts,"source_sha256":hashes,
      "count_convention":"The same ^theorem public-declaration convention as the frozen 387-theorem baseline.",
      "private_theorem_helper_count":sum(map(len,private_helpers.values())),
      "private_theorem_helpers":private_helpers,
      "private_helper_trust":"Private helpers are kernel checked during source elaboration and their axioms are included transitively in audited public theorem dependencies.",
      "local_proof_hashes_verified":True,
      "baseline_preserved":baseline_preserved,
      "original_baseline_verification":original_baseline,
      "original_added_source_verification":original_added,
      "historical_baseline_verification":provenance.get("historical_baseline_verification"),
      "permitted_axioms":sorted(allowed),"theorem_axioms":records,
      "main_result":"MUBBridge.canonical_probability_gap: arbitrary normalized complex coefficients imply canonical Born energy > 1/72",
      "main_hypotheses":["totalNorm v = 1"],
      "new_snapshot_public_theorem_count":7,
      "campaign_public_theorems_since_142":252,
      "new_snapshot_modules":{"MUBNormalizerObstructions":7},
      "campaign_modules":{
        "MUBNormalizerObstructions":{"public_theorems":7,"result":"Actual primitive cubic root and three-point Fourier Parseval; actual unit triple excludes all shifted Fourier squared moduli6; actual2-by-3 frame/Gram Frobenius identity excludes unit C2 vectors with pairwise squared overlaps1/6.","desired_Fourier_or_Welch_inequality_assumed":False,"normalizer_spectral_gauge_reduction_and_group_classification_formalized":False},
        "MUBSeedDifferential":{"public_theorems":18,"result":"Actual exponential ratio-angle seed equation on the actual mean-zero domain has a genuine strict real Frechet derivative, the verified coefficient matrix and bounded surjectivity; exact phase/product variation, explicit varied triples and seed-zero iff actual block unitarity.","derivative_or_surjectivity_assumed":False,"physical_composed_Sun_transition_registration_formalized":False},
        "MUBSeedLocalChart":{"public_theorems":10,"result":"Explicit actual domain equivalence with R4, actual derivative kernel dimension2, genuine strict IFT chart and full local seed zero-set exhaustion by a two-dimensional kernel.","generic_Jacobian_or_chart_premise":False,"arbitrary_MUB_or_global_seed_coverage":False},
        "MUBSunDiscriminant":{"public_theorems":15,"result":"Actual ratio Vandermonde slack and opposite-correlation sum give q²+18q<=27 and q<=6sqrt3-9<3/2; actual cube Gram determinant, nonzero determinant and rank6 for q!=0, rank2 for q0, and actual rank dichotomy.","sharp_attainer_or_global_geometry_claimed":False},
        "MUBUniformSubmersion":{"public_theorems":23,"result":"Actual projected ratio-angle coefficient matrix Gram and characteristic polynomial; uniform quadratic coercivity 3/2; actual canonical right inverse in the mean-zero domain with squared Euclidean norm bound 2/3.","structural_hypotheses":["unit triples u and v","actual block C†C=6I"],"Gram_range_or_surjectivity_assumed":False,"analytic_differentiation_formalized_in_MUBSeedDifferential":True,"physical_seed_registration_formalized":False},
        "MUBSunCubeGram":{"public_theorems":24,"result":"Actual unregistered Hankel block unitarity derives correlation cancellation and actual cube Gram; positivity gives0<=q<=3/2; literal normalization, trace/energy formulas, zero equivalences, sharp maxima and an actual attaining block are verified.","structural_hypotheses":["u and v have unit modulus","actual block C†C=6I"],"desired_Gram_Newton_or_range_assumed":False,"composed_seed_to_block_and_registration_formalized":False},
        "MUBSunCubeSpectrum":{"public_theorems":4,"result":"Explicit parity reindexing and actual3x3 determinant yield the cube Gram characteristic polynomial (X-(18-12q))²(X-6q)⁴.","spectral_multiplicities_assumed":False},
        "MUBSeedGluing":{"public_theorems":9,"result":"Explicit S3xS3 faces, six edge maps, fixed-point-free involutions, adjacent commutation, actual orbit/cell counts36/108/54, Euler-18 and actual gluing-graph connectivity.","continuous_surface_or_genus_identification_formalized":False},
        "MUBLocalGermAlgebra":{"public_theorems":6,"result":"Generic invertible coefficient matrices preserve generated ideals; actual4x4 mixed matrix has determinant -4+2sqrt(3), nonzero; actual constant-matrix criterion gives real formal-power-series ideal invariance.","MUB_derivative_origin_formalized":False},
        "MUBCoordinateProductIdeal":{"public_theorems":9,"result":"Actual polynomial coordinate product/intersection identity from monomial supports, coordinate-kernel identification and primality; original four-generator crossing ideal is radical with reduced quotient.","power_series_or_analytic_reducedness_formalized":False},
        "MUBMixedTransport":{"public_theorems":6,"result":"Actual overlap of two repeated frames, three-projector factorization, mixed partial trace and trace, centered transport and norm-squared scale1/36.","target_factorization_assumed":False,"centered_hypotheses":["B unitary","B entry norm squares1/6"],"uncentered_hypotheses":[]},
        "MUBBalancedSmallTables":{"public_theorems":10,"result":"Actual five rational Gram inverses and all80 sign extensions,62 positive Schur cases, exact trace polynomial bounds <25/2 and an explicit three-moment conditional square-root-sum bridge.","trace_moments_are_actual_matrix_traces":True,"spectral_transport_formalized":False},
        "MUBFourLineForms":{"public_theorems":5,"result":"Ten balanced antipodal representatives, actual tight-frame entries, all8 actual characteristic polynomials and1/1/6 multiplicities.","arbitrary_Gram_normalization_formalized":False},
        "MUBMatchingGram":{"public_theorems":7,"result":"Actual balanced sign witness and Gram matrix; all64 signed polynomial projectors, arbitrary-rational-vector kernel characterization, and nonzero imbalance >=24.","arbitrary_maximizer_classification_formalized":False},
        "MUBBalancedRows":{"public_theorems":7,"result":"Kernel-checked balanced-row count20, zero sign sum and all pair dot products in {-6,-2,2,6}.","external_or_native_oracle":False},
        "MUBBalancedGram":{"public_theorems":8,"result":"Actual complex two-phase formula, unit entries, row sums, Gram entries and ||SS*−6I||²>=160/3; direct actual non-Hadamard corollary.","hypotheses":["six rows chosen from the exactly balanced Boolean row subtype"],"desired_Gram_inequality_assumed":False},
        "MUBBalancedSpectralEnvelope":{"public_theorems":4,"result":"Exact cubic-majorant factorization; q(x)>=sqrt(x) for x>=0; kappa>2; separate scalar e²>7/5 conversion.","excluded_scope":["177100-case finite spectral certificate","matrix norm comparison for scalar distance conversion","regular Hadamard distance>7/2","physical tensor distance>21"]},
        "MUBDensityTrace":{"public_theorems":1,"result":"The strict cubic trace deficit 1−Re tr(R³)>1/144 follows directly from the actual operator/kernel bound and purity.","hypotheses":["Hermitian R","tr(R²)=1","actual canonical expectations all1/6"],"spectral_input_assumed":False},'MUBMeasurementProjectors':{'public_theorems': 8, 'result': 'Actual canonical projectors, Born trace identities, exact Gram table and completeness.', 'coordinate_scope': 'C=D²F coefficient coordinates and actual outcome relabeling; b=0 is not coordinate diagonal.'},'MUBMeasurementBessel':{'public_theorems': 4, 'result': 'Exact Gram-square identity, derived Bessel bound and actual uniform-density comparison.', 'Bessel_or_Gram_inequality_assumed': False},'MUBDensityGap':{'public_theorems': 10, 'result': 'Distance >1/72 from every pure state; under purity one, (143/144)I−R is positive definite and Q−R²/144 is positive semidefinite with kernel ker R; strict direction iff R u is nonzero.', 'hypotheses': ['Hermitian R', 'actual canonical projector expectations all 1/6', 'tr(R²)=1 for Rayleigh/cubic results'], 'positivity_of_R_assumed': False, 'trace_one_assumed': False, 'arbitrary_MUB_triples_covered': False},
        "MUBLocalExhaustion":{
          "public_theorems":2,
          "result":"Generic Mathlib IFT local full-zero-set exhaustion and seed-property transfer.",
          "hypotheses":["selected strict derivative and invertible partial derivative","selected anchor zero","full zeros imply selected zeros","continuous seed through anchor","eventually full seed equations"],
          "uniqueness_or_exhaustion_assumed":False,
          "concrete_Sun_instantiation_verified":False
        },
        "MUBTetrahedral":{
          "public_theorems":8,
          "result":"Tetrahedral phase conditions are equivalent to six shared normalized flat-unitary edges realizing all four faces; the actual six basis overlaps are checked.",
          "hypotheses":["four unit tensors","full tetrahedral cocycle","all three line-sum families on faces012,013,023"],
          "boxes_assumed":False,
          "fourth_face_line_sums_assumed":False,
          "existence_or_exclusion_conclusion":False
        },
        "MUBSixPhasePolynomial":{
          "public_theorems":3,
          "result":"P/Q positivity, exact rational gap identities, and the 3+2+1 envelope bound f+sqrt(g)≤98/3 with equality iff L=9.",
          "hypotheses":["t≥0 for polynomial positivity","L≠0 for rational identities","1≤L≤9 for the sharp envelope bound"],
          "excluded_scope":["phase-to-envelope derivation","stationary-support reduction","other multiplicity cases","the full sharp six-phase theorem"]
        },
        "MUBAnchoredPurity":{
          "public_theorems":10,
          "result":"Exact anchored Gram/distance identities, rank-one positivity detection, actual principal-minor Newton identity, and finite-family aggregate certificate.",
          "hypotheses":["Hermitian R and tr(R²)=1 for the square identity", "add Raa≠0 for normalized projection, detection and error bound", "add tr R=1 for the aggregate principal-minor certificate"],
          "minor_identity_scope":"The determinant identity itself holds for every square complex matrix.",
          "no_domain_certificate_assumed_as_conclusion":True
        },
        "MUBResidualBounds":{
          "public_theorems":4,
          "result":"Exact completed-square and Gram-cap trace identities imply W²/36≤E and, under the cap, E≤18W.",
          "hypotheses":["tr(M†M)=36","the upper bound additionally assumes 18I−M†M PSD"]
        },
        "MUBQuantumTransport":{
          "public_theorems":9,
          "result":"Actual repetition/tensor-cube partial trace, scaled Frobenius transport, traceless centering and energy identity ||T||²=5184||Xi||²+864delta².",
          "hypotheses":["U is unitary of order 6","every entry of U has squared modulus 1/6"],
          "partial_trace_identity_assumed":False,
          "algebraic_scope":"The partial-trace and factorization identities require no unitarity or flatness.",
          "hermiticity":"O and Xi need not be Hermitian; energies use conjugate transpose."
        },
        "MUBSquarefreePhysical":{
          "public_theorems":5,
          "result":"Actual squarefree/incidence constructions imply 18I−(H entrywise cubed)†(H entrywise cubed) is positive semidefinite.",
          "hypotheses":["unit-modulus entries","HH†=6I","explicit complementary-triple Fourier vanishing"]
        },
        "MUBCompatibility":{
          "public_theorems":5,
          "result":"The coupled equations force A,B,C to be unitary in any finite dimension.",
          "hypotheses":["AC=B","A†B=C","BC†=A","tr(A†A)=dimension"],
          "flat_corollary":"For nonempty dimension, normalized flatness of A supplies the trace; no invertibility or orthogonality premise."
        },
        "MUBPhaseTensor":{
          "public_theorems":6,
          "result":"Constructively reconstruct normalized flat unitary matrices from unit tensor entries, non-anchor boxes, and all three line-sum families."
        },
        "MUBPhaseTensorConverse":{
          "public_theorems":5,
          "result":"Physical transitions satisfy all tensor constraints; the complete physical existence equivalence is formalized."
        }
      },
      "main_new_equivalence":{
        "theorem":"MUBPhaseTensorConverse.phase_tensor_equivalence",
        "tensor_side":"UnitTensor t and all125 non-anchor boxes and all three axis-line families summing to the positive sqrt(6)",
        "physical_side":"There exist normalized flat unitary A,B,C with AC=B and t_ikj=sqrt(6)A_ik C_kj/B_ij",
        "signature_and_predicate_definitions_checked_in":"logs/axioms-all.log",
        "no_global_purity_conclusion":True
      },
      "not_formalized":["full fixed-ray common-normalizer reduction, coherent four-form equivalences and normalizer group-order corollaries","the composed physical Sun seed-to-block and registration-gauge bridges","continuous seed gluing and genus10 identification","the actual MUB analytic crossing germ and Hessian origin","coordinate product-ideal reducedness in formal or convergent power series","unrestricted global MUB exclusion","cube-rank finite classification",
                        "concrete quartic moment certificate","projector operator-norm interface",
                        "the externally cited non-Tao Fourier vanishing theorem",
                        "universal vanishing of the degree-36 three-edge purity product",
                        "paired cube-Gram spectrum or cube-product saturation",
                        "uniqueness of phase-tensor reconstruction up to common diagonal gauge",
                        "a MUB-domain proof of the aggregate anchored-minor inequality",
                        "the full sharp six-phase stationary-support theorem",
                        "the concrete Sun local-neighborhood analytic/minor instantiation",
                        "the full complex Sun component and 301-component count",
                        "the exhaustive Procrustes spectral certificate and distance>7/2",
                        "the physical tensor line distance>21"]}
    (root/"verification.json").write_text(json.dumps(result,indent=2)+"\n")
    artifact_files=sorted(p for p in root.iterdir()
                          if p.is_file() and p.name!="hash-manifest.json")
    artifact_files+=sorted((root/"logs").glob("*"))
    manifest={"status":"PASS","public_theorem_count":len(names),
              "private_theorem_helper_count":sum(map(len,private_helpers.values())),
              "module_count":len(modules),"local_proof_hashes_verified":True,
              "baseline_preserved":baseline_preserved,
              "original_baseline_verification":original_baseline,
              "files":{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in artifact_files if p.is_file()}}
    (root/"hash-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(f"PASS: all {len(names)} theorems use only permitted axioms.")
else: raise SystemExit("Use prepare or verify.")
