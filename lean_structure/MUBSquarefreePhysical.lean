module

public import MUBCubicGram
public import MUBGramCap
public import Mathlib.Data.Finset.Card
public import Mathlib.Data.Finset.BooleanAlgebra
public import Mathlib.Tactic.FinCases
public import Lean.Elab.Tactic.Omega

@[expose] public section
noncomputable section

namespace MUBSquarefreePhysical

open Matrix
open scoped ComplexOrder

abbrev Six := Fin 6
abbrev Twenty := Fin 20

/-- The twenty three-element subsets, listed in lexicographic order. -/
def triple : Twenty → Finset Six :=
  ![{0,1,2}, {0,1,3}, {0,1,4}, {0,1,5}, {0,2,3},
    {0,2,4}, {0,2,5}, {0,3,4}, {0,3,5}, {0,4,5},
    {1,2,3}, {1,2,4}, {1,2,5}, {1,3,4}, {1,3,5},
    {1,4,5}, {2,3,4}, {2,3,5}, {2,4,5}, {3,4,5}]

private theorem triple_card (I : Twenty) : (triple I).card = 3 := by
  fin_cases I <;> decide

def squarefreeLift (H : Matrix Six Six ℂ) : Matrix Twenty Six ℂ :=
  fun I j => ∏ a ∈ triple I, H a j

def entrywiseCube (H : Matrix Six Six ℂ) : Matrix Six Six ℂ :=
  fun i j => H i j ^ 3

def incidenceSignInt (I : Twenty) (a : Six) : ℤ :=
  if a ∈ triple I then 1 else -1

def incidenceSign (I : Twenty) (a : Six) : ℂ :=
  incidenceSignInt I a

/-- A rational complex replacement for the usual factor 1/sqrt(2). -/
def incidenceFactor (H : Matrix Six Six ℂ) : Matrix Twenty (Six × Six) ℂ :=
  fun I aj => ((1 + Complex.I) / 2) * incidenceSign I aj.1 * squarefreeLift H I aj.2

/-- Explicit complementary-triple Fourier hypothesis. Its derivation for
non-Tao Hadamards is external to this module. -/
def FourierVanishing (H : Matrix Six Six ℂ) : Prop :=
  ∀ s : Finset Six, s.card = 3 →
    ∑ j, (∏ a ∈ s, H a j) * (starRingEnd ℂ) (∏ a ∈ sᶜ, H a j) = 0

private theorem phase_product_unit (z : Six → ℂ)
    (hu : ∀ a, z a * (starRingEnd ℂ) (z a) = 1) (s : Finset Six) :
    (∏ a ∈ s, z a) * (starRingEnd ℂ) (∏ a ∈ s, z a) = 1 := by
  rw [map_prod, ← Finset.prod_mul_distrib]
  simp only [hu, Finset.prod_const_one]

private theorem triple_sum (z : Six → ℂ) :
    ∑ I : Twenty, ∏ a ∈ triple I, z a =
      MUBCubicGram.thirdElementary (z 0) (z 1) (z 2) (z 3) (z 4) (z 5) := by
  simp [triple, Fin.sum_univ_succ, MUBCubicGram.thirdElementary]
  ring

private theorem column_orthogonality (H : Matrix Six Six ℂ)
    (ho : H * Hᴴ = (6 : ℂ) • (1 : Matrix Six Six ℂ)) :
    Hᴴ * H = (6 : ℂ) • (1 : Matrix Six Six ℂ) := by
  have hi : H * ((6 : ℂ)⁻¹ • Hᴴ) = 1 := by
    rw [Matrix.mul_smul, ho, smul_smul]
    norm_num
  have hi' := mul_eq_one_comm.mp hi
  have hh := congrArg (fun M : Matrix Six Six ℂ => (6 : ℂ) • M) hi'
  simpa only [Matrix.smul_mul, smul_smul, mul_inv_cancel₀ (by norm_num : (6 : ℂ) ≠ 0),
    one_smul] using hh

