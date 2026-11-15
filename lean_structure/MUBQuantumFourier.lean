module

public import MUBQuantum

@[expose] public section

noncomputable section

namespace MUBQuantum

def qutritCoherence (r : ℝ) (v : Coefficients) (b : Fin 3) : ℂ :=
  overlap v 0 + phase r b * overlap v 1 + star (phase r b) * overlap v 2

def marginalProbability (r : ℝ) (v : Coefficients) (b j : Fin 3) : ℝ :=
  let w := amplitude r v b j
  (Complex.normSq (w 0) + Complex.normSq (w 1)) / 3

def signedProbability (r : ℝ) (v : Coefficients) (b j : Fin 3) : ℝ :=
  let w := amplitude r v b j
  (pauliForm b w w).re / 3

/-- The pair decomposition now applies to the actual Z/X/Y Born probabilities. -/
theorem born_pair_deviation (r : ℝ) (v : Coefficients) (b j : Fin 3) (N : ℝ) :
    (∑ a, (probability r v b j a - N / 6) ^ 2) =
      (marginalProbability r v b j - N / 3) ^ 2 / 2 +
      signedProbability r v b j ^ 2 / 2 := by
  unfold probability marginalProbability signedProbability
  generalize amplitude r v b j = w
  fin_cases b <;>
    simp [Fin.sum_univ_two, pauliForm, Complex.normSq_apply,
      Complex.add_re, Complex.add_im, Complex.sub_re, Complex.sub_im,
      Complex.mul_re, Complex.mul_im, Complex.star_def, Complex.conj_re,
      Complex.conj_im, Complex.neg_re, Complex.neg_im,
      Complex.I_re, Complex.I_im] <;> ring

theorem real_phase_parseval (r : ℝ) (hr : r ^ 2 = 3) (c : ℝ) (z : ℂ) :
    (∑ j, (c + 2 * (phase r j * star z).re) ^ 2) =
      3 * c ^ 2 + 6 * Complex.normSq z := by
  simp [Fin.sum_univ_three, phase, Complex.normSq_apply, Complex.mul_re,
    Complex.star_def, Complex.conj_re, Complex.conj_im]
  ring_nf
  rw [hr]
  ring

theorem complex_three_parseval (r : ℝ) (hr : r ^ 2 = 3) (x y z : ℂ) :
    (∑ b, Complex.normSq (x + phase r b * y + star (phase r b) * z)) =
      3 * (Complex.normSq x + Complex.normSq y + Complex.normSq z) := by
  simp [Fin.sum_univ_three, phase, Complex.normSq_apply, Complex.mul_re,
    Complex.mul_im, Complex.add_re, Complex.add_im, Complex.star_def,
    Complex.conj_re, Complex.conj_im]
  ring_nf
  rw [hr]
  ring

theorem coherence_parseval (r : ℝ) (hr : r ^ 2 = 3) (v : Coefficients) :
    (∑ b, Complex.normSq (qutritCoherence r v b)) = 3 * overlapEnergy v := by
  simpa only [qutritCoherence, overlapEnergy, Fin.sum_univ_three] using
    complex_three_parseval r hr (overlap v 0) (overlap v 1) (overlap v 2)

set_option maxHeartbeats 0 in
/-- A literal Born marginal is the Fourier transform of the cyclic overlaps. -/
theorem marginal_eq_fourier (r : ℝ) (hr : r ^ 2 = 3) (v : Coefficients)
    (b j : Fin 3) :
    marginalProbability r v b j =
      (totalNorm v + 2 * (phase r j * star (qutritCoherence r v b)).re) / 3 := by
  have h3 : r ^ 3 = 3 * r := by calc
    r ^ 3 = r ^ 2 * r := by ring
    _ = 3 * r := by rw [hr]
  have h4 : r ^ 4 = 9 := by calc
    r ^ 4 = r ^ 2 * r ^ 2 := by ring
    _ = 9 := by rw [hr]; norm_num
  fin_cases b <;> fin_cases j <;>
    simp [marginalProbability, amplitude, qutritCoherence, overlap, innerQ,
      totalNorm, weight, phase, Fin.sum_univ_three, Complex.normSq_apply,
      Complex.add_re, Complex.add_im, Complex.sub_re, Complex.sub_im,
      Complex.mul_re, Complex.mul_im, Complex.star_def, Complex.conj_re,
      Complex.conj_im]
  all_goals ring_nf
  all_goals (try simp only [hr, h3, h4])
  all_goals ring

