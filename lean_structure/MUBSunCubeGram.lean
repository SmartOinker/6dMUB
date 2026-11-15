module
public import Mathlib.Analysis.Complex.Basic
public import Mathlib.LinearAlgebra.Matrix.Notation
public import Mathlib.LinearAlgebra.Matrix.Trace
public import Mathlib.LinearAlgebra.Matrix.Hermitian
public import Mathlib.LinearAlgebra.Matrix.PosDef
public import Mathlib.Analysis.Complex.Order
public import Mathlib.Analysis.RCLike.Basic
public import Mathlib.Tactic.NoncommRing
public import Mathlib.Algebra.BigOperators.Fin
public import Mathlib.Tactic.LinearCombination
public import Mathlib.Tactic.Ring
public import Mathlib.Tactic.NormNum
public import Mathlib.Tactic.FinCases
@[expose] public section
noncomputable section
namespace MUBSunCubeGram
open Matrix
open scoped ComplexOrder
abbrev Triple := Fin 3 → ℂ
abbrev SixMatrix := Matrix (Fin 6) (Fin 6) ℂ

def UnitTriple (u : Triple) : Prop := ∀ j, u j * (starRingEnd ℂ) (u j) = 1

def gamma (u : Triple) : ℂ :=
  u 1 * (starRingEnd ℂ) (u 0) + u 2 * (starRingEnd ℂ) (u 1) +
    u 0 * (starRingEnd ℂ) (u 2)

/-- The unregistered Hankel-block transition, in ternary-then-binary order.
The identity with a composed physical seed is not assumed by this definition. -/
def blockMatrix (u v : Triple) : SixMatrix :=
  !![u 0,Complex.I*(starRingEnd ℂ) (v 0),u 1,Complex.I*(starRingEnd ℂ) (v 2),u 2,Complex.I*(starRingEnd ℂ) (v 1);
     Complex.I*v 0,(starRingEnd ℂ) (u 0),Complex.I*v 1,(starRingEnd ℂ) (u 2),Complex.I*v 2,(starRingEnd ℂ) (u 1);
     u 1,Complex.I*(starRingEnd ℂ) (v 2),u 2,Complex.I*(starRingEnd ℂ) (v 1),u 0,Complex.I*(starRingEnd ℂ) (v 0);
     Complex.I*v 1,(starRingEnd ℂ) (u 2),Complex.I*v 2,(starRingEnd ℂ) (u 1),Complex.I*v 0,(starRingEnd ℂ) (u 0);
     u 2,Complex.I*(starRingEnd ℂ) (v 1),u 0,Complex.I*(starRingEnd ℂ) (v 0),u 1,Complex.I*(starRingEnd ℂ) (v 2);
     Complex.I*v 2,(starRingEnd ℂ) (u 1),Complex.I*v 0,(starRingEnd ℂ) (u 0),Complex.I*v 1,(starRingEnd ℂ) (u 2)]

def correlationGram (z : ℂ) : SixMatrix :=
  !![6,0,z,0,(starRingEnd ℂ) z,0;
     0,6,0,z,0,(starRingEnd ℂ) z;
     (starRingEnd ℂ) z,0,6,0,z,0;
     0,(starRingEnd ℂ) z,0,6,0,z;
     z,0,(starRingEnd ℂ) z,0,6,0;
     0,z,0,(starRingEnd ℂ) z,0,6]

def entryCube (C : SixMatrix) : SixMatrix := fun i j => C i j ^ 3

set_option maxHeartbeats 4000000
set_option maxRecDepth 100000

theorem actual_block_gram (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v) :
    (blockMatrix u v)ᴴ * blockMatrix u v = correlationGram (gamma u + gamma v) := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [Matrix.mul_apply, Matrix.conjTranspose_apply, Fin.sum_univ_succ,
      blockMatrix, correlationGram, gamma, map_add, map_mul]
  all_goals ring_nf
  all_goals rw [Complex.I_sq]
  all_goals ring_nf
  all_goals linear_combination hu 0 + hu 1 + hu 2 + hv 0 + hv 1 + hv 2

