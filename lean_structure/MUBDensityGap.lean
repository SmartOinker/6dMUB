module

public import MUBMeasurementBessel
public import MUBBridge

@[expose] public section
noncomputable section

namespace MUBDensityGap

open Matrix MUBQuantum MUBMeasurementProjectors MUBMeasurementBessel
open scoped ComplexOrder

/-- The rank-one matrix uses the same state coordinates and norm as the
existing Born-gap theorem. -/
theorem pure_state_trace (v : Coefficients) :
    Matrix.trace (pureState (fun x : Coordinate => v x.1 x.2)) = (totalNorm v : ℂ) := by
  simp [pureState, Matrix.trace_vecMulVec, dotProduct, Pi.star_apply,
    Complex.mul_conj, Fintype.sum_prod_type, totalNorm, weight, Fin.sum_univ_two,
    Complex.ofReal_sum, Complex.ofReal_add]

/-- Uniform canonical observables force trace one for a Hermitian matrix;
trace normalization is derived from the actual resolution of identity. -/
theorem uniform_density_trace (r : ℝ) (hr : r^2 = 3)
    (R : Matrix Coordinate Coordinate ℂ) (hR : R.IsHermitian)
    (hu : ∀ b o, expectation (canonicalProjector r b o) R = (1 : ℝ)/6) :
    Matrix.trace R = 1 := by
  have he : Matrix.trace R = ∑ o, Matrix.trace (canonicalProjector r 0 o * R) := by
    rw [← Matrix.trace_sum, ← Finset.sum_mul, canonical_projector_complete r hr,
      Matrix.one_mul]
  have hre : (Matrix.trace R).re = 1 := by
    rw [he]
    change Complex.reCLM (∑ o, Matrix.trace (canonicalProjector r 0 o * R)) = 1
    rw [map_sum]
    change (∑ o, expectation (canonicalProjector r 0 o) R) = 1
    norm_num [hu, Outcome]
  have hreal : ((Matrix.trace R).re : ℂ) = Matrix.trace R := by
    apply Complex.conj_eq_iff_re.mp
    change star (Matrix.trace R) = Matrix.trace R
    rw [← Matrix.trace_conjTranspose, hR.eq]
  rw [← hreal, hre]
  norm_num

/-- The existing strict canonical Born gap and the proved measurement Bessel
map imply a Frobenius separation from every Hermitian matrix with uniform
canonical observables. No energy-versus-distance inequality is assumed. -/
theorem canonical_density_distance_gap (R : Matrix Coordinate Coordinate ℂ)
    (hR : R.IsHermitian)
    (hu : ∀ b o, expectation (canonicalProjector (Real.sqrt 3) b o) R = (1 : ℝ)/6)
    (v : Coefficients) (hv : totalNorm v = 1) :
    (1 : ℝ)/72 <
      (Matrix.trace ((pureState (fun x : Coordinate => v x.1 x.2) - R)ᴴ *
        (pureState (fun x : Coordinate => v x.1 x.2) - R))).re := by
  have hr : (Real.sqrt 3)^2 = 3 := Real.sq_sqrt (by norm_num)
  have hS : (pureState (fun x : Coordinate => v x.1 x.2)).IsHermitian :=
    (Matrix.posSemidef_vecMulVec_self_star _).1
  have htrace : Matrix.trace (pureState (fun x : Coordinate => v x.1 x.2)) =
      Matrix.trace R := by
    rw [pure_state_trace, hv, uniform_density_trace _ hr R hR hu]
    norm_num
  have hb := canonical_uniform_comparison (Real.sqrt 3) hr R
    (pureState (fun x : Coordinate => v x.1 x.2)) hR hS htrace hu
  have hb' : (∑ b, ∑ j, ∑ a,
      (canonicalProbability (Real.sqrt 3) v b j a - 1/6)^2) ≤
      (Matrix.trace ((pureState (fun x : Coordinate => v x.1 x.2) - R)ᴴ *
        (pureState (fun x : Coordinate => v x.1 x.2) - R))).re := by
    simpa only [Fintype.sum_prod_type, canonical_projector_born _ hr] using hb
  exact lt_of_lt_of_le (MUBBridge.canonical_probability_gap v hv) hb'

