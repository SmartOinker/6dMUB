module
public import MUBBalancedSmallTables
@[expose] public section
noncomputable section
namespace MUBMatchingGram
open Matrix
abbrev Index := Fin 6
abbrev Orientation := Index → Bool

def sign (d : Orientation) (i : Index) : ℚ := if d i then 1 else -1

def gram : Matrix Index Index ℚ :=
  !![6,2,-2,-2,-2,-2;
     2,6,-2,-2,-2,-2;
     -2,-2,6,2,-2,-2;
     -2,-2,2,6,-2,-2;
     -2,-2,-2,-2,6,2;
     -2,-2,-2,-2,2,6]

def witness : Matrix Index Index ℚ :=
  !![1,1,1,-1,-1,-1;
     1,1,-1,1,-1,-1;
     1,-1,-1,-1,1,1;
     -1,1,-1,-1,1,1;
     -1,-1,1,1,1,-1;
     -1,-1,1,1,-1,1]

def orientedGram (d : Orientation) : Matrix Index Index ℚ :=
  fun i j => sign d i * gram i j * sign d j

def nullPolynomial (K : Matrix Index Index ℚ) : Matrix Index Index ℚ :=
  fun i j => ((K*K) i j - 16*K i j + 48*(1 : Matrix Index Index ℚ) i j)/48

def signProjection (d : Orientation) : Matrix Index Index ℚ :=
  fun i j => sign d i * sign d j / 6

def imbalance (d : Orientation) : ℚ :=
  ∑ i, ∑ j, (orientedGram d) i j

set_option maxRecDepth 100000
set_option maxHeartbeats 8000000

/-- This explicit sign matrix is balanced in both rows and columns. -/
theorem balanced_witness :
    (∀ (i j : Index), witness i j = 1 ∨ witness i j = (-1 : ℚ)) ∧
    (∀ i : Index, (∑ j : Index, witness i j) = 0) ∧
    (∀ j : Index, (∑ i : Index, witness i j) = 0) := by
  constructor
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [witness]
  · decide +kernel

theorem witness_gram : witness * witness.transpose = gram := by
  decide +kernel

/-- The proposed null-space projector is checked against the actual matrix
polynomial, for each of the 64 signed orientations. -/
theorem signed_null_polynomial (d : Orientation) :
    nullPolynomial (orientedGram d) = signProjection d := by
  revert d
  decide +kernel

theorem signed_projection_certificate (d : Orientation) :
    orientedGram d * signProjection d = 0 ∧
    signProjection d * signProjection d = signProjection d ∧
    (signProjection d).transpose = signProjection d ∧
    (∀ i, signProjection d i i = 1/6) := by
  revert d
  decide +kernel

/-- The displayed projector fixes exactly the rational kernel of the actual
oriented Gram matrix; no kernel-dimension claim is used as a premise. -/
theorem signed_kernel_characterization (d : Orientation) (x : Index → ℚ) :
    orientedGram d *ᵥ x = 0 ↔ signProjection d *ᵥ x = x := by
  have hp := (signed_projection_certificate d).1
  constructor
  · intro hx
    have hm : nullPolynomial (orientedGram d) =
        1 - (1/3 : ℚ) • orientedGram d +
          (1/48 : ℚ) • (orientedGram d * orientedGram d) := by
      ext i j
      simp only [nullPolynomial, Matrix.add_apply, Matrix.sub_apply,
        Matrix.smul_apply, smul_eq_mul]
      ring
    rw [← signed_null_polynomial d, hm, Matrix.add_mulVec,
      Matrix.sub_mulVec, Matrix.one_mulVec, Matrix.smul_mulVec,
      Matrix.smul_mulVec, ← Matrix.mulVec_mulVec, hx, Matrix.mulVec_zero]
    simp
  · intro hx
    calc
      orientedGram d *ᵥ x = orientedGram d *ᵥ (signProjection d *ᵥ x) := by rw [hx]
      _ = (orientedGram d * signProjection d) *ᵥ x := Matrix.mulVec_mulVec _ _ _
      _ = 0 := by rw [hp, Matrix.zero_mulVec]

theorem all_orientation_imbalances (d : Orientation) :
    imbalance d = 0 ∨ imbalance d = 24 ∨ imbalance d = 32 ∨
    imbalance d = 56 ∨ imbalance d = 64 := by
  revert d
  decide +kernel

theorem nonzero_orientation_gap (d : Orientation) (h : imbalance d ≠ 0) :
    24 ≤ imbalance d := by
  rcases all_orientation_imbalances d with hz | h24 | h32 | h56 | h64
  · exact (h hz).elim
  all_goals norm_num [*]

end MUBMatchingGram
