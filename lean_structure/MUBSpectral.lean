module

public import MUBIdentities
public import MUBGap
public import Mathlib.Analysis.Complex.Norm
public import Mathlib.Analysis.Normed.Lp.PiLp
public import Mathlib.LinearAlgebra.Dimension.Constructions
public import Mathlib.LinearAlgebra.LinearIndependent.Lemmas
public import Mathlib.Data.Finset.Max
public import Mathlib.Tactic

@[expose] public section
noncomputable section

namespace MUBSpectral

abbrev Qubit := Fin 2 → ℂ

def innerQ (u v : Qubit) : ℂ := star (u 0) * v 0 + star (u 1) * v 1
def weight (u : Qubit) : ℝ := Complex.normSq (u 0) + Complex.normSq (u 1)
def overlapSum (v : Fin 3 → Qubit) : ℝ :=
  Complex.normSq (innerQ (v 0) (v 1)) +
    Complex.normSq (innerQ (v 1) (v 2)) +
    Complex.normSq (innerQ (v 2) (v 0))

theorem weight_nonneg (u : Qubit) : 0 ≤ weight u :=
  add_nonneg (Complex.normSq_nonneg _) (Complex.normSq_nonneg _)

theorem innerQ_self (u : Qubit) : innerQ u u = (weight u : ℂ) := by
  simp only [innerQ, weight, Complex.ofReal_add,
    Complex.normSq_eq_conj_mul_self, Complex.star_def]

theorem innerQ_swap (u v : Qubit) : innerQ v u = star (innerQ u v) := by
  simp only [innerQ, star_add, star_mul, star_star]

theorem norm_innerQ_swap (u v : Qubit) : ‖innerQ v u‖ = ‖innerQ u v‖ := by
  rw [innerQ_swap, norm_star]

theorem normSq_innerQ_swap (u v : Qubit) :
    Complex.normSq (innerQ v u) = Complex.normSq (innerQ u v) := by
  rw [Complex.normSq_eq_norm_sq, Complex.normSq_eq_norm_sq, norm_innerQ_swap]

/-- Three vectors in complex dimension two have a nontrivial linear relation. -/
theorem qubit_relation (v : Fin 3 → Qubit) :
    ∃ c : Fin 3 → ℂ, (∑ k, c k • v k) = 0 ∧ ∃ k, c k ≠ 0 := by
  apply Fintype.not_linearIndependent_iff.mp
  intro hi
  have hd := hi.fintype_card_le_finrank
  norm_num [Qubit, Module.finrank_pi] at hd

theorem relation_innerQ (v : Fin 3 → Qubit) (c : Fin 3 → ℂ)
    (hc : (∑ k, c k • v k) = 0) (u : Qubit) :
    c 0 * innerQ u (v 0) + c 1 * innerQ u (v 1) +
      c 2 * innerQ u (v 2) = 0 := by
  have h0 : c 0 * v 0 0 + c 1 * v 1 0 + c 2 * v 2 0 = 0 := by
    simpa [Fin.sum_univ_succ, add_assoc] using congrFun hc 0
  have h1 : c 0 * v 0 1 + c 1 * v 1 1 + c 2 * v 2 1 = 0 := by
    simpa [Fin.sum_univ_succ, add_assoc] using congrFun hc 1
  calc
    _ = star (u 0) * (c 0 * v 0 0 + c 1 * v 1 0 + c 2 * v 2 0) +
        star (u 1) * (c 0 * v 0 1 + c 1 * v 1 1 + c 2 * v 2 1) := by
          simp only [innerQ]
          ring
    _ = 0 := by rw [h0, h1]; ring

