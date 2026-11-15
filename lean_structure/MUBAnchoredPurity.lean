module

public import MUBResidual
public import Mathlib.LinearAlgebra.Matrix.PosDef
public import Mathlib.Tactic.FieldSimp

@[expose] public section
noncomputable section

namespace MUBAnchoredPurity

open Matrix
open scoped ComplexOrder

variable {n : Type*} [Fintype n] [DecidableEq n]

def anchorMass (R : Matrix n n ℂ) (a : n) : ℂ := (R * R) a a

def anchorOuter (R : Matrix n n ℂ) (a : n) : Matrix n n ℂ :=
  Matrix.vecMulVec (fun i => R i a) (fun j => R a j)

def anchorDefect (R : Matrix n n ℂ) (a : n) : ℂ :=
  (R * R - R * R * R) a a

def anchorProjection (R : Matrix n n ℂ) (a : n) : Matrix n n ℂ :=
  (anchorMass R a)⁻¹ • anchorOuter R a

omit [DecidableEq n] in
private theorem outer_trace (R : Matrix n n ℂ) (a : n) :
    Matrix.trace (anchorOuter R a) = anchorMass R a := by
  simp only [anchorOuter, Matrix.trace_vecMulVec, dotProduct, anchorMass,
    Matrix.mul_apply]
  apply Finset.sum_congr rfl
  intro i hi
  ring

omit [DecidableEq n] in
private theorem outer_square (R : Matrix n n ℂ) (a : n) :
    anchorOuter R a * anchorOuter R a = anchorMass R a • anchorOuter R a := by
  ext i j
  simp only [anchorOuter, anchorMass, Matrix.mul_apply, Matrix.vecMulVec_apply,
    Matrix.smul_apply, smul_eq_mul, Finset.sum_mul]
  apply Finset.sum_congr rfl
  intro k hk
  ring

