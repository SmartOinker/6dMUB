module

public import MUBPhaseTensorConverse

@[expose] public section
noncomputable section

namespace MUBTetrahedral

open Matrix MUBPhaseTensor MUBPhaseTensorConverse

variable {n : Type*}

def Cocycle (t u v w : Tensor n) : Prop :=
  ∀ a b c d, t a b c * v a c d = u a b d * w b c d

def ratio (t : Tensor n) (o a b c : n) : ℂ := t a b c / t o b c

def edge01 (u : Tensor n) (o : n) : Matrix n n ℂ := fun a b => ratio u o a b o
def edge02 (v : Tensor n) (o : n) : Matrix n n ℂ := fun a c => ratio v o a c o
def edge03 (v : Tensor n) (o : n) : Matrix n n ℂ :=
  fun a d => ratio v o a o o / ratio v o a o d
def edge12 (t : Tensor n) (o : n) : Matrix n n ℂ := fun b c => t o b c
def edge13 (u : Tensor n) (o : n) : Matrix n n ℂ := fun b d => u o b d
def edge23 (v : Tensor n) (o : n) : Matrix n n ℂ := fun c d => v o c d

private theorem phase_ne_zero {z : ℂ} (h : z * (starRingEnd ℂ) z = 1) : z ≠ 0 := by
  intro hz
  rw [hz, zero_mul] at h
  exact zero_ne_one h

private theorem ratio_nonzero (t : Tensor n) (hn : ∀ a b c, t a b c ≠ 0)
    (o a b c : n) : ratio t o a b c ≠ 0 := div_ne_zero (hn a b c) (hn o b c)

private theorem ratio_cocycle (t u v w : Tensor n) (o : n)
    (ht : ∀ a b c, t a b c ≠ 0) (hu : ∀ a b d, u a b d ≠ 0)
    (hv : ∀ a c d, v a c d ≠ 0) (hc : Cocycle t u v w) (a b c d : n) :
    ratio t o a b c * ratio v o a c d = ratio u o a b d := by
  have h1 := hc a b c d
  have h0 := hc o b c d
  unfold ratio
  field_simp [ht o b c, hu o b d, hv o c d]
  linear_combination (u o b d) * h1 - (u a b d) * h0

/-- A nonzero tetrahedral cocycle reconstructs six shared edge factors.
No line-sum, unitary, or box premise is needed for this algebraic result. -/
theorem phase_edges_factorization (t u v w : Tensor n) (o : n)
    (ht : ∀ a b c, t a b c ≠ 0) (hu : ∀ a b d, u a b d ≠ 0)
    (hv : ∀ a c d, v a c d ≠ 0) (hc : Cocycle t u v w) :
    (∀ a b c, t a b c * edge02 v o a c = edge01 u o a b * edge12 t o b c) ∧
    (∀ a b d, u a b d * edge03 v o a d = edge01 u o a b * edge13 u o b d) ∧
    (∀ a c d, v a c d * edge03 v o a d = edge02 v o a c * edge23 v o c d) ∧
    (∀ b c d, w b c d * edge13 u o b d = edge12 t o b c * edge23 v o c d) := by
  have hf := ratio_cocycle t u v w o ht hu hv hc
  have h13 (a b d : n) : ratio u o a b d * edge03 v o a d = edge01 u o a b := by
    change ratio u o a b d * (ratio v o a o o / ratio v o a o d) = ratio u o a b o
    rw [← hf a b o d]
    calc
      _ = ratio t o a b o * ratio v o a o o := by
        field_simp [ratio_nonzero v hv o a o d]
      _ = _ := hf a b o o
  have h23 (a c d : n) : ratio v o a c d * edge03 v o a d = edge02 v o a c := by
    apply mul_left_cancel₀ (ratio_nonzero t ht o a o c)
    calc
      _ = (ratio t o a o c * ratio v o a c d) * edge03 v o a d := by ring
      _ = ratio u o a o d * edge03 v o a d := by rw [hf]
      _ = edge01 u o a o := h13 a o d
      _ = ratio t o a o c * edge02 v o a c := (hf a o c o).symm
  refine ⟨?_, ?_, ?_, ?_⟩
  · intro a b c
    change t a b c * ratio v o a c o = ratio u o a b o * t o b c
    calc
      _ = (ratio t o a b c * ratio v o a c o) * t o b c := by
        unfold ratio
        field_simp [ht o b c]
      _ = _ := by rw [hf]
  · intro a b d
    change u a b d * edge03 v o a d = edge01 u o a b * u o b d
    calc
      _ = (ratio u o a b d * edge03 v o a d) * u o b d := by
        unfold ratio
        field_simp [hu o b d]
      _ = _ := by rw [h13]
  · intro a c d
    change v a c d * edge03 v o a d = edge02 v o a c * v o c d
    calc
      _ = (ratio v o a c d * edge03 v o a d) * v o c d := by
        unfold ratio
        field_simp [hv o c d]
      _ = _ := by rw [h23]
  · intro b c d
    change w b c d * u o b d = t o b c * v o c d
    rw [mul_comm]
    exact (hc o b c d).symm