/-- A diagonal row of a kernel relation is bounded by its off-diagonal row sum.
The selected coefficient has maximal modulus, so it can be cancelled. -/
theorem diagonal_row_bound {n : ℝ} {a b ci cj ck : ℂ}
    (hn : 0 ≤ n) (hci : ci ≠ 0) (hj : ‖cj‖ ≤ ‖ci‖) (hk : ‖ck‖ ≤ ‖ci‖)
    (hrel : (n : ℂ) * ci + a * cj + b * ck = 0) : n ≤ ‖a‖ + ‖b‖ := by
  have heq : (n : ℂ) * ci = -(a * cj + b * ck) := by linear_combination hrel
  have hnorm : n * ‖ci‖ ≤ (‖a‖ + ‖b‖) * ‖ci‖ := by
    calc
      n * ‖ci‖ = ‖(n : ℂ) * ci‖ := by simp [abs_of_nonneg hn]
      _ = ‖a * cj + b * ck‖ := by rw [heq, norm_neg]
      _ ≤ ‖a * cj‖ + ‖b * ck‖ := norm_add_le _ _
      _ = ‖a‖ * ‖cj‖ + ‖b‖ * ‖ck‖ := by simp only [norm_mul]
      _ ≤ (‖a‖ + ‖b‖) * ‖ci‖ := by
        nlinarith only [mul_nonneg (norm_nonneg a) (sub_nonneg.mpr hj),
          mul_nonneg (norm_nonneg b) (sub_nonneg.mpr hk)]
  exact (mul_le_mul_iff_left₀ (norm_pos_iff.mpr hci)).mp (by nlinarith only [hnorm])

/-- Genuine rank-two Gram estimate: every common lower bound h on the three
weights satisfies h² ≤ twice the sum of squared pairwise overlaps. -/
theorem rank_two_small_weight (v : Fin 3 → Qubit) {h : ℝ}
    (hh : 0 ≤ h) (hlower : ∀ k, h ≤ weight (v k)) :
    h ^ 2 ≤ 2 * overlapSum v := by
  obtain ⟨c, hc, k, hk⟩ := qubit_relation v
  obtain ⟨i, _, himax⟩ := Finset.exists_max_image Finset.univ (fun j => ‖c j‖)
    (Finset.univ_nonempty : (Finset.univ : Finset (Fin 3)).Nonempty)
  have hmax : ∀ j, ‖c j‖ ≤ ‖c i‖ := fun j => himax j (Finset.mem_univ j)
  have hci : c i ≠ 0 := by
    intro hz
    have hpos := norm_pos_iff.mpr hk
    have := hmax k
    rw [hz, norm_zero] at this
    linarith
  fin_cases i <;> dsimp only at hci hmax
  · have hr := diagonal_row_bound (weight_nonneg (v 0)) hci (hmax 1) (hmax 2)
      (show (weight (v 0) : ℂ) * c 0 + innerQ (v 0) (v 1) * c 1 +
        innerQ (v 0) (v 2) * c 2 = 0 by
          have hsum := relation_innerQ v c hc (v 0)
          rw [innerQ_self] at hsum
          linear_combination hsum)
    have hs := sq_nonneg (‖innerQ (v 0) (v 1)‖ - ‖innerQ (v 0) (v 2)‖)
    have hn := Complex.normSq_nonneg (innerQ (v 1) (v 2))
    simp only [overlapSum, Complex.normSq_eq_norm_sq]
    rw [norm_innerQ_swap (v 0) (v 2)]
    rw [Complex.normSq_eq_norm_sq] at hn
    nlinarith only [hr, hlower 0, hh, hs, hn, norm_nonneg (innerQ (v 0) (v 1)),
      norm_nonneg (innerQ (v 0) (v 2))]
  · have hr := diagonal_row_bound (weight_nonneg (v 1)) hci (hmax 0) (hmax 2)
      (show (weight (v 1) : ℂ) * c 1 + innerQ (v 1) (v 0) * c 0 +
        innerQ (v 1) (v 2) * c 2 = 0 by
          have hsum := relation_innerQ v c hc (v 1)
          rw [innerQ_self] at hsum
          linear_combination hsum)
    rw [norm_innerQ_swap] at hr
    have hs := sq_nonneg (‖innerQ (v 0) (v 1)‖ - ‖innerQ (v 1) (v 2)‖)
    have hn := Complex.normSq_nonneg (innerQ (v 2) (v 0))
    simp only [overlapSum, Complex.normSq_eq_norm_sq]
    rw [Complex.normSq_eq_norm_sq] at hn
    nlinarith only [hr, hlower 1, hh, hs, hn, norm_nonneg (innerQ (v 0) (v 1)),
      norm_nonneg (innerQ (v 1) (v 2))]
  · have hr := diagonal_row_bound (weight_nonneg (v 2)) hci (hmax 0) (hmax 1)
      (show (weight (v 2) : ℂ) * c 2 + innerQ (v 2) (v 0) * c 0 +
        innerQ (v 2) (v 1) * c 1 = 0 by
          have hsum := relation_innerQ v c hc (v 2)
          rw [innerQ_self] at hsum
          linear_combination hsum)
    rw [norm_innerQ_swap (v 1) (v 2)] at hr
    have hs := sq_nonneg (‖innerQ (v 2) (v 0)‖ - ‖innerQ (v 1) (v 2)‖)
    have hn := Complex.normSq_nonneg (innerQ (v 0) (v 1))
    simp only [overlapSum, Complex.normSq_eq_norm_sq]
    rw [Complex.normSq_eq_norm_sq] at hn
    nlinarith only [hr, hlower 2, hh, hs, hn, norm_nonneg (innerQ (v 2) (v 0)),
      norm_nonneg (innerQ (v 1) (v 2))]

