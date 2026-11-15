import Mathlib.Analysis.InnerProductSpace.PiL2
import MUB6Bridge.BridgeLemma

/-!
# From a vector to a basis, for orthonormal bases of `ℂ^6` (report, Theorem "From a vector to a basis")

`BridgeLemma.lean` proves the theorem for arrays of real numbers. This file supplies the step from orthonormal bases
to arrays (squared overlaps lie in `[0,1]`; the 36 squared overlaps of two orthonormal bases sum to 6, by
Parseval) and states the theorem for bases of `EuclideanSpace ℂ (Fin 6)`.

* `energy B ψ`     : `∑_{r,k} (|⟨B r k, ψ⟩|^2 - 1/6)^2`, the energy of `ψ` against the three bases `B 0, B 1, B 2`.
* `pairSum e g`    : `∑_{i,j} |⟨e i, g j⟩|`.
* `gameScore B F`  : `1/2 + (1/72) * (average of pairSum over the six pairs among B 0, B 1, B 2, F)`, the score of
                     the four-basis random-access-code game (the formula for one pair is cited in the report).

Main statements:
* `bridge_bias` : if every unit vector has energy at least `γ`, each vector of any orthonormal basis `F` has some
                  squared overlap with the triple deviating from `1/6` by at least `√(γ/18)`.
