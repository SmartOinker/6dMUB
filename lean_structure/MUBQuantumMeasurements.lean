module

public import MUBQuantumFourier
public import Mathlib.Analysis.Real.Sqrt

@[expose] public section
noncomputable section

namespace MUBQuantum

def outcomeAmplitude (b : Fin 3) (a : Fin 2) (w : Qubit) : ℂ :=
  if b = 0 then w a
  else if b = 1 then if a = 0 then w 0 + w 1 else w 0 - w 1
  else if a = 0 then w 0 - Complex.I * w 1 else w 0 + Complex.I * w 1

theorem probability_eq_outcome (r : ℝ) (v : Coefficients)
    (b j : Fin 3) (a : Fin 2) :
    probability r v b j a = Complex.normSq (outcomeAmplitude b a (amplitude r v b j)) /
      (if b = 0 then 3 else 6) := by
  unfold probability outcomeAmplitude
  split_ifs <;> rfl

theorem outcome_scale (b : Fin 3) (a : Fin 2) (c : ℂ) (w : Qubit) :
    outcomeAmplitude b a (fun k => c * w k) = c * outcomeAmplitude b a w := by
  unfold outcomeAmplitude
  split_ifs <;> ring

/-- Unnormalized measurement rows. Their squared row norms are three. -/
def qutritRow (r : ℝ) (b j k : Fin 3) : ℂ :=
  if k = 0 then 1 else if k = 1 then phase r j
  else star (phase r b) * star (phase r j)

def qubitRow (b : Fin 3) (a c : Fin 2) : ℂ :=
  if b = 0 then if c = a then 1 else 0
  else if c = 0 then 1
  else if b = 1 then if a = 0 then 1 else -1
  else if a = 0 then -Complex.I else Complex.I

theorem amplitude_row_formula (r : ℝ) (v : Coefficients)
    (b j : Fin 3) (a : Fin 2) :
    amplitude r v b j a = ∑ k, qutritRow r b j k * v k a := by
  simp [amplitude, qutritRow, Fin.sum_univ_three]

theorem outcome_row_formula (b : Fin 3) (a : Fin 2) (w : Qubit) :
    outcomeAmplitude b a w = ∑ c, qubitRow b a c * w c := by
  fin_cases b <;> fin_cases a <;>
    simp [outcomeAmplitude, qubitRow, Fin.sum_univ_two] <;> ring

set_option maxHeartbeats 0 in
/-- The qutrit rows are pairwise orthogonal. Dividing them by √3 gives a basis. -/
theorem qutrit_rows_orthogonal (r : ℝ) (hr : r ^ 2 = 3)
    (b j l : Fin 3) :
    (∑ k, star (qutritRow r b j k) * qutritRow r b l k) =
      if j = l then 3 else 0 := by
  have h3 : r ^ 3 = 3 * r := by calc
    r ^ 3 = r ^ 2 * r := by ring
    _ = 3 * r := by rw [hr]
  have h4 : r ^ 4 = 9 := by calc
    r ^ 4 = r ^ 2 * r ^ 2 := by ring
    _ = 9 := by rw [hr]; norm_num
  fin_cases b <;> fin_cases j <;> fin_cases l <;> apply Complex.ext <;>
    simp [qutritRow, phase, Fin.sum_univ_three, Complex.add_re,
      Complex.add_im, Complex.mul_re, Complex.mul_im, Complex.star_def,
      Complex.conj_re, Complex.conj_im]
  all_goals ring_nf
  all_goals (try simp only [hr, h3, h4])
  all_goals ring

theorem qubit_rows_orthogonal (b : Fin 3) (a d : Fin 2) :
    (∑ c, star (qubitRow b a c) * qubitRow b d c) =
      if a = d then (if b = 0 then 1 else 2) else 0 := by
  fin_cases b <;> fin_cases a <;> fin_cases d <;>
    simp [qubitRow, Fin.sum_univ_two, Complex.star_def] <;> ring

theorem joint_rows_orthogonal (r : ℝ) (hr : r ^ 2 = 3)
    (b j l : Fin 3) (a d : Fin 2) :
    (∑ k, ∑ c,
      star (qutritRow r b j k * qubitRow b a c) *
        (qutritRow r b l k * qubitRow b d c)) =
      if j = l ∧ a = d then (if b = 0 then 3 else 6) else 0 := by
  calc
    _ = (∑ k, star (qutritRow r b j k) * qutritRow r b l k) *
        (∑ c, star (qubitRow b a c) * qubitRow b d c) := by
      simp only [Fin.sum_univ_three, Fin.sum_univ_two, star_mul]
      ring
    _ = _ := by
      rw [qutrit_rows_orthogonal r hr, qubit_rows_orthogonal]
      split_ifs <;> simp_all <;> ring

