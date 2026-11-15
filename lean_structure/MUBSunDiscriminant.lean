module
public import MUBUniformSubmersion
public import MUBSunCubeSpectrum
public import MUBResidual
@[expose] public section
noncomputable section
namespace MUBSunDiscriminant
open Matrix MUBSunCubeGram MUBUniformSubmersion

set_option maxHeartbeats 4000000

theorem ratio_product (u : Triple) (hu : UnitTriple u) :
    ratios u 0 * ratios u 1 * ratios u 2 = 1 := by
  calc
    _ = (u 0*(starRingEnd ℂ) (u 0)) * (u 1*(starRingEnd ℂ) (u 1)) *
          (u 2*(starRingEnd ℂ) (u 2)) := by simp [ratios]; ring
    _ = _ := by rw [hu 0,hu 1,hu 2]; ring

theorem ratio_second_symmetric (u : Triple) (hu : UnitTriple u) :
    ratios u 0 * ratios u 1 + ratios u 1 * ratios u 2 + ratios u 2 * ratios u 0 =
      (starRingEnd ℂ) (gamma u) := by
  have hs := ratio_square_sum u hu
  have hg : ratios u 0 + ratios u 1 + ratios u 2 = gamma u := rfl
  rw [← hg] at hs ⊢
  linear_combination -hs/2

def vandermonde (u : Triple) : ℂ :=
  (ratios u 0-ratios u 1)*(ratios u 0-ratios u 2)*(ratios u 1-ratios u 2)

theorem vandermonde_square (u : Triple) (hu : UnitTriple u) :
    vandermonde u ^ 2 = (gamma u)^2*((starRingEnd ℂ) (gamma u))^2 -
      4*((starRingEnd ℂ) (gamma u))^3 - 4*(gamma u)^3 - 27 +
      18*gamma u*(starRingEnd ℂ) (gamma u) := by
  let a := ratios u 0
  let b := ratios u 1
  let c := ratios u 2
  have hd : ((a-b)*(a-c)*(b-c))^2 =
      (a+b+c)^2*(a*b+b*c+c*a)^2-4*(a*b+b*c+c*a)^3-
      4*(a+b+c)^3*(a*b*c)-27*(a*b*c)^2+18*(a+b+c)*(a*b+b*c+c*a)*(a*b*c) := by ring
  change vandermonde u ^ 2 = _ at hd
  have hg : a+b+c = gamma u := rfl
  have he : a*b+b*c+c*a = (starRingEnd ℂ) (gamma u) := ratio_second_symmetric u hu
  have hp : a*b*c = 1 := ratio_product u hu
  rw [hg,he,hp] at hd
  simpa using hd

theorem vandermonde_conjugate (u : Triple) (hu : UnitTriple u) :
    (starRingEnd ℂ) (vandermonde u) = -vandermonde u := by
  let a := ratios u 0
  let b := ratios u 1
  let c := ratios u 2
  have ha : a*(starRingEnd ℂ) a = 1 := ratio_unit u hu 0
  have hb : b*(starRingEnd ℂ) b = 1 := ratio_unit u hu 1
  have hc : c*(starRingEnd ℂ) c = 1 := ratio_unit u hu 2
  have pair (x y : ℂ) (hx : x*(starRingEnd ℂ) x = 1)
      (hy : y*(starRingEnd ℂ) y = 1) :
      x*y*((starRingEnd ℂ) x-(starRingEnd ℂ) y) = y-x := by
    linear_combination y*hx-x*hy
  have hab := pair a b ha hb
  have hac := pair a c ha hc
  have hbc := pair b c hb hc
  have hp : a*b*c = 1 := ratio_product u hu
  have he : (a*b*c)^2*(starRingEnd ℂ) (vandermonde u) = -vandermonde u := by
    change (a*b*c)^2*(starRingEnd ℂ) ((a-b)*(a-c)*(b-c)) = -((a-b)*(a-c)*(b-c))
    simp only [map_mul,map_sub]
    calc
      _ = (a*b*((starRingEnd ℂ) a-(starRingEnd ℂ) b))*
          (a*c*((starRingEnd ℂ) a-(starRingEnd ℂ) c))*
          (b*c*((starRingEnd ℂ) b-(starRingEnd ℂ) c)) := by ring
      _ = _ := by rw [hab,hac,hbc]; ring
  simpa [hp] using he

