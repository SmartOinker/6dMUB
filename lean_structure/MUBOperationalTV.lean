module

public import MUBBridge

@[expose] public section
noncomputable section

namespace MUBOperationalTV

open MUBQuantum

/-- Half the l1 norm of a deviation vector. For equal-mass probability
vectors this is their total variation distance. -/
def variation {α : Type*} [Fintype α] (d : α → ℝ) : ℝ :=
  (∑ i, |d i|) / 2

theorem variation_nonneg {α : Type*} [Fintype α] (d : α → ℝ) :
    0 ≤ variation d := by
  exact div_nonneg (Finset.sum_nonneg fun i _ => abs_nonneg (d i)) (by norm_num)

/-- Zero total deviation bounds each coordinate by half the l1 norm. -/
theorem abs_le_variation {α : Type*} [Fintype α] (d : α → ℝ)
    (hd : ∑ i, d i = 0) (i : α) : |d i| ≤ variation d := by
  classical
  have he := Finset.sum_erase_add Finset.univ d (Finset.mem_univ i)
  have ha := Finset.sum_erase_add Finset.univ (fun j => |d j|) (Finset.mem_univ i)
  have hz : ∑ j ∈ Finset.univ.erase i, d j = -d i := by
    rw [hd] at he
    linarith
  have ht := Finset.abs_sum_le_sum_abs d (Finset.univ.erase i)
  rw [hz, abs_neg] at ht
  unfold variation
  linarith

/-- The factor two is sharp, attained by a deviation supported on two outcomes. -/
theorem energy_le_two_variation_sq {α : Type*} [Fintype α] (d : α → ℝ)
    (hd : ∑ i, d i = 0) :
    ∑ i, d i ^ 2 ≤ 2 * variation d ^ 2 := by
  have hp (i : α) : d i ^ 2 ≤ variation d * |d i| := by
    have h := mul_le_mul_of_nonneg_right (abs_le_variation d hd i) (abs_nonneg (d i))
    nlinarith [sq_abs (d i)]
  have hs := Finset.sum_le_sum (fun i (_ : i ∈ Finset.univ) => hp i)
  rw [← Finset.mul_sum] at hs
  unfold variation at *
  nlinarith

/-- Equal-prior success of guessing p on the event s, and q otherwise. -/
def decisionSuccess {α : Type*} [Fintype α] (p q : α → ℝ)
    (s : α → Prop) [DecidablePred s] : ℝ :=
  (∑ i, if s i then p i else q i) / 2

/-- The likelihood comparison rule achieves the exact total variation
advantage for two normalized distributions. -/
theorem likelihood_success {α : Type*} [Fintype α] (p q : α → ℝ)
    (hp : ∑ i, p i = 1) (hq : ∑ i, q i = 1) :
    decisionSuccess p q (fun i => q i ≤ p i) =
      1 / 2 + variation (fun i => p i - q i) / 2 := by
  have hi (i : α) : (if q i ≤ p i then p i else q i) =
      (p i + q i + |p i - q i|) / 2 := by
    by_cases h : q i ≤ p i
    · simp only [h, ↓reduceIte, abs_of_nonneg (sub_nonneg.mpr h)]
      ring
    · have hh : p i - q i ≤ 0 := by linarith
      simp only [h, ↓reduceIte, abs_of_nonpos hh]
      ring
  unfold decisionSuccess
  simp_rw [hi]
  rw [← Finset.sum_div, Finset.sum_add_distrib, Finset.sum_add_distrib, hp, hq]
  unfold variation
  ring

/-- The comparison rule is optimal among all deterministic decisions on the
observed outcome. Randomized rules are not formalized in this module. -/
theorem decision_success_le_likelihood {α : Type*} [Fintype α] (p q : α → ℝ)
    (s : α → Prop) [DecidablePred s] :
    decisionSuccess p q s ≤ decisionSuccess p q (fun i => q i ≤ p i) := by
  apply div_le_div_of_nonneg_right _ (by norm_num)
  apply Finset.sum_le_sum
  intro i _
  by_cases hs : s i <;> by_cases h : q i ≤ p i <;> simp [hs, h]
  linarith

abbrev Outcome := Fin 3 × Fin 2

/-- Deviations of the canonical Born probabilities from uniform measurement. -/
def canonicalDeviation (v : Coefficients) (b : Fin 3) (x : Outcome) : ℝ :=
  canonicalProbability (Real.sqrt 3) v b x.1 x.2 - 1 / 6

def canonicalTV (v : Coefficients) (b : Fin 3) : ℝ :=
  variation (canonicalDeviation v b)

theorem canonical_deviation_sum_zero (v : Coefficients)
    (hv : totalNorm v = 1) (b : Fin 3) :
    ∑ x, canonicalDeviation v b x = 0 := by
  unfold canonicalDeviation
  rw [Finset.sum_sub_distrib]
  rw [Fintype.sum_prod_type]
  rw [normalized_canonical_measurement_mass (Real.sqrt 3)
    (Real.sq_sqrt (by norm_num)) v hv b]
  norm_num

