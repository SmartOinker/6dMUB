import MUB6Bridge.Bases
import MUB6Bridge.FiniteSample

/-!
# Numerical corollaries, stated for bases of `ℂ^6`, and the remaining shot-count arithmetic

`Bases.lean` proves the theorem "From a vector to a basis" with a free constant `γ`. This file

* defines `gameLoss B F := 1/2 + √6/12 - gameScore B F` (the report's "game loss");
* proves `gameScore_le`: for ANY four orthonormal bases the game score is at most `1/2 + √6/12`
  (so the loss is nonnegative);
* proves `corollary_T0` and `corollary_T1`: IF every unit vector has energy at least `0.03849999999`
  (respectively `0.02349999999`) against three orthonormal bases `B`, THEN for every orthonormal basis `F`
  each vector of `F` has a squared overlap with the triple that deviates from `1/6` by more than `0.046248`
  (respectively `0.036132`), and the game loss of `(B, F)` exceeds `3.302e-4` (respectively `2.015e-4`).

What is NOT in Lean: the hypothesis itself. That the two product triples of the report satisfy the energy bounds
is the output of the interval-arithmetic checker `cert/verify.py`, not a Lean fact. "Bias" (the largest deviation
over all pairs of the four bases) is not defined in Lean; the statement proved is the existence of one deviating
overlap for every vector of `F`, which implies the bound on the bias.

* `missBound`, `faBound`, `shots_of` and the five `shots_*` statements: the arithmetic behind every shot count of
  the report's finite-sample corollary. `missBound` and `faBound` are the two closed-form expressions of the
  theorem; that they bound probabilities is NOT formalized.
* `pearson_total`, `zeta2_le`, `three_halves_le`: three more deterministic steps of the finite-sample theorem
  (Pearson's statistic as a function of the collision statistic over all three settings; two steps of the
  variance bound). The variance formula of the U-statistic and Cantelli's inequality are NOT formalized.
-/

namespace MUB6Bridge

open Finset BigOperators

noncomputable section

/-- The report's game loss: `1/2 + √6/12` minus the game score. -/
def gameLoss (B : Fin 3 → Basis6) (F : Basis6) : ℝ := 1 / 2 + Real.sqrt 6 / 12 - gameScore B F

/-- For any four orthonormal bases of `ℂ^6` the game score is at most `1/2 + √6/12`. -/
theorem gameScore_le (B : Fin 3 → Basis6) (F : Basis6) : gameScore B F ≤ 1 / 2 + Real.sqrt 6 / 12 := by
  have h1 := pairSum_le (B 0) (B 1)
  have h2 := pairSum_le (B 0) (B 2)
  have h3 := pairSum_le (B 1) (B 2)
  have h4 := pairSum_le (B 0) F
  have h5 := pairSum_le (B 1) F
  have h6 := pairSum_le (B 2) F
  unfold gameScore
  linarith

/-- The game loss is nonnegative. -/
theorem gameLoss_nonneg (B : Fin 3 → Basis6) (F : Basis6) : 0 ≤ gameLoss B F := by
  have := gameScore_le B F
  unfold gameLoss
  linarith

/-- Generic numerical form of the theorem: if `b < √(γ/18)` and `ℓ < c* γ / 72`, the deviation exceeds `b`
and the game loss exceeds `ℓ`. -/
theorem corollary_of (B : Fin 3 → Basis6) (γ b ℓ : ℝ)
    (hb : b < Real.sqrt (γ / 18)) (hℓ : ℓ < cstar * γ / 72)
    (hγ : ∀ ψ : H6, ‖ψ‖ = 1 → γ ≤ energy B ψ) (F : Basis6) :
    (∀ j, ∃ r k, b < |‖inner ℂ (B r k) (F j)‖ ^ 2 - 1 / 6|) ∧ ℓ < gameLoss B F := by
  constructor
  · intro j
    obtain ⟨r, k, h⟩ := bridge_bias B γ hγ F j
    exact ⟨r, k, lt_of_lt_of_le hb h⟩
  · have h := bridge_game B γ hγ F
    unfold gameLoss
    linarith

/-- Corollary for a triple with certified energy bound `0.03849999999` (the canonical product triple,
by the external certificate). -/
theorem corollary_T0 (B : Fin 3 → Basis6)
    (hγ : ∀ ψ : H6, ‖ψ‖ = 1 → (0.03849999999 : ℝ) ≤ energy B ψ) (F : Basis6) :
    (∀ j, ∃ r k, (0.046248 : ℝ) < |‖inner ℂ (B r k) (F j)‖ ^ 2 - 1 / 6|) ∧
      (3.302e-4 : ℝ) < gameLoss B F :=
  corollary_of B _ _ _ numbers_T0.1 numbers_T0.2 hγ F

/-- Corollary for a triple with certified energy bound `0.02349999999` (the second product triple,
by the external certificate). -/
theorem corollary_T1 (B : Fin 3 → Basis6)
    (hγ : ∀ ψ : H6, ‖ψ‖ = 1 → (0.02349999999 : ℝ) ≤ energy B ψ) (F : Basis6) :
    (∀ j, ∃ r k, (0.036132 : ℝ) < |‖inner ℂ (B r k) (F j)‖ ^ 2 - 1 / 6|) ∧
      (2.015e-4 : ℝ) < gameLoss B F :=
  corollary_of B _ _ _ numbers_T1.1 numbers_T1.2 hγ F

/-- The report's closed-form bound on the missed-detection probability (Theorem "finite-sample detection",
part (ii)): `V / (V + ((1-t) γ)^2)` with `V = (4/N) γ (1/6 + √γ) + 3/(2N(N-1))`. That this bounds a probability is
NOT formalized. -/
def missBound (γ N t : ℝ) : ℝ :=
  (4 / N * γ * (1 / 6 + Real.sqrt γ) + 3 / (2 * N * (N - 1)))
    / ((4 / N * γ * (1 / 6 + Real.sqrt γ) + 3 / (2 * N * (N - 1))) + ((1 - t) * γ) ^ 2)