/-- The correlation cancellation follows from actual unitarity of the displayed
block matrix; it is not an extra relaxed-model premise. -/
theorem correlation_from_unitarity (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    gamma u + gamma v = 0 := by
  rw [actual_block_gram u v hu hv] at hunit
  have h := congrFun (congrFun hunit 0) 2
  simpa [correlationGram, Matrix.smul_apply, Matrix.one_apply] using h

theorem gamma_cube (u : Triple) (hu : UnitTriple u) :
    gamma (fun j => u j ^ 3) =
      (gamma u)^3 - 3 * gamma u * (starRingEnd ℂ) (gamma u) + 3 := by
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
  have habc : a*b*c = 1 := by
    calc
      _ = (u 0*(starRingEnd ℂ) (u 0)) * (u 1*(starRingEnd ℂ) (u 1)) *
          (u 2*(starRingEnd ℂ) (u 2)) := by dsimp [a,b,c]; ring
      _ = _ := by rw [hu 0, hu 1, hu 2]; ring
  have he2 : a*b+b*c+c*a = (starRingEnd ℂ) (gamma u) := by
    rw [hab,hbc,hca]
    simp [gamma, map_add, map_mul]
    ring
  have hsum : a+b+c = gamma u := rfl
  have hcube : gamma (fun j => u j ^ 3) = a^3+b^3+c^3 := by
    simp [gamma,a,b,c,map_pow,mul_pow]
  have hn : a^3+b^3+c^3 = (a+b+c)^3-3*(a+b+c)*(a*b+b*c+c*a)+3*a*b*c := by ring
  rw [hcube, hn, hsum, he2]
  linear_combination 3*habc

def q (u : Triple) : ℝ := Complex.normSq (gamma u)

theorem cube_correlation_cancellation (u v : Triple)
    (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    gamma (fun j => u j ^ 3) + gamma (fun j => v j ^ 3) =
      6-6*(q u : ℂ) := by
  have hg := correlation_from_unitarity u v hu hv hunit
  have hgv : gamma v = -gamma u := by linear_combination hg
  rw [gamma_cube u hu, gamma_cube v hv, hgv, map_neg]
  have hnorm := Complex.mul_conj (gamma u)
  change gamma u * (starRingEnd ℂ) (gamma u) = (q u : ℂ) at hnorm
  linear_combination -6*hnorm

theorem cube_block_formula (u v : Triple) :
    entryCube (blockMatrix u v) = blockMatrix (fun j => u j ^ 3) (fun j => -(v j ^ 3)) := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [entryCube, blockMatrix, mul_pow, map_pow]

theorem actual_cube_gram (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    (entryCube (blockMatrix u v))ᴴ * entryCube (blockMatrix u v) =
      correlationGram (6-6*(q u : ℂ)) := by
  have hu3 : UnitTriple (fun j => u j^3) := by
    intro j
    change u j^3 * (starRingEnd ℂ) (u j^3) = 1
    rw [map_pow, ← mul_pow, hu j]
    norm_num
  have hv3 : UnitTriple (fun j => -(v j^3)) := by
    intro j
    change -(v j^3) * (starRingEnd ℂ) (-(v j^3)) = 1
    rw [map_neg, neg_mul_neg, map_pow, ← mul_pow, hv j]
    norm_num
  rw [cube_block_formula, actual_block_gram _ _ hu3 hv3]
  have hneg : gamma (fun j => -(v j^3)) = gamma (fun j => v j^3) := by simp [gamma]
  rw [hneg, cube_correlation_cancellation u v hu hv hunit]

/-- Positivity of the actual cube Gram gives the range, rather than postulating
nonnegative eigenvalues of a desired spectral formula. -/
theorem actual_parameter_range (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    0 ≤ q u ∧ q u ≤ 3/2 := by
  constructor
  · exact Complex.normSq_nonneg _
  · have hp := Matrix.posSemidef_conjTranspose_mul_self (entryCube (blockMatrix u v))
    have hh := hp.dotProduct_mulVec_nonneg (![1,0,1,0,1,0] : Fin 6 → ℂ)
    have hr := (RCLike.nonneg_iff.mp hh).1
    rw [actual_cube_gram u v hu hv hunit] at hr
    norm_num [dotProduct, Matrix.mulVec, Fin.sum_univ_succ, correlationGram] at hr
    linarith

def modelGram (t : ℝ) : SixMatrix := correlationGram (6-6*(t : ℂ))

theorem model_quadratic_identity (t : ℝ) :
    (modelGram t - (18-12*(t : ℂ)) • (1 : SixMatrix)) *
      (modelGram t - (6*(t : ℂ)) • (1 : SixMatrix)) = 0 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [modelGram, correlationGram, Matrix.mul_apply, Matrix.smul_apply,
      Matrix.one_apply, Fin.sum_univ_succ, map_ofNat] <;> ring

theorem actual_cube_quadratic_identity (u v : Triple)
    (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    let G := (entryCube (blockMatrix u v))ᴴ * entryCube (blockMatrix u v)
    (G-(18-12*(q u : ℂ)) • (1 : SixMatrix)) *
      (G-(6*(q u : ℂ)) • (1 : SixMatrix)) = 0 := by
  dsimp only
  rw [actual_cube_gram u v hu hv hunit]
  exact model_quadratic_identity _

theorem model_trace_square (t : ℝ) :
    (Matrix.trace (modelGram t ^ 2)).re = 648-864*t+432*t^2 := by
  simp [modelGram, correlationGram, Matrix.trace, Matrix.diag_apply, pow_succ,
    Fin.sum_univ_succ]
  ring

def frobeniusSq (M : SixMatrix) : ℝ := ∑ i, ∑ j, Complex.normSq (M i j)
def residual (M : SixMatrix) : SixMatrix := M*Mᴴ*M - 18*M

theorem frobenius_trace (M : SixMatrix) :
    frobeniusSq M = (Matrix.trace (Mᴴ*M)).re := by
  simp [frobeniusSq, Matrix.trace, Matrix.diag_apply, Matrix.mul_apply,
    Matrix.conjTranspose_apply, Fin.sum_univ_succ, Complex.normSq_apply]
  ring

theorem residual_square_identity (M : SixMatrix) :
    (residual M)ᴴ * residual M = (Mᴴ*M)^3 - 36*(Mᴴ*M)^2 + 324*(Mᴴ*M) := by
  simp only [residual, Matrix.conjTranspose_sub, Matrix.conjTranspose_mul,
    Matrix.conjTranspose_conjTranspose, Matrix.conjTranspose_ofNat]
  noncomm_ring

theorem model_residual_trace (t : ℝ) :
    (Matrix.trace (modelGram t^3 - 36*modelGram t^2 + 324*modelGram t)).re =
      2592*t*(3-t^2) := by
  simp [modelGram, correlationGram, Matrix.trace, Matrix.diag_apply, pow_succ,
    Matrix.mul_apply, Matrix.ofNat_apply, Fin.sum_univ_succ]
  ring

/-- The normalization is written explicitly in the phase-matrix scale. -/
def normalizedDeficit (M : SixMatrix) : ℝ :=
  1/72 - (Matrix.trace ((Mᴴ*M)^2)).re/46656

theorem actual_deficit_formula (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    normalizedDeficit (entryCube (blockMatrix u v)) = q u*(2-q u)/108 := by
  unfold normalizedDeficit
  rw [actual_cube_gram u v hu hv hunit]
  change 1/72 - (Matrix.trace (modelGram (q u)^2)).re/46656 = _
  rw [model_trace_square]
  ring

theorem actual_residual_energy (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    frobeniusSq (residual (entryCube (blockMatrix u v))) = 2592*q u*(3-(q u)^2) := by
  rw [frobenius_trace, residual_square_identity, actual_cube_gram u v hu hv hunit]
  exact model_residual_trace _

/-- The actual entrywise Frobenius sum detects the zero matrix. -/
theorem frobenius_zero_iff (M : SixMatrix) : frobeniusSq M = 0 ↔ M = 0 := by
  constructor
  · intro h
    have hi : ∀ i, (∑ j, Complex.normSq (M i j)) = 0 := by
      intro i
      exact (Finset.sum_eq_zero_iff_of_nonneg
        (fun i _ => Finset.sum_nonneg (fun j _ => Complex.normSq_nonneg (M i j)))).mp h
        i (Finset.mem_univ i)
    ext i j
    have hij := (Finset.sum_eq_zero_iff_of_nonneg
      (fun j _ => Complex.normSq_nonneg (M i j))).mp (hi i) j (Finset.mem_univ j)
    exact Complex.normSq_eq_zero.mp hij
  · intro h
    rw [h]
    simp [frobeniusSq]

theorem actual_deficit_zero_iff (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    normalizedDeficit (entryCube (blockMatrix u v)) = 0 ↔ q u = 0 := by
  have hq := (actual_parameter_range u v hu hv hunit).2
  have hn : 2-q u ≠ 0 := by linarith
  rw [actual_deficit_formula u v hu hv hunit]
  simp [div_eq_zero_iff, mul_eq_zero, hn]

theorem actual_residual_zero_iff (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    residual (entryCube (blockMatrix u v)) = 0 ↔ q u = 0 := by
  obtain ⟨hq0,hq⟩ := actual_parameter_range u v hu hv hunit
  have hq2 : (q u)^2 ≤ (3/2 : ℝ)^2 := (sq_le_sq₀ hq0 (by norm_num)).mpr hq
  have hn : 3-(q u)^2 ≠ 0 := by nlinarith
  rw [← frobenius_zero_iff, actual_residual_energy u v hu hv hunit]
  simp [mul_eq_zero, hn]

theorem actual_deficit_maximum (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    normalizedDeficit (entryCube (blockMatrix u v)) ≤ 1/108 ∧
      (normalizedDeficit (entryCube (blockMatrix u v)) = 1/108 ↔ q u = 1) := by
  rw [actual_deficit_formula u v hu hv hunit]
  constructor
  · nlinarith [sq_nonneg (q u-1)]
  · constructor
    · intro h
      nlinarith [sq_nonneg (q u-1)]
    · intro h
      rw [h]
      norm_num

theorem actual_energy_maximum (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    frobeniusSq (residual (entryCube (blockMatrix u v))) ≤ 5184 ∧
      (frobeniusSq (residual (entryCube (blockMatrix u v))) = 5184 ↔ q u = 1) := by
  rw [actual_residual_energy u v hu hv hunit]
  have hq0 := (actual_parameter_range u v hu hv hunit).1
  have hp : 0 < q u+2 := by linarith
  have hfac : 5184-2592*q u*(3-(q u)^2) = 2592*(q u-1)^2*(q u+2) := by ring
  have hnonneg := mul_nonneg (sq_nonneg (q u-1)) (le_of_lt hp)
  constructor
  · nlinarith [hfac]
  · constructor
    · intro he
      have hz : (q u-1)^2*(q u+2) = 0 := by nlinarith [hfac]
      have hs := (mul_eq_zero.mp hz).resolve_right (ne_of_gt hp)
      nlinarith
    · intro he
      rw [he]
      norm_num

def witnessU : Triple := ![1,Complex.I,Complex.I]
def witnessV : Triple := ![1,-1,-1]

/-- An explicit phase-unitary block with q=1; no identification with the
previously registered Sun anchor is asserted. -/
theorem actual_maximum_witness :
    UnitTriple witnessU ∧ UnitTriple witnessV ∧
      (blockMatrix witnessU witnessV)ᴴ * blockMatrix witnessU witnessV =
        (6 : ℂ) • (1 : SixMatrix) ∧ q witnessU = 1 := by
  have hu : UnitTriple witnessU := by
    intro j
    fin_cases j <;> norm_num [witnessU]
  have hv : UnitTriple witnessV := by
    intro j
    fin_cases j <;> norm_num [witnessV]
  refine ⟨hu,hv,?_,?_⟩
  · rw [actual_block_gram _ _ hu hv]
    ext i j
    fin_cases i <;> fin_cases j <;>
      norm_num [correlationGram, gamma, witnessU, witnessV, Matrix.smul_apply, Matrix.one_apply]
  · norm_num [q,gamma,witnessU]

theorem actual_witness_values :
    normalizedDeficit (entryCube (blockMatrix witnessU witnessV)) = 1/108 ∧
      frobeniusSq (residual (entryCube (blockMatrix witnessU witnessV))) = 5184 := by
  obtain ⟨hu,hv,hh,hq⟩ := actual_maximum_witness
  rw [actual_deficit_formula _ _ hu hv hh, actual_residual_energy _ _ hu hv hh, hq]
  norm_num

theorem actual_block_entries_unit (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (i j : Fin 6) : Complex.normSq (blockMatrix u v i j) = 1 := by
  have hnu (k : Fin 3) : Complex.normSq (u k) = 1 := by
    apply Complex.ofReal_injective
    simpa only [Complex.mul_conj, Complex.ofReal_one] using hu k
  have hnv (k : Fin 3) : Complex.normSq (v k) = 1 := by
    apply Complex.ofReal_injective
    simpa only [Complex.mul_conj, Complex.ofReal_one] using hv k
  fin_cases i <;> fin_cases j <;>
    norm_num [blockMatrix, map_mul, hnu, hnv]

def phaseNormalize (C : SixMatrix) : SixMatrix := ((1/Real.sqrt 6 : ℝ) : ℂ) • C

/-- The rational phase-scale deficit is exactly the purity deficit of the
entrywise cube of the normalized matrix C/sqrt(6). -/
theorem actual_normalization_identity (C : SixMatrix) :
    normalizedDeficit (entryCube C) =
      1/72 - (Matrix.trace (((entryCube (phaseNormalize C))ᴴ *
        entryCube (phaseNormalize C))^2)).re := by
  let r : ℝ := 1/(6*Real.sqrt 6)
  have hs : (Real.sqrt 6)^2 = 6 := Real.sq_sqrt (by norm_num)
  have hn : Real.sqrt 6 ≠ 0 := Real.sqrt_ne_zero'.mpr (by norm_num)
  have hs3 : (Real.sqrt 6)^3 = 6*Real.sqrt 6 := by rw [pow_succ,hs]
  have hs4 : (Real.sqrt 6)^4 = 36 := by
    calc
      (Real.sqrt 6)^4 = ((Real.sqrt 6)^2)^2 := by ring
      _ = 36 := by rw [hs]; norm_num
  have hr3 : (1/Real.sqrt 6 : ℝ)^3 = r := by
    dsimp [r]
    field_simp [hn]
    nlinarith [hs3]
  have hr4 : r^4 = 1/46656 := by
    norm_num [r,div_pow,mul_pow,hs4]
  have hcube : entryCube (phaseNormalize C) = (r : ℂ) • entryCube C := by
    ext i j
    simp only [entryCube, phaseNormalize, Matrix.smul_apply, smul_eq_mul, mul_pow]
    have hh : (((1/Real.sqrt 6 : ℝ) : ℂ))^3 = (r : ℂ) := by exact_mod_cast hr3
    rw [hh]
  have hscale (M : SixMatrix) :
      (Matrix.trace ((((r : ℂ) • M)ᴴ * ((r : ℂ) • M))^2)).re =
        r^4*(Matrix.trace ((Mᴴ*M)^2)).re := by
    simp only [pow_two, Matrix.conjTranspose_smul, Matrix.smul_mul,
      Matrix.mul_smul, Matrix.trace_smul, smul_smul, smul_eq_mul]
    simp [pow_succ, mul_assoc]
  rw [hcube,hscale,hr4]
  unfold normalizedDeficit
  ring

end MUBSunCubeGram
