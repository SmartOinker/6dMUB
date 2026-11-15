import Mathlib.Analysis.Real.Sqrt
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NthRewrite
import Mathlib.Tactic.Push

/-!
# From a vector to a basis: the bridge lemma (Problem 124, mutually unbiased bases in dimension six)

Paper statement (report, Lemma "A quadratic cap on the square root" and Theorem "From a vector to a basis").

Let `c* = 3 √6 / (√6 + 1)^2`. For `p ∈ [0,1]`:

  `√p ≤ 1/√6 + (√6/2) (p - 1/6) - c* (p - 1/6)^2`.

Consequences, stated here for arrays of real numbers (the squared overlaps `p = |⟨e, g⟩|^2`):

* (bias)  if 18 numbers `x` satisfy `γ ≤ ∑ (x - 1/6)^2`, one of them has `√(γ/18) ≤ |x - 1/6|`;
* (pair)  if a 6 × 6 array `p` has entries in `[0,1]` and total 6, then
          `∑ √p ≤ 6 √6 - c* ∑ (p - 1/6)^2`;
* (game)  if `q r k j` (triple basis `r`, its vector `k`, fourth-basis vector `j`) has entries in `[0,1]`,
          total 6 for each `r`, and energy `γ ≤ ∑_{r,k} (q r k j - 1/6)^2` for each `j`, then
          `∑ √q ≤ 18 √6 - 6 c* γ`.

Difference from the paper statement: the paper speaks about orthonormal bases of `ℂ^6`; this file is about arrays
of real numbers. The facts `0 ≤ |⟨e,g⟩|^2 ≤ 1` and `∑_{i,j} |⟨e_i,g_j⟩|^2 = 6` (Parseval) that connect the two are
proved in `Bases.lean` (`sq_overlap_le_one`, `sq_overlap_total`), which is part of the built project.

STATUS: this file builds with Lean v4.35.0 and Mathlib v4.35.0 (see `lean/README.md` and `lean/BUILD_LOG.txt`).
-/

namespace MUB6Bridge

open Finset BigOperators

noncomputable section

/-- The constant `c* = 3 √6 / (√6 + 1)^2 = (21 √6 - 36)/25 ≈ 0.617571`. -/
def cstar : ℝ := 3 * Real.sqrt 6 / (Real.sqrt 6 + 1) ^ 2

theorem sqrt6_sq : Real.sqrt 6 ^ 2 = 6 := Real.sq_sqrt (by norm_num)

theorem sqrt6_pos : 0 < Real.sqrt 6 := Real.sqrt_pos.mpr (by norm_num)

/-- `2.44948 < √6 < 2.4495`. -/
theorem sqrt6_bounds : (2.44948 : ℝ) < Real.sqrt 6 ∧ Real.sqrt 6 < 2.4495 := by
  constructor
  · rw [show (2.44948 : ℝ) = Real.sqrt (2.44948 ^ 2) from (Real.sqrt_sq (by norm_num)).symm]
    exact Real.sqrt_lt_sqrt (by norm_num) (by norm_num)
  · rw [show (2.4495 : ℝ) = Real.sqrt (2.4495 ^ 2) from (Real.sqrt_sq (by norm_num)).symm]
    exact Real.sqrt_lt_sqrt (by norm_num) (by norm_num)

theorem cstar_pos : 0 < cstar := by
  unfold cstar
  have h := sqrt6_pos
  positivity

/-- Closed form of the constant. -/
theorem cstar_eq : cstar = (21 * Real.sqrt 6 - 36) / 25 := by
  unfold cstar
  have h := sqrt6_pos
  rw [div_eq_div_iff (by positivity) (by norm_num)]
  linear_combination (-(21 * Real.sqrt 6 + 6)) * sqrt6_sq