/-- The report's closed-form bound on the false-alarm probability (part (i)):
`1 / (1 + (6/5) (t γ)^2 N (N-1))`. That this bounds a probability is NOT formalized. -/
def faBound (γ N t : ℝ) : ℝ := 1 / (1 + 6 / 5 * (t * γ) ^ 2 * N * (N - 1))

/-- Shot-count arithmetic, generic form: given an upper bound `s` for `√γ` and two rational inequalities,
`missBound γ N t ≤ β` and `faBound γ N t ≤ α`. -/
theorem shots_of (γ N t s β α : ℝ) (hγ : 0 < γ) (hN : 1 < N) (hβ1 : β < 1)
    (hs : Real.sqrt γ ≤ s)
    (hmiss : 4 / N * γ * (1 / 6 + s) + 3 / (2 * N * (N - 1)) ≤ β / (1 - β) * ((1 - t) * γ) ^ 2)
    (hfa : 1 ≤ α * (1 + 6 / 5 * (t * γ) ^ 2 * N * (N - 1))) :
    missBound γ N t ≤ β ∧ faBound γ N t ≤ α := by
  have hN0 : 0 < N := by linarith
  have hN1 : 0 < N - 1 := by linarith
  have hs0 : 0 ≤ Real.sqrt γ := Real.sqrt_nonneg _
  unfold missBound faBound
  set V : ℝ := 4 / N * γ * (1 / 6 + Real.sqrt γ) + 3 / (2 * N * (N - 1)) with hVdef
  have hV0 : 0 < V := by positivity
  have hD0 : 0 ≤ ((1 - t) * γ) ^ 2 := sq_nonneg _
  have hV : V ≤ 4 / N * γ * (1 / 6 + s) + 3 / (2 * N * (N - 1)) := by
    have : 4 / N * γ * (1 / 6 + Real.sqrt γ) ≤ 4 / N * γ * (1 / 6 + s) := by
      apply mul_le_mul_of_nonneg_left _ (by positivity)
      linarith
    linarith
  have h1β : 0 < 1 - β := by linarith
  constructor
  · rw [div_le_iff₀ (by positivity)]
    have h := mul_le_mul_of_nonneg_right (hV.trans hmiss) h1β.le
    have e : β / (1 - β) * ((1 - t) * γ) ^ 2 * (1 - β) = β * ((1 - t) * γ) ^ 2 := by
      field_simp
    rw [e] at h
    linarith
  · have hX : 0 < 1 + 6 / 5 * (t * γ) ^ 2 * N * (N - 1) := by
      have : 0 ≤ 6 / 5 * (t * γ) ^ 2 * N * (N - 1) := by positivity
      linarith
    rw [div_le_iff₀ hX]
    exact hfa