theorem born_pair_sum (r : ℝ) (v : Coefficients) (b j : Fin 3) :
    (∑ a, probability r v b j a) = marginalProbability r v b j := by
  unfold probability marginalProbability
  generalize amplitude r v b j = w
  fin_cases b <;>
    simp [Fin.sum_univ_two, Complex.normSq_apply,
      Complex.add_re, Complex.add_im, Complex.sub_re, Complex.sub_im,
      Complex.mul_re, Complex.mul_im] <;> ring

theorem phase_sum_real (r : ℝ) (z : ℂ) :
    (∑ j, (phase r j * star z).re) = 0 := by
  simp [Fin.sum_univ_three, phase, Complex.mul_re, Complex.star_def,
    Complex.conj_re, Complex.conj_im]
  ring

/-- Every concrete measurement has total mass equal to the squared state norm. -/
theorem measurement_mass (r : ℝ) (hr : r ^ 2 = 3) (v : Coefficients) (b : Fin 3) :
    (∑ j, ∑ a, probability r v b j a) = totalNorm v := by
  simp_rw [born_pair_sum, marginal_eq_fourier r hr]
  calc
    _ = totalNorm v + (2 / 3) * ∑ j, (phase r j * star (qutritCoherence r v b)).re := by
      simp only [Fin.sum_univ_three]
      ring
    _ = _ := by rw [phase_sum_real]; ring

theorem normalized_measurement_mass (r : ℝ) (hr : r ^ 2 = 3)
    (v : Coefficients) (hv : totalNorm v = 1) (b : Fin 3) :
    (∑ j, ∑ a, probability r v b j a) = 1 := by
  rw [measurement_mass r hr, hv]

theorem concrete_energy_decomposition (v : Coefficients) :
    measurementEnergy (Real.sqrt 3) v = overlapEnergy v +
      (∑ b, imbalance v b ^ 2) / 6 +
      (∑ b, Complex.normSq (correlation (Real.sqrt 3) v b)) / 3 := by
  exact measurement_energy_decomposition _ (Real.sq_sqrt (by norm_num)) v

/-- Unnormalized qutrit amplitudes in the original I,F,DF bases for a state
given in C=D²F coordinates. b=0 has one Fourier normalization; b=1,2 have two. -/
def canonicalRawAmplitude (r : ℝ) (v : Coefficients) (b j : Fin 3) : Qubit :=
  let f := fun k => amplitude r v 0 k
  if b = 0 then fun a => (if j = 0 then 1 else phase r 2) * f j a
  else if b = 1 then fun a => f 0 a + star (phase r j) * phase r 2 * f 1 a +
    phase r j * phase r 2 * f 2 a
  else fun a => f 0 a + star (phase r j) * phase r 1 * f 1 a +
    phase r j * phase r 1 * f 2 a

def canonicalRelabel (b j : Fin 3) : Fin 3 :=
  if b = 0 then j
  else if b = 1 then if j = 0 then 1 else if j = 1 then 2 else 0
  else if j = 0 then 2 else if j = 1 then 1 else 0

def canonicalFactor (r : ℝ) (b j : Fin 3) : ℂ :=
  if b = 0 then if j = 0 then 1 else phase r 2
  else if b = 1 then if j = 0 then 1 + 2 * phase r 2 else 1 - phase r 2
  else if j = 0 then 1 + 2 * phase r 1 else 1 - phase r 1

def canonicalProbability (r : ℝ) (v : Coefficients) (b j : Fin 3) (a : Fin 2) : ℝ :=
  Complex.normSq (outcomeAmplitude b a (canonicalRawAmplitude r v b j)) /
    (if b = 0 then 3 else 18)

def canonicalEnergy (r : ℝ) (v : Coefficients) : ℝ :=
  ∑ b, ∑ j, ∑ a, (canonicalProbability r v b j a - totalNorm v / 6) ^ 2

set_option maxHeartbeats 0 in
/-- The original qutrit measurement amplitudes equal the Weyl amplitudes up to
an explicit scalar and an outcome permutation. -/
theorem canonical_amplitude_eq (r : ℝ) (hr : r ^ 2 = 3)
    (v : Coefficients) (b j : Fin 3) (a : Fin 2) :
    canonicalRawAmplitude r v b j a =
      canonicalFactor r b j * amplitude r v b (canonicalRelabel b j) a := by
  have h3 : r ^ 3 = 3 * r := by calc
    r ^ 3 = r ^ 2 * r := by ring
    _ = 3 * r := by rw [hr]
  have h4 : r ^ 4 = 9 := by calc
    r ^ 4 = r ^ 2 * r ^ 2 := by ring
    _ = 9 := by rw [hr]; norm_num
  fin_cases b <;> fin_cases j <;> apply Complex.ext <;>
    simp [canonicalRawAmplitude, canonicalFactor, canonicalRelabel,
      amplitude, phase, Complex.add_re, Complex.add_im, Complex.sub_re,
      Complex.sub_im, Complex.mul_re, Complex.mul_im, Complex.star_def,
      Complex.conj_re, Complex.conj_im]
  all_goals ring_nf
  all_goals (try simp only [hr, h3, h4])
  all_goals ring