/-- Every normalized pure state has a canonical basis with strictly separated
measurement statistics. This is the exact square of the threshold
deduced from the previously proved energy gap. -/
theorem canonical_TV_sq_witness (v : Coefficients) (hv : totalNorm v = 1) :
    ∃ b : Fin 3, (1 : ℝ) / 432 < canonicalTV v b ^ 2 := by
  by_contra h
  have hb : ∀ b : Fin 3, canonicalTV v b ^ 2 ≤ 1 / 432 := by
    simpa only [not_exists, not_lt] using h
  have he (b : Fin 3) :
      ∑ x, canonicalDeviation v b x ^ 2 ≤ 1 / 216 := by
    have hh := energy_le_two_variation_sq (canonicalDeviation v b)
      (canonical_deviation_sum_zero v hv b)
    change (∑ x, canonicalDeviation v b x ^ 2) ≤ 2 * canonicalTV v b ^ 2 at hh
    nlinarith [hb b]
  have hs := Finset.sum_le_sum (fun b (_ : b ∈ Finset.univ) => he b)
  have hg := MUBBridge.canonical_probability_gap v hv
  simp only [canonicalDeviation, Fintype.sum_prod_type] at hs
  norm_num at hs
  norm_num at hg
  linarith

theorem canonical_TV_witness (v : Coefficients) (hv : totalNorm v = 1) :
    ∃ b : Fin 3, 1 / (12 * Real.sqrt 3) < canonicalTV v b := by
  obtain ⟨b, hb⟩ := canonical_TV_sq_witness v hv
  refine ⟨b, ?_⟩
  have hpos : 0 < Real.sqrt 3 := Real.sqrt_pos.mpr (by norm_num)
  have hsq : Real.sqrt 3 ^ 2 = 3 := Real.sq_sqrt (by norm_num)
  have ht : (1 / (12 * Real.sqrt 3) : ℝ) ^ 2 = 1 / 432 := by
    field_simp
    nlinarith
  have hn : 0 ≤ canonicalTV v b := variation_nonneg _
  have hc : 0 ≤ (1 / (12 * Real.sqrt 3) : ℝ) := by positivity
  nlinarith

/-- A convenient purely rational operational separation. -/
theorem canonical_TV_rational_witness (v : Coefficients) (hv : totalNorm v = 1) :
    ∃ b : Fin 3, (1 : ℝ) / 21 < canonicalTV v b := by
  obtain ⟨b, hb⟩ := canonical_TV_sq_witness v hv
  refine ⟨b, ?_⟩
  have hn : 0 ≤ canonicalTV v b := variation_nonneg _
  nlinarith

/-- Born probabilities used in the operational witness are nonnegative. -/
theorem canonical_probability_nonneg (v : Coefficients) (b : Fin 3) (x : Outcome) :
    0 ≤ canonicalProbability (Real.sqrt 3) v b x.1 x.2 := by
  unfold canonicalProbability
  apply div_nonneg (Complex.normSq_nonneg _)
  split_ifs <;> norm_num

/-- For every normalized pure state, one canonical basis distinguishes its
Born outcome distribution from uniform with equal-prior success strictly
greater than 1/2 + 1/(24 sqrt(3)). The basis may depend on the state. -/
theorem canonical_distinguishing_witness (v : Coefficients) (hv : totalNorm v = 1) :
    ∃ b : Fin 3,
      1 / 2 + 1 / (24 * Real.sqrt 3) <
        decisionSuccess
          (fun x : Outcome => canonicalProbability (Real.sqrt 3) v b x.1 x.2)
          (fun _ => (1 : ℝ) / 6)
          (fun x => 1 / 6 ≤ canonicalProbability (Real.sqrt 3) v b x.1 x.2) := by
  obtain ⟨b, hb⟩ := canonical_TV_witness v hv
  refine ⟨b, ?_⟩
  have hp : (∑ x : Outcome, canonicalProbability (Real.sqrt 3) v b x.1 x.2) = 1 := by
    rw [Fintype.sum_prod_type]
    exact normalized_canonical_measurement_mass (Real.sqrt 3)
      (Real.sq_sqrt (by norm_num)) v hv b
  have hq : (∑ _ : Outcome, (1 : ℝ) / 6) = 1 := by norm_num
  rw [likelihood_success _ _ hp hq]
  change 1 / 2 + 1 / (24 * Real.sqrt 3) < 1 / 2 + canonicalTV v b / 2
  have hscale : (1 / (24 * Real.sqrt 3) : ℝ) = (1 / (12 * Real.sqrt 3)) / 2 := by
    ring
  rw [hscale]
  linarith

#print axioms variation_nonneg
#print axioms abs_le_variation
#print axioms energy_le_two_variation_sq
#print axioms likelihood_success
#print axioms decision_success_le_likelihood
#print axioms canonical_deviation_sum_zero
#print axioms canonical_TV_sq_witness
#print axioms canonical_TV_witness
#print axioms canonical_TV_rational_witness
#print axioms canonical_probability_nonneg
#print axioms canonical_distinguishing_witness

end MUBOperationalTV

