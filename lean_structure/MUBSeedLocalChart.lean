module
public import MUBSeedDifferential
public import Mathlib.Analysis.Calculus.Implicit
public import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
public import Mathlib.LinearAlgebra.Complex.FiniteDimensional
@[expose] public section
noncomputable section
namespace MUBSeedLocalChart
open Matrix MUBSunCubeGram MUBUniformSubmersion MUBSeedDifferential
open Filter
open scoped Topology
set_option maxHeartbeats 4000000

def packAngles (x : Fin 4 → ℝ) : AngleSpace :=
  ![x 0,x 1,-x 0-x 1,x 2,x 3,-x 2-x 3]

def angleCoordinates : (Fin 4 → ℝ) ≃ₗ[ℝ] angleDomain where
  toFun x := ⟨packAngles x,by constructor <;> simp [packAngles]⟩
  invFun theta := ![(theta : AngleSpace) 0,(theta : AngleSpace) 1,
    (theta : AngleSpace) 3,(theta : AngleSpace) 4]
  left_inv x := by ext j; fin_cases j <;> rfl
  right_inv theta := by
    apply Subtype.ext
    ext j
    have h0 := theta.property.1
    have h1 := theta.property.2
    fin_cases j <;> norm_num [packAngles] <;> linarith
  map_add' x y := by apply Subtype.ext; ext j; fin_cases j <;> simp [packAngles] <;> ring
  map_smul' c x := by apply Subtype.ext; ext j; fin_cases j <;> simp [packAngles] <;> ring

theorem angle_domain_finrank : Module.finrank ℝ angleDomain = 4 := by
  simpa using angleCoordinates.finrank_eq.symm

theorem actual_derivative_range (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    (seedDifferential u v).range = ⊤ :=
  LinearMap.range_eq_top.mpr (actual_seed_differential_surjective u v hu hv hunit)

theorem actual_kernel_finrank (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    Module.finrank ℝ (seedDifferential u v).ker = 2 := by
  have h := (seedDifferential u v).toLinearMap.finrank_range_add_finrank_ker
  have hr := actual_derivative_range u v hu hv hunit
  change Module.finrank ℝ (seedDifferential u v).range +
    Module.finrank ℝ (seedDifferential u v).ker = Module.finrank ℝ angleDomain at h
  rw [hr,angle_domain_finrank] at h
  norm_num [Complex.finrank_real_complex] at h
  omega

noncomputable instance : CompleteSpace angleDomain := FiniteDimensional.complete ℝ angleDomain

def seedChart (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    OpenPartialHomeomorph angleDomain (ℂ × (seedDifferential u v).ker) :=
  (seed_hasStrictFDerivAt u v).implicitToOpenPartialHomeomorph
    (seedEquation u v) (seedDifferential u v) (actual_derivative_range u v hu hv hunit)

theorem actual_chart_source (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    (0 : angleDomain) ∈ (seedChart u v hu hv hunit).source :=
  (seed_hasStrictFDerivAt u v).mem_implicitToOpenPartialHomeomorph_source _

theorem actual_chart_origin (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    seedChart u v hu hv hunit 0 = (0,0) := by
  simp [seedChart,actual_seed_zero u v hu hv hunit]

theorem actual_chart_first_coordinate (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) (theta : angleDomain) :
    (seedChart u v hu hv hunit theta).1 = seedEquation u v theta := by
  simp [seedChart]

theorem actual_chart_target_origin (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    (0,0) ∈ (seedChart u v hu hv hunit).target := by
  have h := (seedChart u v hu hv hunit).map_source (actual_chart_source u v hu hv hunit)
  simpa only [actual_chart_origin u v hu hv hunit] using h

theorem actual_zero_set_chart (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix))
    (theta : angleDomain) (htheta : theta ∈ (seedChart u v hu hv hunit).source) :
    seedEquation u v theta = 0 ↔
      ∃ k : (seedDifferential u v).ker, (0,k) ∈ (seedChart u v hu hv hunit).target ∧
        (seedChart u v hu hv hunit).symm (0,k) = theta := by
  let e := seedChart u v hu hv hunit
  constructor
  · intro hzero
    have he : (0,(e theta).2) = e theta := by
      ext
      · simpa only [e,actual_chart_first_coordinate] using hzero.symm
      · rfl
    refine ⟨(e theta).2,?_,?_⟩
    · change (0,(e theta).2) ∈ e.target
      rw [he]
      exact e.map_source htheta
    · change e.symm (0,(e theta).2)=theta
      rw [he]
      exact e.left_inv htheta
  · rintro ⟨k,hk,he⟩
    rw [← he,← actual_chart_first_coordinate u v hu hv hunit]
    rw [(seedChart u v hu hv hunit).right_inv hk]

theorem actual_eventual_zero_set_chart (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    ∀ᶠ theta : angleDomain in 𝓝 0, seedEquation u v theta = 0 ↔
      ∃ k : (seedDifferential u v).ker, (0,k) ∈ (seedChart u v hu hv hunit).target ∧
        (seedChart u v hu hv hunit).symm (0,k) = theta := by
  filter_upwards [(seedChart u v hu hv hunit).open_source.mem_nhds
    (actual_chart_source u v hu hv hunit)] with theta htheta
  exact actual_zero_set_chart u v hu hv hunit theta htheta

theorem actual_implicit_function_strict_derivative (u v : Triple)
    (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    HasStrictFDerivAt ((seed_hasStrictFDerivAt u v).implicitFunction
      (seedEquation u v) (seedDifferential u v) (actual_derivative_range u v hu hv hunit) 0)
      (seedDifferential u v).ker.subtypeL 0 := by
  simpa only [actual_seed_zero u v hu hv hunit] using
    (seed_hasStrictFDerivAt u v).to_implicitFunction (actual_derivative_range u v hu hv hunit)

end MUBSeedLocalChart
