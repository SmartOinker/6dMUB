module

public import MUBTensorFrame
public import Mathlib.LinearAlgebra.UnitaryGroup
public import Mathlib.LinearAlgebra.Matrix.Trace
public import Mathlib.Tactic.NoncommRing

@[expose] public section
noncomputable section

set_option backward.isDefEq.respectTransparency false

namespace MUBQuantumTransport

open Matrix MUBTensorFrame

variable {n : Type*} [Fintype n] [DecidableEq n]

/-- Entrywise reweighting followed by the inverse basis transformation. -/
def transport (U R : Matrix n n ℂ) : Matrix n n ℂ :=
  Matrix.of (fun i j => R i j * star ((U i j) ^ 2)) * Uᴴ

def cube (U : Matrix n n ℂ) : Matrix n n ℂ := fun i j => U i j ^ 3

/-- The actual repeated-copy frame, using the previously verified tensor cube. -/
def repeatedFrame (U : Matrix n n ℂ) : Matrix (Triple n) n ℂ :=
  tensorCube U * repetition n

/-- Partial trace over the first and second tensor factors in their standard bases. -/
def partialTrace12 (Q : Matrix (Triple n) (Triple n) ℂ) : Matrix n n ℂ :=
  fun i j => ∑ a, ∑ b, Q (a, b, i) (a, b, j)

def overlapSquare (U : Matrix n n ℂ) : Matrix n n ℂ :=
  let P₀ := repetition n * (repetition n)ᴴ
  let Pᵤ := repeatedFrame U * (repeatedFrame U)ᴴ
  partialTrace12 ((P₀ * Pᵤ) * (P₀ * Pᵤ))

private theorem repeatedFrame_entry (U : Matrix n n ℂ) (a b i j : n) :
    repeatedFrame U (a, b, i) j = U a j * U b j * U i j := by
  rw [repeatedFrame, repetition_mul_right]
  rfl

