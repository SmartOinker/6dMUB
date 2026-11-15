module
public import MUBBalancedSpectralEnvelope
public import Mathlib.LinearAlgebra.Matrix.Trace
public import Mathlib.LinearAlgebra.Matrix.Notation
public import Mathlib.Data.Fintype.Pi
@[expose] public section
noncomputable section
namespace MUBBalancedSmallTables
open Matrix
abbrev Graph := Fin 5
abbrev SignChoice := Fin 4 → Bool

def epsilon (e : SignChoice) (i : Fin 4) : ℚ := if e i then 1 else -1

def graphGram (g : Graph) : Matrix (Fin 4) (Fin 4) ℚ :=
  match g.val with
  | 0 => !![6, 2, -2, -2;
      2, 6, -2, -2;
      -2, -2, 6, -2;
      -2, -2, -2, 6]
  | 1 => !![6, 2, 2, -2;
      2, 6, -2, -2;
      2, -2, 6, -2;
      -2, -2, -2, 6]
  | 2 => !![6, 2, -2, -2;
      2, 6, -2, -2;
      -2, -2, 6, 2;
      -2, -2, 2, 6]
  | 3 => !![6, 2, 2, -2;
      2, 6, 2, -2;
      2, 2, 6, -2;
      -2, -2, -2, 6]
  | _ => !![6, 2, -2, -2;
      2, 6, 2, -2;
      -2, 2, 6, 2;
      -2, -2, 2, 6]

def graphInverse (g : Graph) : Matrix (Fin 4) (Fin 4) ℚ :=
  match g.val with
  | 0 => !![(1/4), 0, (1/8), (1/8);
      0, (1/4), (1/8), (1/8);
      (1/8), (1/8), (5/16), (3/16);
      (1/8), (1/8), (3/16), (5/16)]
  | 1 => !![(1/4), (-1/8), (-1/8), 0;
      (-1/8), (5/16), (3/16), (1/8);
      (-1/8), (3/16), (5/16), (1/8);
      0, (1/8), (1/8), (1/4)]
  | 2 => !![(5/24), (-1/24), (1/24), (1/24);
      (-1/24), (5/24), (1/24), (1/24);
      (1/24), (1/24), (5/24), (-1/24);
      (1/24), (1/24), (-1/24), (5/24)]
  | 3 => !![(5/24), (-1/24), (-1/24), (1/24);
      (-1/24), (5/24), (-1/24), (1/24);
      (-1/24), (-1/24), (5/24), (1/24);
      (1/24), (1/24), (1/24), (5/24)]
  | _ => !![(1/4), (-1/8), (1/8), 0;
      (-1/8), (5/16), (-3/16), (1/8);
      (1/8), (-3/16), (5/16), (-1/8);
      0, (1/8), (-1/8), (1/4)]

def tailIndex (i : Fin 5) : Fin 4 := ⟨(i.val+3)%4, Nat.mod_lt _ (by decide)⟩
def extension (g : Graph) (e : SignChoice) : Matrix (Fin 5) (Fin 5) ℚ := fun i j =>
  if i=0 then (if j=0 then 6 else 2*epsilon e (tailIndex j))
  else if j=0 then 2*epsilon e (tailIndex i)
  else graphGram g (tailIndex i) (tailIndex j)
def centeringWeight : Matrix (Fin 5) (Fin 5) ℚ := fun i j =>
  (if i=j then (if i=0 then 2 else 1) else 0) - (if i=0 ∨ j=0 then 0 else 1/6)
def schur (g : Graph) (e : SignChoice) : ℚ :=
  6-4*(∑ i, ∑ j, epsilon e i * graphInverse g i j * epsilon e j)
def moment (g : Graph) (e : SignChoice) (k : ℕ) : ℚ :=
  Matrix.trace ((extension g e * centeringWeight)^k)
def coeffA (g : Graph) (e : SignChoice) : ℚ :=
  5*(-9/4)+(99/48)*moment g e 1+(-57/192)*moment g e 2+(9/768)*moment g e 3
def coeffB (g : Graph) (e : SignChoice) : ℚ :=
  5*(7/4)+(-47/48)*moment g e 1+(31/192)*moment g e 2+(-5/768)*moment g e 3
def tableBound (g : Graph) : ℚ :=
  match g.val with
  | 0 => 7993/648
  | 1 => 15637/1296
  | 2 => 979/81
  | 3 => 1717/144
  | _ => 189/16

set_option maxHeartbeats 8000000
set_option maxRecDepth 100000

theorem graph_inverse_certificate (g : Graph) : graphGram g * graphInverse g = 1 := by
  revert g
  decide +kernel

theorem positive_extension_certificate (g : Graph) (e : SignChoice) (h : 0 < schur g e) :
    0 < coeffB g e ∧ coeffA g e + coeffB g e*(7/4) ≤ tableBound g := by
  revert g e h
  decide +kernel

theorem table_bound_lt (g : Graph) : tableBound g < 25/2 := by
  revert g
  decide +kernel

def expectedPositiveCount (g : Graph) : ℕ := if g=2 ∨ g=3 then 16 else 10

theorem positive_extension_counts (g : Graph) :
    (∑ e : SignChoice, if 0 < schur g e then (1 : ℕ) else 0) = expectedPositiveCount g := by
  revert g
  decide +kernel