theorem canonical_factor_norm (r : ℝ) (hr : r ^ 2 = 3) (b j : Fin 3) :
    Complex.normSq (canonicalFactor r b j) = if b = 0 then 1 else 3 := by
  fin_cases b <;> fin_cases j <;>
    simp [canonicalFactor, phase, Complex.normSq_apply, Complex.add_re,
      Complex.add_im, Complex.sub_re, Complex.sub_im, Complex.mul_re,
      Complex.mul_im]
  all_goals ring_nf
  all_goals (try rw [hr])
  all_goals norm_num

theorem canonical_probability_eq (r : ℝ) (hr : r ^ 2 = 3)
    (v : Coefficients) (b j : Fin 3) (a : Fin 2) :
    canonicalProbability r v b j a = probability r v b (canonicalRelabel b j) a := by
  have hamp : canonicalRawAmplitude r v b j =
      fun a => canonicalFactor r b j * amplitude r v b (canonicalRelabel b j) a := by
    funext a
    exact canonical_amplitude_eq r hr v b j a
  unfold canonicalProbability
  rw [hamp, outcome_scale, Complex.normSq_mul, canonical_factor_norm r hr,
    probability_eq_outcome]
  split_ifs <;> ring

/-- Squared-norm transport under C=D²F, expressed without a matrix wrapper.
The raw transform omits 1/√3, so its norm squares are divided by three. -/
theorem canonical_norm_transport (r : ℝ) (hr : r ^ 2 = 3) (v : Coefficients) :
    (∑ j, ∑ a, Complex.normSq (canonicalRawAmplitude r v 0 j a) / 3) =
      totalNorm v := by
  calc
    _ = ∑ j, ∑ a, canonicalProbability r v 0 j a := by
      simp [canonicalProbability, outcomeAmplitude]
    _ = ∑ j, ∑ a, probability r v 0 j a := by
      simp_rw [canonical_probability_eq r hr]
      simp [canonicalRelabel]
    _ = _ := measurement_mass r hr v 0

theorem canonical_measurement_mass (r : ℝ) (hr : r ^ 2 = 3)
    (v : Coefficients) (b : Fin 3) :
    (∑ j, ∑ a, canonicalProbability r v b j a) = totalNorm v := by
  calc
    _ = ∑ j, ∑ a, probability r v b j a := by
      simp_rw [canonical_probability_eq r hr]
      fin_cases b <;> simp [Fin.sum_univ_three, canonicalRelabel] <;> ring
    _ = _ := measurement_mass r hr v b

theorem normalized_canonical_measurement_mass (r : ℝ) (hr : r ^ 2 = 3)
    (v : Coefficients) (hv : totalNorm v = 1) (b : Fin 3) :
    (∑ j, ∑ a, canonicalProbability r v b j a) = 1 := by
  rw [canonical_measurement_mass r hr, hv]

theorem canonical_energy_eq (r : ℝ) (hr : r ^ 2 = 3) (v : Coefficients) :
    canonicalEnergy r v = measurementEnergy r v := by
  unfold canonicalEnergy measurementEnergy
  simp_rw [canonical_probability_eq r hr]
  simp only [Fin.sum_univ_three]
  simp [canonicalRelabel]
  ring

theorem canonical_energy_decomposition (r : ℝ) (hr : r ^ 2 = 3)
    (v : Coefficients) :
    canonicalEnergy r v = overlapEnergy v + (∑ b, imbalance v b ^ 2) / 6 +
      (∑ b, Complex.normSq (correlation r v b)) / 3 := by
  rw [canonical_energy_eq r hr, measurement_energy_decomposition r hr]

#print axioms probability_eq_outcome
#print axioms outcome_scale
#print axioms amplitude_row_formula
#print axioms outcome_row_formula
#print axioms qutrit_rows_orthogonal
#print axioms qubit_rows_orthogonal
#print axioms joint_rows_orthogonal
#print axioms born_pair_sum
#print axioms phase_sum_real
#print axioms measurement_mass
#print axioms normalized_measurement_mass
#print axioms concrete_energy_decomposition
#print axioms canonical_amplitude_eq
#print axioms canonical_factor_norm
#print axioms canonical_probability_eq
#print axioms canonical_norm_transport
#print axioms canonical_measurement_mass
#print axioms normalized_canonical_measurement_mass
#print axioms canonical_energy_eq
#print axioms canonical_energy_decomposition

end MUBQuantum