private theorem unit_div {z q : ℂ}
    (hz : z * (starRingEnd ℂ) z = 1) (hq : q * (starRingEnd ℂ) q = 1) :
    (z/q) * (starRingEnd ℂ) (z/q) = 1 := by
  rw [map_div₀, div_mul_div_comm, hz, hq, div_self one_ne_zero]

/-- Unit entries on the three anchor faces make all six constructed edge
factors unit phases. -/
theorem phase_edges_unit (t u v : Tensor n) (o : n)
    (ht : UnitTensor t) (hu : UnitTensor u) (hv : UnitTensor v) :
    UnitEntries (edge01 u o) ∧ UnitEntries (edge02 v o) ∧ UnitEntries (edge03 v o) ∧
    UnitEntries (edge12 t o) ∧ UnitEntries (edge13 u o) ∧ UnitEntries (edge23 v o) := by
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩
  · intro a b
    exact unit_div (hu a b o) (hu o b o)
  · intro a c
    exact unit_div (hv a c o) (hv o c o)
  · intro a d
    exact unit_div (unit_div (hv a o o) (hv o o o)) (unit_div (hv a o d) (hv o o d))
  · intro b c
    exact ht o b c
  · intro b d
    exact hu o b d
  · intro c d
    exact hv o c d

private theorem root_nonzero : rootSix ≠ 0 := by
  unfold rootSix
  exact_mod_cast (ne_of_gt (Real.sqrt_pos.2 (by norm_num : (0 : ℝ) < 6)))

private theorem root_real : (starRingEnd ℂ) rootSix = rootSix := by
  simp [rootSix]

private theorem phase_normSq {z : ℂ}
    (hz : z * (starRingEnd ℂ) z = 1) : Complex.normSq z = 1 := by
  apply Complex.ofReal_injective
  simpa only [Complex.mul_conj, Complex.ofReal_one] using hz

private theorem normalize_flat (a : Matrix Six Six ℂ) (ha : UnitEntries a) :
    ∀ i j, Complex.normSq (MUBPhaseTensor.normalize a i j) = (1 : ℝ) / 6 := by
  have hr : Complex.normSq rootSix = 6 := by
    simp only [rootSix, Complex.normSq_ofReal]
    exact Real.mul_self_sqrt (by norm_num)
  intro i j
  change Complex.normSq (rootSix⁻¹ * a i j) = (1 : ℝ) / 6
  rw [Complex.normSq_mul, Complex.normSq_inv, hr, phase_normSq (ha i j)]
  norm_num

private theorem normalize_adjoint (a : Matrix Six Six ℂ) :
    (MUBPhaseTensor.normalize a)ᴴ = MUBPhaseTensor.normalize aᴴ := by
  simp [MUBPhaseTensor.normalize, rootSix]

