module
public import Mathlib.RingTheory.MvPolynomial.Ideal
public import Mathlib.RingTheory.Ideal.Quotient.Nilpotent
@[expose] public section
noncomputable section
namespace MUBCoordinateProductIdeal
open MvPolynomial
open scoped Pointwise
variable {σ R : Type*} [CommRing R]

def coordinateIdeal (s : Set σ) : Ideal (MvPolynomial σ R) :=
  Ideal.span (MvPolynomial.X '' s)

def crossExponents (s t : Set σ) : Set (σ →₀ ℕ) :=
  {d | ∃ i ∈ s, ∃ j ∈ t, d = Finsupp.single i 1 + Finsupp.single j 1}

theorem coordinate_product_monomials (s t : Set σ) :
    coordinateIdeal (R := R) s * coordinateIdeal t =
      Ideal.span ((fun d => monomial d (1 : R)) '' crossExponents s t) := by
  classical
  rw [coordinateIdeal, coordinateIdeal, Ideal.span_mul_span]
  congr 1
  ext p
  constructor
  · rintro ⟨a, ⟨i, hi, rfl⟩, b, ⟨j, hj, rfl⟩, rfl⟩
    refine ⟨Finsupp.single i 1 + Finsupp.single j 1, ⟨i,hi,j,hj,rfl⟩, ?_⟩
    simp [MvPolynomial.X]
  · rintro ⟨d, ⟨i, hi, j, hj, rfl⟩, rfl⟩
    refine ⟨X i, ⟨i,hi,rfl⟩, X j, ⟨j,hj,rfl⟩, ?_⟩
    simp [MvPolynomial.X]

/-- For disjoint coordinate sets the product ideal is exactly the intersection,
proved from actual polynomial monomial supports. -/
theorem coordinate_product_eq_inf (s t : Set σ) (hst : Disjoint s t) :
    coordinateIdeal (R := R) s * coordinateIdeal t =
      coordinateIdeal s ⊓ coordinateIdeal t := by
  classical
  apply le_antisymm Ideal.mul_le_inf
  intro p hp
  rw [coordinate_product_monomials, mem_ideal_span_monomial_image]
  intro d hd
  obtain ⟨i, hi, hdi⟩ := mem_ideal_span_X_image.mp hp.1 d hd
  obtain ⟨j, hj, hdj⟩ := mem_ideal_span_X_image.mp hp.2 d hd
  have hij : i ≠ j := by
    intro h
    exact Set.disjoint_left.mp hst hi (h.symm ▸ hj)
  refine ⟨Finsupp.single i 1 + Finsupp.single j 1, ⟨i,hi,j,hj,rfl⟩, ?_⟩
  change ∀ k, _ ≤ _
  intro k
  by_cases hki : k = i
  · subst k
    simpa [hij, Ne.symm hij] using Nat.one_le_iff_ne_zero.mpr hdi
  · by_cases hkj : k = j
    · subst k
      simpa [hij, Ne.symm hij] using Nat.one_le_iff_ne_zero.mpr hdj
    · simp [hki, hkj]

/-- Retaining only the complementary variables identifies the actual coordinate ideal
with a ring-homomorphism kernel. This is proved coefficient by coefficient. -/
theorem coordinate_ideal_eq_kernel (s : Set σ) :
    coordinateIdeal (R := R) s =
      RingHom.ker (MvPolynomial.killCompl
        (Subtype.val_injective : Function.Injective (Subtype.val : {i // i ∉ s} → σ))) := by
  classical
  let f : {i // i ∉ s} → σ := Subtype.val
  have hf : Function.Injective f := Subtype.val_injective
  ext p
  change p ∈ coordinateIdeal s ↔ MvPolynomial.killCompl hf p = 0
  constructor
  · intro hp
    apply MvPolynomial.ext
    intro m
    rw [MvPolynomial.coeff_killCompl, AddMonoidAlgebra.coeff_zero]
    by_contra hc
    obtain ⟨i, hi, hmi⟩ := mem_ideal_span_X_image.mp hp _ (mem_support_iff.mpr hc)
    obtain ⟨j, hj⟩ := Finsupp.mem_range_of_mapDomain_ne_zero hmi
    apply j.property
    change f j ∈ s
    rw [hj]
    exact hi
  · intro hp
    rw [coordinateIdeal, mem_ideal_span_X_image]
    intro d hd
    by_contra hn
    push Not at hn
    have hsupport : (↑d.support : Set σ) ⊆ Set.range f := by
      intro i hi
      refine ⟨⟨i, ?_⟩, rfl⟩
      intro his
      exact Finsupp.mem_support_iff.mp hi (hn i his)
    have hc := congrArg (fun q : MvPolynomial {i // i ∉ s} R => q.coeff (d.comapDomain f hf.injOn)) hp
    rw [MvPolynomial.coeff_killCompl, Finsupp.mapDomain_comapDomain f hf d hsupport,
      AddMonoidAlgebra.coeff_zero] at hc
    exact mem_support_iff.mp hd hc

theorem coordinate_ideal_prime [IsDomain R] (s : Set σ) :
    (coordinateIdeal (R := R) s).IsPrime := by
  rw [coordinate_ideal_eq_kernel]
  exact RingHom.ker_isPrime _

abbrev FourPoly (R : Type*) [CommRing R] := MvPolynomial (Fin 4) R

def leftPlane : Ideal (FourPoly R) := Ideal.span {X 0, X 1}
def rightPlane : Ideal (FourPoly R) := Ideal.span {X 2, X 3}
def crossIdeal : Ideal (FourPoly R) :=
  Ideal.span {X 0 * X 2, X 0 * X 3, X 1 * X 2, X 1 * X 3}

theorem actual_cross_product :
    crossIdeal (R := R) = leftPlane * rightPlane := by
  exact (Ideal.span_pair_mul_span_pair _ _ _ _).symm

theorem actual_cross_intersection :
    crossIdeal (R := R) = leftPlane ⊓ rightPlane := by
  rw [actual_cross_product]
  have h := coordinate_product_eq_inf (R := R) ({0,1} : Set (Fin 4)) {2,3}
    (by simp [Set.disjoint_left])
  simpa [coordinateIdeal, leftPlane, rightPlane] using h

/-- The original four-generator polynomial ideal is radical; no passage to its
radical is built into the definition. -/
theorem actual_cross_radical [IsDomain R] : (crossIdeal (R := R)).IsRadical := by
  rw [actual_cross_intersection]
  have hl := (coordinate_ideal_prime (R := R) ({0,1} : Set (Fin 4))).isRadical
  have hr := (coordinate_ideal_prime (R := R) ({2,3} : Set (Fin 4))).isRadical
  apply Ideal.IsRadical.inf
  · simpa [coordinateIdeal, leftPlane] using hl
  · simpa [coordinateIdeal, rightPlane] using hr

theorem actual_cross_quotient_reduced [IsDomain R] :
    IsReduced (FourPoly R ⧸ crossIdeal) :=
  (Ideal.isRadical_iff_quotient_reduced _).mp actual_cross_radical

theorem prime_over_cross_contains_plane (P : Ideal (FourPoly R))
    (hP : P.IsPrime) (h : crossIdeal ≤ P) : leftPlane ≤ P ∨ rightPlane ≤ P := by
  rw [actual_cross_product] at h
  exact hP.mul_le.mp h

end MUBCoordinateProductIdeal
