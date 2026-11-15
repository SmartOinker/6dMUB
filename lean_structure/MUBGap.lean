module

public import Mathlib.Basic.Real.Basic
public import Mathlib.Algebra.Order.BigOperators.Group.Finset
public import Mathlib.Tactic.Linarith
public import Mathlib.Tactic.NormNum
public import MUBIdentities

@[expose] public section

/-!
# A conditional scalar certificate for the canonical product MUB triple

The structure below records the analytic inequalities derived in
`../fourier/product_gap.md`. The main theorem checks their *algebraic consequence*.
The construction of this structure from a normalized complex quantum state is
not formalized here. In particular this file does not establish the general
dimension-six MUB conjecture.
-/

namespace MUBGap

/-- Explicit scalar assumptions; none is an added logical axiom. -/
structure ScalarCertificate (E s a lam h i j m r t : ℝ) : Prop where
  energy : E = s + a ^ 2 / 6 + t ^ 2 / 3
  overlap_nonneg : 0 ≤ s
  bloch_nonneg : 0 ≤ a
  weight_nonneg : 0 ≤ h
  main_nonneg : 0 ≤ m
  remainder_nonneg : 0 ≤ r
  correlation_nonneg : 0 ≤ t
  eigenvalue : lam = (1 - a) / 2
  rank_bound : h ^ 2 ≤ 2 * s
  rayleigh : h * (lam - h) ≤ s
  first_weight : lam - h ≤ i
  second_weight : lam - h ≤ j
  weight_sum : i + j = 1 - h
  main_bound : 2 * i * j - s ≤ m ^ 2
  remainder_bound : r ^ 2 ≤ 4 * h * (1 - h)
  reverse_triangle : m - r ≤ t

/-- A concrete witness shows that the scalar premises are consistent. This is
not asserted to be the scalar data of any particular physical state. -/
theorem scalar_certificate_consistent :
    ScalarCertificate (1 / 6) 0 1 0 0 1 0 0 0 0 := by
  constructor <;> norm_num

/-- The explicit rational scalar contradiction gives the strict gap 1/72. -/
theorem scalar_gap {E s a lam h i j m r t : ℝ}
    (c : ScalarCertificate E s a lam h i j m r t) : 1 / 72 < E := by
  by_contra hE
  have hE : E ≤ 1 / 72 := le_of_not_gt hE
  have hsE : s ≤ E := by
    nlinarith only [c.energy, sq_nonneg a, sq_nonneg t]
  have ha2 : a ^ 2 ≤ 1 / 12 := by
    nlinarith only [c.energy, c.overlap_nonneg, sq_nonneg t, hE]
  have ha : a < 29 / 100 := by
    nlinarith only [ha2, c.bloch_nonneg]
  have hlam : 71 / 200 < lam := by linarith only [c.eigenvalue, ha]
  have hlamU : lam ≤ 1 / 2 := by
    linarith only [c.eigenvalue, c.bloch_nonneg]
  have hhU : h ≤ 1 / 6 := by
    nlinarith only [c.rank_bound, hsE, hE, c.weight_nonneg]
  have hh : h < 9 / 200 := by
    by_contra hh
    have hhL : 9 / 200 ≤ h := le_of_not_gt hh
    have hc : 0 ≤ (h - 9 / 200) * (1 / 6 - h) :=
      mul_nonneg (sub_nonneg.mpr hhL) (sub_nonneg.mpr hhU)
    have hp : 0 < h * (lam - 71 / 200) :=
      mul_pos (by linarith only [hhL]) (sub_pos.mpr hlam)
    nlinarith only [hc, hp, c.rayleigh, hsE, hE, hhL]
  have hij : (lam - h) * (1 - lam) ≤ i * j := by
    have hp := mul_nonneg (sub_nonneg.mpr c.first_weight)
      (sub_nonneg.mpr c.second_weight)
    have heq := congrArg (fun x : ℝ => x * (lam - h)) c.weight_sum
    nlinarith only [hp, heq]
  have hbase : 3999 / 20000 < (lam - h) * (1 - lam) := by
    have hpos : 0 < 1 + h - lam - 71 / 200 := by
      linarith only [c.weight_nonneg, hlamU]
    have hp := mul_pos (sub_pos.mpr hlam) hpos
    nlinarith only [hp, hh]
  have hm : 31 / 50 < m := by
    nlinarith only [hij, hbase, c.main_bound, hsE, hE, c.main_nonneg]
  have hr2 : r ^ 2 < 1719 / 10000 := by
    have hp := mul_pos (sub_pos.mpr hh)
      (show 0 < 1 - 9 / 200 - h by linarith only [hh])
    nlinarith only [hp, c.remainder_bound]
  have hr : r < 83 / 200 := by
    nlinarith only [hr2, c.remainder_nonneg]
  have ht : 41 / 200 < t := by
    linarith only [c.reverse_triangle, hm, hr]
  nlinarith only [c.energy, c.overlap_nonneg, sq_nonneg a, ht,
    c.correlation_nonneg, hE]