* `bridge_game` : under the same hypothesis, `gameScore B F ≤ 1/2 + √6/12 - c* γ/72`.
The three bases `B r` are NOT assumed mutually unbiased (the report's theorem does not assume it either).
-/

namespace MUB6Bridge

open Finset BigOperators

noncomputable section

/-- The six-dimensional complex Hilbert space. -/
abbrev H6 : Type := EuclideanSpace ℂ (Fin 6)

/-- An orthonormal basis of `ℂ^6`, indexed by `Fin 6`. -/
abbrev Basis6 : Type := OrthonormalBasis (Fin 6) ℂ H6

/-- Energy of `ψ` against three bases: `∑_{r,k} (|⟨B r k, ψ⟩|^2 - 1/6)^2`. -/
def energy (B : Fin 3 → Basis6) (ψ : H6) : ℝ :=
  ∑ r, ∑ k, (‖inner ℂ (B r k) ψ‖ ^ 2 - 1 / 6) ^ 2

/-- `∑_{i,j} |⟨e i, g j⟩|` for two bases. -/
def pairSum (e g : Basis6) : ℝ := ∑ i, ∑ j, ‖inner ℂ (e i) (g j)‖

/-- Score of the four-basis game: `1/2 + (1/72) *` the average of `pairSum` over the six pairs of bases. -/
def gameScore (B : Fin 3 → Basis6) (F : Basis6) : ℝ :=
  1 / 2 + 1 / 72 *
    ((pairSum (B 0) (B 1) + pairSum (B 0) (B 2) + pairSum (B 1) (B 2)
      + pairSum (B 0) F + pairSum (B 1) F + pairSum (B 2) F) / 6)

/-- Squared overlaps are at most one (Cauchy-Schwarz and unit norms). -/
theorem sq_overlap_le_one (e g : Basis6) (i j : Fin 6) : ‖inner ℂ (e i) (g j)‖ ^ 2 ≤ 1 := by
  have h1 : ‖inner ℂ (e i) (g j)‖ ≤ 1 := by
    have := norm_inner_le_norm (𝕜 := ℂ) (e i) (g j)
    rwa [e.norm_eq_one, g.norm_eq_one, mul_one] at this
  have h0 : 0 ≤ ‖inner ℂ (e i) (g j)‖ := norm_nonneg _
  nlinarith

/-- Parseval: the squared overlaps of one basis vector with a basis sum to one. -/
theorem sq_overlap_row_sum (e g : Basis6) (j : Fin 6) : ∑ i, ‖inner ℂ (e i) (g j)‖ ^ 2 = 1 := by
  rw [e.sum_sq_norm_inner_right (g j), g.norm_eq_one, one_pow]

/-- The 36 squared overlaps of two orthonormal bases sum to six. -/
theorem sq_overlap_total (e g : Basis6) : ∑ i, ∑ j, ‖inner ℂ (e i) (g j)‖ ^ 2 = 6 := by
  rw [Finset.sum_comm]
  simp only [sq_overlap_row_sum, Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul]
  norm_num

/-- For any two orthonormal bases, `∑ |⟨e i, g j⟩| ≤ 6 √6`. -/
theorem pairSum_le (e g : Basis6) : pairSum e g ≤ 6 * Real.sqrt 6 := by
  have h := pair_sum_bound (fun i j => ‖inner ℂ (e i) (g j)‖ ^ 2) (fun i j => by positivity)
    (fun i j => sq_overlap_le_one e g i j) (sq_overlap_total e g)
  have hnn : 0 ≤ cstar * ∑ i, ∑ j, (‖inner ℂ (e i) (g j)‖ ^ 2 - 1 / 6) ^ 2 := by
    have := cstar_pos
    positivity
  have heq : pairSum e g = ∑ i, ∑ j, Real.sqrt (‖inner ℂ (e i) (g j)‖ ^ 2) := by
    unfold pairSum
    simp only [Real.sqrt_sq (norm_nonneg _)]
  rw [heq]
  linarith

/-- Theorem "From a vector to a basis", part (a), for bases of `ℂ^6`. -/
theorem bridge_bias (B : Fin 3 → Basis6) (γ : ℝ)
    (hγ : ∀ ψ : H6, ‖ψ‖ = 1 → γ ≤ energy B ψ) (F : Basis6) (j : Fin 6) :
    ∃ r k, Real.sqrt (γ / 18) ≤ |‖inner ℂ (B r k) (F j)‖ ^ 2 - 1 / 6| := by
  have h := hγ (F j) (F.norm_eq_one j)
  unfold energy at h
  exact bias_bound (fun r k => ‖inner ℂ (B r k) (F j)‖ ^ 2) γ h

/-- The three pairs (triple basis, fourth basis) together: `∑_r pairSum (B r) F ≤ 18 √6 - 6 c* γ`. -/
theorem bridge_three_pairs (B : Fin 3 → Basis6) (γ : ℝ)
    (hγ : ∀ ψ : H6, ‖ψ‖ = 1 → γ ≤ energy B ψ) (F : Basis6) :
    pairSum (B 0) F + pairSum (B 1) F + pairSum (B 2) F ≤ 18 * Real.sqrt 6 - 6 * cstar * γ := by
  have h := game_bound (fun r k j => ‖inner ℂ (B r k) (F j)‖ ^ 2) γ (fun r k j => by positivity)
    (fun r k j => sq_overlap_le_one (B r) F k j) (fun r => sq_overlap_total (B r) F)
    (fun j => hγ (F j) (F.norm_eq_one j))
  have heq : ∀ r, pairSum (B r) F = ∑ k, ∑ j, Real.sqrt (‖inner ℂ (B r k) (F j)‖ ^ 2) := by
    intro r
    unfold pairSum
    simp only [Real.sqrt_sq (norm_nonneg _)]
  simp only [Fin.sum_univ_three] at h
  rw [heq 0, heq 1, heq 2]
  linarith

/-- Theorem "From a vector to a basis", part (b), for bases of `ℂ^6`:
the game score is at most `1/2 + √6/12 - c* γ / 72`. -/
theorem bridge_game (B : Fin 3 → Basis6) (γ : ℝ)
    (hγ : ∀ ψ : H6, ‖ψ‖ = 1 → γ ≤ energy B ψ) (F : Basis6) :
    gameScore B F ≤ 1 / 2 + Real.sqrt 6 / 12 - cstar * γ / 72 := by
  have h1 := pairSum_le (B 0) (B 1)
  have h2 := pairSum_le (B 0) (B 2)
  have h3 := pairSum_le (B 1) (B 2)
  have h4 := bridge_three_pairs B γ hγ F
  unfold gameScore
  linarith

end

end MUB6Bridge
#print axioms MUB6Bridge.sq_overlap_le_one
#print axioms MUB6Bridge.sq_overlap_row_sum
#print axioms MUB6Bridge.sq_overlap_total
#print axioms MUB6Bridge.pairSum_le
#print axioms MUB6Bridge.bridge_bias
#print axioms MUB6Bridge.bridge_three_pairs
#print axioms MUB6Bridge.bridge_game
#print axioms MUB6Bridge.energy
#print axioms MUB6Bridge.pairSum
#print axioms MUB6Bridge.gameScore
