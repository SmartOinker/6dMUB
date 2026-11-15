module

public import Mathlib.LinearAlgebra.Matrix.Hermitian
public import Mathlib.LinearAlgebra.Matrix.Rank
public import Mathlib.LinearAlgebra.Trace
public import Mathlib.Analysis.Complex.Order
public import Mathlib.Analysis.RCLike.Basic
public import Mathlib.Analysis.Complex.Basic
public import Mathlib.Tactic.NoncommRing
public import Mathlib.Tactic.NormNum

@[expose] public section
noncomputable section

namespace MUBResidual

open Matrix
open scoped ComplexOrder

variable {n : Type*} [Fintype n] [DecidableEq n]

/-- The balanced rank-two residual, applied to the entrywise cube of a
phase Hadamard matrix in the dimension-six application. -/
def residual (M : Matrix n n ℂ) : Matrix n n ℂ :=
  M * Mᴴ * M - (18 : ℂ) • M

def gramProjection (M : Matrix n n ℂ) : Matrix n n ℂ :=
  (18 : ℂ)⁻¹ • (M * Mᴴ)

omit [DecidableEq n] in
theorem residual_zero_iff (M : Matrix n n ℂ) :
    residual M = 0 ↔ M * Mᴴ * M = (18 : ℂ) • M := by
  exact sub_eq_zero

theorem residual_unitary_covariance (U M V : Matrix n n ℂ)
    (hU : Uᴴ * U = 1) (hV : V * Vᴴ = 1) :
    residual (U * M * V) = U * residual M * V := by
  have hcore :
      (U * M * V) * (U * M * V)ᴴ * (U * M * V) =
        U * (M * Mᴴ * M) * V := by
    simp only [Matrix.conjTranspose_mul]
    calc
      _ = U * M * (V * Vᴴ) * Mᴴ * (Uᴴ * U) * M * V := by noncomm_ring
      _ = _ := by rw [hV, hU]; simp only [Matrix.mul_one, Matrix.mul_assoc]
  unfold residual
  rw [hcore]
  simp only [Matrix.mul_sub, Matrix.sub_mul, Matrix.mul_smul, Matrix.smul_mul]

omit [DecidableEq n] in
theorem residual_adjoint (M : Matrix n n ℂ) :
    residual Mᴴ = (residual M)ᴴ := by
  simp [residual, Matrix.mul_assoc]

omit [DecidableEq n] in
theorem residual_transpose (M : Matrix n n ℂ) :
    residual Mᵀ = (residual M)ᵀ := by
  simp [residual, Matrix.mul_assoc,
    Matrix.conjTranspose_transpose_eq_transpose_conjTranspose]

omit [DecidableEq n] in
theorem gramProjection_hermitian (M : Matrix n n ℂ) :
    (gramProjection M)ᴴ = gramProjection M := by
  simp [gramProjection]

omit [DecidableEq n] in
theorem gram_square_of_residual_zero (M : Matrix n n ℂ) (h : residual M = 0) :
    (M * Mᴴ) * (M * Mᴴ) = (18 : ℂ) • (M * Mᴴ) := by
  have hcore := (residual_zero_iff M).mp h
  calc
    _ = (M * Mᴴ * M) * Mᴴ := by simp only [Matrix.mul_assoc]
    _ = ((18 : ℂ) • M) * Mᴴ := by rw [hcore]
    _ = _ := by rw [Matrix.smul_mul]

omit [DecidableEq n] in
theorem gramProjection_idempotent (M : Matrix n n ℂ) (h : residual M = 0) :
    gramProjection M * gramProjection M = gramProjection M := by
  unfold gramProjection
  rw [Matrix.smul_mul, Matrix.mul_smul, gram_square_of_residual_zero M h]
  simp only [smul_smul]
  norm_num