theorem sqrt_T0_le : Real.sqrt (0.0384999 : ℝ) ≤ 0.196214 := by
  rw [show (0.196214 : ℝ) = Real.sqrt (0.196214 ^ 2) from (Real.sqrt_sq (by norm_num)).symm]
  exact Real.sqrt_le_sqrt (by norm_num)

theorem sqrt_T1_le : Real.sqrt (0.0234999 : ℝ) ≤ 0.153297 := by
  rw [show (0.153297 : ℝ) = Real.sqrt (0.153297 ^ 2) from (Real.sqrt_sq (by norm_num)).symm]
  exact Real.sqrt_le_sqrt (by norm_num)

/-- Canonical product triple (`γ = 0.0384999`), `N = 1936`, `t = 0.38751`: miss at most 5%, false alarm at most
0.1% (the same numbers as `shots_T0` in `FiniteSample.lean`, restated with `missBound` and `faBound`). -/
theorem shots_T0_95 : missBound 0.0384999 1936 0.38751 ≤ 0.05 ∧ faBound 0.0384999 1936 0.38751 ≤ 0.001 :=
  shots_of 0.0384999 1936 0.38751 0.196214 0.05 0.001 (by norm_num) (by norm_num) (by norm_num)
    sqrt_T0_le (by norm_num) (by norm_num)

/-- Canonical product triple, `N = 5142`, `t = 0.14579`: miss at most 1%, false alarm at most 0.1%. -/
theorem shots_T0_99 : missBound 0.0384999 5142 0.14579 ≤ 0.01 ∧ faBound 0.0384999 5142 0.14579 ≤ 0.001 :=
  shots_of 0.0384999 5142 0.14579 0.196214 0.01 0.001 (by norm_num) (by norm_num) (by norm_num)
    sqrt_T0_le (by norm_num) (by norm_num)

/-- Canonical product triple, `N = 2892`, `t = 1/2` (threshold not optimized): miss at most 5%,
false alarm at most `2.7e-4`. -/
theorem shots_T0_half : missBound 0.0384999 2892 0.5 ≤ 0.05 ∧ faBound 0.0384999 2892 0.5 ≤ 0.00027 :=
  shots_of 0.0384999 2892 0.5 0.196214 0.05 0.00027 (by norm_num) (by norm_num) (by norm_num)
    sqrt_T0_le (by norm_num) (by norm_num)

/-- Energy bound `0.0234999` (second product triple and every certified Fourier-pair triple), `N = 3007`,
`t = 0.40853`: miss at most 5%, false alarm at most 0.1%. -/
theorem shots_T1_95 : missBound 0.0234999 3007 0.40853 ≤ 0.05 ∧ faBound 0.0234999 3007 0.40853 ≤ 0.001 :=
  shots_of 0.0234999 3007 0.40853 0.153297 0.05 0.001 (by norm_num) (by norm_num) (by norm_num)
    sqrt_T1_le (by norm_num) (by norm_num)