private theorem normalize_product (a b c : Matrix Six Six ℂ)
    (h : a * c = rootSix • b) : MUBPhaseTensor.normalize a * MUBPhaseTensor.normalize c = MUBPhaseTensor.normalize b := by
  unfold MUBPhaseTensor.normalize
  rw [Matrix.smul_mul, Matrix.mul_smul, h]
  simp only [smul_smul]
  congr 1
  field_simp [root_nonzero]

private theorem normalized_recovery (t : Tensor Six) (a b c : Matrix Six Six ℂ)
    (hb : UnitEntries b) (hf : ∀ i k j, t i k j * b i j = a i k * c k j)
    (i k j : Six) :
    t i k j = rootSix * MUBPhaseTensor.normalize a i k * MUBPhaseTensor.normalize c k j / MUBPhaseTensor.normalize b i j := by
  have hn := phase_ne_zero (hb i j)
  calc
    _ = a i k * c k j / b i j := (eq_div_iff hn).mpr (hf i k j)
    _ = _ := by
      change a i k * c k j / b i j =
        rootSix * (rootSix⁻¹ * a i k) * (rootSix⁻¹ * c k j) / (rootSix⁻¹ * b i j)
      field_simp [root_nonzero]

/-- Any unit-phase pair factorization with the three line sums normalizes to a
physical realization. The edge matrices need not use the single-face anchor gauge. -/
theorem factorized_face_realization (t : Tensor Six) (a b c : Matrix Six Six ℂ)
    (ht : UnitTensor t) (ha : UnitEntries a) (hb : UnitEntries b) (hc : UnitEntries c)
    (hf : ∀ i k j, t i k j * b i j = a i k * c k j)
    (hl : LineSums t rootSix) :
    PhysicalRealization t (MUBPhaseTensor.normalize a) (MUBPhaseTensor.normalize b) (MUBPhaseTensor.normalize c) := by
  have he := phase_equations_of_line_sums t a b c rootSix root_real ht ha hc hf hl
  have h1 := normalize_product a b c he.1
  have h2 : (MUBPhaseTensor.normalize a)ᴴ * MUBPhaseTensor.normalize b = MUBPhaseTensor.normalize c := by
    simpa only [normalize_adjoint] using normalize_product aᴴ c b he.2.1
  have h3 : MUBPhaseTensor.normalize b * (MUBPhaseTensor.normalize c)ᴴ = MUBPhaseTensor.normalize a := by
    simpa only [normalize_adjoint] using normalize_product b a cᴴ he.2.2
  have hu := MUBCompatibility.coupled_flat_unitary (MUBPhaseTensor.normalize a) (MUBPhaseTensor.normalize b)
    (MUBPhaseTensor.normalize c) h1 h2 h3 (by simpa [Six] using normalize_flat a ha)
  exact ⟨hu.1, hu.2.1, hu.2.2, h1, normalize_flat a ha, normalize_flat b hb,
    normalize_flat c hc, normalized_recovery t a b c hb hf⟩

/-- Four shared-edge physical realizations encode a quartet: the first basis is
standard and the other three are represented by A, B, D. -/
def PhysicalQuartet (t u v w : Tensor Six) (A B D C E F : Matrix Six Six ℂ) : Prop :=
  PhysicalRealization t A B C ∧ PhysicalRealization u A D E ∧
  PhysicalRealization v B D F ∧ PhysicalRealization w C E F

/-- No anchored boxes or fourth-face line sums are included in this predicate. -/
def TetrahedralConditions (t u v w : Tensor Six) : Prop :=
  UnitTensor t ∧ UnitTensor u ∧ UnitTensor v ∧ UnitTensor w ∧ Cocycle t u v w ∧
  LineSums t rootSix ∧ LineSums u rootSix ∧ LineSums v rootSix