/-- The squarefree lift has exactly the column Gram matrix needed by the
cube-cap certificate. No Fourier hypothesis is used in this identity. -/
theorem squarefree_column_gram (H : Matrix Six Six ℂ)
    (hu : ∀ a j, H a j * (starRingEnd ℂ) (H a j) = 1)
    (ho : H * Hᴴ = (6 : ℂ) • (1 : Matrix Six Six ℂ)) :
    (squarefreeLift H)ᴴ * squarefreeLift H =
      (3 : ℂ)⁻¹ • ((entrywiseCube H)ᴴ * entrywiseCube H) +
        (18 : ℂ) • (1 : Matrix Six Six ℂ) := by
  have hc := column_orthogonality H ho
  ext j k
  by_cases hjk : j = k
  · subst k
    have hV : ((squarefreeLift H)ᴴ * squarefreeLift H) j j = 20 := by
      change (∑ I : Twenty, (starRingEnd ℂ) (∏ a ∈ triple I, H a j) *
        (∏ a ∈ triple I, H a j)) = 20
      have hunit (I : Twenty) :
          (starRingEnd ℂ) (∏ a ∈ triple I, H a j) * (∏ a ∈ triple I, H a j) = 1 := by
        rw [mul_comm]
        exact phase_product_unit (fun a => H a j) (fun a => hu a j) (triple I)
      simp only [hunit]
      norm_num
    have hM : ((entrywiseCube H)ᴴ * entrywiseCube H) j j = 6 := by
      change (∑ a, (starRingEnd ℂ) (H a j ^ 3) * H a j ^ 3) = 6
      have hunit (a : Six) : (starRingEnd ℂ) (H a j ^ 3) * H a j ^ 3 = 1 := by
        rw [map_pow, ← mul_pow, mul_comm, hu a j]
        norm_num
      simp only [hunit]
      norm_num
    simp only [Matrix.add_apply, Matrix.smul_apply, smul_eq_mul, Matrix.one_apply,
      ↓reduceIte, hV, hM]
    norm_num
  · let z : Six → ℂ := fun a => (starRingEnd ℂ) (H a j) * H a k
    have hz : ∑ a, z a = 0 := by
      have hh := congrArg (fun N : Matrix Six Six ℂ => N j k) hc
      simpa [z, Matrix.mul_apply, Matrix.conjTranspose_apply, Matrix.one_apply, hjk]
        using hh
    have hz' : z 0 + z 1 + z 2 + z 3 + z 4 + z 5 = 0 := by
      simpa [Fin.sum_univ_succ, add_assoc] using hz
    have hn := MUBCubicGram.six_cubes_eq_three_elementary
      (z 0) (z 1) (z 2) (z 3) (z 4) (z 5) hz'
    have hV : ((squarefreeLift H)ᴴ * squarefreeLift H) j k =
        MUBCubicGram.thirdElementary (z 0) (z 1) (z 2) (z 3) (z 4) (z 5) := by
      calc
        _ = ∑ I : Twenty, ∏ a ∈ triple I, z a := by
          simp only [Matrix.mul_apply, Matrix.conjTranspose_apply, squarefreeLift,
            ← starRingEnd_apply, map_prod, ← Finset.prod_mul_distrib, z]
        _ = _ := triple_sum z
    have hM : ((entrywiseCube H)ᴴ * entrywiseCube H) j k =
        z 0 ^ 3 + z 1 ^ 3 + z 2 ^ 3 + z 3 ^ 3 + z 4 ^ 3 + z 5 ^ 3 := by
      simp [Matrix.mul_apply, Matrix.conjTranspose_apply, entrywiseCube, z,
        Fin.sum_univ_succ, mul_pow, add_assoc]
    simp only [Matrix.add_apply, Matrix.smul_apply, smul_eq_mul, Matrix.one_apply,
      hjk, ↓reduceIte, mul_zero, add_zero, hV, hM, hn]
    ring

private theorem cancel_common_phases (z : Six → ℂ)
    (hu : ∀ a, z a * (starRingEnd ℂ) (z a) = 1) (s t : Finset Six) :
    (∏ a ∈ s, z a) * (starRingEnd ℂ) (∏ a ∈ t, z a) =
      (∏ a ∈ s \ t, z a) * (starRingEnd ℂ) (∏ a ∈ t \ s, z a) := by
  have hs : (∏ a ∈ s \ t, z a) * (∏ a ∈ s ∩ t, z a) = ∏ a ∈ s, z a := by
    simpa only [Finset.sdiff_inter_self_left] using
      (Finset.prod_sdiff (f := z) (Finset.inter_subset_left (s₁ := s) (s₂ := t)))
  have ht : (∏ a ∈ t \ s, z a) * (∏ a ∈ s ∩ t, z a) = ∏ a ∈ t, z a := by
    simpa only [Finset.sdiff_inter_self_right] using
      (Finset.prod_sdiff (f := z) (Finset.inter_subset_right (s₁ := s) (s₂ := t)))
  rw [← hs, ← ht, map_mul]
  calc
    _ = ((∏ a ∈ s \ t, z a) * (starRingEnd ℂ) (∏ a ∈ t \ s, z a)) *
      ((∏ a ∈ s ∩ t, z a) * (starRingEnd ℂ) (∏ a ∈ s ∩ t, z a)) := by ring
    _ = _ := by rw [phase_product_unit z hu]; ring

