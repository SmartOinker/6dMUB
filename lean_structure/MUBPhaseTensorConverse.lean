module

public import MUBPhaseTensor

@[expose] public section
noncomputable section

namespace MUBPhaseTensorConverse

open Matrix MUBPhaseTensor

def transitionTensor (A B C : Matrix Six Six ℂ) : Tensor Six :=
  fun i k j => rootSix * A i k * C k j / B i j

private theorem rootSix_normSq : Complex.normSq rootSix = 6 := by
  simp only [rootSix, Complex.normSq_ofReal]
  exact Real.mul_self_sqrt (by norm_num)

/-- Normalized flatness alone makes the transition tensor unit-modulus. -/
theorem transition_tensor_unit (A B C : Matrix Six Six ℂ)
    (hA : ∀ i j, Complex.normSq (A i j) = (1 : ℝ) / 6)
    (hB : ∀ i j, Complex.normSq (B i j) = (1 : ℝ) / 6)
    (hC : ∀ i j, Complex.normSq (C i j) = (1 : ℝ) / 6) :
    UnitTensor (transitionTensor A B C) := by
  intro i k j
  have hn : Complex.normSq (transitionTensor A B C i k j) = 1 := by
    simp only [transitionTensor, Complex.normSq_div, Complex.normSq_mul,
      rootSix_normSq, hA, hB, hC]
    norm_num
  rw [Complex.mul_conj, hn]
  norm_num

/-- The anchored box identity is an algebraic identity for every pair-factor
tensor, independently of orthogonality or physical compatibility. -/
theorem transition_tensor_boxes (A B C : Matrix Six Six ℂ) :
    AnchoredBoxes (transitionTensor A B C) 0 := by
  intro i k j _ _ _
  simp only [transitionTensor, div_eq_mul_inv]
  ring

private theorem flat_phase_product {z : ℂ}
    (hz : Complex.normSq z = (1 : ℝ) / 6) :
    z * (starRingEnd ℂ) z = (1 : ℂ) / 6 := by
  rw [Complex.mul_conj, hz]
  norm_num

private theorem flat_tensor_entry (A B C : Matrix Six Six ℂ)
    (hB : ∀ i j, Complex.normSq (B i j) = (1 : ℝ) / 6) (i k j : Six) :
    transitionTensor A B C i k j =
      6 * rootSix * A i k * C k j * (starRingEnd ℂ) (B i j) := by
  simp only [transitionTensor, div_eq_mul_inv, Complex.inv_def, hB]
  norm_num
  ring

