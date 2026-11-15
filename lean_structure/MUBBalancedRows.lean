module
public import Mathlib.Data.Fintype.Pi
public import Mathlib.Algebra.BigOperators.Group.Finset.Basic
public import Mathlib.Data.Fintype.Fin
public import Mathlib.Basic.Real.Basic
public import Mathlib.Tactic.NormNum
@[expose] public section
noncomputable section
namespace MUBBalancedRows
open scoped BigOperators
abbrev Index := Fin 6
abbrev Row := {v : Index → Bool // (∑ j, if v j then (1 : ℕ) else 0) = 3}
def sign (p : Row) (j : Index) : ℤ := if p.val j then 1 else -1
def rowDot (p q : Row) : ℤ := ∑ j, sign p j * sign q j
set_option maxRecDepth 100000 in
set_option maxHeartbeats 4000000 in
theorem row_sum (p : Row) : ∑ j, sign p j = 0 := by
  revert p
  decide
set_option maxRecDepth 100000 in
set_option maxHeartbeats 4000000 in
theorem row_dot_values (p q : Row) :
    rowDot p q = -6 ∨ rowDot p q = -2 ∨ rowDot p q = 2 ∨ rowDot p q = 6 := by
  revert p q
  decide
theorem sign_square (p : Row) (j : Index) : sign p j * sign p j = 1 := by
  simp only [sign]
  cases p.val j <;> norm_num

theorem row_dot_self (p : Row) : rowDot p p = 6 := by
  simp [rowDot, sign_square]

theorem row_dot_square (p q : Row) : (4 : ℝ) ≤ (rowDot p q : ℝ)^2 := by
  rcases row_dot_values p q with h | h | h | h <;> rw [h] <;> norm_num

theorem balanced_sign_iff (v : Index → Bool) :
    (∑ j, if v j then (1 : ℤ) else -1) = 0 ↔
      (∑ j, if v j then (1 : ℕ) else 0) = 3 := by
  revert v
  decide

theorem balanced_row_count : Fintype.card Row = 20 := by decide

end MUBBalancedRows