private theorem pure_state_square (v : Coefficients) :
    pureState (fun x : Coordinate => v x.1 x.2) *
      pureState (fun x : Coordinate => v x.1 x.2) =
      (totalNorm v : ℂ) • pureState (fun x : Coordinate => v x.1 x.2) := by
  rw [pureState, Matrix.vecMulVec_mul_vecMulVec]
  have hn : star (fun x : Coordinate => v x.1 x.2) ⬝ᵥ
      (fun x : Coordinate => v x.1 x.2) = (totalNorm v : ℂ) := by
    rw [dotProduct_comm]
    exact pure_state_trace v
  rw [hn]
  ext i j
  simp only [Matrix.vecMulVec_apply, Pi.smul_apply, Matrix.smul_apply, smul_eq_mul]
  ring

/-- A concrete uniform Hermitian purity-one matrix has a strict Rayleigh
bound on every normalized complex vector. Positivity of the matrix is not
assumed. The bound is derived through the actual canonical measurements. -/
theorem canonical_density_rayleigh_gap (R : Matrix Coordinate Coordinate ℂ)
    (hR : R.IsHermitian) (hpurity : Matrix.trace (R * R) = 1)
    (hu : ∀ b o, expectation (canonicalProjector (Real.sqrt 3) b o) R = (1 : ℝ)/6)
    (v : Coefficients) (hv : totalNorm v = 1) :
    expectation (pureState (fun x : Coordinate => v x.1 x.2)) R < (143 : ℝ)/144 := by
  have hg := canonical_density_distance_gap R hR hu v hv
  have hp := (Matrix.posSemidef_vecMulVec_self_star
    (fun x : Coordinate => v x.1 x.2)).1.eq
  change (pureState (fun x : Coordinate => v x.1 x.2))ᴴ =
    pureState (fun x : Coordinate => v x.1 x.2) at hp
  rw [Matrix.conjTranspose_sub, hp, hR.eq, Matrix.sub_mul, Matrix.mul_sub,
    Matrix.mul_sub, Matrix.trace_sub, Matrix.trace_sub, Matrix.trace_sub,
    pure_state_square, hv, Complex.ofReal_one, one_smul, pure_state_trace, hv,
    Complex.ofReal_one, hpurity, Matrix.trace_mul_comm R] at hg
  simp only [Complex.sub_re, Complex.one_re] at hg
  unfold expectation
  linarith

private theorem scaled_norm (a : ℝ) (v : Coefficients) :
    totalNorm (fun j k => (a : ℂ) * v j k) = a^2 * totalNorm v := by
  simp only [totalNorm, weight, Complex.normSq_mul, Complex.normSq_ofReal,
    ← mul_add, ← Finset.mul_sum, pow_two]

private theorem scaled_pure_state (a : ℝ) (v : Coefficients) :
    pureState (fun x : Coordinate => (a : ℂ) * v x.1 x.2) =
      (a^2 : ℝ) • pureState (fun x : Coordinate => v x.1 x.2) := by
  ext i j
  simp only [pureState, Matrix.vecMulVec_apply, Pi.star_apply, star_mul,
    Complex.star_def, Complex.conj_ofReal, Matrix.smul_apply, Complex.real_smul,
    Complex.ofReal_pow]
  ring

/-- Homogeneous form of the concrete Rayleigh gap. A nonzero squared mass is
explicit, and neither positivity nor idempotency of R is assumed. -/
theorem canonical_density_homogeneous_gap (R : Matrix Coordinate Coordinate ℂ)
    (hR : R.IsHermitian) (hpurity : Matrix.trace (R * R) = 1)
    (hu : ∀ b o, expectation (canonicalProjector (Real.sqrt 3) b o) R = (1 : ℝ)/6)
    (v : Coefficients) (hv : 0 < totalNorm v) :
    expectation (pureState (fun x : Coordinate => v x.1 x.2)) R <
      (143 : ℝ)/144 * totalNorm v := by
  let a : ℝ := (Real.sqrt (totalNorm v))⁻¹
  have ha : a^2 * totalNorm v = 1 := by
    dsimp [a]
    rw [inv_pow, Real.sq_sqrt (le_of_lt hv), inv_mul_cancel₀ (ne_of_gt hv)]
  have hn : totalNorm (fun j k => (a : ℂ) * v j k) = 1 := by
    rw [scaled_norm, ha]
  have hg := canonical_density_rayleigh_gap R hR hpurity hu
    (fun j k => (a : ℂ) * v j k) hn
  rw [scaled_pure_state] at hg
  have he : expectation ((a^2 : ℝ) • pureState (fun x : Coordinate => v x.1 x.2)) R =
      a^2 * expectation (pureState (fun x : Coordinate => v x.1 x.2)) R := by
    simp only [expectation, Matrix.smul_mul, Matrix.trace_smul, Complex.real_smul,
      Complex.mul_re, Complex.ofReal_re, Complex.ofReal_im, zero_mul, sub_zero]
  rw [he] at hg
  have hh := mul_lt_mul_of_pos_right hg hv
  calc
    _ = (a^2 * expectation (pureState (fun x : Coordinate => v x.1 x.2)) R) *
        totalNorm v := by rw [mul_right_comm, ha, one_mul]
    _ < _ := hh