/-- Quadratic cap on the square root on `[0,1]`.
Proof idea: put `s = √p`, `a = √6`, so `a^2 = 6`, `p = s^2`, `0 ≤ s ≤ 1`, `1/a = a/6`. Then
`RHS - s = (s - a/6)^2 * (a/2 - c* (s + a/6)^2)`, and `c* (1 + a/6)^2 = a/2`, `(s + a/6)^2 ≤ (1 + a/6)^2`. -/
theorem sqrt_le_quadratic_cap {p : ℝ} (hp0 : 0 ≤ p) (hp1 : p ≤ 1) :
    Real.sqrt p ≤ 1 / Real.sqrt 6 + Real.sqrt 6 / 2 * (p - 1 / 6) - cstar * (p - 1 / 6) ^ 2 := by
  have ha2 : Real.sqrt 6 ^ 2 = 6 := sqrt6_sq
  have hapos : 0 < Real.sqrt 6 := sqrt6_pos
  have hs2 : Real.sqrt p ^ 2 = p := Real.sq_sqrt hp0
  have hs0 : 0 ≤ Real.sqrt p := Real.sqrt_nonneg p
  have hs1 : Real.sqrt p ≤ 1 := Real.sqrt_le_one.mpr hp1 |>.trans_eq rfl
  have h1a : 1 / Real.sqrt 6 = Real.sqrt 6 / 6 := by
    field_simp
    linarith [ha2]
  have hc : 0 < (21 * Real.sqrt 6 - 36) / 25 := by
    rw [← cstar_eq]; exact cstar_pos
  -- the bracket `a/2 - c (s + a/6)^2` is nonnegative
  have hcap : (21 * Real.sqrt 6 - 36) / 25 * (1 + Real.sqrt 6 / 6) ^ 2 = Real.sqrt 6 / 2 := by
    linear_combination ((7 * Real.sqrt 6 + 72) / 300) * ha2
  have hmono : (Real.sqrt p + Real.sqrt 6 / 6) ^ 2 ≤ (1 + Real.sqrt 6 / 6) ^ 2 := by
    apply pow_le_pow_left₀ (by positivity)
    linarith
  have hbr : 0 ≤ Real.sqrt 6 / 2 - (21 * Real.sqrt 6 - 36) / 25 * (Real.sqrt p + Real.sqrt 6 / 6) ^ 2 := by
    have := mul_le_mul_of_nonneg_left hmono hc.le
    linarith [hcap]
  have hprod : 0 ≤ (Real.sqrt p - Real.sqrt 6 / 6) ^ 2 *
      (Real.sqrt 6 / 2 - (21 * Real.sqrt 6 - 36) / 25 * (Real.sqrt p + Real.sqrt 6 / 6) ^ 2) :=
    mul_nonneg (sq_nonneg _) hbr
  -- the factorization, modulo `a^2 = 6`
  have key : Real.sqrt 6 / 6 + Real.sqrt 6 / 2 * (Real.sqrt p ^ 2 - 1 / 6)
        - (21 * Real.sqrt 6 - 36) / 25 * (Real.sqrt p ^ 2 - 1 / 6) ^ 2 - Real.sqrt p
      = (Real.sqrt p - Real.sqrt 6 / 6) ^ 2 *
        (Real.sqrt 6 / 2 - (21 * Real.sqrt 6 - 36) / 25 * (Real.sqrt p + Real.sqrt 6 / 6) ^ 2) := by
    linear_combination
      (-(-7 * Real.sqrt 6 ^ 3 + 12 * Real.sqrt 6 ^ 2 + 504 * Real.sqrt 6 * Real.sqrt p ^ 2
          + 108 * Real.sqrt 6 - 864 * Real.sqrt p ^ 2 - 1800 * Real.sqrt p + 72) / 10800) * ha2
  rw [cstar_eq, h1a]
  nth_rewrite 2 [← hs2]
  nth_rewrite 3 [← hs2]
  linarith [key, hprod]

/-- Bias: among 18 outcomes with energy at least `γ`, one deviates from `1/6` by at least `√(γ/18)`. -/
theorem bias_bound (x : Fin 3 → Fin 6 → ℝ) (γ : ℝ)
    (hE : γ ≤ ∑ r, ∑ k, (x r k - 1 / 6) ^ 2) :
    ∃ r k, Real.sqrt (γ / 18) ≤ |x r k - 1 / 6| := by
  by_contra hcon
  push Not at hcon
  have hlt : ∀ r k, (x r k - 1 / 6) ^ 2 < γ / 18 := by
    intro r k
    have h := hcon r k
    have h0 : 0 ≤ |x r k - 1 / 6| := abs_nonneg _
    have hpos : 0 < Real.sqrt (γ / 18) := lt_of_le_of_lt h0 h
    have hγ : 0 ≤ γ / 18 := (Real.sqrt_pos.mp hpos).le
    calc (x r k - 1 / 6) ^ 2 = |x r k - 1 / 6| ^ 2 := (sq_abs _).symm
      _ < Real.sqrt (γ / 18) ^ 2 := by
          exact pow_lt_pow_left₀ h h0 (by norm_num)
      _ = γ / 18 := Real.sq_sqrt hγ
  have hsum : ∑ r : Fin 3, ∑ k : Fin 6, (x r k - 1 / 6) ^ 2 < ∑ _r : Fin 3, ∑ _k : Fin 6, γ / 18 := by
    apply Finset.sum_lt_sum_of_nonempty Finset.univ_nonempty
    intro r _
    apply Finset.sum_lt_sum_of_nonempty Finset.univ_nonempty
    intro k _
    exact hlt r k
  simp at hsum
  linarith

