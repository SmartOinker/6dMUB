module
public import MUBUniformSubmersion
public import Mathlib.Analysis.SpecialFunctions.ExpDeriv
public import Mathlib.Analysis.Calculus.FDeriv.Prod
@[expose] public section
noncomputable section
namespace MUBSeedDifferential
open Matrix MUBSunCubeGram MUBUniformSubmersion

abbrev AngleSpace := Fin 6 → ℝ

def coordinate (j : Fin 6) : AngleSpace →L[ℝ] ℂ :=
  Complex.ofRealCLM.comp (ContinuousLinearMap.proj j)

def ratioCoefficients (u v : Triple) : Fin 6 → ℂ :=
  ![ratios u 0,ratios u 1,ratios u 2,ratios v 0,ratios v 1,ratios v 2]

def rawSeedEquation (u v : Triple) (theta : AngleSpace) : ℂ :=
  ∑ j, ratioCoefficients u v j * Complex.exp (Complex.I*(theta j : ℂ))

def rawDifferential (u v : Triple) : AngleSpace →L[ℝ] ℂ :=
  ∑ j, (Complex.I*ratioCoefficients u v j) • coordinate j

set_option maxHeartbeats 4000000

theorem phase_hasStrictFDerivAt (j : Fin 6) :
    HasStrictFDerivAt (fun theta : AngleSpace => Complex.exp (Complex.I*(theta j : ℂ)))
      (Complex.I • coordinate j) 0 := by
  simpa [coordinate] using (((coordinate j).hasStrictFDerivAt (x := 0)).const_smul Complex.I).cexp

theorem raw_seed_hasStrictFDerivAt (u v : Triple) :
    HasStrictFDerivAt (rawSeedEquation u v) (rawDifferential u v) 0 := by
  have h : ∀ j ∈ (Finset.univ : Finset (Fin 6)),
      HasStrictFDerivAt (fun theta : AngleSpace => ratioCoefficients u v j *
        Complex.exp (Complex.I*(theta j : ℂ)))
        ((Complex.I*ratioCoefficients u v j) • coordinate j) 0 := by
    intro j _
    simpa [smul_smul,mul_comm] using (phase_hasStrictFDerivAt j).const_mul (ratioCoefficients u v j)
  have he : rawSeedEquation u v =
      ∑ j, (fun theta : AngleSpace => ratioCoefficients u v j *
        Complex.exp (Complex.I*(theta j : ℂ))) := by
    ext theta
    simp [rawSeedEquation]
  rw [he]
  exact HasStrictFDerivAt.sum h

def angleDomain : Submodule ℝ AngleSpace where
  carrier := {theta | MeanZeroPair theta}
  zero_mem' := by simp [MeanZeroPair]
  add_mem' := by
    intro a b ha hb
    rcases ha with ⟨ha1,ha2⟩
    rcases hb with ⟨hb1,hb2⟩
    constructor
    · change (a 0+b 0)+(a 1+b 1)+(a 2+b 2)=0
      linarith
    · change (a 3+b 3)+(a 4+b 4)+(a 5+b 5)=0
      linarith
  smul_mem' := by
    intro c a ha
    rcases ha with ⟨ha1,ha2⟩
    constructor
    · change c*a 0+c*a 1+c*a 2=0
      linear_combination c*ha1
    · change c*a 3+c*a 4+c*a 5=0
      linear_combination c*ha2

def seedEquation (u v : Triple) (theta : angleDomain) : ℂ := rawSeedEquation u v theta

def seedDifferential (u v : Triple) : angleDomain →L[ℝ] ℂ :=
  (rawDifferential u v).comp angleDomain.subtypeL

theorem seed_hasStrictFDerivAt (u v : Triple) :
    HasStrictFDerivAt (seedEquation u v) (seedDifferential u v) 0 := by
  exact (raw_seed_hasStrictFDerivAt u v).comp 0 angleDomain.subtypeL.hasStrictFDerivAt

