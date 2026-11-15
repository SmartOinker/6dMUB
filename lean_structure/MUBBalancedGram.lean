module
public import MUBBalancedRows
public import Mathlib.LinearAlgebra.Matrix.ConjTranspose
public import Mathlib.Analysis.Complex.Basic
public import Mathlib.Analysis.SpecialFunctions.Sqrt
public import Mathlib.Tactic.Ring
public import Mathlib.Tactic.Linarith
@[expose] public section
noncomputable section
namespace MUBBalancedGram
open Matrix MUBBalancedRows

def phaseEntry (p : Row) (j : Index) : ℂ :=
  (Real.sqrt (1/6 : ℝ) : ℂ) + Complex.I * (Real.sqrt (5/6 : ℝ) : ℂ) * (sign p j : ℂ)
def phaseMatrix (rows : Index → Row) : Matrix Index Index ℂ :=
  fun i j => phaseEntry (rows i) j

def frobeniusSq (M : Matrix Index Index ℂ) : ℝ :=
  ∑ i, ∑ j, Complex.normSq (M i j)

private theorem pair_re (p q : Row) (j : Index) :
    (phaseEntry p j * star (phaseEntry q j)).re =
      1/6 + (5/6 : ℝ) * (sign p j : ℝ) * (sign q j : ℝ) := by
  simp only [phaseEntry, Complex.star_def, Complex.mul_re, Complex.add_re,
    Complex.ofReal_re, Complex.I_re, Complex.mul_im, Complex.add_im,
    Complex.ofReal_im, Complex.I_im, Complex.intCast_re, Complex.intCast_im,
    Complex.conj_re, Complex.conj_im]
  have ha := Real.sq_sqrt (show (0 : ℝ) ≤ 1/6 by norm_num)
  have hb := Real.sq_sqrt (show (0 : ℝ) ≤ 5/6 by norm_num)
  ring_nf
  rw [ha, hb]
  ring

private theorem pair_im (p q : Row) (j : Index) :
    (phaseEntry p j * star (phaseEntry q j)).im =
      Real.sqrt (1/6 : ℝ) * Real.sqrt (5/6 : ℝ) *
        ((sign p j : ℝ) - (sign q j : ℝ)) := by
  simp only [phaseEntry, Complex.star_def, Complex.mul_re, Complex.add_re,
    Complex.ofReal_re, Complex.I_re, Complex.mul_im, Complex.add_im,
    Complex.ofReal_im, Complex.I_im, Complex.intCast_re, Complex.intCast_im,
    Complex.conj_re, Complex.conj_im]
  ring

private theorem real_row_sum (p : Row) : ∑ j, (sign p j : ℝ) = 0 := by
  exact_mod_cast row_sum p

/-- The entries are exactly the two phases used in the scalar equality set. -/
theorem phase_entry_formula (p : Row) (j : Index) :
    phaseEntry p j = (1 + Complex.I * (Real.sqrt 5 : ℂ) * (sign p j : ℂ)) /
      (Real.sqrt 6 : ℂ) := by
  unfold phaseEntry
  rw [Real.sqrt_div (show (0 : ℝ) ≤ 1 by norm_num),
    Real.sqrt_div (show (0 : ℝ) ≤ 5 by norm_num)]
  simp only [Real.sqrt_one, Complex.ofReal_div, Complex.ofReal_one]
  ring

theorem phase_entry_unit (p : Row) (j : Index) : Complex.normSq (phaseEntry p j) = 1 := by
  have hs : (sign p j : ℝ) * (sign p j : ℝ) = 1 := by exact_mod_cast sign_square p j
  have hp := pair_re p p j
  have hn : Complex.normSq (phaseEntry p j) =
      (phaseEntry p j * star (phaseEntry p j)).re := by
    simp [Complex.normSq_apply, Complex.mul_re]
  rw [hn, hp]
  nlinarith

theorem phase_row_sum (p : Row) : ∑ j, phaseEntry p j = (Real.sqrt 6 : ℂ) := by
  have hs : (∑ j, (sign p j : ℂ)) = 0 := by exact_mod_cast row_sum p
  have ha := Real.sq_sqrt (show (0 : ℝ) ≤ 1/6 by norm_num)
  have h6 := Real.sq_sqrt (show (0 : ℝ) ≤ 6 by norm_num)
  have heq : 6*Real.sqrt (1/6 : ℝ) = Real.sqrt 6 := by
    apply (sq_eq_sq₀ (by positivity) (Real.sqrt_nonneg _)).mp
    nlinarith
  calc
    _ = 6*(Real.sqrt (1/6 : ℝ) : ℂ) := by
      simp only [phaseEntry, Finset.sum_add_distrib, ← Finset.mul_sum, hs, mul_zero,
        add_zero]
      norm_num
    _ = _ := by exact_mod_cast heq

