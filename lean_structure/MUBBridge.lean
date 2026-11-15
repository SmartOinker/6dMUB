module

public import MUBQuantumFourier
public import MUBQuantumMeasurements
public import MUBSpectral

@[expose] public section
noncomputable section

namespace MUBBridge

open MUBQuantum

theorem overlap_energy_eq (v : Coefficients) : overlapEnergy v = MUBSpectral.overlapSum v := by
  simp only [overlapEnergy, overlap, Fin.sum_univ_three]
  norm_num only [Fin.isValue, ↓reduceIte]
  change Complex.normSq (MUBSpectral.innerQ (v 1) (v 0)) +
      Complex.normSq (MUBSpectral.innerQ (v 2) (v 1)) +
      Complex.normSq (MUBSpectral.innerQ (v 0) (v 2)) = _
  rw [MUBSpectral.normSq_innerQ_swap (v 0) (v 1),
    MUBSpectral.normSq_innerQ_swap (v 1) (v 2),
    MUBSpectral.normSq_innerQ_swap (v 2) (v 0)]
  rfl

/-- The observable Bloch components agree with the reduced-frame coordinates. -/
theorem bloch_square_identity (v : Coefficients) :
    (∑ b, imbalance v b ^ 2) =
      (MUBSpectral.frameAlpha v - MUBSpectral.frameBeta v) ^ 2 +
        4 * Complex.normSq (MUBSpectral.frameCross v) := by
  simp [imbalance, pauliForm, MUBSpectral.frameAlpha, MUBSpectral.frameBeta,
    MUBSpectral.frameCross, Fin.sum_univ_three, Complex.normSq_apply,
    Complex.mul_re, Complex.mul_im, Complex.conj_re,
    Complex.conj_im, Complex.I_re, Complex.I_im]
  ring

theorem phase_normSq (r : ℝ) (hr : r ^ 2 = 3) (b : Fin 3) :
    Complex.normSq (phase r b) = 1 := by
  fin_cases b <;> norm_num [phase, Complex.normSq_apply] <;> nlinarith only [hr]

def correlationPhases (r : ℝ) (k b : Fin 3) : ℂ :=
  if k = 0 then 1 else if k = 1 then phase r b else star (phase r b)

theorem correlation_phases_unit (r : ℝ) (hr : r ^ 2 = 3) :
    ∀ k b, Complex.normSq (correlationPhases r k b) = 1 := by
  intro k b
  fin_cases k
  · simp [correlationPhases]
  · simpa [correlationPhases] using phase_normSq r hr b
  · simpa [correlationPhases, Complex.star_def] using phase_normSq r hr b

theorem correlation_eq (r : ℝ) (v : Coefficients) :
    MUBSpectral.correlation3 (correlationPhases r) v = correlation r v := by
  funext b
  simp [MUBSpectral.correlation3, MUBSpectral.phasePair, correlationPhases,
    correlation, MUBSpectral.pauli, pauliForm]

/-- Complete bridge theorem for the concrete 18 Born probabilities: only a
normalized complex state and a real square root of 3 are assumed. All scalar,
Gram, spectral, Fourier, and correlation inequalities are derived in Lean. -/
theorem normalized_born_gap (r : ℝ) (hr : r ^ 2 = 3)
    (v : Coefficients) (hv : totalNorm v = 1) :
    (1 : ℝ) / 72 < ∑ b, ∑ j, ∑ a, (probability r v b j a - 1 / 6) ^ 2 := by
  let A : ℝ := Real.sqrt (∑ b, imbalance v b ^ 2)
  have hs : 0 ≤ ∑ b, imbalance v b ^ 2 := Finset.sum_nonneg fun b _ => sq_nonneg _
  have hA : 0 ≤ A := Real.sqrt_nonneg _
  have hAsq : A ^ 2 = ∑ b, imbalance v b ^ 2 := Real.sq_sqrt hs
  have hBloch : A ^ 2 =
      (MUBSpectral.frameAlpha v - MUBSpectral.frameBeta v) ^ 2 +
      4 * Complex.normSq (MUBSpectral.frameCross v) := by
    rw [hAsq, bloch_square_identity]
  have hUnit : ∑ k, MUBSpectral.weight (v k) = 1 := hv
  have hCorr : MUBSpectral.vectorNorm (MUBSpectral.correlation3 (correlationPhases r) v) ^ 2 =
      ∑ b, Complex.normSq (correlation r v b) := by
    rw [MUBSpectral.vectorNorm_sq, correlation_eq]
  apply MUBSpectral.energy_gap_of_quantum_identities v (correlationPhases r)
    hA hBloch hUnit (correlation_phases_unit r hr)
  rw [hAsq, hCorr, ← overlap_energy_eq]
  exact normalized_measurement_energy r hr v hv