theorem actual_discriminant_slack (u : Triple) (hu : UnitTriple u) :
    Complex.normSq (vandermonde u) =
      27-18*q u-(q u)^2+8*((gamma u)^3).re := by
  have hn := Complex.mul_conj (vandermonde u)
  rw [vandermonde_conjugate u hu] at hn
  have hd := vandermonde_square u hu
  have hq := Complex.mul_conj (gamma u)
  change gamma u*(starRingEnd ℂ) (gamma u) = (q u : ℂ) at hq
  have hqq : (gamma u)^2*((starRingEnd ℂ) (gamma u))^2 = (q u : ℂ)^2 := by
    rw [← mul_pow,hq]
  rw [hqq,mul_assoc (18 : ℂ),hq] at hd
  have hc : (Complex.normSq (vandermonde u) : ℂ) =
      27-18*(q u : ℂ)-(q u : ℂ)^2+
        4*((gamma u)^3+(starRingEnd ℂ) ((gamma u)^3)) := by
    rw [map_pow]
    linear_combination -hn-hd
  have hr := congrArg Complex.re hc
  norm_num [← Complex.ofReal_pow] at hr
  have hh : (((starRingEnd ℂ) (gamma u))^3).re = ((gamma u)^3).re := by
    rw [← map_pow]
    rfl
  rw [hh] at hr
  linarith

