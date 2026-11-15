module

public import MUBCompatibility
public import Mathlib.Tactic.LinearCombination
public import Mathlib.Tactic.FieldSimp

@[expose] public section
noncomputable section

namespace MUBPhaseTensor

open Matrix

abbrev Tensor (n : Type*) := n → n → n → ℂ

variable {n : Type*}

def UnitTensor (t : Tensor n) : Prop :=
  ∀ i k j, t i k j * (starRingEnd ℂ) (t i k j) = 1

def UnitEntries (A : Matrix n n ℂ) : Prop :=
  ∀ i j, A i j * (starRingEnd ℂ) (A i j) = 1

/-- Only boxes whose three moving indices differ from the anchor are imposed.
For Fin 6 and anchor zero there are 5^3 = 125 such equations. -/
def AnchoredBoxes (t : Tensor n) (o : n) : Prop :=
  ∀ i k j, i ≠ o → k ≠ o → j ≠ o →
    t i k j * t i o o * t o k o * t o o j =
      t i k o * t i o j * t o k j * t o o o

def phaseA (t : Tensor n) (o : n) : Matrix n n ℂ :=
  fun i k => t i k o

def phaseB (t : Tensor n) (o : n) : Matrix n n ℂ :=
  fun i j => t i o o * t o o j / (t i o j * t o o o)

def phaseC (t : Tensor n) (o : n) : Matrix n n ℂ :=
  fun k j => t o k j / t o k o

private theorem all_anchored_boxes (t : Tensor n) (o : n)
    (hb : AnchoredBoxes t o) (i k j : n) :
    t i k j * t i o o * t o k o * t o o j =
      t i k o * t i o j * t o k j * t o o o := by
  by_cases hi : i = o
  · subst i
    ring
  by_cases hk : k = o
  · subst k
    ring
  by_cases hj : j = o
  · subst j
    ring
  exact hb i k j hi hk hj

/-- Nonzero anchored box relations reconstruct the pair-factor tensor
exactly. Neither flatness nor orthogonality is assumed here. -/
theorem factorization_of_anchored_boxes (t : Tensor n) (o : n)
    (hn : ∀ i k j, t i k j ≠ 0) (hb : AnchoredBoxes t o)
    (i k j : n) :
    t i k j * phaseB t o i j = phaseA t o i k * phaseC t o k j := by
  have hh := all_anchored_boxes t o hb i k j
  dsimp only [phaseA, phaseB, phaseC]
  field_simp [hn i o j, hn o o o, hn o k o]
  linear_combination hh

private theorem phase_nonzero {z : ℂ}
    (hz : z * (starRingEnd ℂ) z = 1) : z ≠ 0 := by
  intro h
  rw [h, zero_mul] at hz
  exact zero_ne_one hz

private theorem phase_mul {z w : ℂ}
    (hz : z * (starRingEnd ℂ) z = 1)
    (hw : w * (starRingEnd ℂ) w = 1) :
    (z * w) * (starRingEnd ℂ) (z * w) = 1 := by
  rw [map_mul]
  calc
    _ = (z * (starRingEnd ℂ) z) * (w * (starRingEnd ℂ) w) := by ring
    _ = 1 := by rw [hz, hw]; ring

private theorem phase_div {z w : ℂ}
    (hz : z * (starRingEnd ℂ) z = 1)
    (hw : w * (starRingEnd ℂ) w = 1) :
    (z / w) * (starRingEnd ℂ) (z / w) = 1 := by
  rw [map_div₀, div_mul_div_comm, hz, hw, div_self one_ne_zero]

/-- Unit tensor entries ensure every reconstructed phase matrix has unit
entries; no box or line condition is needed for this step. -/
theorem reconstructed_phases_unit (t : Tensor n) (o : n)
    (hu : UnitTensor t) :
    UnitEntries (phaseA t o) ∧ UnitEntries (phaseB t o) ∧ UnitEntries (phaseC t o) := by
  refine ⟨fun i k => hu i k o, ?_, ?_⟩
  · intro i j
    exact phase_div (phase_mul (hu i o o) (hu o o j))
      (phase_mul (hu i o j) (hu o o o))
  · intro k j
    exact phase_div (hu o k j) (hu o k o)

section Finite

variable [Fintype n]

def LineSums (t : Tensor n) (s : ℂ) : Prop :=
  (∀ i j, ∑ k, t i k j = s) ∧
  (∀ k j, ∑ i, t i k j = s) ∧
  (∀ i k, ∑ j, t i k j = s)

private theorem second_phase_identity {t a b c : ℂ}
    (ht : t * (starRingEnd ℂ) t = 1)
    (ha : a * (starRingEnd ℂ) a = 1) (hf : t * b = a * c) :
    (starRingEnd ℂ) a * b = c * (starRingEnd ℂ) t := by
  linear_combination
    ((starRingEnd ℂ) a * (starRingEnd ℂ) t) * hf -
    ((starRingEnd ℂ) a * b) * ht +
    (c * (starRingEnd ℂ) t) * ha