/-- The squared length of a pure qubit's unnormalized Bloch vector. -/
theorem pure_bloch_length (u : Qubit) :
    (2 * (star (u 0) * u 1).re) ^ 2 +
      (2 * (star (u 0) * u 1).im) ^ 2 +
      (Complex.normSq (u 0) - Complex.normSq (u 1)) ^ 2 = (weight u) ^ 2 := by
  simp only [weight, Complex.normSq_apply, Complex.mul_re, Complex.mul_im,
    Complex.star_def, Complex.conj_re, Complex.conj_im]
  ring

theorem real_cauchy_three (a b c x y z : ℝ) :
    (a * x + b * y + c * z) ^ 2 ≤
      (a ^ 2 + b ^ 2 + c ^ 2) * (x ^ 2 + y ^ 2 + z ^ 2) := by
  nlinarith only [sq_nonneg (a * y - b * x), sq_nonneg (a * z - c * x),
    sq_nonneg (b * z - c * y)]

def quadratic (alpha beta : ℝ) (cross : ℂ) (u : Qubit) : ℝ :=
  alpha * Complex.normSq (u 0) + beta * Complex.normSq (u 1) +
    2 * (cross * (u 0 * star (u 1))).re

theorem quadratic_bloch (alpha beta : ℝ) (cross : ℂ) (u : Qubit) :
    2 * quadratic alpha beta cross u - (alpha + beta) * weight u =
      (2 * cross.re) * (2 * (star (u 0) * u 1).re) +
      (2 * cross.im) * (2 * (star (u 0) * u 1).im) +
      (alpha - beta) * (Complex.normSq (u 0) - Complex.normSq (u 1)) := by
  simp only [quadratic, weight, Complex.normSq_apply, Complex.mul_re, Complex.mul_im,
    Complex.star_def, Complex.conj_re, Complex.conj_im]
  ring

/-- The reduced-qubit Rayleigh bound, derived from Bloch coordinates rather
than assumed as a spectral oracle. Only the explicit squared Bloch length is
required of A. No positivity hypothesis on the Hermitian matrix is needed. -/
theorem bloch_rayleigh (alpha beta A : ℝ) (cross : ℂ) (u : Qubit)
    (hA : 0 ≤ A) (hAsq : A ^ 2 = (alpha - beta) ^ 2 + 4 * Complex.normSq cross) :
    (alpha + beta - A) / 2 * weight u ≤ quadratic alpha beta cross u := by
  have hc := real_cauchy_three (2 * cross.re) (2 * cross.im) (alpha - beta)
    (2 * (star (u 0) * u 1).re) (2 * (star (u 0) * u 1).im)
    (Complex.normSq (u 0) - Complex.normSq (u 1))
  have hleft : (2 * cross.re) ^ 2 + (2 * cross.im) ^ 2 + (alpha - beta) ^ 2 = A ^ 2 := by
    rw [Complex.normSq_apply] at hAsq
    nlinarith only [hAsq]
  rw [hleft, pure_bloch_length] at hc
  rw [← quadratic_bloch alpha beta cross u] at hc
  have hprod := mul_nonneg hA (weight_nonneg u)
  have habs : |2 * quadratic alpha beta cross u - (alpha + beta) * weight u| ≤
      A * weight u := by
    apply (sq_le_sq₀ (abs_nonneg _) hprod).mp
    simpa only [sq_abs, mul_pow] using hc
  have hlo := (abs_le.mp habs).1
  nlinarith only [hlo]