/-- The cocycle glues the three anchor faces into one genuine shared-edge
physical quartet. Fourth-face unitarity and composition are derived. -/
theorem tetrahedral_realization (t u v w : Tensor Six)
    (h : TetrahedralConditions t u v w) :
    ∃ A B D C E F : Matrix Six Six ℂ, PhysicalQuartet t u v w A B D C E F := by
  rcases h with ⟨ht, hu, hv, _, hco, hlt, hlu, hlv⟩
  have hnT : ∀ a b c, t a b c ≠ 0 := fun a b c => phase_ne_zero (ht a b c)
  have hnU : ∀ a b d, u a b d ≠ 0 := fun a b d => phase_ne_zero (hu a b d)
  have hnV : ∀ a c d, v a c d ≠ 0 := fun a c d => phase_ne_zero (hv a c d)
  rcases phase_edges_factorization t u v w 0 hnT hnU hnV hco with ⟨ft, fu, fv, fw⟩
  rcases phase_edges_unit t u v 0 ht hu hv with ⟨ha, hb, hd, hc, he, hf⟩
  have pt := factorized_face_realization t _ _ _ ht ha hb hc ft hlt
  have pu := factorized_face_realization u _ _ _ hu ha hd he fu hlu
  have pv := factorized_face_realization v _ _ _ hv hb hd hf fv hlv
  let A := MUBPhaseTensor.normalize (edge01 u 0)
  let B := MUBPhaseTensor.normalize (edge02 v 0)
  let D := MUBPhaseTensor.normalize (edge03 v 0)
  let C := MUBPhaseTensor.normalize (edge12 t 0)
  let E := MUBPhaseTensor.normalize (edge13 u 0)
  let F := MUBPhaseTensor.normalize (edge23 v 0)
  change PhysicalRealization t A B C at pt
  change PhysicalRealization u A D E at pu
  change PhysicalRealization v B D F at pv
  have hAC : A * C = B := pt.2.2.2.1
  have hAE : A * E = D := pu.2.2.2.1
  have hBF : B * F = D := pv.2.2.2.1
  have hAl : Aᴴ * A = 1 := by
    simpa only [Matrix.star_eq_conjTranspose] using Matrix.mem_unitaryGroup_iff'.mp pt.1
  have hCF : C * F = E := by
    calc
      _ = (Aᴴ * A) * (C * F) := by rw [hAl, Matrix.one_mul]
      _ = Aᴴ * ((A * C) * F) := by simp only [Matrix.mul_assoc]
      _ = Aᴴ * (A * E) := by rw [hAC, hBF, hAE]
      _ = E := by rw [← Matrix.mul_assoc, hAl, Matrix.one_mul]
  have pw : PhysicalRealization w C E F := by
    refine ⟨pt.2.2.1, pu.2.2.1, pv.2.2.1, hCF, normalize_flat _ hc,
      normalize_flat _ he, normalize_flat _ hf, ?_⟩
    exact normalized_recovery w _ _ _ he fw
  exact ⟨A, B, D, C, E, F, pt, pu, pv, pw⟩

private theorem flat_nonzero {z : ℂ} (h : Complex.normSq z = (1 : ℝ)/6) : z ≠ 0 := by
  intro hz
  rw [hz, Complex.normSq_zero] at h
  norm_num at h

/-- Every actual shared-edge quartet satisfies the four unit conditions, the
full tetrahedral cocycle, and the three anchor-face line-sum families. -/
theorem physical_quartet_conditions (t u v w : Tensor Six) (A B D C E F : Matrix Six Six ℂ)
    (h : PhysicalQuartet t u v w A B D C E F) : TetrahedralConditions t u v w := by
  rcases h with ⟨pt, pu, pv, pw⟩
  have ct := physical_realization_conditions t A B C pt
  have cu := physical_realization_conditions u A D E pu
  have cv := physical_realization_conditions v B D F pv
  have cw := physical_realization_conditions w C E F pw
  refine ⟨ct.1, cu.1, cv.1, cw.1, ?_, ct.2.2, cu.2.2, cv.2.2⟩
  intro a b c d
  rw [pt.2.2.2.2.2.2.2 a b c, pu.2.2.2.2.2.2.2 a b d,
    pv.2.2.2.2.2.2.2 a c d, pw.2.2.2.2.2.2.2 b c d]
  field_simp [flat_nonzero (pt.2.2.2.2.2.1 a c),
    flat_nonzero (pu.2.2.2.2.2.1 a d), flat_nonzero (pu.2.2.2.2.2.2.1 b d)]