/-- Pair sum: quantitative form of "a pair of bases maximizes `∑ |⟨e_i, g_j⟩|` iff it is unbiased". -/
theorem pair_sum_bound (p : Fin 6 → Fin 6 → ℝ) (h0 : ∀ i j, 0 ≤ p i j) (h1 : ∀ i j, p i j ≤ 1)
    (hsum : ∑ i, ∑ j, p i j = 6) :
    ∑ i, ∑ j, Real.sqrt (p i j) ≤ 6 * Real.sqrt 6 - cstar * ∑ i, ∑ j, (p i j - 1 / 6) ^ 2 := by
  have hterm : ∀ i j, Real.sqrt (p i j) ≤
      1 / Real.sqrt 6 + Real.sqrt 6 / 2 * (p i j - 1 / 6) - cstar * (p i j - 1 / 6) ^ 2 :=
    fun i j => sqrt_le_quadratic_cap (h0 i j) (h1 i j)
  have hle : ∑ i, ∑ j, Real.sqrt (p i j) ≤
      ∑ i : Fin 6, ∑ j : Fin 6,
        (1 / Real.sqrt 6 + Real.sqrt 6 / 2 * (p i j - 1 / 6) - cstar * (p i j - 1 / 6) ^ 2) :=
    Finset.sum_le_sum fun i _ => Finset.sum_le_sum fun j _ => hterm i j
  have h1a : 1 / Real.sqrt 6 = Real.sqrt 6 / 6 := by
    have := sqrt6_pos
    field_simp
    linarith [sqrt6_sq]
  have hexp : ∑ i : Fin 6, ∑ j : Fin 6,
        (1 / Real.sqrt 6 + Real.sqrt 6 / 2 * (p i j - 1 / 6) - cstar * (p i j - 1 / 6) ^ 2)
      = 36 * (1 / Real.sqrt 6) + Real.sqrt 6 / 2 * ((∑ i, ∑ j, p i j) - 6)
        - cstar * ∑ i, ∑ j, (p i j - 1 / 6) ^ 2 := by
    simp only [Finset.sum_sub_distrib, Finset.sum_add_distrib, ← Finset.mul_sum, Finset.sum_const,
      Finset.card_univ, Fintype.card_fin, nsmul_eq_mul]
    push_cast
    ring
  rw [hexp, hsum, h1a] at hle
  linarith