private theorem third_phase_identity {t a b c : ℂ}
    (ht : t * (starRingEnd ℂ) t = 1)
    (hc : c * (starRingEnd ℂ) c = 1) (hf : t * b = a * c) :
    b * (starRingEnd ℂ) c = a * (starRingEnd ℂ) t := by
  linear_combination
    ((starRingEnd ℂ) c * (starRingEnd ℂ) t) * hf -
    (b * (starRingEnd ℂ) c) * ht +
    (a * (starRingEnd ℂ) t) * hc

/-- All three line-sum directions give all three coupled matrix equations.
The real line value is explicit, and unitarity is not assumed. -/
theorem phase_equations_of_line_sums (t : Tensor n) (a b c : Matrix n n ℂ)
    (s : ℂ) (hs : (starRingEnd ℂ) s = s)
    (hu : UnitTensor t) (ha : UnitEntries a) (hc : UnitEntries c)
    (hf : ∀ i k j, t i k j * b i j = a i k * c k j)
    (hl : LineSums t s) :
    a * c = s • b ∧ aᴴ * b = s • c ∧ b * cᴴ = s • a := by
  refine ⟨?_, ?_, ?_⟩
  · ext i j
    change (∑ k, a i k * c k j) = s * b i j
    calc
      _ = ∑ k, t i k j * b i j := by
        apply Finset.sum_congr rfl
        intro k _
        exact (hf i k j).symm
      _ = (∑ k, t i k j) * b i j := by rw [Finset.sum_mul]
      _ = _ := by rw [hl.1 i j]
  · ext k j
    change (∑ i, (starRingEnd ℂ) (a i k) * b i j) = s * c k j
    calc
      _ = ∑ i, c k j * (starRingEnd ℂ) (t i k j) := by
        apply Finset.sum_congr rfl
        intro i _
        exact second_phase_identity (hu i k j) (ha i k) (hf i k j)
      _ = c k j * (starRingEnd ℂ) (∑ i, t i k j) := by
        rw [map_sum, Finset.mul_sum]
      _ = _ := by rw [hl.2.1 k j, hs]; ring
  · ext i k
    change (∑ j, b i j * (starRingEnd ℂ) (c k j)) = s * a i k
    calc
      _ = ∑ j, a i k * (starRingEnd ℂ) (t i k j) := by
        apply Finset.sum_congr rfl
        intro j _
        exact third_phase_identity (hu i k j) (hc k j) (hf i k j)
      _ = a i k * (starRingEnd ℂ) (∑ j, t i k j) := by
        rw [map_sum, Finset.mul_sum]
      _ = _ := by rw [hl.2.2 i k, hs]; ring

end Finite

abbrev Six := Fin 6

def rootSix : ℂ := (Real.sqrt 6 : ℝ)

def normalize (A : Matrix Six Six ℂ) : Matrix Six Six ℂ :=
  rootSix⁻¹ • A

def normalizedA (t : Tensor Six) : Matrix Six Six ℂ := normalize (phaseA t 0)
def normalizedB (t : Tensor Six) : Matrix Six Six ℂ := normalize (phaseB t 0)
def normalizedC (t : Tensor Six) : Matrix Six Six ℂ := normalize (phaseC t 0)

private theorem rootSix_nonzero : rootSix ≠ 0 := by
  unfold rootSix
  exact_mod_cast (ne_of_gt (Real.sqrt_pos.2 (by norm_num : (0 : ℝ) < 6)))

private theorem rootSix_real : (starRingEnd ℂ) rootSix = rootSix := by
  simp [rootSix]

private theorem rootSix_normSq : Complex.normSq rootSix = 6 := by
  simp only [rootSix, Complex.normSq_ofReal]
  exact Real.mul_self_sqrt (by norm_num)

private theorem phase_normSq {z : ℂ}
    (hz : z * (starRingEnd ℂ) z = 1) : Complex.normSq z = 1 := by
  apply Complex.ofReal_injective
  simpa only [Complex.mul_conj, Complex.ofReal_one] using hz

private theorem normalize_unit_flat (a : Matrix Six Six ℂ)
    (ha : UnitEntries a) :
    ∀ i j, Complex.normSq (normalize a i j) = (1 : ℝ) / 6 := by
  intro i j
  change Complex.normSq (rootSix⁻¹ * a i j) = (1 : ℝ) / 6
  rw [Complex.normSq_mul, Complex.normSq_inv, rootSix_normSq, phase_normSq (ha i j)]
  norm_num

private theorem normalize_adjoint (a : Matrix Six Six ℂ) :
    (normalize a)ᴴ = normalize aᴴ := by
  simp [normalize, rootSix]

private theorem normalize_phase_product (a b c : Matrix Six Six ℂ)
    (h : a * c = rootSix • b) :
    normalize a * normalize c = normalize b := by
  unfold normalize
  rw [Matrix.smul_mul, Matrix.mul_smul, h]
  simp only [smul_smul]
  congr 1
  field_simp [rootSix_nonzero]

