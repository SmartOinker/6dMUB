module

public import Mathlib.LinearAlgebra.Matrix.PosDef
public import Mathlib.LinearAlgebra.UnitaryGroup
public import Mathlib.Analysis.Complex.Basic
public import Mathlib.Analysis.Complex.Order
public import Mathlib.Tactic.NoncommRing
public import Mathlib.Tactic.NormNum

@[expose] public section
noncomputable section

namespace MUBCompatibility

open Matrix
open scoped ComplexOrder

variable {n : Type*} [Fintype n] [DecidableEq n]

omit [DecidableEq n] in
/-- The three coupled equations force the shared Gram matrix to be
idempotent, even before any invertibility or normalization is known. -/
theorem coupled_gram_idempotent (A B C : Matrix n n ℂ)
    (hAC : A * C = B) (hAB : Aᴴ * B = C) (hBC : B * Cᴴ = A) :
    Aᴴ * A = C * Cᴴ ∧ (Aᴴ * A) * (Aᴴ * A) = Aᴴ * A := by
  have hg : Aᴴ * A = C * Cᴴ := by
    calc
      _ = Aᴴ * (B * Cᴴ) := by rw [hBC]
      _ = (Aᴴ * B) * Cᴴ := by rw [Matrix.mul_assoc]
      _ = C * Cᴴ := by rw [hAB]
  refine ⟨hg, ?_⟩
  calc
    _ = (Aᴴ * A) * (C * Cᴴ) := by rw [← hg]
    _ = Aᴴ * (A * C) * Cᴴ := by simp only [Matrix.mul_assoc]
    _ = Aᴴ * B * Cᴴ := by rw [hAC]
    _ = Aᴴ * (B * Cᴴ) := by rw [Matrix.mul_assoc]
    _ = Aᴴ * A := by rw [hBC]

/-- A Hermitian idempotent with full trace is the identity. The proof uses
the zero Gram trace of I-P, without a rank test or invertibility premise. -/
theorem hermitian_idempotent_eq_one_of_trace (P : Matrix n n ℂ)
    (hherm : Pᴴ = P) (hidem : P * P = P)
    (htrace : Matrix.trace P = (Fintype.card n : ℂ)) :
    P = 1 := by
  have hq : (1 - P)ᴴ * (1 - P) = 1 - P := by
    simp only [Matrix.conjTranspose_sub, Matrix.conjTranspose_one, hherm]
    calc
      _ = 1 - P - P + P * P := by noncomm_ring
      _ = 1 - P := by rw [hidem]; abel
  have hzero : Matrix.trace ((1 - P)ᴴ * (1 - P)) = 0 := by
    rw [hq, Matrix.trace_sub, Matrix.trace_one, htrace, sub_self]
  have heq : (1 : Matrix n n ℂ) - P = 0 :=
    Matrix.trace_conjTranspose_mul_self_eq_zero_iff.mp hzero
  exact (sub_eq_zero.mp heq).symm

/-- Closure of the coupled equations in arbitrary finite dimension:
normalization of one Gram trace forces all three square matrices to be unitary. -/
theorem coupled_equations_unitary (A B C : Matrix n n ℂ)
    (hAC : A * C = B) (hAB : Aᴴ * B = C) (hBC : B * Cᴴ = A)
    (htrace : Matrix.trace (Aᴴ * A) = (Fintype.card n : ℂ)) :
    A ∈ Matrix.unitaryGroup n ℂ ∧
      B ∈ Matrix.unitaryGroup n ℂ ∧
      C ∈ Matrix.unitaryGroup n ℂ := by
  obtain ⟨hg, hi⟩ := coupled_gram_idempotent A B C hAC hAB hBC
  have hA : Aᴴ * A = 1 := hermitian_idempotent_eq_one_of_trace (Aᴴ * A)
    (by simp only [Matrix.conjTranspose_mul, Matrix.conjTranspose_conjTranspose])
    hi htrace
  have hC : C * Cᴴ = 1 := hg.symm.trans hA
  have hAU : A ∈ Matrix.unitaryGroup n ℂ :=
    Matrix.mem_unitaryGroup_iff'.mpr (by simpa only [Matrix.star_eq_conjTranspose] using hA)
  have hCU : C ∈ Matrix.unitaryGroup n ℂ :=
    Matrix.mem_unitaryGroup_iff.mpr (by simpa only [Matrix.star_eq_conjTranspose] using hC)
  have hBU : B ∈ Matrix.unitaryGroup n ℂ := by
    rw [← hAC]
    exact (Matrix.unitaryGroup n ℂ).mul_mem hAU hCU
  exact ⟨hAU, hBU, hCU⟩

omit [DecidableEq n] in
/-- Flatness supplies the required trace without assuming orthogonality. -/
theorem trace_gram_of_normalized_flat [Nonempty n] (A : Matrix n n ℂ)
    (hflat : ∀ i j, Complex.normSq (A i j) = (Fintype.card n : ℝ)⁻¹) :
    Matrix.trace (Aᴴ * A) = (Fintype.card n : ℂ) := by
  have hc : (Fintype.card n : ℂ) ≠ 0 := by
    exact_mod_cast Fintype.card_ne_zero
  have he (i j : n) : star (A i j) * A i j = (Fintype.card n : ℂ)⁻¹ := by
    rw [mul_comm, Complex.star_def, Complex.mul_conj, hflat]
    simp only [Complex.ofReal_inv, Complex.ofReal_natCast]
  simp only [Matrix.trace, Matrix.diag_apply, Matrix.mul_apply,
    Matrix.conjTranspose_apply, he, Finset.sum_const, Finset.card_univ, nsmul_eq_mul]
  simp [hc]

/-- In particular, the reconstructed flat matrix needs no additional
invertibility or orthogonality assumption for coupled closure. -/
theorem coupled_flat_unitary [Nonempty n] (A B C : Matrix n n ℂ)
    (hAC : A * C = B) (hAB : Aᴴ * B = C) (hBC : B * Cᴴ = A)
    (hflat : ∀ i j, Complex.normSq (A i j) = (Fintype.card n : ℝ)⁻¹) :
    A ∈ Matrix.unitaryGroup n ℂ ∧
      B ∈ Matrix.unitaryGroup n ℂ ∧
      C ∈ Matrix.unitaryGroup n ℂ :=
  coupled_equations_unitary A B C hAC hAB hBC (trace_gram_of_normalized_flat A hflat)

#print axioms coupled_gram_idempotent
#print axioms hermitian_idempotent_eq_one_of_trace
#print axioms coupled_equations_unitary
#print axioms trace_gram_of_normalized_flat
#print axioms coupled_flat_unitary

end MUBCompatibility