theorem actual_seed_zero (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    seedEquation u v 0 = 0 := by
  have hg := correlation_from_unitarity u v hu hv hunit
  simpa [seedEquation,rawSeedEquation,ratioCoefficients,ratios,gamma,
    Fin.sum_univ_succ,add_assoc] using hg

theorem raw_differential_apply (u v : Triple) (theta : AngleSpace) :
    rawDifferential u v theta = Complex.I *
      ((∑ j, ratios u j*(![theta 0,theta 1,theta 2] j : ℂ))+
       (∑ j, ratios v j*(![theta 3,theta 4,theta 5] j : ℂ))) := by
  simp [rawDifferential,coordinate,ratioCoefficients,Fin.sum_univ_succ]
  ring

theorem actual_seed_differential_coefficient (u v : Triple) (theta : angleDomain) :
    ![(seedDifferential u v theta).re,(seedDifferential u v theta).im] =
      coefficientMatrix u v *ᵥ (theta : AngleSpace) := by
  have ht : ∑ j, ![(theta : AngleSpace) 0,(theta : AngleSpace) 1,(theta : AngleSpace) 2] j = 0 := by
    simpa [Fin.sum_univ_succ,add_assoc] using theta.property.1
  have hp : ∑ j, ![(theta : AngleSpace) 3,(theta : AngleSpace) 4,(theta : AngleSpace) 5] j = 0 := by
    simpa [Fin.sum_univ_succ,add_assoc] using theta.property.2
  have he : ![(theta : AngleSpace) 0,(theta : AngleSpace) 1,(theta : AngleSpace) 2,(theta : AngleSpace) 3,(theta : AngleSpace) 4,(theta : AngleSpace) 5] =
      (theta : AngleSpace) := by ext j; fin_cases j <;> rfl
  have h := coefficient_action_on_mean_zero u v
    ![(theta : AngleSpace) 0,(theta : AngleSpace) 1,(theta : AngleSpace) 2]
    ![(theta : AngleSpace) 3,(theta : AngleSpace) 4,(theta : AngleSpace) 5] ht hp
  simp only [Matrix.cons_val_zero,Matrix.cons_val_one,Matrix.cons_val_two,Matrix.head_cons,Matrix.tail_cons] at h
  rw [he] at h
  simpa only [seedDifferential,ContinuousLinearMap.comp_apply,Submodule.subtypeL_apply,
    raw_differential_apply] using h.symm

theorem actual_seed_bounded_preimage (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix))
    (eta : ℂ) :
    ∃ theta : angleDomain, seedDifferential u v theta = eta ∧
      (∑ j, (theta : AngleSpace) j^2) ≤ (2/3)*Complex.normSq eta := by
  obtain ⟨x,hx,hL,hbound⟩ := actual_bounded_mean_zero_preimage u v hu hv hunit ![eta.re,eta.im]
  let theta : angleDomain := ⟨x,hx⟩
  refine ⟨theta,?_,?_⟩
  · have h := actual_seed_differential_coefficient u v theta
    change ![(seedDifferential u v theta).re,(seedDifferential u v theta).im] =
      coefficientMatrix u v *ᵥ x at h
    rw [hL] at h
    apply Complex.ext
    · simpa using congrFun h 0
    · simpa using congrFun h 1
  · simpa [theta,Fin.sum_univ_succ,Complex.normSq_apply,pow_two] using hbound