set_option maxHeartbeats 0 in
/-- The signed Z/X/Y probability is the Fourier transform of Pauli correlations. -/
theorem signed_eq_fourier (r : ℝ) (hr : r ^ 2 = 3) (v : Coefficients)
    (b j : Fin 3) :
    signedProbability r v b j =
      (imbalance v b + 2 * (phase r j * star (correlation r v b)).re) / 3 := by
  have h3 : r ^ 3 = 3 * r := by calc
    r ^ 3 = r ^ 2 * r := by ring
    _ = 3 * r := by rw [hr]
  have h4 : r ^ 4 = 9 := by calc
    r ^ 4 = r ^ 2 * r ^ 2 := by ring
    _ = 9 := by rw [hr]; norm_num
  fin_cases b <;> fin_cases j <;>
    simp [signedProbability, amplitude, correlation, imbalance, pauliForm,
      phase, Fin.sum_univ_three, Complex.normSq_apply,
      Complex.add_re, Complex.add_im, Complex.sub_re, Complex.sub_im,
      Complex.mul_re, Complex.mul_im, Complex.star_def, Complex.conj_re,
      Complex.conj_im, Complex.I_re, Complex.I_im]
  all_goals ring_nf
  all_goals (try simp only [hr, h3, h4])
  all_goals ring

theorem spectral_energy_scalars (r : ℝ) (hr : r ^ 2 = 3)
    (q t : ℂ) (a N : ℝ) :
    (∑ j : Fin 3,
      (((N + 2 * (phase r j * star q).re) / 3 - N / 3) ^ 2 / 2 +
      ((a + 2 * (phase r j * star t).re) / 3) ^ 2 / 2)) =
      Complex.normSq q / 3 + a ^ 2 / 6 + Complex.normSq t / 3 := by
  calc
    _ = (∑ j : Fin 3, (0 + 2 * (phase r j * star q).re) ^ 2) / 18 +
        (∑ j : Fin 3, (a + 2 * (phase r j * star t).re) ^ 2) / 18 := by
      simp only [Fin.sum_univ_three]
      ring
    _ = _ := by
      rw [real_phase_parseval r hr 0 q, real_phase_parseval r hr a t]
      ring

theorem basis_energy_decomposition (r : ℝ) (hr : r ^ 2 = 3)
    (v : Coefficients) (b : Fin 3) :
    (∑ j, ∑ a, (probability r v b j a - totalNorm v / 6) ^ 2) =
      Complex.normSq (qutritCoherence r v b) / 3 +
        imbalance v b ^ 2 / 6 + Complex.normSq (correlation r v b) / 3 := by
  simp_rw [born_pair_deviation, marginal_eq_fourier r hr, signed_eq_fourier r hr]
  exact spectral_energy_scalars r hr _ _ _ _

/-- The full energy identity for concrete six-dimensional measurement formulas.
No rank, spectral, or scalar-certificate assumptions appear. -/
theorem measurement_energy_decomposition (r : ℝ) (hr : r ^ 2 = 3)
    (v : Coefficients) :
    measurementEnergy r v = overlapEnergy v +
      (∑ b, imbalance v b ^ 2) / 6 +
      (∑ b, Complex.normSq (correlation r v b)) / 3 := by
  unfold measurementEnergy
  simp_rw [basis_energy_decomposition r hr]
  calc
    _ = (∑ b, Complex.normSq (qutritCoherence r v b)) / 3 +
        (∑ b, imbalance v b ^ 2) / 6 +
        (∑ b, Complex.normSq (correlation r v b)) / 3 := by
      simp only [Fin.sum_univ_three]
      ring
    _ = _ := by rw [coherence_parseval r hr]; ring

theorem normalized_measurement_energy (r : ℝ) (hr : r ^ 2 = 3)
    (v : Coefficients) (hv : totalNorm v = 1) :
    (∑ b, ∑ j, ∑ a, (probability r v b j a - 1 / 6) ^ 2) =
      overlapEnergy v + (∑ b, imbalance v b ^ 2) / 6 +
      (∑ b, Complex.normSq (correlation r v b)) / 3 := by
  simpa only [measurementEnergy, hv, one_div] using measurement_energy_decomposition r hr v

#print axioms born_pair_deviation
#print axioms real_phase_parseval
#print axioms complex_three_parseval
#print axioms coherence_parseval
#print axioms marginal_eq_fourier
#print axioms signed_eq_fourier
#print axioms spectral_energy_scalars
#print axioms basis_energy_decomposition
#print axioms measurement_energy_decomposition
#print axioms normalized_measurement_energy

end MUBQuantum
