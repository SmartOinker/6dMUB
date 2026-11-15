module

public import MUBResidual
public import MUBPurityGap
public import Mathlib.Tactic.Linarith

@[expose] public section
noncomputable section

namespace MUBResidualBounds

open Matrix MUBResidual MUBPurityGap
open scoped ComplexOrder

variable {n : Type*} [Fintype n] [DecidableEq n]

/-- The squared Frobenius norm of the balanced cubic residual. -/
def residualEnergy (M : Matrix n n ℂ) : ℂ :=
  Matrix.trace ((MUBResidual.residual M)ᴴ * MUBResidual.residual M)

omit [DecidableEq n] in
private theorem purityGap_star (M : Matrix n n ℂ) :
    star (purityGap M) = purityGap M := by
  unfold purityGap
  rw [star_sub, star_ofNat, ← Matrix.trace_conjTranspose]
  simp only [Matrix.conjTranspose_mul, Matrix.conjTranspose_conjTranspose]

omit [DecidableEq n] in
private theorem residual_cross_trace (M : Matrix n n ℂ)
    (ht : Matrix.trace (Mᴴ * M) = 36) :
    Matrix.trace (Mᴴ * MUBResidual.residual M) = -purityGap M := by
  simp only [MUBResidual.residual, Matrix.mul_sub, Matrix.mul_smul, Matrix.trace_sub,
    Matrix.trace_smul]
  have heq : Mᴴ * (M * Mᴴ * M) = (Mᴴ * M) * (Mᴴ * M) := by
    simp only [Matrix.mul_assoc]
  rw [heq, ht]
  unfold purityGap
  ring

omit [DecidableEq n] in
private theorem residual_cross_trace_reverse (M : Matrix n n ℂ)
    (ht : Matrix.trace (Mᴴ * M) = 36) :
    Matrix.trace ((MUBResidual.residual M)ᴴ * M) = -purityGap M := by
  have h := congrArg star (residual_cross_trace M ht)
  rw [← Matrix.trace_conjTranspose, star_neg, purityGap_star] at h
  simpa only [Matrix.conjTranspose_mul, Matrix.conjTranspose_conjTranspose] using h

omit [DecidableEq n] in
/-- Completing the Frobenius square gives an exact certificate for the lower bound.
The trace normalization is the only premise. -/
theorem residual_purity_square_identity (M : Matrix n n ℂ)
    (ht : Matrix.trace (Mᴴ * M) = 36) :
    let Z := (36 : ℂ) • MUBResidual.residual M + purityGap M • M
    Matrix.trace (Zᴴ * Z) = 1296 * residualEnergy M - 36 * purityGap M ^ 2 := by
  dsimp only
  simp only [Matrix.conjTranspose_add, Matrix.conjTranspose_smul, star_ofNat,
    purityGap_star, Matrix.add_mul, Matrix.mul_add, Matrix.smul_mul,
    Matrix.mul_smul, Matrix.trace_add, Matrix.trace_smul, smul_eq_mul]
  rw [residual_cross_trace M ht, residual_cross_trace_reverse M ht, ht]
  unfold residualEnergy
  ring

/-- The Gram-cap defect supplies an exact nonnegative certificate for the upper bound. -/
theorem residual_purity_cap_identity (M : Matrix n n ℂ)
    (ht : Matrix.trace (Mᴴ * M) = 36) :
    18 * purityGap M - residualEnergy M =
      Matrix.trace ((Mᴴ * M) * ((18 : ℂ) • (1 : Matrix n n ℂ) - Mᴴ * M) *
        (Mᴴ * M)) := by
  unfold purityGap residualEnergy MUBResidual.residual
  simp only [Matrix.conjTranspose_sub, Matrix.conjTranspose_mul,
    Matrix.conjTranspose_smul, Matrix.conjTranspose_conjTranspose, star_ofNat,
    Matrix.mul_sub, Matrix.sub_mul, Matrix.mul_smul, Matrix.smul_mul,
    Matrix.mul_one, Matrix.trace_sub, Matrix.trace_smul, smul_eq_mul]
  simp only [Matrix.mul_assoc] at ht ⊢
  rw [ht]
  ring

omit [DecidableEq n] in
/-- With Frobenius mass 36, the residual energy controls the square of the purity gap,
without requiring a Gram cap. ComplexOrder asserts both reality and the real inequality. -/
theorem residual_purity_lower_bound (M : Matrix n n ℂ)
    (ht : Matrix.trace (Mᴴ * M) = 36) :
    purityGap M ^ 2 / 36 ≤ residualEnergy M := by
  have hp := (Matrix.posSemidef_conjTranspose_mul_self
    ((36 : ℂ) • MUBResidual.residual M + purityGap M • M)).trace_nonneg
  rw [residual_purity_square_identity M ht] at hp
  have he : 0 ≤ residualEnergy M :=
    (Matrix.posSemidef_conjTranspose_mul_self (MUBResidual.residual M)).trace_nonneg
  have hw : ((purityGap M).re : ℂ) = purityGap M :=
    Complex.conj_eq_iff_re.mp (purityGap_star M)
  have hr : ((residualEnergy M).re : ℂ) = residualEnergy M :=
    (Complex.eq_re_of_ofReal_le he).symm
  rw [← hw, ← hr] at hp ⊢
  have hpR : 0 ≤ 1296 * (residualEnergy M).re - 36 * (purityGap M).re ^ 2 := by
    exact_mod_cast hp
  have hle : (purityGap M).re ^ 2 / 36 ≤ (residualEnergy M).re := by
    nlinarith
  exact_mod_cast hle

/-- Under the Gram cap, the residual energy is at most eighteen times the purity gap. -/
theorem residual_purity_upper_bound (M : Matrix n n ℂ)
    (hcap : ((18 : ℂ) • (1 : Matrix n n ℂ) - Mᴴ * M).PosSemidef)
    (ht : Matrix.trace (Mᴴ * M) = 36) :
    residualEnergy M ≤ 18 * purityGap M := by
  have hp := (hcap.conjTranspose_mul_mul_same (Mᴴ * M)).trace_nonneg
  simp only [Matrix.conjTranspose_mul, Matrix.conjTranspose_conjTranspose] at hp
  rw [← residual_purity_cap_identity M ht] at hp
  exact sub_nonneg.mp hp

end MUBResidualBounds
