module

public import Mathlib.Analysis.Complex.Basic
public import Mathlib.Tactic.LinearCombination
public import Mathlib.Tactic.Ring
public import Mathlib.Tactic.NormNum
public import Mathlib.Algebra.BigOperators.Fin
public import Mathlib.LinearAlgebra.Matrix.Hermitian

@[expose] public section
noncomputable section

namespace MUBCubicGram

def thirdElementary (a b c d e f : ℂ) : ℂ :=
  a * b * c +
    a * b * d +
    a * b * e +
    a * b * f +
    a * c * d +
    a * c * e +
    a * c * f +
    a * d * e +
    a * d * f +
    a * e * f +
    b * c * d +
    b * c * e +
    b * c * f +
    b * d * e +
    b * d * f +
    b * e * f +
    c * d * e +
    c * d * f +
    c * e * f +
    d * e * f

/-- Newton's degree-three identity specialized to six numbers of sum zero. -/
theorem six_cubes_eq_three_elementary (a b c d e f : ℂ)
    (hs : a + b + c + d + e + f = 0) :
    a^3 + b^3 + c^3 + d^3 + e^3 + f^3 = 3 * thirdElementary a b c d e f := by
  unfold thirdElementary
  linear_combination ((a + b + c + d + e + f)^2 - 3 * (a * b + a * c + a * d + a * e + a * f + b * c + b * d + b * e + b * f + c * d + c * e + c * f + d * e + d * f + e * f)) * hs