theorem trace_eq_rank_of_idempotent (P : Matrix n n ℂ) (h : P * P = P) :
    Matrix.trace P = (P.rank : ℂ) := by
  have hp : IsIdempotentElem P.toLin' := by
    change P.toLin'.comp P.toLin' = P.toLin'
    rw [← Matrix.toLin'_mul, h]
  calc
    Matrix.trace P = LinearMap.trace ℂ (n → ℂ) P.toLin' :=
      (Matrix.trace_toLin'_eq P).symm
    _ = (Module.finrank ℂ (LinearMap.range P.toLin') : ℂ) :=
      (LinearMap.IsIdempotentElem.isProj_range _ hp).trace
    _ = _ := rfl

omit [DecidableEq n] in
theorem gramProjection_rank (M : Matrix n n ℂ) :
    (gramProjection M).rank = M.rank := by
  rw [gramProjection, Matrix.rank_smul_of_mem_nonZeroDivisors]
  · exact Matrix.rank_self_mul_conjTranspose M
  · exact mem_nonZeroDivisors_of_ne_zero (by norm_num)

theorem rank_two_of_residual_zero_of_trace (M : Matrix n n ℂ)
    (h : residual M = 0) (htrace : Matrix.trace (M * Mᴴ) = 36) :
    M.rank = 2 := by
  have ht : Matrix.trace (gramProjection M) = 2 := by
    rw [gramProjection, Matrix.trace_smul, htrace]
    norm_num
  rw [trace_eq_rank_of_idempotent _ (gramProjection_idempotent M h),
    gramProjection_rank] at ht
  exact_mod_cast ht

theorem trace_gram_of_flat (M : Matrix (Fin 6) (Fin 6) ℂ)
    (hflat : ∀ i j, Complex.normSq (M i j) = 1) :
    Matrix.trace (M * Mᴴ) = 36 := by
  simp only [Matrix.trace, Matrix.diag_apply, Matrix.mul_apply,
    Matrix.conjTranspose_apply, Complex.star_def, Complex.mul_conj, hflat]
  norm_num

theorem rank_two_of_flat_residual_zero (M : Matrix (Fin 6) (Fin 6) ℂ)
    (hflat : ∀ i j, Complex.normSq (M i j) = 1) (h : residual M = 0) :
    M.rank = 2 :=
  rank_two_of_residual_zero_of_trace M h (trace_gram_of_flat M hflat)

def entrywiseCube (M : Matrix n n ℂ) : Matrix n n ℂ := fun i j => M i j ^ 3

omit [DecidableEq n] [Fintype n] in
theorem entrywiseCube_flat (M : Matrix n n ℂ)
    (hflat : ∀ i j, Complex.normSq (M i j) = 1) :
    ∀ i j, Complex.normSq (entrywiseCube M i j) = 1 := by
  intro i j
  simp [entrywiseCube, map_pow, hflat]

theorem phase_cube_residual_rank_two (H : Matrix (Fin 6) (Fin 6) ℂ)
    (hflat : ∀ i j, Complex.normSq (H i j) = 1)
    (h : residual (entrywiseCube H) = 0) :
    (entrywiseCube H).rank = 2 :=
  rank_two_of_flat_residual_zero _ (entrywiseCube_flat H hflat) h

/-- A general algebraic trace/rank bridge. Positivity is unnecessary once the
balanced Gram identity and its nonzero coefficient are explicitly given. -/
theorem rank_two_of_balanced_gram (M : Matrix n n ℂ) (c : ℂ) (hc : c ≠ 0)
    (h : M * Mᴴ * M = c • M)
    (htrace : Matrix.trace (M * Mᴴ) = 2 * c) :
    M.rank = 2 := by
  let P : Matrix n n ℂ := c⁻¹ • (M * Mᴴ)
  have hgram : (M * Mᴴ) * (M * Mᴴ) = c • (M * Mᴴ) := by
    calc
      _ = (M * Mᴴ * M) * Mᴴ := by simp only [Matrix.mul_assoc]
      _ = (c • M) * Mᴴ := by rw [h]
      _ = _ := by rw [Matrix.smul_mul]
  have hP : P * P = P := by
    dsimp [P]
    rw [Matrix.smul_mul, Matrix.mul_smul, hgram]
    simp only [smul_smul]
    congr 1
    field_simp
  have hPrank : P.rank = M.rank := by
    dsimp only [P]
    rw [Matrix.rank_smul_of_mem_nonZeroDivisors]
    · exact Matrix.rank_self_mul_conjTranspose M
    · exact mem_nonZeroDivisors_of_ne_zero (inv_ne_zero hc)
  have hPt : Matrix.trace P = 2 := by
    dsimp only [P]
    rw [Matrix.trace_smul, htrace]
    change c⁻¹ * (2 * c) = 2
    field_simp
  rw [trace_eq_rank_of_idempotent P hP, hPrank] at hPt
  exact_mod_cast hPt

def normalizedResidual (N : Matrix n n ℂ) : Matrix n n ℂ :=
  (12 : ℂ) • (N * Nᴴ * N) - N

/-- Direct rational-coordinate form for a normalized flat transition matrix A.
The entrywise cube has squared entry modulus 1/216. -/
theorem normalized_cube_residual_rank_two (A : Matrix (Fin 6) (Fin 6) ℂ)
    (hflat : ∀ i j, Complex.normSq (A i j) = (1 : ℝ) / 6)
    (h : normalizedResidual (entrywiseCube A) = 0) :
    (entrywiseCube A).rank = 2 := by
  let N := entrywiseCube A
  have hN : ∀ i j, Complex.normSq (N i j) = (1 : ℝ) / 216 := by
    intro i j
    dsimp [N, entrywiseCube]
    rw [map_pow, hflat]
    norm_num
  have heq : (12 : ℂ) • (N * Nᴴ * N) = N := sub_eq_zero.mp h
  have hbalanced : N * Nᴴ * N = ((12 : ℂ)⁻¹) • N := by
    have := congrArg (fun B : Matrix (Fin 6) (Fin 6) ℂ => (12 : ℂ)⁻¹ • B) heq
    simpa only [smul_smul, inv_mul_cancel₀ (by norm_num : (12 : ℂ) ≠ 0), one_smul]
      using this
  have htrace : Matrix.trace (N * Nᴴ) = 2 * (12 : ℂ)⁻¹ := by
    simp only [Matrix.trace, Matrix.diag_apply, Matrix.mul_apply,
      Matrix.conjTranspose_apply, Complex.star_def, Complex.mul_conj, hN]
    norm_num
  exact rank_two_of_balanced_gram N _ (by norm_num) hbalanced htrace

omit [DecidableEq n] [Fintype n] in
theorem one_matrix_zero_of_entry_products (X Y Z : Matrix n n ℂ)
    (h : ∀ i j k l p q, X i j * Y k l * Z p q = 0) :
    X = 0 ∨ Y = 0 ∨ Z = 0 := by
  classical
  by_cases hX : X = 0
  · exact Or.inl hX
  by_cases hY : Y = 0
  · exact Or.inr (Or.inl hY)
  have hxe : ∃ i j, X i j ≠ 0 := by
    by_contra hn
    apply hX
    ext i j
    exact not_not.mp (fun hne => hn ⟨i, j, hne⟩)
  have hye : ∃ k l, Y k l ≠ 0 := by
    by_contra hn
    apply hY
    ext k l
    exact not_not.mp (fun hne => hn ⟨k, l, hne⟩)
  obtain ⟨i, j, hij⟩ := hxe
  obtain ⟨k, l, hkl⟩ := hye
  right; right
  ext p q
  exact (mul_eq_zero.mp (h i j k l p q)).resolve_left (mul_ne_zero hij hkl)

/-- Conditional global algebraic bridge. It does not prove the universal
entry-product vanishing hypothesis; that is precisely the missing global step.
No compatibility hypothesis is required for this implication alone. -/
theorem low_cube_rank_of_residual_products (A B C : Matrix (Fin 6) (Fin 6) ℂ)
    (hA : ∀ i j, Complex.normSq (A i j) = (1 : ℝ) / 6)
    (hB : ∀ i j, Complex.normSq (B i j) = (1 : ℝ) / 6)
    (hC : ∀ i j, Complex.normSq (C i j) = (1 : ℝ) / 6)
    (hproducts : ∀ i j k l p q,
      normalizedResidual (entrywiseCube A) i j *
      normalizedResidual (entrywiseCube B) k l *
      normalizedResidual (entrywiseCube C) p q = 0) :
    (entrywiseCube A).rank = 2 ∨ (entrywiseCube B).rank = 2 ∨
      (entrywiseCube C).rank = 2 := by
  rcases one_matrix_zero_of_entry_products _ _ _ hproducts with h | h | h
  · exact Or.inl (normalized_cube_residual_rank_two A hA h)
  · exact Or.inr (Or.inl (normalized_cube_residual_rank_two B hB h))
  · exact Or.inr (Or.inr (normalized_cube_residual_rank_two C hC h))

#print axioms residual_zero_iff
#print axioms residual_unitary_covariance
#print axioms residual_adjoint
#print axioms residual_transpose
#print axioms gramProjection_hermitian
#print axioms gram_square_of_residual_zero
#print axioms gramProjection_idempotent
#print axioms trace_eq_rank_of_idempotent
#print axioms gramProjection_rank
#print axioms rank_two_of_residual_zero_of_trace
#print axioms trace_gram_of_flat
#print axioms rank_two_of_flat_residual_zero
#print axioms entrywiseCube_flat
#print axioms phase_cube_residual_rank_two
#print axioms rank_two_of_balanced_gram
#print axioms normalized_cube_residual_rank_two
#print axioms one_matrix_zero_of_entry_products
#print axioms low_cube_rank_of_residual_products

end MUBResidual
