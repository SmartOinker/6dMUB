module

public import Mathlib.Data.Nat.Basic
public import Lean.Elab.Tactic.Omega

@[expose] public section

namespace MUBCubeCounts

/-- A nonnegative 3 by 3 count array with a common row, column, and
cyclic-difference diagonal sum has three constant antidiagonal classes.
The variables are listed in row-major order. -/
theorem balanced_counts_classes
    (a b c d e f g h i t : ℕ)
    (r0 : a + b + c = t) (r1 : d + e + f = t) (r2 : g + h + i = t)
    (c0 : a + d + g = t) (c1 : b + e + h = t) (_c2 : c + f + i = t)
    (d0 : a + e + i = t) (d1 : b + f + g = t) (_d2 : c + d + h = t) :
    a = f ∧ f = h ∧ b = d ∧ d = i ∧ c = e ∧ e = g := by
  omega

/-- If the common margin is positive, one of the three constant classes
contains three positive counts. The quantum six-row application sets t=2. -/
theorem balanced_counts_positive_class
    (a b c d e f g h i t : ℕ) (ht : 0 < t)
    (r0 : a + b + c = t) (r1 : d + e + f = t) (r2 : g + h + i = t)
    (c0 : a + d + g = t) (c1 : b + e + h = t) (c2 : c + f + i = t)
    (d0 : a + e + i = t) (d1 : b + f + g = t) (d2 : c + d + h = t) :
    (0 < a ∧ 0 < f ∧ 0 < h) ∨
    (0 < b ∧ 0 < d ∧ 0 < i) ∨
    (0 < c ∧ 0 < e ∧ 0 < g) := by
  have hc := balanced_counts_classes a b c d e f g h i t
    r0 r1 r2 c0 c1 c2 d0 d1 d2
  omega

#print axioms balanced_counts_classes
#print axioms balanced_counts_positive_class

end MUBCubeCounts