/-- The middle elementary symmetric polynomial of six unit phases is
self-conjugate up to their total product. -/
theorem third_elementary_self_conjugate (a b c d e f : ℂ)
    (ha : a * (starRingEnd ℂ) a = 1)
    (hb : b * (starRingEnd ℂ) b = 1)
    (hc : c * (starRingEnd ℂ) c = 1)
    (hd : d * (starRingEnd ℂ) d = 1)
    (he : e * (starRingEnd ℂ) e = 1)
    (hf : f * (starRingEnd ℂ) f = 1) :
    thirdElementary a b c d e f =
      (a*b*c*d*e*f) * (starRingEnd ℂ) (thirdElementary a b c d e f) := by
  have h012 : (a*b*c*d*e*f) * (starRingEnd ℂ) (a * b * c) = d * e * f := by
    calc
      _ = (a * (starRingEnd ℂ) a) * (b * (starRingEnd ℂ) b) * (c * (starRingEnd ℂ) c) * (d * e * f) := by
        simp only [map_mul]
        ring
      _ = _ := by rw [ha, hb, hc]; ring
  have h013 : (a*b*c*d*e*f) * (starRingEnd ℂ) (a * b * d) = c * e * f := by
    calc
      _ = (a * (starRingEnd ℂ) a) * (b * (starRingEnd ℂ) b) * (d * (starRingEnd ℂ) d) * (c * e * f) := by
        simp only [map_mul]
        ring
      _ = _ := by rw [ha, hb, hd]; ring
  have h014 : (a*b*c*d*e*f) * (starRingEnd ℂ) (a * b * e) = c * d * f := by
    calc
      _ = (a * (starRingEnd ℂ) a) * (b * (starRingEnd ℂ) b) * (e * (starRingEnd ℂ) e) * (c * d * f) := by
        simp only [map_mul]
        ring
      _ = _ := by rw [ha, hb, he]; ring
  have h015 : (a*b*c*d*e*f) * (starRingEnd ℂ) (a * b * f) = c * d * e := by
    calc
      _ = (a * (starRingEnd ℂ) a) * (b * (starRingEnd ℂ) b) * (f * (starRingEnd ℂ) f) * (c * d * e) := by
        simp only [map_mul]
        ring
      _ = _ := by rw [ha, hb, hf]; ring
  have h023 : (a*b*c*d*e*f) * (starRingEnd ℂ) (a * c * d) = b * e * f := by
    calc
      _ = (a * (starRingEnd ℂ) a) * (c * (starRingEnd ℂ) c) * (d * (starRingEnd ℂ) d) * (b * e * f) := by
        simp only [map_mul]
        ring
      _ = _ := by rw [ha, hc, hd]; ring
  have h024 : (a*b*c*d*e*f) * (starRingEnd ℂ) (a * c * e) = b * d * f := by
    calc
      _ = (a * (starRingEnd ℂ) a) * (c * (starRingEnd ℂ) c) * (e * (starRingEnd ℂ) e) * (b * d * f) := by
        simp only [map_mul]
        ring
      _ = _ := by rw [ha, hc, he]; ring
  have h025 : (a*b*c*d*e*f) * (starRingEnd ℂ) (a * c * f) = b * d * e := by
    calc
      _ = (a * (starRingEnd ℂ) a) * (c * (starRingEnd ℂ) c) * (f * (starRingEnd ℂ) f) * (b * d * e) := by
        simp only [map_mul]
        ring
      _ = _ := by rw [ha, hc, hf]; ring
  have h034 : (a*b*c*d*e*f) * (starRingEnd ℂ) (a * d * e) = b * c * f := by
    calc
      _ = (a * (starRingEnd ℂ) a) * (d * (starRingEnd ℂ) d) * (e * (starRingEnd ℂ) e) * (b * c * f) := by
        simp only [map_mul]
        ring
      _ = _ := by rw [ha, hd, he]; ring
  have h035 : (a*b*c*d*e*f) * (starRingEnd ℂ) (a * d * f) = b * c * e := by
    calc
      _ = (a * (starRingEnd ℂ) a) * (d * (starRingEnd ℂ) d) * (f * (starRingEnd ℂ) f) * (b * c * e) := by
        simp only [map_mul]
        ring
      _ = _ := by rw [ha, hd, hf]; ring
  have h045 : (a*b*c*d*e*f) * (starRingEnd ℂ) (a * e * f) = b * c * d := by
    calc
      _ = (a * (starRingEnd ℂ) a) * (e * (starRingEnd ℂ) e) * (f * (starRingEnd ℂ) f) * (b * c * d) := by
        simp only [map_mul]
        ring
      _ = _ := by rw [ha, he, hf]; ring
  have h123 : (a*b*c*d*e*f) * (starRingEnd ℂ) (b * c * d) = a * e * f := by
    calc
      _ = (b * (starRingEnd ℂ) b) * (c * (starRingEnd ℂ) c) * (d * (starRingEnd ℂ) d) * (a * e * f) := by
        simp only [map_mul]
        ring
      _ = _ := by rw [hb, hc, hd]; ring
  have h124 : (a*b*c*d*e*f) * (starRingEnd ℂ) (b * c * e) = a * d * f := by
    calc
      _ = (b * (starRingEnd ℂ) b) * (c * (starRingEnd ℂ) c) * (e * (starRingEnd ℂ) e) * (a * d * f) := by
        simp only [map_mul]
        ring
      _ = _ := by rw [hb, hc, he]; ring
  have h125 : (a*b*c*d*e*f) * (starRingEnd ℂ) (b * c * f) = a * d * e := by
    calc
      _ = (b * (starRingEnd ℂ) b) * (c * (starRingEnd ℂ) c) * (f * (starRingEnd ℂ) f) * (a * d * e) := by
        simp only [map_mul]
        ring
      _ = _ := by rw [hb, hc, hf]; ring
  have h134 : (a*b*c*d*e*f) * (starRingEnd ℂ) (b * d * e) = a * c * f := by
    calc
      _ = (b * (starRingEnd ℂ) b) * (d * (starRingEnd ℂ) d) * (e * (starRingEnd ℂ) e) * (a * c * f) := by
        simp only [map_mul]
        ring
      _ = _ := by rw [hb, hd, he]; ring
  have h135 : (a*b*c*d*e*f) * (starRingEnd ℂ) (b * d * f) = a * c * e := by
    calc
      _ = (b * (starRingEnd ℂ) b) * (d * (starRingEnd ℂ) d) * (f * (starRingEnd ℂ) f) * (a * c * e) := by
        simp only [map_mul]
        ring
      _ = _ := by rw [hb, hd, hf]; ring
  have h145 : (a*b*c*d*e*f) * (starRingEnd ℂ) (b * e * f) = a * c * d := by
    calc
      _ = (b * (starRingEnd ℂ) b) * (e * (starRingEnd ℂ) e) * (f * (starRingEnd ℂ) f) * (a * c * d) := by
        simp only [map_mul]
        ring
      _ = _ := by rw [hb, he, hf]; ring
  have h234 : (a*b*c*d*e*f) * (starRingEnd ℂ) (c * d * e) = a * b * f := by
    calc
      _ = (c * (starRingEnd ℂ) c) * (d * (starRingEnd ℂ) d) * (e * (starRingEnd ℂ) e) * (a * b * f) := by
        simp only [map_mul]
        ring
      _ = _ := by rw [hc, hd, he]; ring
  have h235 : (a*b*c*d*e*f) * (starRingEnd ℂ) (c * d * f) = a * b * e := by
    calc
      _ = (c * (starRingEnd ℂ) c) * (d * (starRingEnd ℂ) d) * (f * (starRingEnd ℂ) f) * (a * b * e) := by
        simp only [map_mul]
        ring
      _ = _ := by rw [hc, hd, hf]; ring
  have h245 : (a*b*c*d*e*f) * (starRingEnd ℂ) (c * e * f) = a * b * d := by
    calc
      _ = (c * (starRingEnd ℂ) c) * (e * (starRingEnd ℂ) e) * (f * (starRingEnd ℂ) f) * (a * b * d) := by
        simp only [map_mul]
        ring
      _ = _ := by rw [hc, he, hf]; ring
  have h345 : (a*b*c*d*e*f) * (starRingEnd ℂ) (d * e * f) = a * b * c := by
    calc
      _ = (d * (starRingEnd ℂ) d) * (e * (starRingEnd ℂ) e) * (f * (starRingEnd ℂ) f) * (a * b * c) := by
        simp only [map_mul]
        ring
      _ = _ := by rw [hd, he, hf]; ring
  unfold thirdElementary
  simp only [map_add, mul_add]
  rw [h012, h013, h014, h015, h023, h024, h025, h034, h035, h045, h123, h124, h125, h134, h135, h145, h234, h235, h245, h345]
  ring

