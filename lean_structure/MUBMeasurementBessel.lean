module

public import MUBMeasurementProjectors

@[expose] public section
noncomputable section

namespace MUBMeasurementBessel

open Matrix MUBMeasurementProjectors
open scoped ComplexOrder

def coefficient (r : ℝ) (R : Matrix Coordinate Coordinate ℂ) (b : Fin 3) (o : Outcome) : ℂ :=
  Matrix.trace (centeredProjector r b o * R)

def reconstruction (r : ℝ) (R : Matrix Coordinate Coordinate ℂ) : Matrix Coordinate Coordinate ℂ :=
  ∑ b, ∑ o, coefficient r R b o • centeredProjector r b o

def energy (r : ℝ) (R : Matrix Coordinate Coordinate ℂ) : ℝ :=
  ∑ b, ∑ o, Complex.normSq (coefficient r R b o)

private theorem centered_hermitian (r : ℝ) (b : Fin 3) (o : Outcome) :
    (centeredProjector r b o)ᴴ = centeredProjector r b o := by
  have hp := (projector_positive r b (MUBQuantum.canonicalRelabel b o.1, o.2)).1.eq
  change (canonicalProjector r b o)ᴴ = canonicalProjector r b o at hp
  simp only [centeredProjector, Matrix.conjTranspose_sub, Matrix.conjTranspose_smul,
    Matrix.conjTranspose_one]
  change (canonicalProjector r b o)ᴴ - (star (1/6 : ℂ)) • 1 =
    canonicalProjector r b o - (1/6 : ℂ) • 1
  rw [hp]
  norm_num

private theorem centered_sum_zero (r : ℝ) (hr : r^2 = 3) (b : Fin 3) :
    (∑ o, centeredProjector r b o) = 0 := by
  simp only [centeredProjector, Finset.sum_sub_distrib, canonical_projector_complete r hr,
    ← Finset.sum_smul]
  norm_num [Outcome]

private theorem coefficient_sum_zero (r : ℝ) (hr : r^2 = 3)
    (R : Matrix Coordinate Coordinate ℂ) (b : Fin 3) :
    (∑ o, coefficient r R b o) = 0 := by
  simp only [coefficient, ← Matrix.trace_sum, ← Finset.sum_mul,
    centered_sum_zero r hr, Matrix.zero_mul, Matrix.trace_zero]

private theorem reconstruction_pairing (r : ℝ) (hr : r^2 = 3)
    (R : Matrix Coordinate Coordinate ℂ) (b : Fin 3) (o : Outcome) :
    Matrix.trace (centeredProjector r b o * reconstruction r R) = coefficient r R b o := by
  simp only [reconstruction, Finset.mul_sum, Matrix.mul_smul, Matrix.trace_sum,
    Matrix.trace_smul, smul_eq_mul, centered_projector_gram r hr]
  rw [Finset.sum_eq_single b]
  · simp only [ite_true, mul_sub, mul_ite, mul_one, mul_zero, Finset.sum_sub_distrib]
    rw [Finset.sum_ite_eq, ← Finset.sum_mul, coefficient_sum_zero r hr]
    simp
  · intro c hc hcb
    simp only [ite_eq_right (Ne.symm hcb), mul_zero, Finset.sum_const_zero]
  · simp

private theorem adjoint_coefficient (r : ℝ) (R : Matrix Coordinate Coordinate ℂ)
    (b : Fin 3) (o : Outcome) :
    Matrix.trace (Rᴴ * centeredProjector r b o) = star (coefficient r R b o) := by
  rw [coefficient, ← Matrix.trace_conjTranspose, Matrix.conjTranspose_mul,
    centered_hermitian]

private theorem reconstruction_trace (r : ℝ) (hr : r^2 = 3)
    (R : Matrix Coordinate Coordinate ℂ) :
    Matrix.trace ((reconstruction r R)ᴴ * reconstruction r R) = (energy r R : ℂ) := by
  simp only [reconstruction, Matrix.conjTranspose_sum, Matrix.conjTranspose_smul,
    centered_hermitian, Finset.sum_mul, Matrix.smul_mul, Matrix.trace_sum,
    Matrix.trace_smul, smul_eq_mul]
  change (∑ b, ∑ o, star (coefficient r R b o) *
    Matrix.trace (centeredProjector r b o * reconstruction r R)) = _
  simp only [reconstruction_pairing r hr, energy, Complex.ofReal_sum]
  apply Finset.sum_congr rfl
  intro b hb
  apply Finset.sum_congr rfl
  intro o ho
  rw [mul_comm, Complex.star_def, Complex.mul_conj]

private theorem cross_trace (r : ℝ) (R : Matrix Coordinate Coordinate ℂ) :
    Matrix.trace (Rᴴ * reconstruction r R) = (energy r R : ℂ) := by
  simp only [reconstruction, Finset.mul_sum, Matrix.mul_smul, Matrix.trace_sum,
    Matrix.trace_smul, smul_eq_mul, adjoint_coefficient, energy, Complex.ofReal_sum,
    Complex.star_def, Complex.mul_conj]

