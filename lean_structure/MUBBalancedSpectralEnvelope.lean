module
public import Mathlib.Analysis.SpecialFunctions.Sqrt
public import Mathlib.Tactic.Ring
public import Mathlib.Tactic.Linarith
public import Mathlib.Tactic.Positivity
@[expose] public section
noncomputable section
namespace MUBBalancedSpectralEnvelope

def upperPolynomial (r x : ℝ) : ℝ :=
  (-9+7*r)/4 + (99-47*r)*x/48 + (-57+31*r)*x^2/192 + (9-5*r)*x^3/768

theorem majorant_factorization (r y : ℝ) (hr : r^2 = 3) :
    upperPolynomial r (y^2) - y =
      (9-5*r)/768 * (y-2)^2 * (y-2*r)^2 *
        (y^2+4*(1+r)*y+16+12*r) := by
  have hr3 : r^3 = 3*r := by nlinarith [congrArg (fun t : ℝ => t*r) hr]
  have hr4 : r^4 = 9 := by nlinarith [congrArg (fun t : ℝ => t^2) hr]
  unfold upperPolynomial
  ring_nf
  rw [hr, hr3, hr4]
  ring

theorem sqrt_majorant (x : ℝ) (hx : 0 ≤ x) :
    Real.sqrt x ≤ upperPolynomial (Real.sqrt 3) x := by
  have hr := Real.sq_sqrt (show (0 : ℝ) ≤ 3 by norm_num)
  have hr0 := Real.sqrt_nonneg (3 : ℝ)
  have hc : 0 ≤ (9-5*Real.sqrt 3)/768 := by nlinarith
  have hy := Real.sqrt_nonneg x
  have hp := mul_nonneg (mul_nonneg (mul_nonneg hc (sq_nonneg (Real.sqrt x - 2)))
    (sq_nonneg (Real.sqrt x - 2*Real.sqrt 3)))
    (show 0 ≤ (Real.sqrt x)^2+4*(1+Real.sqrt 3)*Real.sqrt x+16+12*Real.sqrt 3 by positivity)
  have hf := majorant_factorization (Real.sqrt 3) (Real.sqrt x) hr
  rw [Real.sq_sqrt hx] at hf hp
  linarith

def regularDistanceConstant : ℝ := 60 - 12*Real.sqrt 5 - 8*Real.sqrt 15

theorem regular_distance_constant_gt_two : 2 < regularDistanceConstant := by
  have h5 := Real.sq_sqrt (show (0 : ℝ) ≤ 5 by norm_num)
  have h15 := Real.sq_sqrt (show (0 : ℝ) ≤ 15 by norm_num)
  have h50 := Real.sqrt_nonneg (5 : ℝ)
  have h150 := Real.sqrt_nonneg (15 : ℝ)
  have h5b : Real.sqrt 5 < 9/4 := by nlinarith
  have h15b : Real.sqrt 15 < 31/8 := by nlinarith
  unfold regularDistanceConstant
  linarith

/-- Only a scalar conversion of a separately supplied Gram-distance inequality.
This theorem does not assert the matrix norm comparison as a hypothesis-free fact. -/
theorem gram_error_scalar_gap (e : ℝ) (_he : 0 ≤ e)
    (h : Real.sqrt (160/3 : ℝ) ≤ 2*Real.sqrt 6*e + e^2) : 7/5 < e^2 := by
  have hs := Real.sq_sqrt (show (0 : ℝ) ≤ 160/3 by norm_num)
  have hs0 := Real.sqrt_nonneg (160/3 : ℝ)
  have hs6 := Real.sq_sqrt (show (0 : ℝ) ≤ 6 by norm_num)
  have hs60 := Real.sqrt_nonneg (6 : ℝ)
  have hsbound : 73/10 < Real.sqrt (160/3 : ℝ) := by nlinarith
  by_contra! hn
  have hb : 59/10 < 2*Real.sqrt 6*e := by nlinarith
  have hb2 : (2*Real.sqrt 6*e)^2 = 24*e^2 := by
    ring_nf
    rw [hs6]
    ring
  nlinarith [sq_nonneg (2*Real.sqrt 6*e - 59/10)]

end MUBBalancedSpectralEnvelope