/-- Exact reciprocal cubic-moment identity for six unit phases of sum zero.
This applies to entrywise ratios of distinct rows of a phase Hadamard. -/
theorem six_unit_cubic_moment_self_conjugate (a b c d e f : ℂ)
    (ha : a * (starRingEnd ℂ) a = 1)
    (hb : b * (starRingEnd ℂ) b = 1)
    (hc : c * (starRingEnd ℂ) c = 1)
    (hd : d * (starRingEnd ℂ) d = 1)
    (he : e * (starRingEnd ℂ) e = 1)
    (hf : f * (starRingEnd ℂ) f = 1)
    (hs : a + b + c + d + e + f = 0) :
    a^3 + b^3 + c^3 + d^3 + e^3 + f^3 =
      (a*b*c*d*e*f) * (starRingEnd ℂ) (a^3 + b^3 + c^3 + d^3 + e^3 + f^3) := by
  have hn := six_cubes_eq_three_elementary a b c d e f hs
  have he := third_elementary_self_conjugate a b c d e f ha hb hc hd he hf
  calc
    _ = 3 * thirdElementary a b c d e f := hn
    _ = 3 * ((a*b*c*d*e*f) * (starRingEnd ℂ) (thirdElementary a b c d e f)) := by rw [← he]
    _ = (a*b*c*d*e*f) * (starRingEnd ℂ) (3 * thirdElementary a b c d e f) := by
      simp only [map_mul, map_ofNat]
      ring
    _ = _ := by rw [← hn]

/-- Function-indexed version for a six-point unit-phase distribution. -/
theorem six_phase_moment (z : Fin 6 → ℂ)
    (hu : ∀ k, z k * (starRingEnd ℂ) (z k) = 1)
    (hs : ∑ k, z k = 0) :
    ∑ k, z k ^ 3 = (∏ k, z k) * (starRingEnd ℂ) (∑ k, z k ^ 3) := by
  have hs' : z 0 + z 1 + z 2 + z 3 + z 4 + z 5 = 0 := by
    simpa [Fin.sum_univ_succ, add_assoc] using hs
  have hh := six_unit_cubic_moment_self_conjugate
    (z 0) (z 1) (z 2) (z 3) (z 4) (z 5)
    (hu 0) (hu 1) (hu 2) (hu 3) (hu 4) (hu 5) hs'
  simpa [Fin.sum_univ_succ, Fin.prod_univ_succ, add_assoc, mul_assoc] using hh