def frameAlpha (v : Fin 3 → Qubit) : ℝ := ∑ k, Complex.normSq (v k 0)
def frameBeta (v : Fin 3 → Qubit) : ℝ := ∑ k, Complex.normSq (v k 1)
def frameCross (v : Fin 3 → Qubit) : ℂ := ∑ k, star (v k 0) * v k 1
def frameForm (v : Fin 3 → Qubit) (u : Qubit) : ℝ :=
  ∑ k, Complex.normSq (innerQ (v k) u)

theorem frame_trace (v : Fin 3 → Qubit) :
    frameAlpha v + frameBeta v = ∑ k, weight (v k) := by
  simp only [frameAlpha, frameBeta, weight, Finset.sum_add_distrib]

/-- The actual three-vector frame quadratic form equals its 2×2 Hermitian
coordinate expression. -/
theorem frame_form_eq_quadratic (v : Fin 3 → Qubit) (u : Qubit) :
    frameForm v u = quadratic (frameAlpha v) (frameBeta v) (frameCross v) u := by
  simp only [frameForm, quadratic, frameAlpha, frameBeta, frameCross,
    Fin.sum_univ_succ, Fin.isValue, innerQ,
    Complex.normSq_apply, Complex.add_re, Complex.add_im, Complex.mul_re,
    Complex.mul_im, Complex.star_def, Complex.conj_re, Complex.conj_im,
    Fin.sum_univ_zero, add_zero]
  ring

theorem frame_rayleigh (v : Fin 3 → Qubit) (u : Qubit) {A : ℝ}
    (hA : 0 ≤ A)
    (hAsq : A ^ 2 = (frameAlpha v - frameBeta v) ^ 2 + 4 * Complex.normSq (frameCross v))
    (hunit : ∑ k, weight (v k) = 1) :
    (1 - A) / 2 * weight u ≤ frameForm v u := by
  have h := bloch_rayleigh (frameAlpha v) (frameBeta v) A (frameCross v) u hA hAsq
  rw [frame_trace, hunit, ← frame_form_eq_quadratic] at h
  exact h

theorem innerQ_cauchy (u w : Qubit) :
    Complex.normSq (innerQ u w) ≤ weight u * weight w := by
  have hid : Complex.normSq (innerQ u w) +
      Complex.normSq (u 0 * w 1 - u 1 * w 0) = weight u * weight w := by
    simp only [innerQ, weight, Complex.normSq_apply, Complex.add_re, Complex.add_im,
      Complex.sub_re, Complex.sub_im, Complex.mul_re, Complex.mul_im,
      Complex.star_def, Complex.conj_re, Complex.conj_im]
    ring
  nlinarith only [hid, Complex.normSq_nonneg (u 0 * w 1 - u 1 * w 0)]

def perp (u : Qubit) : Qubit := ![-star (u 1), star (u 0)]

theorem weight_perp (u : Qubit) : weight (perp u) = weight u := by
  simp [weight, perp, Complex.normSq_conj, add_comm]

theorem innerQ_perp (u : Qubit) : innerQ u (perp u) = 0 := by
  simp [innerQ, perp]
  ring

theorem frame_perp_upper (v : Fin 3 → Qubit) (j : Fin 3) :
    frameForm v (perp (v j)) ≤ ((∑ k, weight (v k)) - weight (v j)) * weight (v j) := by
  calc
    frameForm v (perp (v j)) ≤
        ∑ k, (weight (v k) * weight (v j) - if k = j then weight (v j) ^ 2 else 0) := by
      apply Finset.sum_le_sum
      intro k _
      by_cases hk : k = j
      · subst k
        simp [innerQ_perp, pow_two]
      · simp only [hk, ite_false, sub_zero]
        simpa only [weight_perp] using innerQ_cauchy (v k) (perp (v j))
    _ = _ := by
      rw [Finset.sum_sub_distrib, ← Finset.sum_mul]
      simp
      ring