/-- A unitary basis change makes the repeated-copy frame an isometry, so its
Gram projector is a genuine orthogonal projection. -/
theorem repeated_frame_isometry (U : Matrix n n ℂ)
    (hunit : U ∈ Matrix.unitaryGroup n ℂ) :
    (repeatedFrame U)ᴴ * repeatedFrame U = 1 := by
  have hu : Uᴴ * U = 1 := Matrix.mem_unitaryGroup_iff'.mp hunit
  ext i j
  have hij := congrFun (congrFun hu i) j
  change (∑ a, star (U a i) * U a j) = (1 : Matrix n n ℂ) i j at hij
  calc
    _ = (∑ a, star (U a i) * U a j) ^ 3 := by
      simp only [Matrix.mul_apply, Matrix.conjTranspose_apply,
        Fintype.sum_prod_type, repeatedFrame_entry, star_mul]
      simp only [pow_succ, pow_zero, Finset.sum_mul, Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro a ha
      apply Finset.sum_congr rfl
      intro b hb
      apply Finset.sum_congr rfl
      intro c hc
      ring
    _ = _ := by rw [hij]; simp [Matrix.one_apply]

private theorem repetition_mul_entry {p : Type*} (S : Matrix n p ℂ)
    (a b i : n) (j : p) :
    (repetition n * S) (a, b, i) j = if a = i ∧ b = i then S i j else 0 := by
  classical
  simp only [Matrix.mul_apply, repetition, repeatIndex, Prod.mk.injEq]
  by_cases h : a = i ∧ b = i
  · rcases h with ⟨rfl, rfl⟩
    simp
  · have hzero : ∀ k, ¬(a = k ∧ b = k ∧ i = k) := by
      intro k hk
      exact h ⟨hk.1.trans hk.2.2.symm, hk.2.1.trans hk.2.2.symm⟩
    simp [hzero, h]

/-- Contracting the actual repetition frame gives the transport formula.
This coordinate identity requires no flatness or unitarity. -/
theorem partial_trace_repetition_frame (U K : Matrix n n ℂ) :
    partialTrace12 (repetition n * K * (repeatedFrame U)ᴴ) = transport U K := by
  ext i j
  simp only [partialTrace12, Matrix.mul_assoc]
  simp only [repetition_mul_entry]
  simp only [ite_and]
  simp only [Finset.sum_ite_irrel, Finset.sum_ite_eq', Finset.mem_univ, ite_true, Finset.sum_const_zero]
  simp only [Matrix.mul_apply, Matrix.conjTranspose_apply, repeatedFrame_entry,
    transport, Matrix.of_apply, star_mul, star_pow]
  apply Finset.sum_congr rfl
  intro k hk
  ring

/-- The squared product of the two concrete repeated-copy projectors factors
through the cubic compression. The identity is algebraic for every U. -/
theorem overlap_square_factorization (U : Matrix n n ℂ) :
    let V := repetition n
    let F := repeatedFrame U
    let X := cube U
    ((V * Vᴴ) * (F * Fᴴ)) * ((V * Vᴴ) * (F * Fᴴ)) =
      V * (X * Xᴴ * X) * Fᴴ := by
  dsimp only
  have hc : (repetition n)ᴴ * repeatedFrame U = cube U := by
    rw [repeatedFrame, ← Matrix.mul_assoc, repetition_compression]
    rfl
  have ha : (repeatedFrame U)ᴴ * repetition n = (cube U)ᴴ := by
    rw [← hc]
    simp only [Matrix.conjTranspose_mul, Matrix.conjTranspose_conjTranspose]
  calc
    _ = repetition n * (((repetition n)ᴴ * repeatedFrame U) *
        ((repeatedFrame U)ᴴ * repetition n) *
        ((repetition n)ᴴ * repeatedFrame U)) * (repeatedFrame U)ᴴ := by
      simp only [Matrix.mul_assoc]
    _ = _ := by rw [hc, ha]

/-- The physical partial trace is derived from the explicit tensor construction,
not supplied as a hypothesis. -/
theorem physical_partial_trace (U : Matrix n n ℂ) :
    overlapSquare U = transport U (cube U * (cube U)ᴴ * cube U) := by
  dsimp only [overlapSquare]
  rw [overlap_square_factorization]
  exact partial_trace_repetition_frame U _

private theorem flat_weight_norm (u r : ℂ) (hu : Complex.normSq u = 1 / 6) :
    star (r * star (u ^ 2)) * (r * star (u ^ 2)) =
      (1 / 36 : ℂ) * (star r * r) := by
  simp only [star_mul, star_star, star_pow]
  calc
    _ = (star r * r) * (u * star u) ^ 2 := by ring
    _ = _ := by rw [Complex.star_def, Complex.mul_conj, hu]; norm_num; ring

/-- For a normalized flat unitary, transport scales the exact squared Frobenius
norm by 1/36. The matrix R is arbitrary. -/
theorem transport_gram_trace (U R : Matrix n n ℂ)
    (hunit : U ∈ Matrix.unitaryGroup n ℂ)
    (hflat : ∀ i j, Complex.normSq (U i j) = 1 / 6) :
    Matrix.trace ((transport U R)ᴴ * transport U R) =
      Matrix.trace (Rᴴ * R) / 36 := by
  have hu : Uᴴ * U = 1 := Matrix.mem_unitaryGroup_iff'.mp hunit
  let L : Matrix n n ℂ := fun i j => R i j * star (U i j ^ 2)
  have hi : Matrix.trace ((transport U R)ᴴ * transport U R) =
      Matrix.trace (Lᴴ * L) := by
    change Matrix.trace ((L * Uᴴ)ᴴ * (L * Uᴴ)) = _
    simp only [Matrix.conjTranspose_mul, Matrix.conjTranspose_conjTranspose]
    calc
      _ = Matrix.trace (Uᴴ * U * (Lᴴ * L)) := by
        rw [← Matrix.mul_assoc, Matrix.trace_mul_cycle]
        simp only [Matrix.mul_assoc]
      _ = _ := by rw [hu, Matrix.one_mul]
  rw [hi]
  simp only [Matrix.trace, Matrix.diag_apply, Matrix.mul_apply,
    Matrix.conjTranspose_apply, L]
  simp_rw [flat_weight_norm _ _ (hflat _ _)]
  simp_rw [← Finset.mul_sum]
  ring

/-- Transport sends the compressed cubic transition to the scalar identity. -/
theorem transport_cube (U : Matrix n n ℂ)
    (hunit : U ∈ Matrix.unitaryGroup n ℂ)
    (hflat : ∀ i j, Complex.normSq (U i j) = 1 / 6) :
    transport U (cube U) = (1 / 36 : ℂ) • (1 : Matrix n n ℂ) := by
  have hu : U * Uᴴ = 1 := Matrix.mem_unitaryGroup_iff.mp hunit
  have he : Matrix.of (fun i j => cube U i j * star (U i j ^ 2)) = (1 / 36 : ℂ) • U := by
    ext i j
    simp only [Matrix.of_apply, cube, Matrix.smul_apply, smul_eq_mul, star_pow]
    calc
      _ = U i j * (U i j * star (U i j)) ^ 2 := by ring
      _ = _ := by rw [Complex.star_def, Complex.mul_conj, hflat]; norm_num; ring
  unfold transport
  rw [he, Matrix.smul_mul, hu]

omit [DecidableEq n] in
private theorem transport_sub (U R S : Matrix n n ℂ) :
    transport U (R - S) = transport U R - transport U S := by
  unfold transport
  rw [← Matrix.sub_mul]
  congr 1
  ext i j
  simp [Matrix.of_apply, sub_mul]

omit [DecidableEq n] in
private theorem transport_smul (U R : Matrix n n ℂ) (a : ℂ) :
    transport U (a • R) = a • transport U R := by
  unfold transport
  rw [← Matrix.smul_mul]
  congr 1
  ext i j
  simp [Matrix.of_apply, mul_assoc]

/-- The normalized balanced residual for the compressed cubic transition. -/
def normalizedResidual (U : Matrix n n ℂ) : Matrix n n ℂ :=
  (12 : ℂ) • (cube U * (cube U)ᴴ * cube U) - cube U

/-- The actual partial trace splits into a scalar identity and transported residual. -/
theorem overlap_residual_identity (U : Matrix n n ℂ)
    (hunit : U ∈ Matrix.unitaryGroup n ℂ)
    (hflat : ∀ i j, Complex.normSq (U i j) = 1 / 6) :
    overlapSquare U = (1 / 432 : ℂ) • (1 : Matrix n n ℂ) +
      (1 / 12 : ℂ) • transport U (normalizedResidual U) := by
  rw [normalizedResidual, transport_sub, transport_smul, transport_cube U hunit hflat,
    physical_partial_trace]
  module

omit [DecidableEq n] in
private theorem trace_transport (U R : Matrix n n ℂ) :
    Matrix.trace (transport U R) = Matrix.trace (R * (cube U)ᴴ) := by
  simp only [transport, Matrix.trace, Matrix.diag_apply, Matrix.mul_apply,
    Matrix.of_apply, Matrix.conjTranspose_apply, cube, star_pow]
  apply Finset.sum_congr rfl
  intro i hi
  apply Finset.sum_congr rfl
  intro j hj
  ring

omit [DecidableEq n] in
private theorem trace_square_gram_switch (X : Matrix n n ℂ) :
    Matrix.trace ((X * Xᴴ) * (X * Xᴴ)) = Matrix.trace ((Xᴴ * X) * (Xᴴ * X)) := by
  calc
    _ = Matrix.trace (X * (Xᴴ * X * Xᴴ)) := by simp only [Matrix.mul_assoc]
    _ = Matrix.trace ((Xᴴ * X * Xᴴ) * X) := Matrix.trace_mul_comm _ _
    _ = _ := by simp only [Matrix.mul_assoc]

private theorem cube_gram_trace (U : Matrix (Fin 6) (Fin 6) ℂ)
    (hflat : ∀ i j, Complex.normSq (U i j) = 1 / 6) :
    Matrix.trace (cube U * (cube U)ᴴ) = 1 / 6 := by
  have he : ∀ i j, U i j ^ 3 * star (U i j ^ 3) = (1 / 216 : ℂ) := by
    intro i j
    calc
      _ = (U i j * star (U i j)) ^ 3 := by simp only [star_pow]; ring
      _ = _ := by rw [Complex.star_def, Complex.mul_conj, hflat]; norm_num
  simp only [Matrix.trace, Matrix.diag_apply, Matrix.mul_apply,
    Matrix.conjTranspose_apply, cube, he]
  norm_num

/-- The normalized purity gap; its universal three-edge product remains unproved. -/
def normalizedGap (U : Matrix (Fin 6) (Fin 6) ℂ) : ℂ :=
  1 / 72 - Matrix.trace (((cube U)ᴴ * cube U) * ((cube U)ᴴ * cube U))

/-- The traceless component of the actual partial trace. -/
def tracelessOverlap (U : Matrix (Fin 6) (Fin 6) ℂ) : Matrix (Fin 6) (Fin 6) ℂ :=
  overlapSquare U - (1 / 432 - normalizedGap U / 6) • 1

private theorem normalizedGap_star (U : Matrix (Fin 6) (Fin 6) ℂ) :
    star (normalizedGap U) = normalizedGap U := by
  unfold normalizedGap
  rw [star_sub, star_div₀, star_one, star_ofNat, ← Matrix.trace_conjTranspose]
  simp only [Matrix.conjTranspose_mul, Matrix.conjTranspose_conjTranspose]

omit [DecidableEq n] in
private theorem trace_transported_residual (U : Matrix (Fin 6) (Fin 6) ℂ)
    (hflat : ∀ i j, Complex.normSq (U i j) = 1 / 6) :
    Matrix.trace (transport U (normalizedResidual U)) = -12 * normalizedGap U := by
  rw [trace_transport, normalizedResidual, Matrix.sub_mul, Matrix.smul_mul,
    Matrix.trace_sub, Matrix.trace_smul, cube_gram_trace U hflat]
  have he : (cube U * (cube U)ᴴ * cube U) * (cube U)ᴴ =
      (cube U * (cube U)ᴴ) * (cube U * (cube U)ᴴ) := by
    simp only [Matrix.mul_assoc]
  rw [he, trace_square_gram_switch]
  unfold normalizedGap
  ring

/-- The centered physical partial trace has exactly zero trace. -/
theorem traceless_overlap_trace (U : Matrix (Fin 6) (Fin 6) ℂ)
    (hunit : U ∈ Matrix.unitaryGroup (Fin 6) ℂ)
    (hflat : ∀ i j, Complex.normSq (U i j) = 1 / 6) :
    Matrix.trace (tracelessOverlap U) = 0 := by
  rw [tracelessOverlap, overlap_residual_identity U hunit hflat]
  simp only [Matrix.trace_sub, Matrix.trace_add, Matrix.trace_smul,
    Matrix.trace_one, Fintype.card_fin, Nat.cast_ofNat,
    trace_transported_residual U hflat, smul_eq_mul]
  ring

private theorem transport_residual_centered (U : Matrix (Fin 6) (Fin 6) ℂ)
    (hunit : U ∈ Matrix.unitaryGroup (Fin 6) ℂ)
    (hflat : ∀ i j, Complex.normSq (U i j) = 1 / 6) :
    transport U (normalizedResidual U) =
      (12 : ℂ) • tracelessOverlap U - (2 * normalizedGap U) • 1 := by
  rw [tracelessOverlap, overlap_residual_identity U hunit hflat]
  module

/-- An exact quantum energy split, with the partial trace and its centering both
defined from the physical repeated-copy projectors. No identity is assumed. -/
theorem residual_energy_decomposition (U : Matrix (Fin 6) (Fin 6) ℂ)
    (hunit : U ∈ Matrix.unitaryGroup (Fin 6) ℂ)
    (hflat : ∀ i j, Complex.normSq (U i j) = 1 / 6) :
    Matrix.trace ((normalizedResidual U)ᴴ * normalizedResidual U) =
      5184 * Matrix.trace ((tracelessOverlap U)ᴴ * tracelessOverlap U) +
        864 * normalizedGap U ^ 2 := by
  have hz := traceless_overlap_trace U hunit hflat
  have hzs : Matrix.trace (tracelessOverlap U)ᴴ = 0 := by
    rw [Matrix.trace_conjTranspose, hz, star_zero]
  have he : Matrix.trace ((transport U (normalizedResidual U))ᴴ *
      transport U (normalizedResidual U)) =
      144 * Matrix.trace ((tracelessOverlap U)ᴴ * tracelessOverlap U) +
        24 * normalizedGap U ^ 2 := by
    rw [transport_residual_centered U hunit hflat]
    simp only [Matrix.conjTranspose_sub, Matrix.conjTranspose_smul,
      Matrix.conjTranspose_one, star_mul, star_ofNat, normalizedGap_star,
      Matrix.sub_mul, Matrix.mul_sub, Matrix.smul_mul, Matrix.mul_smul,
      Matrix.one_mul, Matrix.mul_one, Matrix.trace_sub, Matrix.trace_smul,
      Matrix.trace_one, Fintype.card_fin, Nat.cast_ofNat, hz, hzs, smul_eq_mul]
    ring
  have ht := transport_gram_trace U (normalizedResidual U) hunit hflat
  calc
    _ = 36 * Matrix.trace ((transport U (normalizedResidual U))ᴴ *
        transport U (normalizedResidual U)) := by rw [ht]; ring
    _ = _ := by rw [he]; ring

end MUBQuantumTransport