theorem actual_parameter_quadratic_bound (u v : Triple)
    (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    (q u)^2+18*q u ≤ 27 := by
  have hgu := correlation_from_unitarity u v hu hv hunit
  have hgv : gamma v = -gamma u := by linear_combination hgu
  have hqv : q v = q u := by simp [q,hgv]
  have hsu := Complex.normSq_nonneg (vandermonde u)
  have hsv := Complex.normSq_nonneg (vandermonde v)
  rw [actual_discriminant_slack u hu] at hsu
  rw [actual_discriminant_slack v hv,hqv,hgv] at hsv
  have hn3 : (-gamma u)^3 = -(gamma u^3) := by ring
  rw [hn3,Complex.neg_re] at hsv
  linarith

theorem actual_parameter_stronger_bound (u v : Triple)
    (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    q u ≤ 6*Real.sqrt 3-9 := by
  have hq := actual_parameter_quadratic_bound u v hu hv hunit
  have hq0 := (actual_parameter_range u v hu hv hunit).1
  have hs := Real.sqrt_nonneg (3 : ℝ)
  have hs2 : Real.sqrt 3 ^ 2 = 3 := Real.sq_sqrt (by norm_num)
  nlinarith

theorem actual_parameter_strict_bound (u v : Triple)
    (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    q u < 3/2 := by
  have hq := actual_parameter_quadratic_bound u v hu hv hunit
  have hq0 := (actual_parameter_range u v hu hv hunit).1
  nlinarith

theorem actual_discriminant_sum (u v : Triple)
    (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    Complex.normSq (vandermonde u)+Complex.normSq (vandermonde v) =
      54-36*q u-2*(q u)^2 := by
  have hgu := correlation_from_unitarity u v hu hv hunit
  have hgv : gamma v = -gamma u := by linear_combination hgu
  have hqv : q v = q u := by simp [q,hgv]
  rw [actual_discriminant_slack u hu,actual_discriminant_slack v hv,hqv,hgv]
  have hn3 : (-gamma u)^3 = -(gamma u^3) := by ring
  rw [hn3,Complex.neg_re]
  ring

theorem actual_quadratic_boundary_iff (u v : Triple)
    (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    (q u)^2+18*q u = 27 ↔ vandermonde u = 0 ∧ vandermonde v = 0 := by
  have hs := actual_discriminant_sum u v hu hv hunit
  have hnu := Complex.normSq_nonneg (vandermonde u)
  have hnv := Complex.normSq_nonneg (vandermonde v)
  constructor
  · intro h
    constructor <;> apply Complex.normSq_eq_zero.mp <;> nlinarith
  · rintro ⟨h1,h2⟩
    rw [h1,h2] at hs
    norm_num at hs
    linarith

theorem actual_cube_gram_determinant (u v : Triple)
    (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    ((entryCube (blockMatrix u v))ᴴ * entryCube (blockMatrix u v)).det =
      (18-12*(q u : ℂ))^2*(6*(q u : ℂ))^4 := by
  have h := congrArg (fun p : Polynomial ℂ => p.eval 0)
    (MUBSunCubeSpectrum.actual_cube_characteristic_polynomial u v hu hv hunit)
  rw [Matrix.eval_charpoly] at h
  norm_num [Matrix.det_neg] at h
  rw [Matrix.det_mul,Matrix.det_conjTranspose]
  change (starRingEnd ℂ) ((entryCube (blockMatrix u v)).det) *
    (entryCube (blockMatrix u v)).det = _
  linear_combination h

theorem actual_cube_determinant_nonzero (u v : Triple)
    (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix))
    (hq : q u ≠ 0) : (entryCube (blockMatrix u v)).det ≠ 0 := by
  have hr := actual_parameter_strict_bound u v hu hv hunit
  have hleft : (18-12*(q u : ℂ)) ≠ 0 := by
    intro h
    have hh := congrArg Complex.re h
    norm_num at hh
    linarith
  have hright : 6*(q u : ℂ) ≠ 0 := mul_ne_zero (by norm_num) (by exact_mod_cast hq)
  have hd := actual_cube_gram_determinant u v hu hv hunit
  have hn : ((entryCube (blockMatrix u v))ᴴ * entryCube (blockMatrix u v)).det ≠ 0 := by
    rw [hd]
    exact mul_ne_zero (pow_ne_zero _ hleft) (pow_ne_zero _ hright)
  rw [Matrix.det_mul] at hn
  exact (mul_ne_zero_iff.mp hn).2

theorem actual_cube_full_rank (u v : Triple)
    (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix))
    (hq : q u ≠ 0) : (entryCube (blockMatrix u v)).rank = 6 := by
  simpa using Matrix.rank_of_det_ne_zero (actual_cube_determinant_nonzero u v hu hv hunit hq)

theorem actual_zero_parameter_rank_two (u v : Triple)
    (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix))
    (hq : q u = 0) : (entryCube (blockMatrix u v)).rank = 2 := by
  have hr := (actual_residual_zero_iff u v hu hv hunit).mpr hq
  apply MUBResidual.phase_cube_residual_rank_two (blockMatrix u v)
    (actual_block_entries_unit u v hu hv)
  have he (M : SixMatrix) : (18 : ℂ) • M = (18 : SixMatrix)*M := by
    ext i j
    simp [Matrix.mul_apply,Matrix.ofNat_apply,Matrix.smul_apply]
  change entryCube (blockMatrix u v)*(entryCube (blockMatrix u v))ᴴ*
    entryCube (blockMatrix u v)-(18 : ℂ) • entryCube (blockMatrix u v) = 0
  rw [he]
  exact hr

theorem actual_cube_rank_dichotomy (u v : Triple)
    (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    (entryCube (blockMatrix u v)).rank = if q u = 0 then 2 else 6 := by
  split_ifs with hq
  · exact actual_zero_parameter_rank_two u v hu hv hunit hq
  · exact actual_cube_full_rank u v hu hv hunit hq

end MUBSunDiscriminant