/-- Each coefficient weight is at most one minus the smaller qubit eigenvalue.
This supplies the two complementary-weight inequalities in ScalarCertificate. -/
theorem frame_weight_complement (v : Fin 3 → Qubit) (j : Fin 3) {A : ℝ}
    (hA : 0 ≤ A)
    (hAsq : A ^ 2 = (frameAlpha v - frameBeta v) ^ 2 + 4 * Complex.normSq (frameCross v))
    (hunit : ∑ k, weight (v k) = 1) : (1 - A) / 2 ≤ 1 - weight (v j) := by
  by_cases hw : weight (v j) = 0
  · rw [hw]
    linarith only [hA]
  · have hwpos : 0 < weight (v j) := lt_of_le_of_ne (weight_nonneg _) (Ne.symm hw)
    have hl := frame_rayleigh v (perp (v j)) hA hAsq hunit
    rw [weight_perp] at hl
    have hu := frame_perp_upper v j
    rw [hunit] at hu
    exact (mul_le_mul_iff_left₀ hwpos).mp (by nlinarith only [hl, hu])

theorem frame_at_coefficient_upper (v : Fin 3 → Qubit) (j : Fin 3) :
    frameForm v (v j) ≤ weight (v j) ^ 2 + overlapSum v := by
  fin_cases j <;> dsimp only
  · change frameForm v (v 0) ≤ weight (v 0) ^ 2 + overlapSum v
    have hn := Complex.normSq_nonneg (innerQ (v 1) (v 2))
    simp only [frameForm, Fin.sum_univ_three,
      innerQ_self, Complex.normSq_ofReal, overlapSum]
    rw [normSq_innerQ_swap (v 0) (v 1)]
    nlinarith only [hn]
  · change frameForm v (v 1) ≤ weight (v 1) ^ 2 + overlapSum v
    have hn := Complex.normSq_nonneg (innerQ (v 2) (v 0))
    simp only [frameForm, Fin.sum_univ_three,
      innerQ_self, Complex.normSq_ofReal, overlapSum]
    rw [normSq_innerQ_swap (v 1) (v 2)]
    nlinarith only [hn]
  · change frameForm v (v 2) ≤ weight (v 2) ^ 2 + overlapSum v
    have hn := Complex.normSq_nonneg (innerQ (v 0) (v 1))
    simp only [frameForm, Fin.sum_univ_three,
      innerQ_self, Complex.normSq_ofReal, overlapSum]
    rw [normSq_innerQ_swap (v 2) (v 0)]
    nlinarith only [hn]

/-- The h(lambda-h) estimate now follows for every actual coefficient vector. -/
theorem coefficient_rayleigh_bound (v : Fin 3 → Qubit) (j : Fin 3) {A : ℝ}
    (hA : 0 ≤ A)
    (hAsq : A ^ 2 = (frameAlpha v - frameBeta v) ^ 2 + 4 * Complex.normSq (frameCross v))
    (hunit : ∑ k, weight (v k) = 1) :
    weight (v j) * ((1 - A) / 2 - weight (v j)) ≤ overlapSum v := by
  have hl := frame_rayleigh v (v j) hA hAsq hunit
  have hu := frame_at_coefficient_upper v j
  nlinarith only [hl, hu]

def pauli (b : Fin 3) (u v : Qubit) : ℂ :=
  if b = 0 then star (u 0) * v 0 - star (u 1) * v 1
  else if b = 1 then star (u 0) * v 1 + star (u 1) * v 0
  else -Complex.I * star (u 0) * v 1 + Complex.I * star (u 1) * v 0

def vectorNorm (f : Fin 3 → ℂ) : ℝ := ‖WithLp.toLp 2 f‖

theorem vectorNorm_nonneg (f : Fin 3 → ℂ) : 0 ≤ vectorNorm f := norm_nonneg _

theorem vectorNorm_sq (f : Fin 3 → ℂ) :
    vectorNorm f ^ 2 = ∑ b, Complex.normSq (f b) := by
  simp only [vectorNorm, PiLp.norm_sq_eq_of_L2, Complex.sq_norm]

theorem vectorNorm_reverse_triangle (m r : Fin 3 → ℂ) :
    vectorNorm m - vectorNorm r ≤ vectorNorm (fun b => m b + r b) := by
  have h := norm_sub_norm_le (WithLp.toLp 2 m) (-(WithLp.toLp 2 r))
  simpa only [vectorNorm, norm_neg, sub_neg_eq_add, ← WithLp.toLp_add, Pi.add_def] using h

