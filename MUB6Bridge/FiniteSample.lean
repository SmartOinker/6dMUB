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
# Finite-sample detection: the deterministic steps (Problem 124, report Section "Hide and seek")

The report's Theorem "A finite-sample detection guarantee" combines
(1) the algebraic identity between Pearson's statistic and the collision statistic,
(2) the exact variance of the collision U-statistic (probability; NOT formalized here),
(3) two elementary bounds on the terms of that variance,
(4) Cantelli's inequality (probability; NOT formalized here), and
(5) arithmetic giving the shot counts.

This file formalizes (1), (3) and (5). It does not formalize any probability statement, so the theorem itself is
not Lean-verified; only these deterministic ingredients are.
-/

namespace MUB6Bridge

open Finset BigOperators

noncomputable section

/-- (1) Pearson identity for one setting: with counts `n k` summing to `N`,
`∑ (n k - N/6)^2 / (N/6) = 5 + 6 (N-1) (C - 1/6)` where `C = ∑ n k (n k - 1) / (N (N-1))`. -/
theorem pearson_eq_collision (n : Fin 6 → ℝ) (N : ℝ) (hN0 : N ≠ 0) (hN1 : N ≠ 1)
    (hsum : ∑ k, n k = N) :
    ∑ k, (n k - N / 6) ^ 2 / (N / 6)
      = 5 + 6 * (N - 1) * ((∑ k, n k * (n k - 1)) / (N * (N - 1)) - 1 / 6) := by
  have hN1' : N - 1 ≠ 0 := sub_ne_zero.mpr hN1
  have h2 : ∑ k, n k * (n k - 1) = (∑ k, n k ^ 2) - N := by
    rw [← hsum, ← Finset.sum_sub_distrib]
    refine Finset.sum_congr rfl fun k _ => ?_
    ring
  have h1 : ∑ k, (n k - N / 6) ^ 2 / (N / 6) = (6 / N) * ((∑ k, n k ^ 2) - N ^ 2 / 6) := by
    have : ∀ k, (n k - N / 6) ^ 2 / (N / 6) = (6 / N) * (n k ^ 2 - (N / 3) * n k + N ^ 2 / 36) := by
      intro k
      field_simp
      ring
    simp only [this]
    rw [← Finset.mul_sum, Finset.sum_add_distrib, Finset.sum_sub_distrib, ← Finset.mul_sum, hsum]
    simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul]
    congr 1
    push_cast
    ring
  rw [h1, h2]
  field_simp
  ring

/-- (3a) The covariance term is at most the second moment of the deviation:
`∑ p^3 - (∑ p^2)^2 ≤ ∑ p (p - 1/6)^2` for a probability vector `p`. -/
theorem zeta1_le_second_moment (p : Fin 6 → ℝ) (hsum : ∑ k, p k = 1) :
    ∑ k, p k ^ 3 - (∑ k, p k ^ 2) ^ 2 ≤ ∑ k, p k * (p k - 1 / 6) ^ 2 := by
  -- ∑ p (p - 1/6)^2 = ∑ p^3 - (1/3) ∑ p^2 + 1/36, and (θ - 1/6)^2 ≥ 0 with θ = ∑ p^2
  have hexp : ∑ k, p k * (p k - 1 / 6) ^ 2
      = ∑ k, p k ^ 3 - (1 / 3) * ∑ k, p k ^ 2 + (1 / 36) * ∑ k, p k := by
    rw [Finset.mul_sum, Finset.mul_sum, ← Finset.sum_sub_distrib, ← Finset.sum_add_distrib]
    refine Finset.sum_congr rfl fun k _ => ?_
    ring
  rw [hexp, hsum]
  nlinarith [sq_nonneg (∑ k, p k ^ 2 - 1 / 6)]