/-- Squared deviation energy of the 18 labelled measurement outcomes. -/
noncomputable def deviationEnergy (p : Fin 18 → ℝ) : ℝ :=
  ∑ k, (p k - 1 / 6) ^ 2

/-- Uniform coordinatewise error 1/36 permits at most energy 1/72. -/
theorem energy_le_of_uniform_bound (p : Fin 18 → ℝ)
    (hp : ∀ k, |p k - 1 / 6| ≤ 1 / 36) : deviationEnergy p ≤ 1 / 72 := by
  have hsq : ∀ k, (p k - 1 / 6) ^ 2 ≤ (1 / 36 : ℝ) ^ 2 := by
    intro k
    have hl := (abs_le.mp (hp k)).1
    have hu := (abs_le.mp (hp k)).2
    nlinarith only [mul_nonneg (by linarith only [hl] :
      0 ≤ p k - 1 / 6 + 1 / 36) (by linarith only [hu] :
      0 ≤ 1 / 36 - (p k - 1 / 6))]
  calc
    deviationEnergy p ≤ ∑ _k : Fin 18, (1 / 36 : ℝ) ^ 2 :=
      Finset.sum_le_sum fun k _ => hsq k
    _ = 1 / 72 := by norm_num

/-- A gap forces at least one outcome to deviate by strictly more than 1/36. -/
theorem exists_large_deviation (p : Fin 18 → ℝ)
    (hp : 1 / 72 < deviationEnergy p) :
    ∃ k, 1 / 36 < |p k - 1 / 6| := by
  by_contra hn
  have hall : ∀ k, |p k - 1 / 6| ≤ 1 / 36 := by
    intro k
    exact le_of_not_gt (fun hk => hn ⟨k, hk⟩)
  exact (not_lt_of_ge (energy_le_of_uniform_bound p hall)) hp

/-- The scalar certificate implies a large deviation once energy is identified. -/
theorem certificate_deviation (p : Fin 18 → ℝ) {s a lam h i j m r t : ℝ}
    (c : ScalarCertificate (deviationEnergy p) s a lam h i j m r t) :
    ∃ k, 1 / 36 < |p k - 1 / 6| :=
  exists_large_deviation p (scalar_gap c)

/-- A probability-space perturbation corollary. The operator-norm-to-probability
estimate needed to apply it to projectors is an external analytic bridge. -/
theorem no_uniform_perturbation (p q : Fin 18 → ℝ)
    (hgap : 1 / 72 < deviationEnergy p)
    (hclose : ∀ k, |p k - q k| ≤ 1 / 36) :
    ¬ (∀ k, q k = 1 / 6) := by
  intro hq
  have hb : ∀ k, |p k - 1 / 6| ≤ 1 / 36 := by
    intro k
    simpa only [hq k] using hclose k
  exact (not_lt_of_ge (energy_le_of_uniform_bound p hb)) hgap

#print axioms scalar_gap
#print axioms scalar_certificate_consistent
#print axioms energy_le_of_uniform_bound
#print axioms exists_large_deviation
#print axioms certificate_deviation
#print axioms no_uniform_perturbation

end MUBGap