theorem no_common_unbiased_state (r : ℝ) (hr : r ^ 2 = 3)
    (v : Coefficients) (hv : totalNorm v = 1) :
    ¬ (∀ b j a, probability r v b j a = 1 / 6) := by
  intro hp
  have hg := normalized_born_gap r hr v hv
  simp only [hp, sub_self, zero_pow (by decide : 2 ≠ 0), Finset.sum_const_zero] at hg
  norm_num at hg

/-- Specializing the phase parameter removes even the square-root equation
from the theorem's assumptions: only normalization of the complex state remains. -/
theorem canonical_born_gap (v : Coefficients) (hv : totalNorm v = 1) :
    (1 : ℝ) / 72 <
      ∑ b, ∑ j, ∑ a, (probability (Real.sqrt 3) v b j a - 1 / 6) ^ 2 :=
  normalized_born_gap (Real.sqrt 3) (Real.sq_sqrt (by norm_num)) v hv

/-- The quantitative gap for the original I,F,DF qutrit measurements paired
with the Z,X,Y qubit measurements, in the explicit C=D²F state coordinates.
Normalization is the only hypothesis. Coordinate transport is proved. -/
theorem canonical_energy_gap (v : Coefficients) (hv : totalNorm v = 1) :
    (1 : ℝ) / 72 < canonicalEnergy (Real.sqrt 3) v := by
  rw [canonical_energy_eq (Real.sqrt 3) (Real.sq_sqrt (by norm_num))]
  simpa only [measurementEnergy, hv, one_div] using canonical_born_gap v hv

theorem canonical_probability_gap (v : Coefficients) (hv : totalNorm v = 1) :
    (1 : ℝ) / 72 <
      ∑ b, ∑ j, ∑ a, (canonicalProbability (Real.sqrt 3) v b j a - 1 / 6) ^ 2 := by
  simpa only [canonicalEnergy, hv, one_div] using canonical_energy_gap v hv

theorem canonical_no_unbiased_state (v : Coefficients) (hv : totalNorm v = 1) :
    ¬ (∀ b j a, canonicalProbability (Real.sqrt 3) v b j a = 1 / 6) := by
  intro hp
  have hg := canonical_probability_gap v hv
  simp only [hp, sub_self, zero_pow (by decide : 2 ≠ 0), Finset.sum_const_zero] at hg
  norm_num at hg

theorem exists_large_probability_deviation (r : ℝ) (hr : r ^ 2 = 3)
    (v : Coefficients) (hv : totalNorm v = 1) :
    ∃ b j a, (1 : ℝ) / 36 < |probability r v b j a - 1 / 6| := by
  by_contra hn
  have hbound : ∀ b j a, |probability r v b j a - 1 / 6| ≤ (1 : ℝ) / 36 := by
    intro b j a
    exact le_of_not_gt (fun h => hn ⟨b, j, a, h⟩)
  have hsq : ∀ b j a, (probability r v b j a - 1 / 6) ^ 2 ≤ ((1 : ℝ) / 36) ^ 2 := by
    intro b j a
    have h := (sq_le_sq₀ (abs_nonneg (probability r v b j a - 1 / 6))
      (by norm_num : (0 : ℝ) ≤ 1 / 36)).mpr (hbound b j a)
    simpa only [sq_abs] using h
  have henergy : (∑ b, ∑ j, ∑ a, (probability r v b j a - 1 / 6) ^ 2) ≤ (1 : ℝ) / 72 := by
    calc
      _ ≤ ∑ _b : Fin 3, ∑ _j : Fin 3, ∑ _a : Fin 2, ((1 : ℝ) / 36) ^ 2 := by
        apply Finset.sum_le_sum
        intro b _
        apply Finset.sum_le_sum
        intro j _
        exact Finset.sum_le_sum fun a _ => hsq b j a
      _ = _ := by norm_num
  exact (not_lt_of_ge henergy) (normalized_born_gap r hr v hv)

/-- The full probability-space robustness statement for the actual state.
Converting projector operator-norm distance to this hypothesis is separate. -/
theorem no_uniform_probability_perturbation (r : ℝ) (hr : r ^ 2 = 3)
    (v : Coefficients) (hv : totalNorm v = 1)
    (q : Fin 3 → Fin 3 → Fin 2 → ℝ)
    (hclose : ∀ b j a, |probability r v b j a - q b j a| ≤ (1 : ℝ) / 36) :
    ¬ (∀ b j a, q b j a = 1 / 6) := by
  intro hq
  obtain ⟨b, j, a, hlarge⟩ := exists_large_probability_deviation r hr v hv
  have hsmall := hclose b j a
  rw [hq b j a] at hsmall
  exact (not_lt_of_ge hsmall) hlarge

#print axioms overlap_energy_eq
#print axioms bloch_square_identity
#print axioms phase_normSq
#print axioms normalized_born_gap
#print axioms no_common_unbiased_state
#print axioms canonical_born_gap
#print axioms canonical_energy_gap
#print axioms canonical_probability_gap
#print axioms canonical_no_unbiased_state
#print axioms exists_large_probability_deviation
#print axioms no_uniform_probability_perturbation

end MUBBridge