theorem actual_seed_differential_surjective (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    Function.Surjective (seedDifferential u v) := by
  intro eta
  obtain ⟨theta,he,_⟩ := actual_seed_bounded_preimage u v hu hv hunit eta
  exact ⟨theta,he⟩

theorem actual_seed_strict_submersion (u v : Triple) (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    seedEquation u v 0 = 0 ∧
    HasStrictFDerivAt (seedEquation u v) (seedDifferential u v) 0 ∧
    Function.Surjective (seedDifferential u v) :=
  ⟨actual_seed_zero u v hu hv hunit,seed_hasStrictFDerivAt u v,
    actual_seed_differential_surjective u v hu hv hunit⟩

/-- Exact phase variation within the unit/product-one ratio torus. -/
def perturbedRatios (u : Triple) (theta : Fin 3 → ℝ) : Triple :=
  fun j => ratios u j * Complex.exp (Complex.I*(theta j : ℂ))

theorem phase_unit (t : ℝ) :
    Complex.exp (Complex.I*(t : ℂ)) *
      (starRingEnd ℂ) (Complex.exp (Complex.I*(t : ℂ))) = 1 := by
  rw [← Complex.exp_conj,← Complex.exp_add]
  simp

theorem ratio_product_one (u : Triple) (hu : UnitTriple u) :
    (ratios u 0)*(ratios u 1)*(ratios u 2) = 1 := by
  calc
    _ = (u 0*(starRingEnd ℂ) (u 0))*(u 1*(starRingEnd ℂ) (u 1))*
      (u 2*(starRingEnd ℂ) (u 2)) := by simp [ratios]; ring
    _ = _ := by rw [hu 0,hu 1,hu 2]; norm_num

theorem perturbed_ratios_unit (u : Triple) (hu : UnitTriple u) (theta : Fin 3 → ℝ) :
    UnitTriple (perturbedRatios u theta) := by
  intro j
  calc
    _ = (ratios u j*(starRingEnd ℂ) (ratios u j)) *
      (Complex.exp (Complex.I*(theta j : ℂ))*
       (starRingEnd ℂ) (Complex.exp (Complex.I*(theta j : ℂ)))) := by
        simp only [perturbedRatios,map_mul]; ring
    _ = _ := by rw [ratio_unit u hu j,phase_unit]; norm_num

theorem perturbed_ratios_product_one (u : Triple) (hu : UnitTriple u) (theta : Fin 3 → ℝ)
    (htheta : ∑ j, theta j = 0) :
    (perturbedRatios u theta 0)*(perturbedRatios u theta 1)*(perturbedRatios u theta 2) = 1 := by
  have hc : (theta 0 : ℂ)+(theta 1 : ℂ)+(theta 2 : ℂ) = 0 := by
    have he : theta 0+theta 1+theta 2 = 0 := by simpa [Fin.sum_univ_succ,add_assoc] using htheta
    exact_mod_cast he
  calc
    _ = ((ratios u 0)*(ratios u 1)*(ratios u 2))*
      (Complex.exp (Complex.I*(theta 0 : ℂ))*Complex.exp (Complex.I*(theta 1 : ℂ))*
        Complex.exp (Complex.I*(theta 2 : ℂ))) := by simp only [perturbedRatios]; ring
    _ = Complex.exp (Complex.I*((theta 0 : ℂ)+(theta 1 : ℂ)+(theta 2 : ℂ))) := by
      rw [ratio_product_one u hu,one_mul,← Complex.exp_add,← Complex.exp_add]
      congr 1
      ring
    _ = 1 := by rw [hc]; simp

theorem seed_equation_is_torus_sum (u v : Triple) (theta : angleDomain) :
    seedEquation u v theta =
      (∑ j, perturbedRatios u ![(theta : AngleSpace) 0,(theta : AngleSpace) 1,(theta : AngleSpace) 2] j)+
      (∑ j, perturbedRatios v ![(theta : AngleSpace) 3,(theta : AngleSpace) 4,(theta : AngleSpace) 5] j) := by
  simp [seedEquation,rawSeedEquation,ratioCoefficients,perturbedRatios,Fin.sum_univ_succ,add_assoc]

/-- Reconstruct a unit triple from mean-zero variations of its consecutive ratios,
keeping its zeroth phase fixed. -/
def variedTriple (u : Triple) (theta : Fin 3 → ℝ) : Triple :=
  ![u 0,u 1*Complex.exp (Complex.I*(theta 0 : ℂ)),
    u 2*Complex.exp (Complex.I*((theta 0+theta 1 : ℝ) : ℂ))]

theorem varied_triple_unit (u : Triple) (hu : UnitTriple u) (theta : Fin 3 → ℝ) :
    UnitTriple (variedTriple u theta) := by
  have h (j : Fin 3) (t : ℝ) :
      (u j*Complex.exp (Complex.I*(t : ℂ)))*
        (starRingEnd ℂ) (u j*Complex.exp (Complex.I*(t : ℂ))) = 1 := by
    calc
      _ = (u j*(starRingEnd ℂ) (u j))*(Complex.exp (Complex.I*(t : ℂ))*
        (starRingEnd ℂ) (Complex.exp (Complex.I*(t : ℂ)))) := by simp only [map_mul]; ring
      _ = _ := by rw [hu j,phase_unit]; norm_num
  intro j
  fin_cases j
  · simpa [variedTriple] using hu 0
  · simpa [variedTriple] using h 1 (theta 0)
  · simpa [variedTriple] using h 2 (theta 0+theta 1)

theorem varied_triple_ratios (u : Triple) (theta : Fin 3 → ℝ)
    (htheta : ∑ j, theta j = 0) :
    ratios (variedTriple u theta) = perturbedRatios u theta := by
  have hadd : Complex.exp (Complex.I*((theta 0+theta 1 : ℝ) : ℂ)) =
      Complex.exp (Complex.I*(theta 0 : ℂ))*Complex.exp (Complex.I*(theta 1 : ℂ)) := by
    rw [Complex.ofReal_add,mul_add,Complex.exp_add]
  have hsum : theta 0+theta 1 = -theta 2 := by
    have he : theta 0+theta 1+theta 2=0 := by simpa [Fin.sum_univ_succ,add_assoc] using htheta
    linarith
  have hconj : (starRingEnd ℂ) (Complex.exp (Complex.I*((theta 0+theta 1 : ℝ) : ℂ))) =
      Complex.exp (Complex.I*(theta 2 : ℂ)) := by
    rw [hsum,← Complex.exp_conj]
    simp
  simp only [Complex.ofReal_add] at hadd hconj
  ext j
  fin_cases j
  · simp [ratios,variedTriple,perturbedRatios]
    ring
  · norm_num [ratios,variedTriple,perturbedRatios,map_mul]
    rw [hadd]
    calc
      _ = (u 2*(starRingEnd ℂ) (u 1)*Complex.exp (Complex.I*(theta 1 : ℂ)))*
        (Complex.exp (Complex.I*(theta 0 : ℂ))*
         (starRingEnd ℂ) (Complex.exp (Complex.I*(theta 0 : ℂ)))) := by ring
      _ = _ := by rw [phase_unit]; ring
  · norm_num [ratios,variedTriple,perturbedRatios,map_mul]
    rw [hconj]
    ring

theorem seed_equation_is_varied_correlation (u v : Triple) (theta : angleDomain) :
    seedEquation u v theta =
      gamma (variedTriple u ![(theta : AngleSpace) 0,(theta : AngleSpace) 1,(theta : AngleSpace) 2])+
      gamma (variedTriple v ![(theta : AngleSpace) 3,(theta : AngleSpace) 4,(theta : AngleSpace) 5]) := by
  have ht : ∑ j, ![(theta : AngleSpace) 0,(theta : AngleSpace) 1,(theta : AngleSpace) 2] j = 0 := by
    simpa [Fin.sum_univ_succ,add_assoc] using theta.property.1
  have hp : ∑ j, ![(theta : AngleSpace) 3,(theta : AngleSpace) 4,(theta : AngleSpace) 5] j = 0 := by
    simpa [Fin.sum_univ_succ,add_assoc] using theta.property.2
  have hg (w : Triple) : gamma w = ∑ j, ratios w j := by
    simp [gamma,ratios,Fin.sum_univ_succ,add_assoc]
  rw [seed_equation_is_torus_sum,hg,hg,varied_triple_ratios u _ ht,varied_triple_ratios v _ hp]

theorem actual_seed_zero_iff_varied_block_unitary (u v : Triple)
    (hu : UnitTriple u) (hv : UnitTriple v) (theta : angleDomain) :
    seedEquation u v theta = 0 ↔
      let a := variedTriple u ![(theta : AngleSpace) 0,(theta : AngleSpace) 1,(theta : AngleSpace) 2]
      let b := variedTriple v ![(theta : AngleSpace) 3,(theta : AngleSpace) 4,(theta : AngleSpace) 5]
      (blockMatrix a b)ᴴ*blockMatrix a b = (6 : ℂ) • (1 : SixMatrix) := by
  dsimp only
  rw [seed_equation_is_varied_correlation]
  constructor
  · intro h
    rw [actual_block_gram _ _ (varied_triple_unit u hu _) (varied_triple_unit v hv _),h]
    ext i j
    fin_cases i <;> fin_cases j <;> norm_num [correlationGram,Matrix.smul_apply,Matrix.one_apply]
  · exact correlation_from_unitarity _ _ (varied_triple_unit u hu _) (varied_triple_unit v hv _)

end MUBSeedDifferential