/-- Energy bound `0.0234999`, `N = 7687`, `t = 0.15978`: miss at most 1%, false alarm at most 0.1%. -/
theorem shots_T1_99 : missBound 0.0234999 7687 0.15978 ≤ 0.01 ∧ faBound 0.0234999 7687 0.15978 ≤ 0.001 :=
  shots_of 0.0234999 7687 0.15978 0.153297 0.01 0.001 (by norm_num) (by norm_num) (by norm_num)
    sqrt_T1_le (by norm_num) (by norm_num)

/-- Pearson identity summed over the three settings: with counts `n r k` summing to `N` in each setting,
Pearson's statistic equals `15 + 6 (N-1) T` with `T = ∑_r C_r - 1/2`, `C_r = ∑_k n r k (n r k - 1) / (N (N-1))`. -/
theorem pearson_total (n : Fin 3 → Fin 6 → ℝ) (N : ℝ) (hN0 : N ≠ 0) (hN1 : N ≠ 1)
    (hsum : ∀ r, ∑ k, n r k = N) :
    ∑ r, ∑ k, (n r k - N / 6) ^ 2 / (N / 6)
      = 15 + 6 * (N - 1) * ((∑ r, (∑ k, n r k * (n r k - 1)) / (N * (N - 1))) - 1 / 2) := by
  have h : ∀ r, ∑ k, (n r k - N / 6) ^ 2 / (N / 6)
      = 5 + 6 * (N - 1) * ((∑ k, n r k * (n r k - 1)) / (N * (N - 1)) - 1 / 6) :=
    fun r => pearson_eq_collision (n r) N hN0 hN1 (hsum r)
  simp only [h, Fin.sum_univ_three]
  ring

/-- Variance step: `θ (1 - θ) ≤ 1/4` (the variance of the collision indicator is at most one quarter). -/
theorem zeta2_le (θ : ℝ) : θ * (1 - θ) ≤ 1 / 4 := by nlinarith [sq_nonneg (θ - 1 / 2)]

/-- Variance step: `a^(3/2) + b^(3/2) + c^(3/2) ≤ (a+b+c)^(3/2)` for nonnegative reals, written with `x * √x`
(used with the three per-setting energies, whose sum is the energy). -/
theorem three_halves_le (a b c : ℝ) (ha : 0 ≤ a) (hb : 0 ≤ b) (hc : 0 ≤ c) :
    a * Real.sqrt a + b * Real.sqrt b + c * Real.sqrt c ≤ (a + b + c) * Real.sqrt (a + b + c) := by
  have h1 : Real.sqrt a ≤ Real.sqrt (a + b + c) := Real.sqrt_le_sqrt (by linarith)
  have h2 : Real.sqrt b ≤ Real.sqrt (a + b + c) := Real.sqrt_le_sqrt (by linarith)
  have h3 : Real.sqrt c ≤ Real.sqrt (a + b + c) := Real.sqrt_le_sqrt (by linarith)
  have e1 := mul_le_mul_of_nonneg_left h1 ha
  have e2 := mul_le_mul_of_nonneg_left h2 hb
  have e3 := mul_le_mul_of_nonneg_left h3 hc
  linarith

end

end MUB6Bridge
#print axioms MUB6Bridge.gameScore_le
#print axioms MUB6Bridge.gameLoss_nonneg
#print axioms MUB6Bridge.corollary_of
#print axioms MUB6Bridge.corollary_T0
#print axioms MUB6Bridge.corollary_T1
#print axioms MUB6Bridge.shots_of
#print axioms MUB6Bridge.sqrt_T0_le
#print axioms MUB6Bridge.sqrt_T1_le
#print axioms MUB6Bridge.missBound
#print axioms MUB6Bridge.faBound
#print axioms MUB6Bridge.gameLoss
#print axioms MUB6Bridge.shots_T0_95
#print axioms MUB6Bridge.shots_T0_99
#print axioms MUB6Bridge.shots_T0_half
#print axioms MUB6Bridge.shots_T1_95
#print axioms MUB6Bridge.shots_T1_99
#print axioms MUB6Bridge.pearson_total
#print axioms MUB6Bridge.zeta2_le
#print axioms MUB6Bridge.three_halves_le
