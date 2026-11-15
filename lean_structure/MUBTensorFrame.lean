module

public import Mathlib.LinearAlgebra.Matrix.Hermitian
public import Mathlib.Analysis.Complex.Basic
public import Mathlib.Tactic.NormNum

@[expose] public section
noncomputable section

namespace MUBTensorFrame

open Matrix

abbrev Triple (n : Type*) := n × n × n

def repeatIndex {n : Type*} (j : n) : Triple n := (j, j, j)

/-- The repetition isometry sends a basis vector j to the triple (j,j,j). -/
def repetition (n : Type*) [DecidableEq n] : Matrix (Triple n) n ℂ :=
  fun i j => if i = repeatIndex j then 1 else 0

/-- Explicit coordinates for the third tensor power. No tensor-product API
or assumption about a factorized state is used. -/
def tensorCube {n : Type*} (U : Matrix n n ℂ) : Matrix (Triple n) (Triple n) ℂ :=
  fun i j => U i.1 j.1 * U i.2.1 j.2.1 * U i.2.2 j.2.2

variable {n : Type*} [Fintype n] [DecidableEq n]

theorem repetition_mul_right {p : Type*} (T : Matrix p (Triple n) ℂ) (i : p) (j : n) :
    (T * repetition n) i j = T i (repeatIndex j) := by
  simp [Matrix.mul_apply, repetition]

theorem repetition_adjoint_mul_left {p : Type*} (T : Matrix (Triple n) p ℂ)
    (i : n) (j : p) :
    ((repetition n)ᴴ * T) i j = T (repeatIndex i) j := by
  simp [Matrix.mul_apply, repetition, Matrix.conjTranspose_apply]

theorem repetition_isometry :
    (repetition n)ᴴ * repetition n = 1 := by
  ext i j
  rw [repetition_adjoint_mul_left]
  simp [repetition, repeatIndex, Matrix.one_apply]

theorem repetition_compression_entry (U : Matrix n n ℂ) (i j : n) :
    ((repetition n)ᴴ * tensorCube U * repetition n) i j = U i j ^ 3 := by
  rw [repetition_mul_right, repetition_adjoint_mul_left]
  simp [tensorCube, repeatIndex, pow_succ]

theorem repetition_compression (U : Matrix n n ℂ) :
    (repetition n)ᴴ * tensorCube U * repetition n = fun i j => U i j ^ 3 := by
  ext i j
  exact repetition_compression_entry U i j

section Defects

variable {m : Type*} [Fintype m] [DecidableEq m]

/-- The overlap of two frames with the same ambient and coefficient spaces. -/
def overlap (V A : Matrix m n ℂ) : Matrix n n ℂ := Vᴴ * A

omit [DecidableEq n] in
/-- Algebraic projection-defect identity. No isometry premise is needed. -/
theorem first_projection_defect (V A B : Matrix m n ℂ) :
    overlap V B - overlap V A * overlap A B =
      Vᴴ * (1 - A * Aᴴ) * B := by
  simp [overlap, Matrix.mul_sub, Matrix.sub_mul, Matrix.mul_assoc]

omit [DecidableEq n] in
/-- The adjoint of the A-to-B overlap occurs in the second identity. -/
theorem second_projection_defect (V A B : Matrix m n ℂ) :
    overlap V A - overlap V B * (overlap A B)ᴴ =
      Vᴴ * (1 - B * Bᴴ) * A := by
  simp [overlap, Matrix.mul_sub, Matrix.sub_mul, Matrix.mul_assoc]

omit [DecidableEq n] in
theorem third_projection_defect (V A B : Matrix m n ℂ) :
    overlap A B - (overlap V A)ᴴ * overlap V B =
      Aᴴ * (1 - V * Vᴴ) * B := by
  simp [overlap, Matrix.mul_sub, Matrix.sub_mul, Matrix.mul_assoc]

end Defects

#print axioms repetition_mul_right
#print axioms repetition_adjoint_mul_left
#print axioms repetition_isometry
#print axioms repetition_compression_entry
#print axioms repetition_compression
#print axioms first_projection_defect
#print axioms second_projection_defect
#print axioms third_projection_defect

end MUBTensorFrame
