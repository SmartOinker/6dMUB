module

public import Mathlib.Algebra.Field.Subfield.Basic
public import Mathlib.Basic.Complex.Basic
public import Mathlib.Data.Matrix.Mul

@[expose] public section

namespace MUBFieldObstruction

open Matrix

/-- A nonzero entry of a compatible product forces its normalization scalar
into the common coefficient field. This applies to phase Hadamards with
`c = sqrt d`, but does not assume or prove any global MUB classification. -/
theorem normalization_mem_of_composition {n : Type*} [Fintype n]
    (K : Subfield ℂ) (A B C : Matrix n n ℂ) (c : ℂ)
    (hA : ∀ i j, A i j ∈ K) (hC : ∀ i j, C i j ∈ K)
    (hcomp : A * C = c • B) (i j : n)
    (hB : B i j ∈ K) (hne : B i j ≠ 0) : c ∈ K := by
  have hm : (A * C) i j ∈ K := by
    apply K.sum_mem
    intro k _
    exact K.mul_mem (hA i k) (hC k j)
  have hd := K.div_mem hm hB
  simpa [hcomp, Matrix.smul_apply, smul_eq_mul, hne] using hd

#print axioms normalization_mem_of_composition

end MUBFieldObstruction