omit [DecidableEq n] in
private theorem outer_cross_trace (R : Matrix n n ℂ) (a : n) :
    Matrix.trace (R * anchorOuter R a) = (R * R * R) a a := by
  rw [Matrix.mul_assoc]
  simp only [Matrix.trace, Matrix.diag_apply, anchorOuter,
    Matrix.mul_apply, Matrix.vecMulVec_apply, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro i hi
  apply Finset.sum_congr rfl
  intro j hj
  ring

omit [Fintype n] [DecidableEq n] in
private theorem outer_hermitian (R : Matrix n n ℂ) (hR : R.IsHermitian) (a : n) :
    (anchorOuter R a)ᴴ = anchorOuter R a := by
  ext i j
  simp only [anchorOuter, Matrix.conjTranspose_apply, Matrix.vecMulVec_apply,
    star_mul, hR.apply]

private theorem mass_star (R : Matrix n n ℂ) (hR : R.IsHermitian) (a : n) :
    star (anchorMass R a) = anchorMass R a := by
  simpa only [anchorMass, pow_two] using (hR.pow 2).apply a a

omit [DecidableEq n] in
private theorem mass_nonnegative (R : Matrix n n ℂ) (hR : R.IsHermitian) (a : n) :
    0 ≤ anchorMass R a := by
  have hp := (Matrix.posSemidef_conjTranspose_mul_self R).diag_nonneg (i := a)
  simpa only [hR.eq, anchorMass] using hp

omit [DecidableEq n] in
private theorem mass_nonzero (R : Matrix n n ℂ) (hR : R.IsHermitian) (a : n)
    (ha : R a a ≠ 0) : anchorMass R a ≠ 0 := by
  intro hz
  have hz' : (Rᴴ * R) a a = 0 := by rw [hR.eq]; exact hz
  have hh : ∑ i, star (R i a) * R i a = 0 := by
    simpa only [Matrix.mul_apply, Matrix.conjTranspose_apply] using hz' 
  have hp (i : n) : 0 ≤ star (R i a) * R i a := star_mul_self_nonneg _
  have ht := (Finset.sum_eq_zero_iff_of_nonneg (fun i _ => hp i)).mp hh a
    (Finset.mem_univ a)
  rcases mul_eq_zero.mp ht with h | h
  · exact ha (star_eq_zero.mp h)
  · exact ha h

/-- An exact anchored Gram certificate. Only Hermiticity and squared Frobenius
mass one are required; trace one and positivity are not premises. -/
theorem anchored_square_identity (R : Matrix n n ℂ) (hR : R.IsHermitian)
    (hpurity : Matrix.trace (R * R) = 1) (a : n) :
    let Z := anchorMass R a • R - anchorOuter R a
    Matrix.trace (Zᴴ * Z) = 2 * anchorMass R a * anchorDefect R a := by
  dsimp only
  simp only [Matrix.conjTranspose_sub, Matrix.conjTranspose_smul, hR.eq,
    mass_star R hR a, outer_hermitian R hR a, Matrix.sub_mul, Matrix.mul_sub,
    Matrix.smul_mul, Matrix.mul_smul, Matrix.trace_sub, Matrix.trace_smul,
    smul_eq_mul, hpurity, outer_square, outer_trace, outer_cross_trace]
  rw [Matrix.trace_mul_comm (anchorOuter R a) R, outer_cross_trace]
  unfold anchorDefect anchorMass
  simp only [Matrix.sub_apply]
  ring

/-- The normalized column outer product is a rank-one orthogonal projector
whenever the chosen diagonal entry is nonzero. -/
theorem anchor_projection_properties (R : Matrix n n ℂ) (hR : R.IsHermitian)
    (a : n) (ha : R a a ≠ 0) :
    (anchorProjection R a).PosSemidef ∧
    anchorProjection R a * anchorProjection R a = anchorProjection R a ∧
    Matrix.trace (anchorProjection R a) = 1 ∧ (anchorProjection R a).rank = 1 := by
  have hr := mass_nonzero R hR a ha
  have hrpos : 0 < anchorMass R a := lt_of_le_of_ne (mass_nonnegative R hR a) hr.symm
  have houter : (anchorOuter R a).PosSemidef := by
    have he : anchorOuter R a =
        Matrix.vecMulVec (fun i => R i a) (star (fun i => R i a)) := by
      ext i j
      simp only [anchorOuter, Matrix.vecMulVec_apply, Pi.star_apply, hR.apply]
    rw [he]
    exact Matrix.posSemidef_vecMulVec_self_star _
  have hpsd : (anchorProjection R a).PosSemidef :=
    houter.smul (le_of_lt (RCLike.inv_pos_of_pos hrpos))
  have hid : anchorProjection R a * anchorProjection R a = anchorProjection R a := by
    unfold anchorProjection
    rw [Matrix.smul_mul, Matrix.mul_smul, outer_square]
    simp only [smul_smul]
    congr 1
    field_simp
  have ht : Matrix.trace (anchorProjection R a) = 1 := by
    rw [anchorProjection, Matrix.trace_smul, outer_trace]
    exact inv_mul_cancel₀ hr
  refine ⟨hpsd, hid, ht, ?_⟩
  have hRank := MUBResidual.trace_eq_rank_of_idempotent (anchorProjection R a) hid
  rw [ht] at hRank
  exact_mod_cast hRank.symm

/-- The explicit column projector has an exact distance controlled by one
diagonal cubic defect. No spectral decomposition is used. -/
theorem anchored_distance_identity (R : Matrix n n ℂ) (hR : R.IsHermitian)
    (hpurity : Matrix.trace (R * R) = 1) (a : n) (ha : R a a ≠ 0) :
    Matrix.trace ((R - anchorProjection R a)ᴴ * (R - anchorProjection R a)) =
      2 * anchorDefect R a / anchorMass R a := by
  have hr := mass_nonzero R hR a ha
  rcases anchor_projection_properties R hR a ha with ⟨hp, hid, ht, _⟩
  simp only [Matrix.conjTranspose_sub, hR.eq, hp.1.eq, Matrix.sub_mul,
    Matrix.mul_sub, Matrix.trace_sub, hpurity, hid, ht]
  rw [Matrix.trace_mul_comm (anchorProjection R a) R]
  simp only [anchorProjection, Matrix.mul_smul, Matrix.trace_smul, smul_eq_mul,
    outer_cross_trace, anchorDefect, Matrix.sub_apply]
  change 1 - (anchorMass R a)⁻¹ * (R * R * R) a a -
    ((anchorMass R a)⁻¹ * (R * R * R) a a - 1) =
      2 * (anchorMass R a - (R * R * R) a a) / anchorMass R a
  field_simp
  ring

/-- A single vanishing anchored defect detects rank-one positivity under
Hermiticity, purity one, and a nonzero anchor diagonal. -/
theorem anchored_defect_zero_iff (R : Matrix n n ℂ) (hR : R.IsHermitian)
    (hpurity : Matrix.trace (R * R) = 1) (a : n) (ha : R a a ≠ 0) :
    anchorDefect R a = 0 ↔ R.PosSemidef ∧ R * R = R ∧ R.rank = 1 := by
  constructor
  · intro hz
    have hdist := anchored_distance_identity R hR hpurity a ha
    rw [hz, mul_zero, zero_div] at hdist
    have heq := Matrix.trace_conjTranspose_mul_self_eq_zero_iff.mp hdist
    have hRP := sub_eq_zero.mp heq
    rw [hRP]
    rcases anchor_projection_properties R hR a ha with ⟨hp, hid, _, hr⟩
    exact ⟨hp, hid, hr⟩
  · rintro ⟨_, hid, _⟩
    simp [anchorDefect, hid]

/-- Under the anchored hypotheses, the cubic diagonal defect is nonnegative. -/
theorem anchored_defect_nonnegative (R : Matrix n n ℂ) (hR : R.IsHermitian)
    (hpurity : Matrix.trace (R * R) = 1) (a : n) (ha : R a a ≠ 0) :
    0 ≤ anchorDefect R a := by
  have hr := mass_nonzero R hR a ha
  have hp := (Matrix.posSemidef_conjTranspose_mul_self
    (R - anchorProjection R a)).trace_nonneg
  rw [anchored_distance_identity R hR hpurity a ha] at hp
  have hm := mul_nonneg (mass_nonnegative R hR a) hp
  have he : anchorMass R a * (2 * anchorDefect R a / anchorMass R a) =
      2 * anchorDefect R a := by field_simp
  rw [he] at hm
  have hs := mul_nonneg (show (0 : ℂ) ≤ (1 / 2 : ℂ) by norm_num [Complex.le_def]) hm
  convert hs using 1; ring

omit [DecidableEq n] in
private theorem diagonal_norm_le_mass (R : Matrix n n ℂ) (hR : R.IsHermitian)
    (a : n) : (Complex.normSq (R a a) : ℂ) ≤ anchorMass R a := by
  have hp (i : n) : 0 ≤ star (R i a) * R i a := star_mul_self_nonneg _
  have he : (∑ i, star (R i a) * R i a) = anchorMass R a := by
    change (Rᴴ * R) a a = _
    rw [hR.eq]
    rfl
  have hs := Finset.single_le_sum (fun i _ => hp i) (Finset.mem_univ a)
  rw [he] at hs
  simpa only [Complex.star_def, mul_comm, Complex.mul_conj] using hs

/-- An exact a posteriori distance estimate, written without division by the
anchor diagonal. For diagonal 1/d this becomes distance squared at most 2d²q. -/
theorem anchored_distance_weighted_bound (R : Matrix n n ℂ) (hR : R.IsHermitian)
    (hpurity : Matrix.trace (R * R) = 1) (a : n) (ha : R a a ≠ 0) :
    Matrix.trace ((R - anchorProjection R a)ᴴ * (R - anchorProjection R a)) *
      (Complex.normSq (R a a) : ℂ) ≤ 2 * anchorDefect R a := by
  have hr := mass_nonzero R hR a ha
  have hp := (Matrix.posSemidef_conjTranspose_mul_self
    (R - anchorProjection R a)).trace_nonneg
  have hm := mul_le_mul_of_nonneg_left (diagonal_norm_le_mass R hR a) hp
  calc
    _ ≤ Matrix.trace ((R - anchorProjection R a)ᴴ * (R - anchorProjection R a)) *
        anchorMass R a := hm
    _ = _ := by rw [anchored_distance_identity R hR hpurity a ha]; field_simp

/-- A single aggregate cubic inequality certifies every member of a finite
family, provided each member satisfies the explicit anchored purity hypotheses.
This does not establish infeasibility for any MUB domain. -/
theorem aggregate_defect_nonpositive_iff {b : Type*} [Fintype b]
    (R : b → Matrix n n ℂ) (a : n)
    (hHermitian : ∀ k, (R k).IsHermitian)
    (hpurity : ∀ k, Matrix.trace (R k * R k) = 1)
    (hanchor : ∀ k, R k a a ≠ 0) :
    (∑ k, anchorDefect (R k) a) ≤ 0 ↔
      ∀ k, (R k).PosSemidef ∧ R k * R k = R k ∧ (R k).rank = 1 := by
  have hn (k : b) := anchored_defect_nonnegative (R k) (hHermitian k)
    (hpurity k) a (hanchor k)
  constructor
  · intro hs
    have hz : (∑ k, anchorDefect (R k) a) = 0 :=
      le_antisymm hs (Finset.sum_nonneg (fun k _ => hn k))
    intro k
    apply (anchored_defect_zero_iff (R k) (hHermitian k) (hpurity k) a (hanchor k)).mp
    exact (Finset.sum_eq_zero_iff_of_nonneg (fun k _ => hn k)).mp hz k
      (Finset.mem_univ k)
  · intro hp
    have hz (k : b) : anchorDefect (R k) a = 0 :=
      (anchored_defect_zero_iff (R k) (hHermitian k) (hpurity k) a (hanchor k)).mpr (hp k)
    simp only [hz, Finset.sum_const_zero, le_refl]

/-- Half of the ordered sum of anchored principal 3-by-3 determinants.
Repeated indices contribute zero, while the two orders of each distinct pair
contribute the same principal determinant. -/
def anchoredMinorSum (R : Matrix n n ℂ) (a : n) : ℂ :=
  (1 / 2 : ℂ) * ∑ i, ∑ j, Matrix.det (R.submatrix ![a, i, j] ![a, i, j])

omit [DecidableEq n] in
/-- The anchored principal-minor Newton identity, valid for every square complex
matrix, without Hermiticity or positivity assumptions. -/
theorem anchored_minor_identity (R : Matrix n n ℂ) (a : n) :
    anchoredMinorSum R a = (R * R * R) a a -
      Matrix.trace R * (R * R) a a +
      ((Matrix.trace R ^ 2 - Matrix.trace (R * R)) / 2) * R a a := by
  have h1 : (∑ i, ∑ j, R a a * R i i * R j j) =
      R a a * Matrix.trace R * Matrix.trace R := by
    simp only [Matrix.trace, Matrix.diag_apply, Finset.sum_mul, Finset.mul_sum]
    exact Finset.sum_comm
  have h2 : (∑ i, ∑ j, R a a * R i j * R j i) =
      R a a * Matrix.trace (R * R) := by
    simp only [Matrix.trace, Matrix.diag_apply, Matrix.mul_apply, Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro i hi
    apply Finset.sum_congr rfl
    intro j hj
    ring
  have h3 : (∑ i, ∑ j, R a i * R i a * R j j) =
      (R * R) a a * Matrix.trace R := by
    simp only [Matrix.trace, Matrix.diag_apply, Matrix.mul_apply, Finset.sum_mul,
      Finset.mul_sum]
    exact Finset.sum_comm
  have h4 : (∑ i, ∑ j, R a i * R i j * R j a) = (R * R * R) a a := by
    rw [Matrix.mul_assoc]
    simp only [Matrix.mul_apply, Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro i hi
    apply Finset.sum_congr rfl
    intro j hj
    ring
  have h5 : (∑ i, ∑ j, R a j * R i a * R j i) = (R * R * R) a a := by
    rw [Finset.sum_comm, ← h4]
    apply Finset.sum_congr rfl
    intro j hj
    apply Finset.sum_congr rfl
    intro i hi
    ring
  have h6 : (∑ i, ∑ j, R a j * R i i * R j a) =
      Matrix.trace R * (R * R) a a := by
    simp only [Matrix.trace, Matrix.diag_apply, Matrix.mul_apply, Finset.sum_mul,
      Finset.mul_sum]
    rw [Finset.sum_comm]
    apply Finset.sum_congr rfl
    intro i hi
    apply Finset.sum_congr rfl
    intro j hj
    ring
  simp only [anchoredMinorSum, Matrix.det_fin_three, Matrix.submatrix_apply,
    Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.cons_val_two, Matrix.vecHead, Matrix.vecTail,
    Function.comp_apply, Matrix.cons_val_succ,
    Finset.sum_add_distrib, Finset.sum_sub_distrib]
  rw [h1, h2, h3, h4, h5, h6]
  ring

omit [DecidableEq n] in
/-- Under trace and purity one, the anchored principal-minor sum is exactly the
negative cubic diagonal defect. -/
theorem anchored_minor_sum_eq_neg_defect (R : Matrix n n ℂ)
    (htrace : Matrix.trace R = 1) (hpurity : Matrix.trace (R * R) = 1) (a : n) :
    anchoredMinorSum R a = -anchorDefect R a := by
  rw [anchored_minor_identity, htrace, hpurity]
  simp only [anchorDefect, Matrix.sub_apply]
  ring

/-- A single aggregate anchored principal-minor inequality is equivalent to
rank-one positivity for every member of the specified finite family. -/
theorem aggregate_minor_nonnegative_iff {b : Type*} [Fintype b]
    (R : b → Matrix n n ℂ) (a : n)
    (hHermitian : ∀ k, (R k).IsHermitian)
    (htrace : ∀ k, Matrix.trace (R k) = 1)
    (hpurity : ∀ k, Matrix.trace (R k * R k) = 1)
    (hanchor : ∀ k, R k a a ≠ 0) :
    0 ≤ (∑ k, anchoredMinorSum (R k) a) ↔
      ∀ k, (R k).PosSemidef ∧ R k * R k = R k ∧ (R k).rank = 1 := by
  simp only [anchored_minor_sum_eq_neg_defect _ (htrace _) (hpurity _),
    Finset.sum_neg_distrib, neg_nonneg]
  exact aggregate_defect_nonpositive_iff R a hHermitian hpurity hanchor

end MUBAnchoredPurity