theorem total_positive_extensions :
    (∑ g : Graph, ∑ e : SignChoice, if 0 < schur g e then (1 : ℕ) else 0) = 62 := by
  decide +kernel

theorem one_edge_moment_rows (e : SignChoice) (h : 0 < schur 0 e) :
    (moment 0 e 1 = 104/3 ∧ moment 0 e 2 = 3424/9 ∧ moment 0 e 3 = 134144/27) ∨
    (moment 0 e 1 = 104/3 ∧ moment 0 e 2 = 3520/9 ∧ moment 0 e 3 = 147392/27) ∨
    (moment 0 e 1 = 104/3 ∧ moment 0 e 2 = 3520/9 ∧ moment 0 e 3 = 137024/27) := by
  revert e h
  decide +kernel

/-- The sum of the cubic majorant over five spectral variables, written in terms
of the actual first three trace moments of the rational centered extension. -/
def momentMajorant (g : Graph) (e : SignChoice) (r : ℝ) : ℝ :=
  5*(-9+7*r)/4 + (99-47*r)/48*(moment g e 1 : ℝ) +
    (-57+31*r)/192*(moment g e 2 : ℝ) + (9-5*r)/768*(moment g e 3 : ℝ)

theorem moment_majorant_identity (g : Graph) (e : SignChoice) (r : ℝ) :
    momentMajorant g e r = (coeffA g e : ℝ) + (coeffB g e : ℝ)*r := by
  simp only [momentMajorant, coeffA, coeffB, Rat.cast_add, Rat.cast_mul, Rat.cast_neg,
    Rat.cast_div, Rat.cast_ofNat]
  ring

/-- All five graph forms and all sixteen sign extensions are covered. The
positive Schur filter is a structural condition, not the desired trace bound. -/
theorem actual_moment_majorant_bound (g : Graph) (e : SignChoice) (h : 0 < schur g e) :
    momentMajorant g e (Real.sqrt 3) < (tableBound g : ℝ) ∧
      momentMajorant g e (Real.sqrt 3) < 25/2 := by
  obtain ⟨hb, hab⟩ := positive_extension_certificate g e h
  have hbr : (0 : ℝ) < (coeffB g e : ℝ) := by exact_mod_cast hb
  have habr : (coeffA g e : ℝ) + (coeffB g e : ℝ)*(7/4) ≤ (tableBound g : ℝ) := by
    have hh := (Rat.cast_le (K := ℝ)).mpr hab
    norm_num at hh ⊢
    exact hh
  have htr : (tableBound g : ℝ) < 25/2 := by
    have hh := (Rat.cast_lt (K := ℝ)).mpr (table_bound_lt g)
    norm_num at hh ⊢
    exact hh
  have hs := Real.sq_sqrt (show (0 : ℝ) ≤ 3 by norm_num)
  have hs0 := Real.sqrt_nonneg (3 : ℝ)
  have hsb : Real.sqrt 3 < 7/4 := by nlinarith
  rw [moment_majorant_identity]
  constructor <;> nlinarith

/-- The scalar majorant summed over five nonnegative spectral variables is
controlled by the actual rational matrix moments. This identity does not assume
any spectral interpretation of those variables. -/
theorem majorant_sum_of_moments (g : Graph) (e : SignChoice) (r : ℝ)
    (x : Fin 5 → ℝ)
    (h1 : ∑ i, x i = (moment g e 1 : ℝ))
    (h2 : ∑ i, (x i)^2 = (moment g e 2 : ℝ))
    (h3 : ∑ i, (x i)^3 = (moment g e 3 : ℝ)) :
    (∑ i, MUBBalancedSpectralEnvelope.upperPolynomial r (x i)) =
      momentMajorant g e r := by
  calc
    _ = 5*(-9+7*r)/4 + (99-47*r)/48*(∑ i, x i) +
        (-57+31*r)/192*(∑ i, (x i)^2) + (9-5*r)/768*(∑ i, (x i)^3) := by
      simp [MUBBalancedSpectralEnvelope.upperPolynomial, Fin.sum_univ_succ]
      ring
    _ = _ := by rw [h1, h2, h3]; rfl

/-- Conditional spectral-list consequence. Its remaining hypotheses are the
first three moment identities, not a nuclear-norm or trace-majorant bound. -/
theorem sqrt_sum_lt_of_actual_moments (g : Graph) (e : SignChoice)
    (h : 0 < schur g e) (x : Fin 5 → ℝ) (hx : ∀ i, 0 ≤ x i)
    (h1 : ∑ i, x i = (moment g e 1 : ℝ))
    (h2 : ∑ i, (x i)^2 = (moment g e 2 : ℝ))
    (h3 : ∑ i, (x i)^3 = (moment g e 3 : ℝ)) :
    (∑ i, Real.sqrt (x i)) < 25/2 := by
  have hs : (∑ i, Real.sqrt (x i)) ≤
      ∑ i, MUBBalancedSpectralEnvelope.upperPolynomial (Real.sqrt 3) (x i) :=
    Finset.sum_le_sum (fun i _ => MUBBalancedSpectralEnvelope.sqrt_majorant (x i) (hx i))
  rw [majorant_sum_of_moments g e _ x h1 h2 h3] at hs
  exact lt_of_le_of_lt hs (actual_moment_majorant_bound g e h).2

end MUBBalancedSmallTables
