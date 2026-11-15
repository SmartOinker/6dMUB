module
public import MUBSunCubeGram
public import Mathlib.LinearAlgebra.Matrix.Charpoly.Basic
public import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
@[expose] public section
noncomputable section
namespace MUBUniformSubmersion
open Matrix Polynomial MUBSunCubeGram

def ratios (u : Triple) : Triple :=
  ![u 1*(starRingEnd ℂ) (u 0),u 2*(starRingEnd ℂ) (u 1),u 0*(starRingEnd ℂ) (u 2)]

def projected (a b c : ℂ) : Triple :=
  ![Complex.I*(a-(a+b+c)/3),Complex.I*(b-(a+b+c)/3),Complex.I*(c-(a+b+c)/3)]

def projectedRatios (u : Triple) : Triple := projected (ratios u 0) (ratios u 1) (ratios u 2)

set_option maxHeartbeats 4000000
set_option maxRecDepth 100000

theorem ratio_unit (u : Triple) (hu : UnitTriple u) : UnitTriple (ratios u) := by
  have h (i j : Fin 3) : (u i*(starRingEnd ℂ) (u j)) *
      (starRingEnd ℂ) (u i*(starRingEnd ℂ) (u j)) = 1 := by
    calc
      _ = (u i*(starRingEnd ℂ) (u i))*(u j*(starRingEnd ℂ) (u j)) := by
        simp only [map_mul, starRingEnd_self_apply]
        ring
      _ = _ := by rw [hu i,hu j]; ring
  intro j
  fin_cases j <;> simpa [ratios] using h _ _

theorem ratio_square_sum (u : Triple) (hu : UnitTriple u) :
    (ratios u 0)^2+(ratios u 1)^2+(ratios u 2)^2 =
      (gamma u)^2-2*(starRingEnd ℂ) (gamma u) := by
  let a := u 1 * (starRingEnd ℂ) (u 0)
  let b := u 2 * (starRingEnd ℂ) (u 1)
  let c := u 0 * (starRingEnd ℂ) (u 2)
  have hab : a*b = u 2*(starRingEnd ℂ) (u 0) := by
    calc
      _ = (u 1*(starRingEnd ℂ) (u 1)) * (u 2*(starRingEnd ℂ) (u 0)) := by dsimp [a,b]; ring
      _ = _ := by rw [hu 1]; ring
  have hbc : b*c = u 0*(starRingEnd ℂ) (u 1) := by
    calc
      _ = (u 2*(starRingEnd ℂ) (u 2)) * (u 0*(starRingEnd ℂ) (u 1)) := by dsimp [b,c]; ring
      _ = _ := by rw [hu 2]; ring
  have hca : c*a = u 1*(starRingEnd ℂ) (u 2) := by
    calc
      _ = (u 0*(starRingEnd ℂ) (u 0)) * (u 1*(starRingEnd ℂ) (u 2)) := by dsimp [c,a]; ring
      _ = _ := by rw [hu 0]; ring
  have he2 : a*b+b*c+c*a = (starRingEnd ℂ) (gamma u) := by
    rw [hab,hbc,hca]
    simp [gamma, map_add, map_mul]
    ring
  change a^2+b^2+c^2 = (a+b+c)^2-2*(starRingEnd ℂ) (gamma u)
  rw [← he2]
  ring

theorem projected_trace (a b c : ℂ) :
    (∑ j, Complex.normSq (projected a b c j)) =
      Complex.normSq a+Complex.normSq b+Complex.normSq c-Complex.normSq (a+b+c)/3 := by
  norm_num [projected,Fin.sum_univ_succ,Complex.normSq_apply]
  ring

theorem projected_anisotropy (a b c : ℂ) :
    (∑ j, (projected a b c j)^2) = -(a^2+b^2+c^2)+(a+b+c)^2/3 := by
  simp [projected,Fin.sum_univ_succ,mul_pow]
  ring

theorem actual_projected_trace (u : Triple) (hu : UnitTriple u) :
    (∑ j, Complex.normSq (projectedRatios u j)) = 3-q u/3 := by
  have hun (j : Fin 3) : Complex.normSq (ratios u j) = 1 := by
    apply Complex.ofReal_injective
    simpa only [Complex.mul_conj,Complex.ofReal_one] using ratio_unit u hu j
  unfold projectedRatios
  rw [projected_trace,hun,hun,hun]
  change 1+1+1-Complex.normSq (gamma u)/3 = 3-Complex.normSq (gamma u)/3
  ring

theorem actual_projected_anisotropy (u : Triple) (hu : UnitTriple u) :
    (∑ j, (projectedRatios u j)^2) = -(2/3 : ℂ)*(gamma u)^2+2*(starRingEnd ℂ) (gamma u) := by
  unfold projectedRatios
  rw [projected_anisotropy,ratio_square_sum u hu]
  change -((gamma u)^2-2*(starRingEnd ℂ) (gamma u))+(gamma u)^2/3 = _
  ring

