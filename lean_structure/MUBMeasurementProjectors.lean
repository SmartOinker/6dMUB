module

public import MUBQuantumMeasurements
public import Mathlib.LinearAlgebra.Matrix.PosDef
public import Mathlib.Analysis.Complex.Order
public import Mathlib.Analysis.RCLike.Basic
public import Mathlib.Analysis.Complex.Basic
public import Mathlib.Tactic.FieldSimp

@[expose] public section
noncomputable section

namespace MUBMeasurementProjectors

open Matrix MUBQuantum
open scoped ComplexOrder

abbrev Coordinate := Fin 3 × Fin 2
abbrev Outcome := Fin 3 × Fin 2

def row (r : ℝ) (b : Fin 3) (o : Outcome) (x : Coordinate) : ℂ :=
  qutritRow r b o.1 x.1 * qubitRow b o.2 x.2

def denominator (b : Fin 3) : ℝ := if b = 0 then 3 else 6

def projector (r : ℝ) (b : Fin 3) (o : Outcome) : Matrix Coordinate Coordinate ℂ :=
  ((denominator b : ℂ)⁻¹) • Matrix.vecMulVec (star (row r b o)) (row r b o)

def pureState (v : Coordinate → ℂ) : Matrix Coordinate Coordinate ℂ :=
  Matrix.vecMulVec v (star v)

def canonicalProjector (r : ℝ) (b : Fin 3) (o : Outcome) : Matrix Coordinate Coordinate ℂ :=
  projector r b (canonicalRelabel b o.1, o.2)

def expectation (P R : Matrix Coordinate Coordinate ℂ) : ℝ := (Matrix.trace (P * R)).re

private theorem denominator_pos (b : Fin 3) : 0 < denominator b := by
  unfold denominator
  split_ifs <;> norm_num

private theorem denominator_nonzero (b : Fin 3) : (denominator b : ℂ) ≠ 0 := by
  exact_mod_cast ne_of_gt (denominator_pos b)