/-- Every nonzero vector has a strictly positive homogeneous cubic-loss
margin. Substituting v=R u gives the anchor defect u†(R²−R³)u. -/
theorem canonical_density_vector_defect_gap (R : Matrix Coordinate Coordinate ℂ)
    (hR : R.IsHermitian) (hpurity : Matrix.trace (R * R) = 1)
    (hu : ∀ b o, expectation (canonicalProjector (Real.sqrt 3) b o) R = (1 : ℝ)/6)
    (v : Coefficients) (hv : 0 < totalNorm v) :
    totalNorm v / 144 < totalNorm v -
      expectation (pureState (fun x : Coordinate => v x.1 x.2)) R := by
  have h := canonical_density_homogeneous_gap R hR hpurity hu v hv
  linarith

private theorem trace_pure_quadratic (R : Matrix Coordinate Coordinate ℂ)
    (v : Coordinate → ℂ) :
    Matrix.trace (pureState v * R) = star v ⬝ᵥ (R *ᵥ v) := by
  rw [Matrix.trace_mul_comm, pureState, Matrix.mul_vecMulVec,
    Matrix.trace_vecMulVec, dotProduct_comm]

private theorem nonzero_mass (v : Coordinate → ℂ) (hv : v ≠ 0) :
    0 < totalNorm (fun j k => v (j,k)) := by
  have he : totalNorm (fun j k => v (j,k)) = ∑ x, Complex.normSq (v x) := by
    simp [totalNorm, weight, Fintype.sum_prod_type, Fin.sum_univ_two]
  rw [he]
  obtain ⟨x,hx⟩ := Function.ne_iff.mp hv
  exact (Finset.sum_pos_iff_of_nonneg (fun _ _ => Complex.normSq_nonneg _)).2
    ⟨x, Finset.mem_univ x, Complex.normSq_pos.mpr hx⟩

/-- A strict operator upper bound for the actual canonical uniform Hermitian
purity-one locus. This is stronger in form than a coordinate-anchor statement;
it has no positive-semidefiniteness premise on R. -/
theorem canonical_density_operator_gap (R : Matrix Coordinate Coordinate ℂ)
    (hR : R.IsHermitian) (hpurity : Matrix.trace (R * R) = 1)
    (hu : ∀ b o, expectation (canonicalProjector (Real.sqrt 3) b o) R = (1 : ℝ)/6) :
    ((143/144 : ℂ) • (1 : Matrix Coordinate Coordinate ℂ) - R).PosDef := by
  have hD : ((143/144 : ℂ) • (1 : Matrix Coordinate Coordinate ℂ) - R).IsHermitian := by
    apply Matrix.IsHermitian.sub _ hR
    apply Matrix.isHermitian_one.smul
    change star (143/144 : ℂ) = (143/144 : ℂ)
    norm_num
  apply Matrix.PosDef.of_dotProduct_mulVec_pos hD
  intro v hv
  have hm := nonzero_mass v hv
  have hg := canonical_density_homogeneous_gap R hR hpurity hu (fun j k => v (j,k)) hm
  have ht : star v ⬝ᵥ v = (totalNorm (fun j k => v (j,k)) : ℂ) := by
    rw [dotProduct_comm]
    exact pure_state_trace (fun j k => v (j,k))
  have hr : star v ⬝ᵥ (R *ᵥ v) = ((star v ⬝ᵥ (R *ᵥ v)).re : ℂ) := by
    symm
    apply Complex.conj_eq_iff_re.mp
    change star (star v ⬝ᵥ (R *ᵥ v)) = _
    exact hR.star_dotProduct_mulVec_comm v v
  rw [Matrix.sub_mulVec, Matrix.smul_mulVec, Matrix.one_mulVec,
    dotProduct_sub, dotProduct_smul, ht, hr]
  norm_num [Complex.lt_def, Complex.sub_re, Complex.sub_im, Complex.mul_re,
    Complex.mul_im]
  simpa only [expectation, trace_pure_quadratic, Prod.eta] using
    hg

