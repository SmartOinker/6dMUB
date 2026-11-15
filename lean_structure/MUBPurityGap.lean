module

public import Mathlib.LinearAlgebra.Matrix.PosDef
public import Mathlib.Analysis.Complex.Basic
public import Mathlib.Analysis.Complex.Order
public import Mathlib.Tactic.NoncommRing
public import Mathlib.Tactic.NormNum

@[expose] public section
noncomputable section

namespace MUBPurityGap

open Matrix
open scoped ComplexOrder

variable {m n : Type*} [Fintype m] [Fintype n] [DecidableEq n]

omit [DecidableEq n] in
/-- Zero weighted Gram trace means that the positive weight annihilates
every column. This uses positivity, not a cancellation of signed terms. -/
theorem trace_sandwich_zero_iff (D : Matrix m m ℂ) (A : Matrix m n ℂ)
    (hD : D.PosSemidef) :
    Matrix.trace (Aᴴ * D * A) = 0 ↔ D * A = 0 := by
  constructor
  · intro ht
    have hp := hD.conjTranspose_mul_mul_same A
    have hd : ∀ j, (Aᴴ * D * A) j j = 0 := by
      have hsum : ∑ j, (Aᴴ * D * A) j j = 0 := ht
      exact fun j => (Finset.sum_eq_zero_iff_of_nonneg
        (fun i _ => hp.diag_nonneg)).mp hsum j (Finset.mem_univ j)
    ext i j
    have hquad : star (fun k => A k j) ⬝ᵥ D *ᵥ (fun k => A k j) = 0 := by
      have hz := hd j
      rw [Matrix.mul_assoc] at hz
      simpa only [Matrix.mul_apply, Matrix.conjTranspose_apply,
        dotProduct, Matrix.mulVec, Pi.star_apply] using hz
    have hcol := hD.dotProduct_mulVec_zero_iff.mp hquad
    exact congrFun hcol i
  · intro h
    simp [Matrix.mul_assoc, h]

/-- The phase-coordinate purity defect; under the cap and trace premises
it is real and nonnegative in the canonical partial order on the complex numbers. -/
def purityGap (M : Matrix n n ℂ) : ℂ :=
  648 - Matrix.trace ((Mᴴ * M) * (Mᴴ * M))

private theorem trace_gap_identity (M : Matrix n n ℂ)
    (ht : Matrix.trace (Mᴴ * M) = 36) :
    Matrix.trace (M * ((18 : ℂ) • (1 : Matrix n n ℂ) - Mᴴ * M) * Mᴴ) =
      purityGap M := by
  rw [Matrix.trace_mul_cycle]
  simp only [Matrix.mul_sub, Matrix.mul_smul,
    Matrix.mul_one, Matrix.trace_sub, Matrix.trace_smul]
  rw [ht]
  unfold purityGap
  norm_num

theorem purity_gap_nonnegative (M : Matrix n n ℂ)
    (hcap : ((18 : ℂ) • (1 : Matrix n n ℂ) - Mᴴ * M).PosSemidef)
    (ht : Matrix.trace (Mᴴ * M) = 36) :
    0 ≤ purityGap M := by
  rw [← trace_gap_identity M ht]
  exact (hcap.mul_mul_conjTranspose_same M).trace_nonneg

/-- Under the proved Gram cap, vanishing of a degree-four scalar in M is
equivalent to the balanced cube identity. No universal vanishing is asserted. -/
theorem purity_gap_zero_iff_balanced (M : Matrix n n ℂ)
    (hcap : ((18 : ℂ) • (1 : Matrix n n ℂ) - Mᴴ * M).PosSemidef)
    (ht : Matrix.trace (Mᴴ * M) = 36) :
    purityGap M = 0 ↔ M * Mᴴ * M = (18 : ℂ) • M := by
  rw [← trace_gap_identity M ht]
  have hz := trace_sandwich_zero_iff
    ((18 : ℂ) • (1 : Matrix n n ℂ) - Mᴴ * M) Mᴴ hcap
  simp only [Matrix.conjTranspose_conjTranspose] at hz
  rw [hz]
  constructor
  · intro h
    have hh := congrArg Matrix.conjTranspose h
    simp only [Matrix.conjTranspose_mul, Matrix.conjTranspose_sub,
      Matrix.conjTranspose_smul, Matrix.conjTranspose_one, star_ofNat,
      Matrix.conjTranspose_conjTranspose, Matrix.conjTranspose_zero] at hh
    simp only [Matrix.mul_sub, Matrix.mul_smul, Matrix.mul_one] at hh
    simpa only [Matrix.mul_assoc] using (sub_eq_zero.mp hh).symm
  · intro h
    have hh : M * ((18 : ℂ) • (1 : Matrix n n ℂ) - Mᴴ * M) = 0 := by
      simp only [Matrix.mul_sub, Matrix.mul_smul, Matrix.mul_one]
      rw [← Matrix.mul_assoc, h, sub_self]
    have hc := congrArg Matrix.conjTranspose hh
    simpa only [Matrix.conjTranspose_mul, Matrix.conjTranspose_sub,
      Matrix.conjTranspose_smul, Matrix.conjTranspose_one, star_ofNat,
      Matrix.conjTranspose_conjTranspose, Matrix.conjTranspose_zero] using hc

/-- Conditional scalar reduction for three edges. The product being zero is
the still-missing global assertion, not a conclusion of this theorem. -/
theorem three_purity_product_zero_iff (X Y Z : Matrix n n ℂ)
    (hc : ∀ M ∈ ({X, Y, Z} : Set (Matrix n n ℂ)),
      ((18 : ℂ) • (1 : Matrix n n ℂ) - Mᴴ * M).PosSemidef)
    (ht : ∀ M ∈ ({X, Y, Z} : Set (Matrix n n ℂ)),
      Matrix.trace (Mᴴ * M) = 36) :
    purityGap X * purityGap Y * purityGap Z = 0 ↔
      X * Xᴴ * X = (18 : ℂ) • X ∨
      Y * Yᴴ * Y = (18 : ℂ) • Y ∨
      Z * Zᴴ * Z = (18 : ℂ) • Z := by
  rw [mul_eq_zero, mul_eq_zero,
    purity_gap_zero_iff_balanced X (hc X (by simp)) (ht X (by simp)),
    purity_gap_zero_iff_balanced Y (hc Y (by simp)) (ht Y (by simp)),
    purity_gap_zero_iff_balanced Z (hc Z (by simp)) (ht Z (by simp))]
  exact or_assoc

#print axioms trace_sandwich_zero_iff
#print axioms purity_gap_nonnegative
#print axioms purity_gap_zero_iff_balanced
#print axioms three_purity_product_zero_iff

end MUBPurityGap
