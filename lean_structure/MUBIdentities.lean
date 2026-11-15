module

public import Mathlib.Basic.Complex.Basic
public import Mathlib.Algebra.Module.LinearMap.Basic
public import Mathlib.Algebra.Order.BigOperators.Group.Finset
public import Mathlib.Tactic.Linarith
public import Mathlib.Tactic.Ring

@[expose] public section

namespace MUBGap

/-- Splitting a joint qubit/qutrit probability into its sum and difference. -/
theorem joint_pair_deviation (Q D : ℝ) :
    ((Q + D) / 2 - 1 / 6) ^ 2 + ((Q - D) / 2 - 1 / 6) ^ 2 =
      (Q - 1 / 3) ^ 2 / 2 + D ^ 2 / 2 := by
  ring

/-- Three-point real Fourier Parseval in coordinates. The nonconstant Fourier
coefficient has real part x-(y+z)/2 and imaginary part r*(y-z)/2, with r²=3.
No choice of a quantum measurement or spectral operator is made here. -/
theorem three_point_parseval (x y z r : ℝ) (hr : r ^ 2 = 3) :
    (x + y + z) ^ 2 +
      2 * ((x - (y + z) / 2) ^ 2 + (r * (y - z) / 2) ^ 2) =
      3 * (x ^ 2 + y ^ 2 + z ^ 2) := by
  ring_nf
  rw [hr]
  ring

/-- The qubit Fierz identity in coordinates. The three terms on the left are
the squared moduli of u†Zv, u†Xv and u†Yv. This is an unconditional identity
for arbitrary vectors u,v in complex dimension two. -/
theorem qubit_fierz (u₀ u₁ v₀ v₁ : ℂ) :
    Complex.normSq (star u₀ * v₀ - star u₁ * v₁) +
      Complex.normSq (star u₀ * v₁ + star u₁ * v₀) +
      Complex.normSq (-Complex.I * star u₀ * v₁ + Complex.I * star u₁ * v₀) =
    2 * (Complex.normSq u₀ + Complex.normSq u₁) *
      (Complex.normSq v₀ + Complex.normSq v₁) -
      Complex.normSq (star u₀ * v₀ + star u₁ * v₁) := by
  simp only [Complex.normSq_apply, Complex.add_re, Complex.add_im,
    Complex.sub_re, Complex.sub_im, Complex.mul_re, Complex.mul_im,
    Complex.star_def, Complex.conj_re, Complex.conj_im,
    Complex.neg_re, Complex.neg_im, Complex.I_re, Complex.I_im]
  ring

/-- The logical separating-functional step. `square` may represent homogeneous
quadratic polynomials squared, but no concrete moment matrix is asserted here.
Nonnegativity of the functional on these squares is an explicit premise. -/
theorem separating_functional_no_sos
    {V W : Type*} [AddCommGroup V] [Module ℝ V]
    (L : V →ₗ[ℝ] ℝ) (square : W → V) (energy normPower : V)
    (hpos : ∀ w, 0 ≤ L (square w))
    (henergy : L energy = 0) (hnorm : L normPower = 1)
    {gamma : ℝ} (hgamma : 0 < gamma) (n : ℕ) (q : Fin n → W) :
    energy - gamma • normPower ≠ ∑ k, square (q k) := by
  intro heq
  have hsum : 0 ≤ ∑ k, L (square (q k)) :=
    Finset.sum_nonneg fun k _ => hpos (q k)
  have hL := congrArg L heq
  simp only [map_sub, map_smul, map_sum, henergy, hnorm, smul_eq_mul,
    mul_one, zero_sub] at hL
  linarith only [hsum, hL, hgamma]

#print axioms qubit_fierz
#print axioms joint_pair_deviation
#print axioms three_point_parseval
#print axioms separating_functional_no_sos

end MUBGap