private theorem triple_inter_cases :
    ∀ I J : Twenty, I = J ∨ (triple I ∩ triple J).card = 0 ∨
      (triple I ∩ triple J).card = 1 ∨ (triple I ∩ triple J).card = 2 := by
  decide

private theorem triple_complement :
    ∀ I J : Twenty, (triple I ∩ triple J).card = 0 →
      triple J = (triple I)ᶜ := by
  decide

private theorem incidence_dot_int (I J : Twenty) :
    ∑ a : Six, incidenceSignInt I a * incidenceSignInt J a =
      4 * ((triple I ∩ triple J).card : ℤ) - 6 := by
  revert I J
  decide

private theorem incidence_dot (I J : Twenty) :
    ∑ a : Six, incidenceSign I a * incidenceSign J a =
      4 * ((triple I ∩ triple J).card : ℂ) - 6 := by
  have hh := congrArg (fun z : ℤ => (z : ℂ)) (incidence_dot_int I J)
  simpa [incidenceSign] using hh

private theorem squarefree_row_diagonal (H : Matrix Six Six ℂ)
    (hu : ∀ a j, H a j * (starRingEnd ℂ) (H a j) = 1) (I : Twenty) :
    (squarefreeLift H * (squarefreeLift H)ᴴ) I I = 6 := by
  change (∑ j : Six, (∏ a ∈ triple I, H a j) *
    (starRingEnd ℂ) (∏ a ∈ triple I, H a j)) = 6
  simp only [phase_product_unit (fun a => H a _) (fun a => hu a _) (triple I)]
  norm_num

/-- Rows with two common indices are orthogonal, by cancellation of the
shared phases and ordinary Hadamard row orthogonality. -/
theorem squarefree_row_overlap_two (H : Matrix Six Six ℂ)
    (hu : ∀ a j, H a j * (starRingEnd ℂ) (H a j) = 1)
    (ho : H * Hᴴ = (6 : ℂ) • (1 : Matrix Six Six ℂ))
    (I J : Twenty) (hc : (triple I ∩ triple J).card = 2) :
    (squarefreeLift H * (squarefreeLift H)ᴴ) I J = 0 := by
  have hs : (triple I \ triple J).card = 1 := by
    rw [Finset.card_sdiff, Finset.inter_comm, hc, triple_card]
  have ht : (triple J \ triple I).card = 1 := by
    rw [Finset.card_sdiff, hc, triple_card]
  obtain ⟨a, ha⟩ := Finset.card_eq_one.mp hs
  obtain ⟨b, hb⟩ := Finset.card_eq_one.mp ht
  have hab : a ≠ b := by
    intro hab
    subst b
    have hai : a ∈ triple I \ triple J := by rw [ha]; simp
    have haj : a ∈ triple J \ triple I := by rw [hb]; simp
    exact (Finset.mem_sdiff.mp hai).2 (Finset.mem_sdiff.mp haj).1
  have horth : ∑ j, H a j * (starRingEnd ℂ) (H b j) = 0 := by
    have hh := congrArg (fun M : Matrix Six Six ℂ => M a b) ho
    simpa [Matrix.mul_apply, Matrix.conjTranspose_apply, Matrix.one_apply, hab] using hh
  change (∑ j, (∏ a ∈ triple I, H a j) *
    (starRingEnd ℂ) (∏ a ∈ triple J, H a j)) = 0
  have hcancel (j : Six) := cancel_common_phases
    (fun a => H a j) (fun a => hu a j) (triple I) (triple J)
  simp only [ha, hb, Finset.prod_singleton] at hcancel
  simpa only [hcancel] using horth

private theorem incidence_sign_star (I : Twenty) (a : Six) :
    star (incidenceSign I a) = incidenceSign I a := by
  simp [incidenceSign]

