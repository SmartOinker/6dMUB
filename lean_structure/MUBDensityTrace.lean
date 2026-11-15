module

public import MUBDensityGap

@[expose] public section
noncomputable section

namespace MUBDensityTrace

open Matrix MUBMeasurementProjectors MUBDensityGap
open scoped ComplexOrder

/-- A strict cubic trace deficit follows from the actual canonical operator
margin and purity one. No spectral theorem, positivity of R, or trace-gap
premise is used. This remains restricted to the canonical triple. -/
theorem canonical_density_trace_deficit (R : Matrix Coordinate Coordinate ℂ)
    (hR : R.IsHermitian) (hpurity : Matrix.trace (R * R) = 1)
    (hu : ∀ b o, expectation (canonicalProjector (Real.sqrt 3) b o) R = (1 : ℝ)/6) :
    (1 : ℝ)/144 < 1 - (Matrix.trace (R * R * R)).re := by
  let K := R * R - R * R * R - (1/144 : ℂ) • (R * R)
  have hK : K.PosSemidef := canonical_density_cubic_operator_bound R hR hpurity hu
  have hne : R ≠ 0 := by
    intro hz
    simp only [hz, Matrix.zero_mul, Matrix.trace_zero] at hpurity
    exact zero_ne_one hpurity
  obtain ⟨i,hi⟩ := Function.ne_iff.mp hne
  obtain ⟨j,hij⟩ := Function.ne_iff.mp hi
  have hv : R *ᵥ Pi.single j 1 ≠ 0 := by
    intro hz
    have hh := congrFun hz i
    rw [Matrix.mulVec_single_one] at hh
    exact hij hh
  have hp := (canonical_density_cubic_strict R hR hpurity hu (Pi.single j 1)).2 hv
  have hd : 0 < K j j := by
    simpa only [K, Pi.star_single, star_one, Matrix.mulVec_single_one,
      single_one_dotProduct, Matrix.col_apply] using hp
  have ht : 0 < Matrix.trace K := by
    exact (Finset.sum_pos_iff_of_nonneg (fun i _ => hK.diag_nonneg (i := i))).2
      ⟨j, Finset.mem_univ j, hd⟩
  have hr := (Complex.lt_def.mp ht).1
  simp only [K, Matrix.trace_sub, Matrix.trace_smul, smul_eq_mul, hpurity,
    mul_one, Complex.sub_re, Complex.one_re, Complex.zero_re] at hr
  norm_num at hr
  linarith

end MUBDensityTrace