/-- The actual real coefficient matrix after projecting each ratio-angle triple
onto its mean-zero plane. The analytic derivative interpretation is external. -/
def coefficientMatrix (u v : Triple) : Matrix (Fin 2) (Fin 6) ℝ :=
  !![(projectedRatios u 0).re,(projectedRatios u 1).re,(projectedRatios u 2).re,
       (projectedRatios v 0).re,(projectedRatios v 1).re,(projectedRatios v 2).re;
     (projectedRatios u 0).im,(projectedRatios u 1).im,(projectedRatios u 2).im,
       (projectedRatios v 0).im,(projectedRatios v 1).im,(projectedRatios v 2).im]

def gramModel (x y : ℝ) : Matrix (Fin 2) (Fin 2) ℝ :=
  !![3-x^2+y^2/3,-4*x*y/3;
     -4*x*y/3,3+x^2/3-y^2]

theorem actual_coefficient_gram (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    coefficientMatrix u v * (coefficientMatrix u v).transpose =
      gramModel (gamma u).re (gamma u).im := by
  have hg := correlation_from_unitarity u v hu hv hunit
  have hgv : gamma v = -gamma u := by linear_combination hg
  have hqv : q v = q u := by simp [q,hgv]
  have ht : (∑ j, Complex.normSq (projectedRatios u j)) +
      (∑ j, Complex.normSq (projectedRatios v j)) = 6-2*q u/3 := by
    rw [actual_projected_trace u hu, actual_projected_trace v hv, hqv]
    ring
  have ha : (∑ j, (projectedRatios u j)^2) + (∑ j, (projectedRatios v j)^2) =
      -(4/3 : ℂ)*(gamma u)^2 := by
    rw [actual_projected_anisotropy u hu, actual_projected_anisotropy v hv,hgv,map_neg]
    ring
  have hre := congrArg Complex.re ha
  have him := congrArg Complex.im ha
  norm_num [Fin.sum_univ_succ,pow_two,Complex.mul_re,Complex.mul_im] at hre him
  norm_num [Fin.sum_univ_succ,Complex.normSq_apply,q] at ht
  ext i j
  fin_cases i <;> fin_cases j
  all_goals norm_num [coefficientMatrix,Matrix.mul_apply,Matrix.transpose_apply,
    Fin.sum_univ_succ,gramModel]
  · linear_combination (ht+hre)/2
  · linear_combination him/2
  · linear_combination him/2
  · linear_combination (ht-hre)/2

theorem gram_characteristic_polynomial (x y : ℝ) :
    (gramModel x y).charpoly =
      (X-C (3-(x^2+y^2))) * (X-C (3+(x^2+y^2)/3)) := by
  have hk : (3 : Polynomial ℝ)*C (1/3 : ℝ) = 1 := by
    calc
      _ = C ((3 : ℝ)*(1/3)) := by rw [map_mul]; norm_num [Polynomial.C_ofNat]
      _ = _ := by norm_num
  norm_num [Matrix.charpoly,Matrix.det_fin_two,gramModel,div_eq_mul_inv,
    map_sub,map_add,map_mul,map_pow,map_ofNat]
  linear_combination -(5*C (1/3 : ℝ)+1)*(C x)^2*(C y)^2*hk

theorem gram_quadratic_identity (x y a b : ℝ) :
    (![a,b] ⬝ᵥ (gramModel x y *ᵥ ![a,b])) =
      (3-(x^2+y^2))*(a^2+b^2)+(4/3)*(x*b-y*a)^2 := by
  simp [dotProduct,Matrix.mulVec,Fin.sum_univ_succ,gramModel]
  ring

theorem actual_uniform_lower_bound (u v : Triple)
    (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix))
    (a b : ℝ) :
    (3/2)*(a^2+b^2) ≤
      (![a,b] ⬝ᵥ ((coefficientMatrix u v * (coefficientMatrix u v).transpose) *ᵥ ![a,b])) := by
  have hq : (gamma u).re^2+(gamma u).im^2 ≤ 3/2 := by
    simpa [q,Complex.normSq_apply,pow_two] using (actual_parameter_range u v hu hv hunit).2
  have hn : 0 ≤ a^2+b^2 := add_nonneg (sq_nonneg a) (sq_nonneg b)
  have hp := mul_nonneg (show 0 ≤ 3/2-((gamma u).re^2+(gamma u).im^2) by linarith) hn
  rw [actual_coefficient_gram u v hu hv hunit,gram_quadratic_identity]
  nlinarith [sq_nonneg ((gamma u).re*b-(gamma u).im*a)]

