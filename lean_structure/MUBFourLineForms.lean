module
public import MUBBalancedRows
public import Mathlib.LinearAlgebra.Matrix.Charpoly.Basic
public import Mathlib.LinearAlgebra.Matrix.Notation
public import Mathlib.Tactic.Ring
@[expose] public section
noncomputable section
namespace MUBFourLineForms
open Matrix Polynomial MUBBalancedRows
abbrev Signs := Fin 3 → Bool
abbrev Representative := {p : Row // p.val 0 = true}
def signed (e : Signs) (i : Fin 3) : ℚ := if e i then 1 else -1

def gram (e : Signs) : Matrix (Fin 4) (Fin 4) ℚ :=
  !![6,2,2,2;
     2,6,2*signed e 0,2*signed e 1;
     2,2*signed e 0,6,2*signed e 2;
     2,2*signed e 1,2*signed e 2,6]

def expectedCharpoly (e : Signs) : Polynomial ℚ :=
  if (∀ i, e i = true) then (X-12)*(X-4)^3
  else if (∀ i, e i = false) then X*(X-8)^3
  else (X-8)*(X-4)*(X^2-12*X+16)

set_option maxRecDepth 100000
set_option maxHeartbeats 8000000

theorem antipodal_representative_count : Fintype.card Representative = 10 := by decide

theorem tight_frame_entry (i j : Index) :
    (∑ p : Representative, sign p.val i * sign p.val j) =
      12*(if i=j then (1 : ℤ) else 0)-2 := by
  revert i j
  decide +kernel

theorem eight_gram_characteristic_polynomials (e : Signs) :
    Matrix.charpoly (gram e) = expectedCharpoly e := by
  rw [Matrix.charpoly, Matrix.det_succ_row_zero]
  simp only [Matrix.det_fin_three, Matrix.submatrix_apply]
  cases h0 : e 0 <;> cases h1 : e 1 <;> cases h2 : e 2 <;>
    norm_num [gram, signed, expectedCharpoly, Fin.sum_univ_succ, Fin.forall_fin_succ,
      Matrix.charmatrix_apply, Matrix.diagonal_apply, Fin.succAbove, Polynomial.C_ofNat, h0, h1, h2] <;> ring

theorem normal_form_counts :
    (∑ e : Signs, if (∀ i, e i = true) then (1 : ℕ) else 0) = 1 ∧
    (∑ e : Signs, if (∀ i, e i = false) then (1 : ℕ) else 0) = 1 ∧
    (∑ e : Signs, if (¬∀ i, e i = true) ∧ (¬∀ i, e i = false) then (1 : ℕ) else 0) = 6 := by
  decide +kernel

theorem star_gram_singular : Matrix.det (gram (fun _ => false)) = 0 := by
  decide +kernel

end MUBFourLineForms