theorem normSq_add_le_two (z w : ℂ) :
    Complex.normSq (z + w) ≤ 2 * Complex.normSq z + 2 * Complex.normSq w := by
  have hid : Complex.normSq (z + w) + Complex.normSq (z - w) =
      2 * Complex.normSq z + 2 * Complex.normSq w := by
    simp only [Complex.normSq_apply, Complex.add_re, Complex.add_im,
      Complex.sub_re, Complex.sub_im]
    ring
  nlinarith only [hid, Complex.normSq_nonneg (z - w)]

theorem vectorNorm_add_sq_le (f g : Fin 3 → ℂ) :
    vectorNorm (fun b => f b + g b) ^ 2 ≤ 2 * vectorNorm f ^ 2 + 2 * vectorNorm g ^ 2 := by
  rw [vectorNorm_sq, vectorNorm_sq, vectorNorm_sq]
  calc
    _ ≤ ∑ b, (2 * Complex.normSq (f b) + 2 * Complex.normSq (g b)) :=
      Finset.sum_le_sum fun b _ => normSq_add_le_two (f b) (g b)
    _ = _ := by simp only [Finset.sum_add_distrib, ← Finset.mul_sum]

theorem pauli_fierz (u v : Qubit) :
    (∑ b, Complex.normSq (pauli b u v)) =
      2 * weight u * weight v - Complex.normSq (innerQ u v) := by
  simpa [pauli, Fin.sum_univ_three, weight, innerQ] using
    MUBGap.qubit_fierz (u 0) (u 1) (v 0) (v 1)

def phasePair (eta : Fin 3 → ℂ) (u v : Qubit) : Fin 3 → ℂ :=
  fun b => eta b * pauli b u v

theorem phasePair_sq (eta : Fin 3 → ℂ) (u v : Qubit)
    (heta : ∀ b, Complex.normSq (eta b) = 1) :
    vectorNorm (phasePair eta u v) ^ 2 =
      2 * weight u * weight v - Complex.normSq (innerQ u v) := by
  rw [vectorNorm_sq]
  simp only [phasePair, Complex.normSq_mul, heta, one_mul]
  exact pauli_fierz u v

theorem phasePair_sq_upper (eta : Fin 3 → ℂ) (u v : Qubit)
    (heta : ∀ b, Complex.normSq (eta b) = 1) :
    vectorNorm (phasePair eta u v) ^ 2 ≤ 2 * weight u * weight v := by
  rw [phasePair_sq eta u v heta]
  exact sub_le_self _ (Complex.normSq_nonneg _)

/-- The two pairs incident to the small coefficient have the required squared
norm bound. The phases are arbitrary coordinatewise unit phases. -/
theorem correlation_remainder_bound (eta zeta : Fin 3 → ℂ) (u v w : Qubit)
    (heta : ∀ b, Complex.normSq (eta b) = 1)
    (hzeta : ∀ b, Complex.normSq (zeta b) = 1) :
    vectorNorm (fun b => phasePair eta u v b + phasePair zeta w u b) ^ 2 ≤
      4 * weight u * (weight v + weight w) := by
  have hadd := vectorNorm_add_sq_le (phasePair eta u v) (phasePair zeta w u)
  have h1 := phasePair_sq_upper eta u v heta
  have h2 := phasePair_sq_upper zeta w u hzeta
  nlinarith only [hadd, h1, h2]

/-- All three phase-weighted cyclic Pauli pairs. -/
def correlation3 (eta : Fin 3 → Fin 3 → ℂ) (v : Fin 3 → Qubit) : Fin 3 → ℂ :=
  fun b => phasePair (eta 0) (v 1) (v 0) b +
    phasePair (eta 1) (v 2) (v 1) b + phasePair (eta 2) (v 0) (v 2) b

theorem overlapSum_nonneg (v : Fin 3 → Qubit) : 0 ≤ overlapSum v := by
  exact add_nonneg (add_nonneg (Complex.normSq_nonneg _) (Complex.normSq_nonneg _))
    (Complex.normSq_nonneg _)