/-- Explicit Gram factorization of the incidence Schur multiplier. -/
theorem incidence_factor_gram_entry (H : Matrix Six Six ℂ) (I J : Twenty) :
    (incidenceFactor H * (incidenceFactor H)ᴴ) I J =
      (2 * ((triple I ∩ triple J).card : ℂ) - 3) *
        (squarefreeLift H * (squarefreeLift H)ᴴ) I J := by
  have hcoeff : ((1 + Complex.I) / 2 : ℂ) * star ((1 + Complex.I) / 2) = 1 / 2 := by
    norm_num [Complex.ext_iff, Complex.star_def]
  have hterm (a j : Six) :
      incidenceFactor H I (a,j) * star (incidenceFactor H J (a,j)) =
        ((1 / 2 : ℂ) * (incidenceSign I a * incidenceSign J a)) *
          (squarefreeLift H I j * star (squarefreeLift H J j)) := by
    dsimp only [incidenceFactor]
    rw [star_mul, star_mul, incidence_sign_star]
    calc
      _ = (((1 + Complex.I) / 2 : ℂ) * star ((1 + Complex.I) / 2)) *
        (incidenceSign I a * incidenceSign J a) *
        (squarefreeLift H I j * star (squarefreeLift H J j)) := by ring
      _ = _ := by rw [hcoeff]
  change (∑ aj : Six × Six, incidenceFactor H I aj * star (incidenceFactor H J aj)) =
    (2 * ((triple I ∩ triple J).card : ℂ) - 3) *
      (∑ j : Six, squarefreeLift H I j * star (squarefreeLift H J j))
  rw [Fintype.sum_prod_type]
  simp only [hterm, ← Finset.mul_sum, ← Finset.sum_mul]
  rw [incidence_dot]
  ring

/-- The full row-defect identity follows from physical row orthogonality
and the explicit complementary-triple Fourier hypothesis. -/
theorem squarefree_row_defect (H : Matrix Six Six ℂ)
    (hu : ∀ a j, H a j * (starRingEnd ℂ) (H a j) = 1)
    (ho : H * Hᴴ = (6 : ℂ) • (1 : Matrix Six Six ℂ))
    (hfv : FourierVanishing H) :
    incidenceFactor H * (incidenceFactor H)ᴴ =
      (24 : ℂ) • (1 : Matrix Twenty Twenty ℂ) -
        squarefreeLift H * (squarefreeLift H)ᴴ := by
  ext I J
  rw [incidence_factor_gram_entry]
  simp only [Matrix.sub_apply, Matrix.smul_apply, smul_eq_mul, Matrix.one_apply]
  rcases triple_inter_cases I J with hij | hc | hc | hc
  · subst J
    rw [Finset.inter_self, triple_card, squarefree_row_diagonal H hu]
    norm_num
  · have hij : I ≠ J := by
      intro hij
      subst J
      norm_num [triple_card] at hc
    have hzero : (squarefreeLift H * (squarefreeLift H)ᴴ) I J = 0 := by
      change (∑ j : Six, (∏ a ∈ triple I, H a j) *
        (starRingEnd ℂ) (∏ a ∈ triple J, H a j)) = 0
      rw [triple_complement I J hc]
      exact hfv (triple I) (triple_card I)
    simp [hc, hij, hzero]
  · have hij : I ≠ J := by
      intro hij
      subst J
      norm_num [triple_card] at hc
    norm_num [hc, hij]
  · have hij : I ≠ J := by
      intro hij
      subst J
      norm_num [triple_card] at hc
    rw [squarefree_row_overlap_two H hu ho I J hc]
    simp [hij]

/-- Actual physical cube Gram cap, with no abstract lift-identity premises.
The only extra hypothesis beyond a phase Hadamard is FourierVanishing H. -/
theorem physical_cube_gram_cap (H : Matrix Six Six ℂ)
    (hu : ∀ a j, H a j * (starRingEnd ℂ) (H a j) = 1)
    (ho : H * Hᴴ = (6 : ℂ) • (1 : Matrix Six Six ℂ))
    (hfv : FourierVanishing H) :
    ((18 : ℂ) • (1 : Matrix Six Six ℂ) -
      (entrywiseCube H)ᴴ * entrywiseCube H).PosSemidef :=
  MUBGramCap.cube_gram_cap_posSemidef (squarefreeLift H) (incidenceFactor H)
    (entrywiseCube H) (squarefree_row_defect H hu ho hfv)
    (squarefree_column_gram H hu ho)

#print axioms squarefree_column_gram
#print axioms squarefree_row_overlap_two
#print axioms incidence_factor_gram_entry
#print axioms squarefree_row_defect
#print axioms physical_cube_gram_cap

end MUBSquarefreePhysical