/-- The cubic loss obeys a concrete operator lower bound on the canonical
uniform purity-one locus. All vectors/anchors are covered in the actual
coefficient coordinates. This does not quantify over arbitrary MUB triples. -/
theorem canonical_density_cubic_operator_bound (R : Matrix Coordinate Coordinate ℂ)
    (hR : R.IsHermitian) (hpurity : Matrix.trace (R * R) = 1)
    (hu : ∀ b o, expectation (canonicalProjector (Real.sqrt 3) b o) R = (1 : ℝ)/6) :
    (R * R - R * R * R - (1/144 : ℂ) • (R * R)).PosSemidef := by
  have hp := (canonical_density_operator_gap R hR hpurity hu).posSemidef
  have h := hp.conjTranspose_mul_mul_same R
  rw [hR.eq] at h
  convert h using 1
  simp only [Matrix.mul_sub, Matrix.sub_mul, Matrix.mul_smul, Matrix.smul_mul,
    Matrix.mul_one, Matrix.mul_assoc]
  module

/-- The lower-bound margin has exactly the kernel of R. Strict positivity
holds in every direction with nonzero R u, not in directions where R u=0. -/
theorem canonical_density_cubic_kernel (R : Matrix Coordinate Coordinate ℂ)
    (hR : R.IsHermitian) (hpurity : Matrix.trace (R * R) = 1)
    (hu : ∀ b o, expectation (canonicalProjector (Real.sqrt 3) b o) R = (1 : ℝ)/6)
    (u : Coordinate → ℂ) :
    (R * R - R * R * R - (1/144 : ℂ) • (R * R)) *ᵥ u = 0 ↔ R *ᵥ u = 0 := by
  let D := (143/144 : ℂ) • (1 : Matrix Coordinate Coordinate ℂ) - R
  have hD : D.PosDef := canonical_density_operator_gap R hR hpurity hu
  have he : R * R - R * R * R - (1/144 : ℂ) • (R * R) = Rᴴ * D * R := by
    rw [hR.eq]
    simp only [D, Matrix.mul_sub, Matrix.sub_mul, Matrix.mul_smul, Matrix.smul_mul,
      Matrix.mul_one, Matrix.mul_assoc]
    module
  rw [he]
  constructor
  · intro hz
    have hq : star (R *ᵥ u) ⬝ᵥ (D *ᵥ (R *ᵥ u)) = 0 := by
      have hh := congrArg (fun z => star u ⬝ᵥ z) hz
      rw [← Matrix.mulVec_mulVec, ← Matrix.mulVec_mulVec, dotProduct_mulVec,
        Matrix.vecMul_conjTranspose, star_star, dotProduct_zero] at hh
      exact hh
    by_contra hn
    have hp := hD.dotProduct_mulVec_pos hn
    rw [hq] at hp
    exact (lt_irrefl _ hp)
  · intro hz
    rw [← Matrix.mulVec_mulVec, hz, Matrix.mulVec_zero]

/-- Strictness holds exactly in directions with nonzero R u. Together with
the operator bound this supplies the coordinate-free anchored cubic margin. -/
theorem canonical_density_cubic_strict (R : Matrix Coordinate Coordinate ℂ)
    (hR : R.IsHermitian) (hpurity : Matrix.trace (R * R) = 1)
    (hu : ∀ b o, expectation (canonicalProjector (Real.sqrt 3) b o) R = (1 : ℝ)/6)
    (u : Coordinate → ℂ) :
    0 < star u ⬝ᵥ ((R * R - R * R * R - (1/144 : ℂ) • (R * R)) *ᵥ u) ↔
      R *ᵥ u ≠ 0 := by
  have hp := canonical_density_cubic_operator_bound R hR hpurity hu
  have hz := hp.dotProduct_mulVec_zero_iff (x := u)
  have hk := canonical_density_cubic_kernel R hR hpurity hu u
  constructor
  · intro hpos hzero
    rw [hz.mpr (hk.mpr hzero)] at hpos
    exact lt_irrefl _ hpos
  · intro hn
    apply lt_of_le_of_ne (hp.dotProduct_mulVec_nonneg u)
    intro hzero
    exact hn (hk.mp (hz.mp hzero.symm))

end MUBDensityGap