/-- An exact nonnegative-square certificate for the canonical measurement map.
The concrete centered projector Gram table is proved in the imported module.
This identity is valid even when R is not Hermitian. -/
theorem measurement_square_certificate (r : ℝ) (hr : r^2 = 3)
    (R : Matrix Coordinate Coordinate ℂ) :
    Matrix.trace ((R - reconstruction r R)ᴴ * (R - reconstruction r R)) =
      Matrix.trace (Rᴴ * R) - (energy r R : ℂ) := by
  have hc : Matrix.trace ((reconstruction r R)ᴴ * R) = (energy r R : ℂ) := by
    have hh := congrArg star (cross_trace r R)
    rw [← Matrix.trace_conjTranspose, Matrix.conjTranspose_mul,
      Matrix.conjTranspose_conjTranspose] at hh
    simpa using hh
  simp only [Matrix.conjTranspose_sub, Matrix.sub_mul, Matrix.mul_sub, Matrix.trace_sub,
    cross_trace, hc, reconstruction_trace r hr]
  ring

/-- Bessel's inequality for the actual canonical density-matrix measurements,
derived from a Gram square; it is not a premise of the formalization. -/
theorem canonical_measurement_bessel (r : ℝ) (hr : r^2 = 3)
    (R : Matrix Coordinate Coordinate ℂ) :
    energy r R ≤ (Matrix.trace (Rᴴ * R)).re := by
  have hp := (Matrix.posSemidef_conjTranspose_mul_self (R - reconstruction r R)).trace_nonneg
  rw [measurement_square_certificate r hr] at hp
  have hre := (Complex.le_def.mp hp).1
  simpa only [Complex.zero_re, Complex.sub_re, Complex.ofReal_re, sub_nonneg] using hre

/-- For a Hermitian density matrix, the centered complex coefficient is exactly
the real observable deviation from one sixth of its trace. -/
theorem hermitian_coefficient (r : ℝ) (R : Matrix Coordinate Coordinate ℂ)
    (hR : R.IsHermitian) (b : Fin 3) (o : Outcome) :
    coefficient r R b o =
      ((expectation (canonicalProjector r b o) R - (Matrix.trace R).re / 6 : ℝ) : ℂ) := by
  have hc : star (coefficient r R b o) = coefficient r R b o := by
    rw [coefficient, ← Matrix.trace_conjTranspose, Matrix.conjTranspose_mul,
      centered_hermitian, hR.eq, Matrix.trace_mul_comm]
  calc
    _ = ((coefficient r R b o).re : ℂ) := (Complex.conj_eq_iff_re.mp hc).symm
    _ = _ := by
      congr 1
      simp only [coefficient, centeredProjector, Matrix.sub_mul, Matrix.smul_mul,
        Matrix.one_mul, Matrix.trace_sub, Matrix.trace_smul, smul_eq_mul, expectation]
      norm_num [Complex.sub_re, Complex.mul_re]
      ring

/-- If R is uniform in the actual canonical measurements and S has the same
trace, the observed squared deviations of S are bounded by its squared
Frobenius distance from R. The bound is derived from the concrete Gram table. -/
theorem canonical_uniform_comparison (r : ℝ) (hr : r^2 = 3)
    (R S : Matrix Coordinate Coordinate ℂ) (hR : R.IsHermitian) (hS : S.IsHermitian)
    (htrace : Matrix.trace S = Matrix.trace R)
    (huniform : ∀ b o, expectation (canonicalProjector r b o) R = (1 : ℝ)/6) :
    (∑ b, ∑ o, (expectation (canonicalProjector r b o) S - 1/6)^2) ≤
      (Matrix.trace ((S-R)ᴴ * (S-R))).re := by
  have hU (b : Fin 3) (o : Outcome) :
      (Matrix.trace (canonicalProjector r b o * R)).re = (1 : ℝ)/6 := huniform b o
  have he : energy r (S-R) =
      ∑ b, ∑ o, (expectation (canonicalProjector r b o) S - 1/6)^2 := by
    unfold energy
    simp_rw [hermitian_coefficient r (S-R) (hS.sub hR)]
    have ht : Matrix.trace (S-R) = 0 := by rw [Matrix.trace_sub, htrace, sub_self]
    simp only [expectation, Matrix.mul_sub, Matrix.trace_sub, Complex.sub_re,
      ht, Complex.zero_re, zero_div, sub_zero, Complex.normSq_ofReal]
    change (∑ b, ∑ o, (expectation (canonicalProjector r b o) S -
      expectation (canonicalProjector r b o) R) *
      (expectation (canonicalProjector r b o) S - expectation (canonicalProjector r b o) R)) = _
    simp only [pow_two, expectation, hU]
  rw [← he]
  exact canonical_measurement_bessel r hr (S-R)

end MUBMeasurementBessel