/-- The normalized reconstructed matrices satisfy the exact three coupled
equations. No unitarity or invertibility has been assumed or used. -/
theorem normalized_reconstruction_coupled (t : Tensor Six)
    (hu : UnitTensor t) (hb : AnchoredBoxes t 0) (hl : LineSums t rootSix) :
    normalizedA t * normalizedC t = normalizedB t ∧
      (normalizedA t)ᴴ * normalizedB t = normalizedC t ∧
      normalizedB t * (normalizedC t)ᴴ = normalizedA t := by
  have hp := reconstructed_phases_unit t 0 hu
  have hn : ∀ i k j, t i k j ≠ 0 := fun i k j => phase_nonzero (hu i k j)
  have hf := factorization_of_anchored_boxes t 0 hn hb
  have he := phase_equations_of_line_sums t (phaseA t 0) (phaseB t 0)
    (phaseC t 0) rootSix rootSix_real hu hp.1 hp.2.2 hf hl
  refine ⟨normalize_phase_product _ _ _ he.1, ?_, ?_⟩
  · simpa only [normalizedA, normalizedB, normalizedC, normalize_adjoint] using
      normalize_phase_product _ _ _ he.2.1
  · simpa only [normalizedA, normalizedB, normalizedC, normalize_adjoint] using
      normalize_phase_product _ _ _ he.2.2

/-- Normalized entrywise flatness is derived directly from the unit tensor. -/
theorem normalized_reconstruction_flat (t : Tensor Six) (hu : UnitTensor t) :
    (∀ i j, Complex.normSq (normalizedA t i j) = (1 : ℝ) / 6) ∧
    (∀ i j, Complex.normSq (normalizedB t i j) = (1 : ℝ) / 6) ∧
    (∀ i j, Complex.normSq (normalizedC t i j) = (1 : ℝ) / 6) := by
  have hp := reconstructed_phases_unit t 0 hu
  exact ⟨normalize_unit_flat _ hp.1, normalize_unit_flat _ hp.2.1,
    normalize_unit_flat _ hp.2.2⟩

/-- Full physical realization: normalized flat unitaries, ordinary composition,
and recovery of the supplied phase tensor. -/
def PhysicalRealization (t : Tensor Six) (A B C : Matrix Six Six ℂ) : Prop :=
  A ∈ Matrix.unitaryGroup Six ℂ ∧ B ∈ Matrix.unitaryGroup Six ℂ ∧
  C ∈ Matrix.unitaryGroup Six ℂ ∧ A * C = B ∧
  (∀ i j, Complex.normSq (A i j) = (1 : ℝ) / 6) ∧
  (∀ i j, Complex.normSq (B i j) = (1 : ℝ) / 6) ∧
  (∀ i j, Complex.normSq (C i j) = (1 : ℝ) / 6) ∧
  ∀ i k j, t i k j = rootSix * A i k * C k j / B i j

/-- The complete forward phase-tensor bridge in dimension six. Exactly the
unit phases, 125 non-anchor boxes, and all three line-sum families are premises. -/
theorem phase_tensor_realization (t : Tensor Six)
    (hu : UnitTensor t) (hb : AnchoredBoxes t 0) (hl : LineSums t rootSix) :
    PhysicalRealization t (normalizedA t) (normalizedB t) (normalizedC t) := by
  have he := normalized_reconstruction_coupled t hu hb hl
  have hf := normalized_reconstruction_flat t hu
  have huM := MUBCompatibility.coupled_flat_unitary
    (normalizedA t) (normalizedB t) (normalizedC t) he.1 he.2.1 he.2.2
    (by simpa only [Fintype.card_fin, Nat.cast_ofNat, one_div] using hf.1)
  refine ⟨huM.1, huM.2.1, huM.2.2, he.1, hf.1, hf.2.1, hf.2.2, ?_⟩
  intro i k j
  have hp := reconstructed_phases_unit t 0 hu
  have hbn := phase_nonzero (hp.2.1 i j)
  have hn : ∀ i k j, t i k j ≠ 0 := fun i k j => phase_nonzero (hu i k j)
  have hfac : t i k j = phaseA t 0 i k * phaseC t 0 k j / phaseB t 0 i j :=
    (eq_div_iff hbn).mpr (factorization_of_anchored_boxes t 0 hn hb i k j)
  rw [hfac]
  simp only [normalizedA, normalizedB, normalizedC, normalize,
    Matrix.smul_apply, smul_eq_mul]
  field_simp [rootSix_nonzero, hbn]

#print axioms factorization_of_anchored_boxes
#print axioms reconstructed_phases_unit
#print axioms phase_equations_of_line_sums
#print axioms normalized_reconstruction_coupled
#print axioms normalized_reconstruction_flat
#print axioms phase_tensor_realization

end MUBPhaseTensor