/-- Every scalar certificate premise is now derived from actual qubit
coefficients. The remaining hypotheses are normalization, the explicit Bloch
length identity, unit phases, and the Fourier energy identity. -/
theorem energy_gap_of_quantum_identities
    (v : Fin 3 → Qubit) (eta : Fin 3 → Fin 3 → ℂ) {A E : ℝ}
    (hA : 0 ≤ A)
    (hAsq : A ^ 2 = (frameAlpha v - frameBeta v) ^ 2 + 4 * Complex.normSq (frameCross v))
    (hunit : ∑ k, weight (v k) = 1)
    (heta : ∀ k b, Complex.normSq (eta k b) = 1)
    (hE : E = overlapSum v + A ^ 2 / 6 + vectorNorm (correlation3 eta v) ^ 2 / 3) :
    1 / 72 < E := by
  obtain ⟨h, _, hmin⟩ := Finset.exists_min_image Finset.univ (fun j => weight (v j))
    (Finset.univ_nonempty : (Finset.univ : Finset (Fin 3)).Nonempty)
  have hlower : ∀ j, weight (v h) ≤ weight (v j) :=
    fun j => hmin j (Finset.mem_univ j)
  have hrank := rank_two_small_weight v (weight_nonneg (v h)) hlower
  have hray := coefficient_rayleigh_bound v h hA hAsq hunit
  have hnorm := hunit
  rw [Fin.sum_univ_three] at hnorm
  have h01 := Complex.normSq_nonneg (innerQ (v 0) (v 1))
  have h12 := Complex.normSq_nonneg (innerQ (v 1) (v 2))
  have h20 := Complex.normSq_nonneg (innerQ (v 2) (v 0))
  fin_cases h <;> dsimp only at hrank hray
  · let m : Fin 3 → ℂ := phasePair (eta 1) (v 2) (v 1)
    let r : Fin 3 → ℂ := fun b => phasePair (eta 2) (v 0) (v 2) b + phasePair (eta 0) (v 1) (v 0) b
    have hi := frame_weight_complement v 2 hA hAsq hunit
    have hj := frame_weight_complement v 1 hA hAsq hunit
    have hm := phasePair_sq (eta 1) (v 2) (v 1) (heta 1)
    have hp : Complex.normSq (innerQ (v 2) (v 1)) ≤ overlapSum v := by
      rw [normSq_innerQ_swap (v 1) (v 2)]
      unfold overlapSum
      linarith only [h01, h12, h20]
    have hrem := correlation_remainder_bound (eta 2) (eta 0)
      (v 0) (v 2) (v 1) (heta 2) (heta 0)
    have hrest : weight (v 2) + weight (v 1) = 1 - weight (v 0) := by
      linarith only [hnorm]
    rw [hrest] at hrem
    have hfun : (fun b => m b + r b) = correlation3 eta v := by
      funext b
      simp only [m, r, correlation3]
      ring
    have htriangle := vectorNorm_reverse_triangle m r
    rw [hfun] at htriangle
    have cert : MUBGap.ScalarCertificate E (overlapSum v) A ((1 - A) / 2)
        (weight (v 0)) (weight (v 1)) (weight (v 2))
        (vectorNorm m) (vectorNorm r) (vectorNorm (correlation3 eta v)) := {
      energy := hE
      overlap_nonneg := overlapSum_nonneg v
      bloch_nonneg := hA
      weight_nonneg := weight_nonneg (v 0)
      main_nonneg := vectorNorm_nonneg m
      remainder_nonneg := vectorNorm_nonneg r
      correlation_nonneg := vectorNorm_nonneg (correlation3 eta v)
      eigenvalue := rfl
      rank_bound := hrank
      rayleigh := hray
      first_weight := by linarith only [hi, hnorm]
      second_weight := by linarith only [hj, hnorm]
      weight_sum := by linarith only [hnorm]
      main_bound := by dsimp only [m]; nlinarith only [hm, hp]
      remainder_bound := hrem
      reverse_triangle := htriangle
    }
    exact MUBGap.scalar_gap cert
  · let m : Fin 3 → ℂ := phasePair (eta 2) (v 0) (v 2)
    let r : Fin 3 → ℂ := fun b => phasePair (eta 0) (v 1) (v 0) b + phasePair (eta 1) (v 2) (v 1) b
    have hi := frame_weight_complement v 2 hA hAsq hunit
    have hj := frame_weight_complement v 0 hA hAsq hunit
    have hm := phasePair_sq (eta 2) (v 0) (v 2) (heta 2)
    have hp : Complex.normSq (innerQ (v 0) (v 2)) ≤ overlapSum v := by
      rw [normSq_innerQ_swap (v 2) (v 0)]
      unfold overlapSum
      linarith only [h01, h12, h20]
    have hrem := correlation_remainder_bound (eta 0) (eta 1)
      (v 1) (v 0) (v 2) (heta 0) (heta 1)
    have hrest : weight (v 0) + weight (v 2) = 1 - weight (v 1) := by
      linarith only [hnorm]
    rw [hrest] at hrem
    have hfun : (fun b => m b + r b) = correlation3 eta v := by
      funext b
      simp only [m, r, correlation3]
      ring
    have htriangle := vectorNorm_reverse_triangle m r
    rw [hfun] at htriangle
    have cert : MUBGap.ScalarCertificate E (overlapSum v) A ((1 - A) / 2)
        (weight (v 1)) (weight (v 0)) (weight (v 2))
        (vectorNorm m) (vectorNorm r) (vectorNorm (correlation3 eta v)) := {
      energy := hE
      overlap_nonneg := overlapSum_nonneg v
      bloch_nonneg := hA
      weight_nonneg := weight_nonneg (v 1)
      main_nonneg := vectorNorm_nonneg m
      remainder_nonneg := vectorNorm_nonneg r
      correlation_nonneg := vectorNorm_nonneg (correlation3 eta v)
      eigenvalue := rfl
      rank_bound := hrank
      rayleigh := hray
      first_weight := by linarith only [hi, hnorm]
      second_weight := by linarith only [hj, hnorm]
      weight_sum := by linarith only [hnorm]
      main_bound := by dsimp only [m]; nlinarith only [hm, hp]
      remainder_bound := hrem
      reverse_triangle := htriangle
    }
    exact MUBGap.scalar_gap cert
  · let m : Fin 3 → ℂ := phasePair (eta 0) (v 1) (v 0)
    let r : Fin 3 → ℂ := fun b => phasePair (eta 1) (v 2) (v 1) b + phasePair (eta 2) (v 0) (v 2) b
    have hi := frame_weight_complement v 1 hA hAsq hunit
    have hj := frame_weight_complement v 0 hA hAsq hunit
    have hm := phasePair_sq (eta 0) (v 1) (v 0) (heta 0)
    have hp : Complex.normSq (innerQ (v 1) (v 0)) ≤ overlapSum v := by
      rw [normSq_innerQ_swap (v 0) (v 1)]
      unfold overlapSum
      linarith only [h01, h12, h20]
    have hrem := correlation_remainder_bound (eta 1) (eta 2)
      (v 2) (v 1) (v 0) (heta 1) (heta 2)
    have hrest : weight (v 1) + weight (v 0) = 1 - weight (v 2) := by
      linarith only [hnorm]
    rw [hrest] at hrem
    have hfun : (fun b => m b + r b) = correlation3 eta v := by
      funext b
      simp only [m, r, correlation3]
      ring
    have htriangle := vectorNorm_reverse_triangle m r
    rw [hfun] at htriangle
    have cert : MUBGap.ScalarCertificate E (overlapSum v) A ((1 - A) / 2)
        (weight (v 2)) (weight (v 0)) (weight (v 1))
        (vectorNorm m) (vectorNorm r) (vectorNorm (correlation3 eta v)) := {
      energy := hE
      overlap_nonneg := overlapSum_nonneg v
      bloch_nonneg := hA
      weight_nonneg := weight_nonneg (v 2)
      main_nonneg := vectorNorm_nonneg m
      remainder_nonneg := vectorNorm_nonneg r
      correlation_nonneg := vectorNorm_nonneg (correlation3 eta v)
      eigenvalue := rfl
      rank_bound := hrank
      rayleigh := hray
      first_weight := by linarith only [hi, hnorm]
      second_weight := by linarith only [hj, hnorm]
      weight_sum := by linarith only [hnorm]
      main_bound := by dsimp only [m]; nlinarith only [hm, hp]
      remainder_bound := hrem
      reverse_triangle := htriangle
    }
    exact MUBGap.scalar_gap cert

#print axioms energy_gap_of_quantum_identities
#print axioms qubit_relation
#print axioms rank_two_small_weight
#print axioms pure_bloch_length
#print axioms bloch_rayleigh
#print axioms frame_form_eq_quadratic
#print axioms frame_rayleigh
#print axioms frame_weight_complement
#print axioms coefficient_rayleigh_bound
#print axioms pauli_fierz
#print axioms correlation_remainder_bound
#print axioms vectorNorm_reverse_triangle

end MUBSpectral