/-- The cubic overlap of two orthogonal unit-phase rows has a phase fixed
by the products of their entries. -/
theorem cubic_overlap_phase (x y : Fin 6 → ℂ)
    (hx : ∀ k, x k * (starRingEnd ℂ) (x k) = 1)
    (hy : ∀ k, y k * (starRingEnd ℂ) (y k) = 1)
    (hxy : ∑ k, x k * (starRingEnd ℂ) (y k) = 0) :
    (∑ k, x k ^ 3 * (starRingEnd ℂ) (y k ^ 3)) =
      ((∏ k, x k) * (starRingEnd ℂ) (∏ k, y k)) *
        (starRingEnd ℂ) (∑ k, x k ^ 3 * (starRingEnd ℂ) (y k ^ 3)) := by
  have hu (k : Fin 6) :
      (x k * (starRingEnd ℂ) (y k)) *
        (starRingEnd ℂ) (x k * (starRingEnd ℂ) (y k)) = 1 := by
    calc
      _ = (x k * (starRingEnd ℂ) (x k)) *
          (y k * (starRingEnd ℂ) (y k)) := by
        simp only [map_mul]
        simp
        ring
      _ = 1 := by rw [hx k, hy k]; ring
  have hh := six_phase_moment (fun k => x k * (starRingEnd ℂ) (y k)) hu hxy
  simpa only [mul_pow, ← map_pow, Finset.prod_mul_distrib, ← map_prod] using hh

open Matrix

def entrywiseCube (H : Matrix (Fin 6) (Fin 6) ℂ) : Matrix (Fin 6) (Fin 6) ℂ :=
  fun i j => H i j ^ 3

/-- Direct matrix corollary. No classification, non-Tao premise, or spectral
pairing assumption is used. This is a phase-reality statement only. -/
theorem hadamard_cubic_gram_phase
    (H : Matrix (Fin 6) (Fin 6) ℂ)
    (hu : ∀ i k, H i k * (starRingEnd ℂ) (H i k) = 1)
    (ho : H * Hᴴ = (6 : ℂ) • (1 : Matrix (Fin 6) (Fin 6) ℂ))
    (i j : Fin 6) :
    (entrywiseCube H * (entrywiseCube H)ᴴ) i j =
      ((∏ k, H i k) * (starRingEnd ℂ) (∏ k, H j k)) *
        (starRingEnd ℂ) ((entrywiseCube H * (entrywiseCube H)ᴴ) i j) := by
  by_cases hij : i = j
  · subst j
    have hp : (∏ k, H i k) * (starRingEnd ℂ) (∏ k, H i k) = 1 := by
      rw [map_prod, ← Finset.prod_mul_distrib]
      simp only [hu, Finset.prod_const_one]
    have hc (k : Fin 6) : H i k ^ 3 * (starRingEnd ℂ) (H i k ^ 3) = 1 := by
      rw [map_pow, ← mul_pow, hu]
      norm_num
    have hg : (entrywiseCube H * (entrywiseCube H)ᴴ) i i = 6 := by
      change (∑ k, H i k ^ 3 * (starRingEnd ℂ) (H i k ^ 3)) = 6
      simp only [hc]
      norm_num
    rw [hg, hp]
    simp only [map_ofNat, one_mul]
  · have hxy : ∑ k, H i k * (starRingEnd ℂ) (H j k) = 0 := by
      have hh := congrArg (fun M : Matrix (Fin 6) (Fin 6) ℂ => M i j) ho
      simpa [Matrix.mul_apply, Matrix.conjTranspose_apply, Matrix.one_apply, hij] using hh
    simpa only [Matrix.mul_apply, Matrix.conjTranspose_apply, entrywiseCube, starRingEnd_apply] using
      cubic_overlap_phase (H i) (H j) (hu i) (hu j) hxy

#print axioms six_cubes_eq_three_elementary
#print axioms third_elementary_self_conjugate
#print axioms six_unit_cubic_moment_self_conjugate
#print axioms six_phase_moment
#print axioms cubic_overlap_phase
#print axioms hadamard_cubic_gram_phase

end MUBCubicGram