private theorem trace_outer_product {n : Type*} [Fintype n]
    (u v w x : n → ℂ) :
    Matrix.trace (Matrix.vecMulVec u v * Matrix.vecMulVec w x) =
      (∑ i, v i * w i) * (∑ i, u i * x i) := by
  rw [Matrix.vecMulVec_mul_vecMulVec, Matrix.trace_vecMulVec]
  simp only [dotProduct, Pi.smul_apply, smul_eq_mul, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro i hi
  ring

private theorem row_norm (r : ℝ) (hr : r^2 = 3) (b : Fin 3) (o : Outcome) :
    (∑ x, star (row r b o x) * row r b o x) = (denominator b : ℂ) := by
  by_cases hb : b = 0 <;>
    simpa [row, Fintype.sum_prod_type, denominator, hb] using
      joint_rows_orthogonal r hr b o.1 o.1 o.2 o.2

/-- These are actual positive measurement matrices in the coefficient
coordinates used by the original Born-probability theorem. -/
theorem projector_positive (r : ℝ) (b : Fin 3) (o : Outcome) :
    (projector r b o).PosSemidef := by
  have houter := Matrix.posSemidef_vecMulVec_self_star (star (row r b o))
  simp only [star_star] at houter
  apply houter.smul
  exact le_of_lt (RCLike.inv_pos_of_pos (by
    exact_mod_cast denominator_pos b))

/-- Row normalization gives trace one and idempotence of every measurement
projector; no matrix normalization is assumed. -/
theorem projector_trace_idempotent (r : ℝ) (hr : r^2 = 3) (b : Fin 3) (o : Outcome) :
    Matrix.trace (projector r b o) = 1 ∧
    projector r b o * projector r b o = projector r b o := by
  have hn := row_norm r hr b o
  have hd := denominator_nonzero b
  constructor
  · simp only [projector, Matrix.trace_smul, Matrix.trace_vecMulVec,
      dotProduct, Pi.star_apply, smul_eq_mul]
    rw [hn]
    exact inv_mul_cancel₀ hd
  · ext i j
    simp only [projector, Matrix.mul_apply, Matrix.smul_apply, Matrix.vecMulVec_apply,
      Pi.star_apply, smul_eq_mul]
    calc
      _ = ((denominator b : ℂ)⁻¹ * (denominator b : ℂ)⁻¹ *
          star (row r b o i) * row r b o j) *
          (∑ k, star (row r b o k) * row r b o k) := by
        rw [Finset.mul_sum]
        apply Finset.sum_congr rfl
        intro k hk
        ring
      _ = _ := by rw [hn]; field_simp

private theorem trace_projector_pure (r : ℝ) (b : Fin 3) (o : Outcome)
    (v : Coordinate → ℂ) :
    Matrix.trace (projector r b o * pureState v) =
      (Complex.normSq (∑ x, row r b o x * v x) : ℂ) / (denominator b : ℂ) := by
  rw [projector, pureState, Matrix.smul_mul, Matrix.trace_smul, trace_outer_product]
  simp only [Pi.star_apply, smul_eq_mul]
  have hc : (∑ i, star (row r b o i) * star (v i)) =
      star (∑ i, row r b o i * v i) := by simp only [star_sum, star_mul, mul_comm]
  rw [hc, Complex.star_def, Complex.mul_conj]
  ring

/-- The matrix trace equals the previously formalized Born probability, for
arbitrary (not necessarily normalized) coefficient vectors. -/
theorem projector_born_probability (r : ℝ) (v : Coefficients)
    (b : Fin 3) (j : Fin 3) (a : Fin 2) :
    expectation (projector r b (j,a)) (pureState (fun x => v x.1 x.2)) =
      probability r v b j a := by
  unfold expectation
  rw [trace_projector_pure]
  have hamp : (∑ x : Coordinate, row r b (j,a) x * v x.1 x.2) =
      outcomeAmplitude b a (amplitude r v b j) := by
    rw [outcome_row_formula]
    simp_rw [amplitude_row_formula]
    simp only [Fintype.sum_prod_type, row, Finset.mul_sum]
    rw [Finset.sum_comm]
    apply Finset.sum_congr rfl
    intro c hc
    apply Finset.sum_congr rfl
    intro k hk
    ring
  rw [hamp, ← Complex.ofReal_div, Complex.ofReal_re, probability_eq_outcome]
  rfl

/-- The canonical density-matrix observable includes the established outcome
relabeling. In particular b=0 is not silently identified with a coordinate diagonal. -/
theorem canonical_projector_born (r : ℝ) (hr : r^2 = 3) (v : Coefficients)
    (b j : Fin 3) (a : Fin 2) :
    expectation (canonicalProjector r b (j,a)) (pureState (fun x => v x.1 x.2)) =
      canonicalProbability r v b j a := by
  rw [canonicalProjector, projector_born_probability, canonical_probability_eq r hr]

set_option maxHeartbeats 0 in
private theorem qutrit_cross (r : ℝ) (hr : r^2 = 3) (b c j l : Fin 3)
    (hbc : b ≠ c) :
    Complex.normSq (∑ k, star (qutritRow r b j k) * qutritRow r c l k) = 3 := by
  have h3 : r^3 = 3*r := by calc
    r^3 = r^2*r := by ring
    _ = 3*r := by rw [hr]
  have h4 : r^4 = 9 := by calc
    r^4 = (r^2)^2 := by ring
    _ = 9 := by rw [hr]; norm_num
  have h5 : r^5 = 9*r := by calc
    r^5 = r^4*r := by ring
    _ = 9*r := by rw [h4]
  have h6 : r^6 = 27 := by calc
    r^6 = (r^2)^3 := by ring
    _ = 27 := by rw [hr]; norm_num
  have h7 : r^7 = 27*r := by calc
    r^7 = r^6*r := by ring
    _ = 27*r := by rw [h6]
  have h8 : r^8 = 81 := by calc
    r^8 = (r^2)^4 := by ring
    _ = 81 := by rw [hr]; norm_num
  fin_cases b <;> fin_cases c <;> try contradiction
  all_goals fin_cases j <;> fin_cases l <;>
    simp [qutritRow, phase, Fin.sum_univ_three, Complex.normSq_apply,
      Complex.add_re, Complex.add_im, Complex.mul_re, Complex.mul_im,
      Complex.conj_re, Complex.conj_im]
  all_goals ring_nf
  all_goals nlinarith only [hr, h3, h4, h5, h6, h7, h8]

private theorem qubit_cross (b c : Fin 3) (a d : Fin 2) (hbc : b ≠ c) :
    Complex.normSq (∑ k, star (qubitRow b a k) * qubitRow c d k) =
      denominator b * denominator c / 18 := by
  fin_cases b <;> fin_cases c <;> try contradiction
  all_goals fin_cases a <;> fin_cases d <;>
    norm_num [qubitRow, denominator, Fin.sum_univ_two, Complex.normSq_apply,
      Complex.star_def]

private theorem row_inner_factor (r : ℝ) (b c : Fin 3) (o p : Outcome) :
    (∑ x, star (row r b o x) * row r c p x) =
      (∑ k, star (qutritRow r b o.1 k) * qutritRow r c p.1 k) *
      (∑ k, star (qubitRow b o.2 k) * qubitRow c p.2 k) := by
  simp only [row, Fintype.sum_prod_type, Finset.sum_mul, Finset.mul_sum, star_mul]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro a ha
  apply Finset.sum_congr rfl
  intro k hk
  ring

private theorem trace_projector_product (r : ℝ) (b c : Fin 3) (o p : Outcome) :
    Matrix.trace (projector r b o * projector r c p) =
      (Complex.normSq (∑ x, star (row r b o x) * row r c p x) : ℂ) /
        ((denominator b : ℂ) * (denominator c : ℂ)) := by
  simp only [projector, Matrix.smul_mul, Matrix.mul_smul, Matrix.trace_smul,
    smul_eq_mul, trace_outer_product, Pi.star_apply]
  have hc : (∑ x, row r b o x * star (row r c p x)) =
      star (∑ x, star (row r b o x) * row r c p x) := by
    simp only [star_sum, star_mul, star_star, mul_comm]
  rw [hc, Complex.star_def, mul_comm ((starRingEnd ℂ) _), Complex.mul_conj]
  ring

/-- Exact Gram values of the actual projectors: orthogonal within each basis
and mutually unbiased across distinct bases. Cross-basis overlaps are calculated
from the concrete rows rather than assumed. -/
theorem projector_gram (r : ℝ) (hr : r^2 = 3) (b c : Fin 3) (o p : Outcome) :
    Matrix.trace (projector r b o * projector r c p) =
      if b = c then (if o = p then 1 else 0) else (1 : ℂ)/6 := by
  by_cases hbc : b = c
  · subst c
    simp only [ite_true]
    by_cases hop : o = p
    · subst p
      rw [(projector_trace_idempotent r hr b o).2,
        (projector_trace_idempotent r hr b o).1]
      simp
    · rw [ite_eq_right hop, trace_projector_product]
      have hn : (∑ x, star (row r b o x) * row r b p x) = 0 := by
        have hne : ¬(o.1 = p.1 ∧ o.2 = p.2) := by
          intro h
          exact hop (Prod.ext h.1 h.2)
        simpa only [row, Fintype.sum_prod_type, ite_eq_right hne] using
          joint_rows_orthogonal r hr b o.1 p.1 o.2 p.2
      rw [hn, Complex.normSq_zero, Complex.ofReal_zero, zero_div]
  · rw [ite_eq_right hbc, trace_projector_product, row_inner_factor, Complex.normSq_mul,
      qutrit_cross r hr b c o.1 p.1 hbc, qubit_cross b c o.2 p.2 hbc]
    push_cast
    field_simp [denominator_nonzero b, denominator_nonzero c]
    ring

private theorem canonical_relabel_injective (b : Fin 3) :
    Function.Injective (canonicalRelabel b) := by
  fin_cases b <;> decide +kernel

/-- The same physical Gram table holds after the canonical outcome relabeling. -/
theorem canonical_projector_gram (r : ℝ) (hr : r^2 = 3)
    (b c : Fin 3) (o p : Outcome) :
    Matrix.trace (canonicalProjector r b o * canonicalProjector r c p) =
      if b = c then (if o = p then 1 else 0) else (1 : ℂ)/6 := by
  rw [canonicalProjector, canonicalProjector, projector_gram r hr]
  by_cases hbc : b = c
  · subst c
    simp only [ite_true]
    have he : (canonicalRelabel b o.1, o.2) = (canonicalRelabel b p.1, p.2) ↔ o = p := by
      constructor
      · intro h
        have hf := congrArg (fun x : Outcome => x.1) h
        have hs := congrArg (fun x : Outcome => x.2) h
        exact Prod.ext ((canonical_relabel_injective b) hf) hs
      · intro h
        exact congrArg (fun x : Outcome => (canonicalRelabel b x.1, x.2)) h
    simp only [he]
  · rw [ite_eq_right hbc, ite_eq_right hbc]

/-- Each canonical family sums to the identity. This follows from the actual
projector Gram table and trace normalization. -/
theorem canonical_projector_complete (r : ℝ) (hr : r^2 = 3) (b : Fin 3) :
    (∑ o, canonicalProjector r b o) = 1 := by
  let S := ∑ o, canonicalProjector r b o
  have hp (o : Outcome) : (canonicalProjector r b o)ᴴ = canonicalProjector r b o :=
    (projector_positive r b (canonicalRelabel b o.1, o.2)).1.eq
  have ht (o : Outcome) : Matrix.trace (canonicalProjector r b o) = 1 :=
    (projector_trace_idempotent r hr b (canonicalRelabel b o.1, o.2)).1
  have hS : Sᴴ = S := by simp only [S, Matrix.conjTranspose_sum, hp]
  have htrace : Matrix.trace S = 6 := by
    simp [S, Matrix.trace_sum, ht, Outcome]
  have hsquare : Matrix.trace (S * S) = 6 := by
    simp [S, Finset.sum_mul, Finset.mul_sum, Matrix.trace_sum,
      canonical_projector_gram r hr, Outcome]
  have hz : Matrix.trace ((S - 1)ᴴ * (S - 1)) = 0 := by
    simp only [Matrix.conjTranspose_sub, hS, Matrix.conjTranspose_one, Matrix.sub_mul,
      Matrix.mul_sub, Matrix.mul_one, Matrix.one_mul, Matrix.trace_sub, hsquare, htrace]
    norm_num [Matrix.trace_one, Coordinate]
  exact sub_eq_zero.mp (Matrix.trace_conjTranspose_mul_self_eq_zero_iff.mp hz)

def centeredProjector (r : ℝ) (b : Fin 3) (o : Outcome) : Matrix Coordinate Coordinate ℂ :=
  canonicalProjector r b o - (1/6 : ℂ) • 1

/-- The centered canonical projectors have the precise redundant orthogonal
frame Gram matrix needed for a measurement Bessel certificate. -/
theorem centered_projector_gram (r : ℝ) (hr : r^2 = 3)
    (b c : Fin 3) (o p : Outcome) :
    Matrix.trace (centeredProjector r b o * centeredProjector r c p) =
      if b = c then (if o = p then 1 else 0) - (1 : ℂ)/6 else 0 := by
  have ht (d : Fin 3) (q : Outcome) : Matrix.trace (canonicalProjector r d q) = 1 :=
    (projector_trace_idempotent r hr d (canonicalRelabel d q.1, q.2)).1
  simp only [centeredProjector, Matrix.sub_mul, Matrix.mul_sub, Matrix.smul_mul,
    Matrix.mul_smul, Matrix.one_mul, Matrix.mul_one, Matrix.trace_sub, Matrix.trace_smul,
    smul_eq_mul, ht, canonical_projector_gram r hr]
  norm_num [Matrix.trace_one, Coordinate]
  split_ifs <;> ring

end MUBMeasurementProjectors