theorem actual_coefficient_characteristic_polynomial (u v : Triple)
    (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    (coefficientMatrix u v * (coefficientMatrix u v).transpose).charpoly =
      (X-C (3-q u)) * (X-C (3+q u/3)) := by
  rw [actual_coefficient_gram u v hu hv hunit,gram_characteristic_polynomial]
  simp [q,Complex.normSq_apply,pow_two]

/-- On the mean-zero ratio-angle plane, the centered columns act exactly as
i times the original ratios. -/
theorem projected_action_on_mean_zero (u : Triple) (theta : Fin 3 → ℝ)
    (htheta : ∑ j, theta j = 0) :
    (∑ j, projectedRatios u j * (theta j : ℂ)) =
      Complex.I * (∑ j, ratios u j * (theta j : ℂ)) := by
  have hc : (∑ j, (theta j : ℂ)) = 0 := by exact_mod_cast htheta
  norm_num [Fin.sum_univ_succ] at hc
  simp [projectedRatios,projected,Fin.sum_univ_succ]
  linear_combination -(Complex.I*(ratios u 0+ratios u 1+ratios u 2)/3)*hc

theorem coefficient_action_on_mean_zero (u v : Triple) (theta phi : Fin 3 → ℝ)
    (htheta : ∑ j, theta j = 0) (hphi : ∑ j, phi j = 0) :
    coefficientMatrix u v *ᵥ ![theta 0,theta 1,theta 2,phi 0,phi 1,phi 2] =
      ![(Complex.I*((∑ j,ratios u j*(theta j : ℂ))+
          (∑ j,ratios v j*(phi j : ℂ)))).re,
        (Complex.I*((∑ j,ratios u j*(theta j : ℂ))+
          (∑ j,ratios v j*(phi j : ℂ)))).im] := by
  have hc := congrArg₂ (fun a b : ℂ => a+b)
    (projected_action_on_mean_zero u theta htheta) (projected_action_on_mean_zero v phi hphi)
  rw [← mul_add] at hc
  have hre := congrArg Complex.re hc
  have him := congrArg Complex.im hc
  norm_num [Fin.sum_univ_succ,Complex.mul_re,Complex.mul_im] at hre him
  ext i
  fin_cases i
  · simpa [coefficientMatrix,Matrix.mulVec,Fin.sum_univ_succ,add_assoc] using hre
  · simpa [coefficientMatrix,Matrix.mulVec,Fin.sum_univ_succ,add_assoc] using him

theorem gram_determinant (x y : ℝ) :
    (gramModel x y).det = (3-(x^2+y^2))*(3+(x^2+y^2)/3) := by
  simp [Matrix.det_fin_two,gramModel]
  ring

theorem actual_gram_determinant_positive (u v : Triple)
    (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    0 < (coefficientMatrix u v * (coefficientMatrix u v).transpose).det := by
  obtain ⟨hq0,hq⟩ := actual_parameter_range u v hu hv hunit
  rw [actual_coefficient_gram u v hu hv hunit,gram_determinant]
  have he : (gamma u).re^2+(gamma u).im^2 = q u := by simp [q,Complex.normSq_apply,pow_two]
  rw [he]
  exact mul_pos (by linarith) (by linarith)

def canonicalRightInverse (u v : Triple) : Matrix (Fin 6) (Fin 2) ℝ :=
  (coefficientMatrix u v).transpose *
    (coefficientMatrix u v * (coefficientMatrix u v).transpose)⁻¹

theorem actual_right_inverse (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    coefficientMatrix u v * canonicalRightInverse u v = 1 := by
  unfold canonicalRightInverse
  rw [← Matrix.mul_assoc]
  apply Matrix.mul_nonsing_inv
  exact isUnit_iff_ne_zero.mpr (ne_of_gt (actual_gram_determinant_positive u v hu hv hunit))

theorem actual_coefficient_surjective (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    Function.Surjective (Matrix.mulVec (coefficientMatrix u v)) := by
  intro y
  refine ⟨canonicalRightInverse u v *ᵥ y, ?_⟩
  rw [Matrix.mulVec_mulVec,actual_right_inverse u v hu hv hunit,Matrix.one_mulVec]

/-- The mean-zero ratio-angle domain, embedded with its inherited Euclidean metric. -/
def MeanZeroPair (x : Fin 6 → ℝ) : Prop :=
  x 0+x 1+x 2 = 0 ∧ x 3+x 4+x 5 = 0

theorem projected_sum_zero (u : Triple) : ∑ j, projectedRatios u j = 0 := by
  simp [projectedRatios,projected,Fin.sum_univ_succ]
  ring

theorem coefficient_transpose_mean_zero (u v : Triple) (z : Fin 2 → ℝ) :
    MeanZeroPair ((coefficientMatrix u v).transpose *ᵥ z) := by
  have hu := projected_sum_zero u
  have hv := projected_sum_zero v
  have hur := congrArg Complex.re hu
  have hui := congrArg Complex.im hu
  have hvr := congrArg Complex.re hv
  have hvi := congrArg Complex.im hv
  norm_num [Fin.sum_univ_succ] at hur hui hvr hvi
  constructor
  · simp [coefficientMatrix,Matrix.mulVec,dotProduct,Fin.sum_univ_succ]
    linear_combination z 0*hur+z 1*hui
  · simp [coefficientMatrix,Matrix.mulVec,dotProduct,Fin.sum_univ_succ]
    linear_combination z 0*hvr+z 1*hvi

theorem actual_right_inverse_mean_zero (u v : Triple) (y : Fin 2 → ℝ) :
    MeanZeroPair (canonicalRightInverse u v *ᵥ y) := by
  unfold canonicalRightInverse
  rw [← Matrix.mulVec_mulVec]
  exact coefficient_transpose_mean_zero u v _

theorem actual_right_inverse_energy (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix))
    (y : Fin 2 → ℝ) :
    (canonicalRightInverse u v *ᵥ y) ⬝ᵥ (canonicalRightInverse u v *ᵥ y) =
      ((coefficientMatrix u v * (coefficientMatrix u v).transpose)⁻¹ *ᵥ y) ⬝ᵥ y := by
  let z := (coefficientMatrix u v * (coefficientMatrix u v).transpose)⁻¹ *ᵥ y
  have hx : canonicalRightInverse u v *ᵥ y = (coefficientMatrix u v).transpose *ᵥ z := by
    exact (Matrix.mulVec_mulVec _ _ _).symm
  rw [hx, Matrix.dotProduct_mulVec, Matrix.vecMul_transpose, dotProduct_comm]
  change z ⬝ᵥ (coefficientMatrix u v *ᵥ ((coefficientMatrix u v).transpose *ᵥ z)) = _
  rw [← hx, Matrix.mulVec_mulVec, actual_right_inverse u v hu hv hunit, Matrix.one_mulVec]

theorem actual_right_inverse_bound (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix))
    (y : Fin 2 → ℝ) :
    (∑ i, (canonicalRightInverse u v *ᵥ y) i ^ 2) ≤ (2/3)*(∑ i, y i^2) := by
  let z := (coefficientMatrix u v * (coefficientMatrix u v).transpose)⁻¹ *ᵥ y
  let x := canonicalRightInverse u v *ᵥ y
  have hz : ![z 0,z 1] = z := by ext i; fin_cases i <;> rfl
  have hGz : (coefficientMatrix u v * (coefficientMatrix u v).transpose) *ᵥ z = y := by
    rw [Matrix.mulVec_mulVec, Matrix.mul_nonsing_inv]
    · exact Matrix.one_mulVec y
    · exact isUnit_iff_ne_zero.mpr (ne_of_gt (actual_gram_determinant_positive u v hu hv hunit))
  have he := actual_right_inverse_energy u v hu hv hunit y
  change (x ⬝ᵥ x) = z ⬝ᵥ y at he
  have hco := actual_uniform_lower_bound u v hu hv hunit (z 0) (z 1)
  rw [hz,hGz] at hco
  have hc := Finset.sum_mul_sq_le_sq_mul_sq Finset.univ z y
  have hn : 0 ≤ ∑ i, x i^2 := Finset.sum_nonneg (fun _ _ => sq_nonneg _)
  have hy : 0 ≤ ∑ i, y i^2 := Finset.sum_nonneg (fun _ _ => sq_nonneg _)
  have hze : z 0^2+z 1^2 = ∑ i, z i^2 := by simp [Fin.sum_univ_succ]
  rw [hze] at hco
  simp only [dotProduct,← pow_two] at he
  change (∑ i, z i*y i)^2 ≤ _ at hc
  simp only [dotProduct] at hco
  rw [← he] at hco hc
  have hm := mul_le_mul_of_nonneg_right hco hy
  change (∑ i, x i^2) ≤ _
  by_contra h
  have hp : 0 < ∑ i, x i^2 := by linarith
  nlinarith

theorem actual_bounded_mean_zero_preimage (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix))
    (y : Fin 2 → ℝ) :
    ∃ x : Fin 6 → ℝ, MeanZeroPair x ∧ coefficientMatrix u v *ᵥ x = y ∧
      (∑ i, x i^2) ≤ (2/3)*(∑ i, y i^2) := by
  refine ⟨canonicalRightInverse u v *ᵥ y,actual_right_inverse_mean_zero u v y,?_,
    actual_right_inverse_bound u v hu hv hunit y⟩
  rw [Matrix.mulVec_mulVec,actual_right_inverse u v hu hv hunit,Matrix.one_mulVec]

end MUBUniformSubmersion
