module

public import Mathlib.LinearAlgebra.Matrix.PosDef
public import Mathlib.Analysis.Complex.Order
public import Mathlib.Analysis.Complex.Basic
public import Mathlib.Analysis.RCLike.Basic
public import Mathlib.Tactic.NoncommRing
public import Mathlib.Tactic.NormNum

@[expose] public section
noncomputable section

namespace MUBGramCap

open Matrix
open scoped ComplexOrder

variable {m n p : Type*}
  [Fintype m] [Fintype n] [Fintype p]
  [DecidableEq m] [DecidableEq n]

/-- An exact sum-of-Gram factorization for the column defect of a frame
whose row defect has the supplied Gram factor P. -/
theorem gram_defect_factorization (V : Matrix m n ℂ) (P : Matrix m p ℂ)
    (h : P * Pᴴ = (24 : ℂ) • (1 : Matrix m m ℂ) - V * Vᴴ) :
    let Q := (24 : ℂ) • (1 : Matrix n n ℂ) - Vᴴ * V
    Qᴴ * Q + (Pᴴ * V)ᴴ * (Pᴴ * V) = (24 : ℂ) • Q := by
  dsimp only
  have hz : (Pᴴ * V)ᴴ * (Pᴴ * V) =
      (24 : ℂ) • (Vᴴ * V) - (Vᴴ * V) * (Vᴴ * V) := by
    calc
      _ = Vᴴ * (P * Pᴴ) * V := by simp [Matrix.mul_assoc]
      _ = _ := by rw [h]; simp [Matrix.mul_sub, Matrix.sub_mul,
        Matrix.mul_smul, Matrix.smul_mul, Matrix.mul_assoc]
  rw [hz]
  simp only [Matrix.conjTranspose_sub, Matrix.conjTranspose_smul,
    Matrix.conjTranspose_one, Matrix.conjTranspose_mul,
    Matrix.conjTranspose_conjTranspose, star_ofNat]
  simp only [Matrix.sub_mul, Matrix.mul_sub, Matrix.smul_mul, Matrix.mul_smul,
    Matrix.one_mul, Matrix.mul_one, smul_sub, smul_smul]
  abel

/-- The factorization certifies a column Gram cap without spectral theory. -/
theorem gram_cap_posSemidef (V : Matrix m n ℂ) (P : Matrix m p ℂ)
    (h : P * Pᴴ = (24 : ℂ) • (1 : Matrix m m ℂ) - V * Vᴴ) :
    ((24 : ℂ) • (1 : Matrix n n ℂ) - Vᴴ * V).PosSemidef := by
  let Q := (24 : ℂ) • (1 : Matrix n n ℂ) - Vᴴ * V
  have hsum := (Matrix.posSemidef_conjTranspose_mul_self Q).add
    (Matrix.posSemidef_conjTranspose_mul_self (Pᴴ * V))
  rw [gram_defect_factorization V P h] at hsum
  have hp := hsum.smul (show (0 : ℂ) ≤ 24⁻¹ from
    le_of_lt (RCLike.inv_pos_of_pos (by norm_num)))
  simpa only [smul_smul, inv_mul_cancel₀ (by norm_num : (24 : ℂ) ≠ 0),
    one_smul] using hp

/-- The physical squarefree-lift Gram identity translates the cap 24 into
the cube Gram cap 18. Both needed lift identities remain explicit premises. -/
theorem cube_gram_cap_posSemidef (V : Matrix m n ℂ) (P : Matrix m p ℂ)
    (M : Matrix n n ℂ)
    (hrow : P * Pᴴ = (24 : ℂ) • (1 : Matrix m m ℂ) - V * Vᴴ)
    (hcol : Vᴴ * V = (3 : ℂ)⁻¹ • (Mᴴ * M) +
      (18 : ℂ) • (1 : Matrix n n ℂ)) :
    ((18 : ℂ) • (1 : Matrix n n ℂ) - Mᴴ * M).PosSemidef := by
  have hp := (gram_cap_posSemidef V P hrow).smul (show (0 : ℂ) ≤ 3 by norm_num)
  rw [hcol] at hp
  have heq : (3 : ℂ) • ((24 : ℂ) • (1 : Matrix n n ℂ) -
      ((3 : ℂ)⁻¹ • (Mᴴ * M) + (18 : ℂ) • (1 : Matrix n n ℂ))) =
      (18 : ℂ) • (1 : Matrix n n ℂ) - Mᴴ * M := by
    simp only [smul_sub, smul_add, smul_smul]
    norm_num
    module
  rwa [heq] at hp

#print axioms gram_defect_factorization
#print axioms gram_cap_posSemidef
#print axioms cube_gram_cap_posSemidef

end MUBGramCap