/-- Physical composition and unitarity give every line sum. No slice or
Gram relaxation is substituted for the ordinary matrix equations. -/
theorem transition_tensor_line_sums (A B C : Matrix Six Six ℂ)
    (hAU : A ∈ Matrix.unitaryGroup Six ℂ)
    (hCU : C ∈ Matrix.unitaryGroup Six ℂ) (hAC : A * C = B)
    (hA : ∀ i j, Complex.normSq (A i j) = (1 : ℝ) / 6)
    (hB : ∀ i j, Complex.normSq (B i j) = (1 : ℝ) / 6)
    (hC : ∀ i j, Complex.normSq (C i j) = (1 : ℝ) / 6) :
    LineSums (transitionTensor A B C) rootSix := by
  have hAl : Aᴴ * A = 1 := by
    simpa only [Matrix.star_eq_conjTranspose] using Matrix.mem_unitaryGroup_iff'.mp hAU
  have hCr : C * Cᴴ = 1 := by
    simpa only [Matrix.star_eq_conjTranspose] using Matrix.mem_unitaryGroup_iff.mp hCU
  have hAB : Aᴴ * B = C := by
    rw [← hAC, ← Matrix.mul_assoc, hAl, Matrix.one_mul]
  have hBC : B * Cᴴ = A := by
    rw [← hAC, Matrix.mul_assoc, hCr, Matrix.mul_one]
  have hk (i j : Six) : ∑ k, A i k * C k j = B i j := by
    exact congrArg (fun M : Matrix Six Six ℂ => M i j) hAC
  have hi (k j : Six) :
      ∑ i, A i k * (starRingEnd ℂ) (B i j) = (starRingEnd ℂ) (C k j) := by
    have hh : ∑ i, (starRingEnd ℂ) (A i k) * B i j = C k j :=
      congrArg (fun M : Matrix Six Six ℂ => M k j) hAB
    have hs := congrArg (starRingEnd ℂ) hh
    simpa only [map_sum, map_mul, starRingEnd_apply, star_star] using hs
  have hj (i k : Six) :
      ∑ j, C k j * (starRingEnd ℂ) (B i j) = (starRingEnd ℂ) (A i k) := by
    have hh : ∑ j, B i j * (starRingEnd ℂ) (C k j) = A i k :=
      congrArg (fun M : Matrix Six Six ℂ => M i k) hBC
    have hs := congrArg (starRingEnd ℂ) hh
    have hs' : ∑ j, (starRingEnd ℂ) (B i j) * C k j = (starRingEnd ℂ) (A i k) := by
      simpa only [map_sum, map_mul, starRingEnd_apply, star_star] using hs
    calc
      _ = ∑ j, (starRingEnd ℂ) (B i j) * C k j := by
        apply Finset.sum_congr rfl
        intro j _
        ring
      _ = _ := hs'
  refine ⟨?_, ?_, ?_⟩
  · intro i j
    calc
      _ = ∑ k, (6 * rootSix * (starRingEnd ℂ) (B i j)) * (A i k * C k j) := by
        apply Finset.sum_congr rfl
        intro k _
        rw [flat_tensor_entry A B C hB]
        ring
      _ = (6 * rootSix * (starRingEnd ℂ) (B i j)) * (∑ k, A i k * C k j) := by
        rw [Finset.mul_sum]
      _ = 6 * rootSix * (B i j * (starRingEnd ℂ) (B i j)) := by
        rw [hk]
        ring
      _ = rootSix := by rw [flat_phase_product (hB i j)]; ring
  · intro k j
    calc
      _ = ∑ i, (6 * rootSix * C k j) * (A i k * (starRingEnd ℂ) (B i j)) := by
        apply Finset.sum_congr rfl
        intro i _
        rw [flat_tensor_entry A B C hB]
        ring
      _ = (6 * rootSix * C k j) * (∑ i, A i k * (starRingEnd ℂ) (B i j)) := by
        rw [Finset.mul_sum]
      _ = 6 * rootSix * (C k j * (starRingEnd ℂ) (C k j)) := by
        rw [hi]
        ring
      _ = rootSix := by rw [flat_phase_product (hC k j)]; ring
  · intro i k
    calc
      _ = ∑ j, (6 * rootSix * A i k) * (C k j * (starRingEnd ℂ) (B i j)) := by
        apply Finset.sum_congr rfl
        intro j _
        rw [flat_tensor_entry A B C hB]
        ring
      _ = (6 * rootSix * A i k) * (∑ j, C k j * (starRingEnd ℂ) (B i j)) := by
        rw [Finset.mul_sum]
      _ = 6 * rootSix * (A i k * (starRingEnd ℂ) (A i k)) := by
        rw [hj]
        ring
      _ = rootSix := by rw [flat_phase_product (hA i k)]; ring

/-- Every physical realization satisfies the complete tensor constraints. -/
theorem physical_realization_conditions (t : Tensor Six) (A B C : Matrix Six Six ℂ)
    (hp : PhysicalRealization t A B C) :
    UnitTensor t ∧ AnchoredBoxes t 0 ∧ LineSums t rootSix := by
  rcases hp with ⟨hAU, _, hCU, hAC, hA, hB, hC, hrecover⟩
  have ht : t = transitionTensor A B C := by
    funext i k j
    exact hrecover i k j
  rw [ht]
  exact ⟨transition_tensor_unit A B C hA hB hC, transition_tensor_boxes A B C,
    transition_tensor_line_sums A B C hAU hCU hAC hA hB hC⟩

/-- Exact equivalence of the phase-tensor constraints and existence of a
compatible normalized flat-unitary realization. No global purity claim follows. -/
theorem phase_tensor_equivalence (t : Tensor Six) :
    (UnitTensor t ∧ AnchoredBoxes t 0 ∧ LineSums t rootSix) ↔
      ∃ A B C : Matrix Six Six ℂ, PhysicalRealization t A B C := by
  constructor
  · rintro ⟨hu, hb, hl⟩
    exact ⟨normalizedA t, normalizedB t, normalizedC t, phase_tensor_realization t hu hb hl⟩
  · rintro ⟨A, B, C, hp⟩
    exact physical_realization_conditions t A B C hp

#print axioms transition_tensor_unit
#print axioms transition_tensor_boxes
#print axioms transition_tensor_line_sums
#print axioms physical_realization_conditions
#print axioms phase_tensor_equivalence

end MUBPhaseTensorConverse