/-- (3b) `∑ p (p - 1/6)^2 ≤ ε/6 + ε^(3/2)` with `ε = ∑ (p - 1/6)^2`, written with `ε * √ε`. -/
theorem second_moment_le (p : Fin 6 → ℝ) (hsum : ∑ k, p k = 1) :
    ∑ k, p k * (p k - 1 / 6) ^ 2
      ≤ (∑ k, (p k - 1 / 6) ^ 2) / 6
        + (∑ k, (p k - 1 / 6) ^ 2) * Real.sqrt (∑ k, (p k - 1 / 6) ^ 2) := by
  set ε := ∑ k, (p k - 1 / 6) ^ 2 with hε
  have hε0 : 0 ≤ ε := Finset.sum_nonneg fun k _ => sq_nonneg _
  have hdev : ∀ k, p k - 1 / 6 ≤ Real.sqrt ε := by
    intro k
    have hk : (p k - 1 / 6) ^ 2 ≤ ε :=
      Finset.single_le_sum (f := fun k => (p k - 1 / 6) ^ 2) (fun i _ => sq_nonneg _) (Finset.mem_univ k)
    calc p k - 1 / 6 ≤ |p k - 1 / 6| := le_abs_self _
      _ = Real.sqrt ((p k - 1 / 6) ^ 2) := (Real.sqrt_sq_eq_abs _).symm
      _ ≤ Real.sqrt ε := Real.sqrt_le_sqrt hk
  have hterm : ∀ k, p k * (p k - 1 / 6) ^ 2
      ≤ (1 / 6 + Real.sqrt ε) * (p k - 1 / 6) ^ 2 := by
    intro k
    apply mul_le_mul_of_nonneg_right _ (sq_nonneg _)
    linarith [hdev k]
  calc ∑ k, p k * (p k - 1 / 6) ^ 2
      ≤ ∑ k, (1 / 6 + Real.sqrt ε) * (p k - 1 / 6) ^ 2 := Finset.sum_le_sum fun k _ => hterm k
    _ = (1 / 6 + Real.sqrt ε) * ε := by rw [← Finset.mul_sum]
    _ = ε / 6 + ε * Real.sqrt ε := by ring

/-- (5) Shot counts for the canonical product triple (`γ = 0.0384999`, `N = 1936`, threshold `t γ` with
`t = 0.38751`): missed-detection bound at most 5%, false-alarm bound at most 0.1%.
`V = (4/N) γ (1/6 + √γ) + 3/(2N(N-1))`. -/
theorem shots_T0 :
    let γ : ℝ := 0.0384999
    let N : ℝ := 1936
    let t : ℝ := 0.38751
    let V : ℝ := 4 / N * γ * (1 / 6 + Real.sqrt γ) + 3 / (2 * N * (N - 1))
    V / (V + ((1 - t) * γ) ^ 2) ≤ 0.05 ∧ 1 / (1 + 6 / 5 * (t * γ) ^ 2 * N * (N - 1)) ≤ 0.001 := by
  intro γ N t V
  have hs : Real.sqrt γ ≤ 0.196214 := by
    rw [show (0.196214 : ℝ) = Real.sqrt (0.196214 ^ 2) from (Real.sqrt_sq (by norm_num)).symm]
    exact Real.sqrt_le_sqrt (by norm_num [γ])
  have hs0 : 0 ≤ Real.sqrt γ := Real.sqrt_nonneg _
  have hV0 : 0 < V := by positivity
  have hV : V ≤ 4 / N * γ * (1 / 6 + 0.196214) + 3 / (2 * N * (N - 1)) := by
    have : 4 / N * γ * (1 / 6 + Real.sqrt γ) ≤ 4 / N * γ * (1 / 6 + 0.196214) := by
      apply mul_le_mul_of_nonneg_left _ (by norm_num [γ, N])
      linarith
    have hVdef : V = 4 / N * γ * (1 / 6 + Real.sqrt γ) + 3 / (2 * N * (N - 1)) := rfl
    linarith
  constructor
  · rw [div_le_iff₀ (by positivity)]
    have : 4 / N * γ * (1 / 6 + 0.196214) + 3 / (2 * N * (N - 1)) ≤ 0.05 / 0.95 * ((1 - t) * γ) ^ 2 := by
      norm_num [γ, N, t]
    nlinarith
  · rw [div_le_iff₀ (by positivity)]
    norm_num [γ, N, t]

end

end MUB6Bridge
#print axioms MUB6Bridge.pearson_eq_collision
#print axioms MUB6Bridge.zeta1_le_second_moment
#print axioms MUB6Bridge.second_moment_le
#print axioms MUB6Bridge.shots_T0