/-- Game: the three pairs (triple basis, fourth basis) together lose at least `6 c* γ`. -/
theorem game_bound (q : Fin 3 → Fin 6 → Fin 6 → ℝ) (γ : ℝ)
    (h0 : ∀ r k j, 0 ≤ q r k j) (h1 : ∀ r k j, q r k j ≤ 1)
    (hsum : ∀ r, ∑ k, ∑ j, q r k j = 6)
    (hE : ∀ j, γ ≤ ∑ r, ∑ k, (q r k j - 1 / 6) ^ 2) :
    ∑ r, ∑ k, ∑ j, Real.sqrt (q r k j) ≤ 18 * Real.sqrt 6 - 6 * cstar * γ := by
  have hpair : ∀ r, ∑ k, ∑ j, Real.sqrt (q r k j) ≤
      6 * Real.sqrt 6 - cstar * ∑ k, ∑ j, (q r k j - 1 / 6) ^ 2 :=
    fun r => pair_sum_bound (q r) (h0 r) (h1 r) (hsum r)
  have hle : ∑ r, ∑ k, ∑ j, Real.sqrt (q r k j) ≤
      ∑ r : Fin 3, (6 * Real.sqrt 6 - cstar * ∑ k, ∑ j, (q r k j - 1 / 6) ^ 2) :=
    Finset.sum_le_sum fun r _ => hpair r
  -- exchange the order of summation: total energy = ∑_j E(f_j) ≥ 6 γ
  have hswap : ∑ r : Fin 3, ∑ k : Fin 6, ∑ j : Fin 6, (q r k j - 1 / 6) ^ 2
      = ∑ j : Fin 6, ∑ r : Fin 3, ∑ k : Fin 6, (q r k j - 1 / 6) ^ 2 := by
    calc ∑ r : Fin 3, ∑ k : Fin 6, ∑ j : Fin 6, (q r k j - 1 / 6) ^ 2
        = ∑ r : Fin 3, ∑ j : Fin 6, ∑ k : Fin 6, (q r k j - 1 / 6) ^ 2 :=
          Finset.sum_congr rfl fun r _ => Finset.sum_comm
      _ = ∑ j : Fin 6, ∑ r : Fin 3, ∑ k : Fin 6, (q r k j - 1 / 6) ^ 2 := Finset.sum_comm
  have htot : 6 * γ ≤ ∑ r : Fin 3, ∑ k : Fin 6, ∑ j : Fin 6, (q r k j - 1 / 6) ^ 2 := by
    rw [hswap]
    calc 6 * γ = ∑ _j : Fin 6, γ := by simp
      _ ≤ ∑ j : Fin 6, ∑ r : Fin 3, ∑ k : Fin 6, (q r k j - 1 / 6) ^ 2 :=
          Finset.sum_le_sum fun j _ => hE j
  have hexp : ∑ r : Fin 3, (6 * Real.sqrt 6 - cstar * ∑ k, ∑ j, (q r k j - 1 / 6) ^ 2)
      = 18 * Real.sqrt 6 - cstar * ∑ r : Fin 3, ∑ k : Fin 6, ∑ j : Fin 6, (q r k j - 1 / 6) ^ 2 := by
    simp only [Finset.sum_sub_distrib, Finset.mul_sum, Finset.sum_const, Finset.card_univ,
      Fintype.card_fin, nsmul_eq_mul]
    ring
  rw [hexp] at hle
  have := mul_le_mul_of_nonneg_left htot cstar_pos.le
  linarith

/-- Numbers for the canonical product triple (certified `γ = 0.03849999999`, quoted as 0.0385). -/
theorem numbers_T0 : (0.046248 : ℝ) < Real.sqrt (0.03849999999 / 18) ∧
    (3.302e-4 : ℝ) < cstar * 0.03849999999 / 72 := by
  constructor
  · rw [show (0.046248 : ℝ) = Real.sqrt (0.046248 ^ 2) from (Real.sqrt_sq (by norm_num)).symm]
    exact Real.sqrt_lt_sqrt (by norm_num) (by norm_num)
  · rw [cstar_eq]
    have := sqrt6_bounds.1
    linarith

/-- Numbers for the second product triple (certified `γ = 0.02349999999`, quoted as 0.0235). -/
theorem numbers_T1 : (0.036132 : ℝ) < Real.sqrt (0.02349999999 / 18) ∧
    (2.015e-4 : ℝ) < cstar * 0.02349999999 / 72 := by
  constructor
  · rw [show (0.036132 : ℝ) = Real.sqrt (0.036132 ^ 2) from (Real.sqrt_sq (by norm_num)).symm]
    exact Real.sqrt_lt_sqrt (by norm_num) (by norm_num)
  · rw [cstar_eq]
    have := sqrt6_bounds.1
    linarith

end

end MUB6Bridge
#print axioms MUB6Bridge.sqrt6_sq
#print axioms MUB6Bridge.sqrt6_pos
#print axioms MUB6Bridge.sqrt6_bounds
#print axioms MUB6Bridge.cstar_pos
#print axioms MUB6Bridge.cstar_eq
#print axioms MUB6Bridge.sqrt_le_quadratic_cap
#print axioms MUB6Bridge.bias_bound
#print axioms MUB6Bridge.pair_sum_bound
#print axioms MUB6Bridge.game_bound
#print axioms MUB6Bridge.numbers_T0
#print axioms MUB6Bridge.numbers_T1
#print axioms MUB6Bridge.cstar