/-- The standard basis together with A, B, D is mutually unbiased: each basis
is unitary, each is flat relative to the standard basis, and every pairwise
transition is flat. -/
def UnbiasedQuartet (A B D : Matrix Six Six ℂ) : Prop :=
  A ∈ Matrix.unitaryGroup Six ℂ ∧ B ∈ Matrix.unitaryGroup Six ℂ ∧
  D ∈ Matrix.unitaryGroup Six ℂ ∧
  (∀ i j, Complex.normSq (A i j) = (1 : ℝ)/6) ∧
  (∀ i j, Complex.normSq (B i j) = (1 : ℝ)/6) ∧
  (∀ i j, Complex.normSq (D i j) = (1 : ℝ)/6) ∧
  (∀ i j, Complex.normSq ((Aᴴ * B) i j) = (1 : ℝ)/6) ∧
  (∀ i j, Complex.normSq ((Aᴴ * D) i j) = (1 : ℝ)/6) ∧
  (∀ i j, Complex.normSq ((Bᴴ * D) i j) = (1 : ℝ)/6)

/-- Shared physical face realizations give the actual six mutually unbiased
basis overlaps; compatibility is not replaced by a Gram relaxation. -/
theorem physical_quartet_is_unbiased (t u v w : Tensor Six)
    (A B D C E F : Matrix Six Six ℂ) (h : PhysicalQuartet t u v w A B D C E F) :
    UnbiasedQuartet A B D := by
  rcases h with ⟨pt, pu, pv, _⟩
  have hAl : Aᴴ * A = 1 := by
    simpa only [Matrix.star_eq_conjTranspose] using Matrix.mem_unitaryGroup_iff'.mp pt.1
  have hBl : Bᴴ * B = 1 := by
    simpa only [Matrix.star_eq_conjTranspose] using Matrix.mem_unitaryGroup_iff'.mp pv.1
  have hAB : Aᴴ * B = C := by
    rw [← pt.2.2.2.1, ← Matrix.mul_assoc, hAl, Matrix.one_mul]
  have hAD : Aᴴ * D = E := by
    rw [← pu.2.2.2.1, ← Matrix.mul_assoc, hAl, Matrix.one_mul]
  have hBD : Bᴴ * D = F := by
    rw [← pv.2.2.2.1, ← Matrix.mul_assoc, hBl, Matrix.one_mul]
  refine ⟨pt.1, pt.2.1, pu.2.1, pt.2.2.2.2.1, pt.2.2.2.2.2.1,
    pu.2.2.2.2.2.1, ?_, ?_, ?_⟩
  · rw [hAB]
    exact pt.2.2.2.2.2.2.1
  · rw [hAD]
    exact pu.2.2.2.2.2.2.1
  · rw [hBD]
    exact pv.2.2.2.2.2.2.1

/-- Exact equivalence between the tetrahedral phase constraints and existence of
one shared-edge physical quartet. No existence or exclusion assertion is made. -/
theorem tetrahedral_equivalence (t u v w : Tensor Six) :
    TetrahedralConditions t u v w ↔
      ∃ A B D C E F : Matrix Six Six ℂ, PhysicalQuartet t u v w A B D C E F := by
  constructor
  · exact tetrahedral_realization t u v w
  · rintro ⟨A, B, D, C, E, F, h⟩
    exact physical_quartet_conditions t u v w A B D C E F h

/-- All fourth-face constraints, including its previously unassumed line sums,
follow from the tetrahedral data. -/
theorem fourth_face_conditions (t u v w : Tensor Six)
    (h : TetrahedralConditions t u v w) :
    UnitTensor w ∧ AnchoredBoxes w 0 ∧ LineSums w rootSix := by
  rcases tetrahedral_realization t u v w h with ⟨A, B, D, C, E, F, _, _, _, hw⟩
  exact physical_realization_conditions w C E F hw

end MUBTetrahedral