theorem phase_gram_entry (rows : Index → Row) (i j : Index) :
    (phaseMatrix rows * (phaseMatrix rows)ᴴ) i j =
      ((1 + (5/6 : ℝ) * (rowDot (rows i) (rows j) : ℝ) : ℝ) : ℂ) := by
  apply Complex.ext
  · simp only [phaseMatrix, Matrix.mul_apply, Matrix.conjTranspose_apply,
      Complex.re_sum, pair_re, Complex.ofReal_re]
    simp only [mul_assoc, Finset.sum_add_distrib, ← Finset.mul_sum, rowDot, Int.cast_sum,
      Int.cast_mul]
    norm_num
  · simp only [phaseMatrix, Matrix.mul_apply, Matrix.conjTranspose_apply,
      Complex.im_sum, pair_im, Complex.ofReal_im, ← Finset.mul_sum,
      Finset.sum_sub_distrib, real_row_sum, sub_self, mul_zero]


def gramDefect (rows : Index → Row) : Matrix Index Index ℂ :=
  phaseMatrix rows * (phaseMatrix rows)ᴴ - (6 : ℂ) • 1

theorem row_dot_total_square (rows : Index → Row) :
    (∑ i, ∑ j, (rowDot (rows i) (rows j) : ℝ)) =
      ∑ k, (∑ i, (sign (rows i) k : ℝ))^2 := by
  simp only [rowDot, Int.cast_sum, Int.cast_mul]
  calc
    _ = ∑ i, ∑ k, ∑ j, (sign (rows i) k : ℝ) * (sign (rows j) k : ℝ) := by
      apply Finset.sum_congr rfl
      intro i hi
      rw [Finset.sum_comm]
    _ = ∑ k, ∑ i, ∑ j, (sign (rows i) k : ℝ) * (sign (rows j) k : ℝ) := by
      rw [Finset.sum_comm]
    _ = _ := by
      simp only [pow_two, Finset.sum_mul, Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro k hk
      rw [Finset.sum_comm]

private theorem row_dot_total_nonnegative (rows : Index → Row) :
    0 ≤ ∑ i, ∑ j, (rowDot (rows i) (rows j) : ℝ) := by
  rw [row_dot_total_square]
  exact Finset.sum_nonneg (fun k hk => sq_nonneg _)

theorem gram_defect_entry (rows : Index → Row) (i j : Index) :
    Complex.normSq (gramDefect rows i j) =
      (1+(5/6 : ℝ)*(rowDot (rows i) (rows j) : ℝ) - (if i=j then 6 else 0))^2 := by
  by_cases h : i=j <;>
    simp [gramDefect, Matrix.sub_apply, Matrix.smul_apply,
      phase_gram_entry, h, Complex.normSq_apply] <;> ring

private theorem gram_entry_lower_bound (rows : Index → Row) (i j : Index) :
    34/9 + (5/3 : ℝ)*(rowDot (rows i) (rows j) : ℝ) -
        (if i=j then 124/9 else 0) ≤ Complex.normSq (gramDefect rows i j) := by
  rw [gram_defect_entry]
  by_cases h : i=j
  · subst j
    norm_num [row_dot_self]
  · simp only [h, ite_false, sub_zero]
    have hd := row_dot_square (rows i) (rows j)
    nlinarith

/-- The actual complex balanced-binary matrix has a quantitative Gram defect.
Every row is one of the 20 balanced sign patterns. No Gram inequality is a premise. -/
theorem balanced_gram_separation (rows : Index → Row) :
    (160/3 : ℝ) ≤ frobeniusSq (gramDefect rows) := by
  have hsum := Finset.sum_le_sum (s := Finset.univ) (fun i hi =>
    Finset.sum_le_sum (s := Finset.univ) (fun j hj => gram_entry_lower_bound rows i j))
  have hid : (∑ i : Index, ∑ j : Index,
      (34/9 + (5/3 : ℝ)*(rowDot (rows i) (rows j) : ℝ) -
        (if i=j then 124/9 else 0))) =
      160/3 + (5/3 : ℝ)*(∑ i, ∑ j, (rowDot (rows i) (rows j) : ℝ)) := by
    simp only [Finset.sum_sub_distrib, Finset.sum_add_distrib, ← Finset.mul_sum]
    norm_num
    ring
  rw [hid] at hsum
  have hn := row_dot_total_nonnegative rows
  unfold frobeniusSq
  linarith

/-- No matrix formed from six balanced binary phase rows is Hadamard. -/
theorem balanced_matrix_not_hadamard (rows : Index → Row) :
    phaseMatrix rows * (phaseMatrix rows)ᴴ ≠ (6 : ℂ) • 1 := by
  intro h
  have hb := balanced_gram_separation rows
  have hz : gramDefect rows = 0 := by simp [gramDefect, h]
  rw [hz] at hb
  norm_num [frobeniusSq] at hb

end MUBBalancedGram
