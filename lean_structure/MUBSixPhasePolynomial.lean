module

public import Mathlib.Analysis.Real.Sqrt
public import Mathlib.Tactic.FieldSimp
public import Mathlib.Tactic.Positivity
public import Mathlib.Tactic.Ring
public import Mathlib.Tactic.Linarith

@[expose] public section
noncomputable section

namespace MUBSixPhasePolynomial

def polynomialP (L : ℝ) : ℝ :=
  13 * L^5 - 12 * L^4 + 243 * L^3 - 705 * L^2 + 864 * L - 243

def polynomialQ (L : ℝ) : ℝ :=
  4 * L^7 + 3 * L^6 + 9 * L^5 + 435 * L^4 - 2142 * L^3 +
    4293 * L^2 - 4311 * L + 2349

def envelopeCenter (L : ℝ) : ℝ :=
  (13 * L^6 - 129 * L^5 + 351 * L^4 - 540 * L^3 +
    7209 * L^2 - 8019 * L + 2187) / (72 * L^3)

def envelopeVariance (L : ℝ) : ℝ :=
  ((L - 9)^3 * (L - 1)^3 * (L^2 - 30 * L + 9) *
    (L^2 - 3 * L + 9)^2) / (576 * L^6)

def targetGap (L : ℝ) : ℝ := 98 / 3 - envelopeCenter L

/-- The two exact positive-polynomial certificates for the multiplicity 3+2+1
rational envelope. This statement does not assume or prove a phase reduction. -/
theorem positive_polynomial_certificate (t : ℝ) (ht : 0 ≤ t) :
    0 < polynomialP (1 + t) ∧ 0 < polynomialQ (1 + t) := by
  have hp : polynomialP (1 + t) =
      13*t^5 + 53*t^4 + 325*t^3 + 82*t^2 + 200*t + 160 := by
    unfold polynomialP
    ring
  have hq : polynomialQ (1 + t) =
      4*t^7 + 31*t^6 + 111*t^5 + 609*t^4 +
        56*t^2*(t-1)^2 + 640*(t-1/4)^2 + 600 := by
    unfold polynomialQ
    ring
  rw [hp, hq]
  constructor <;> positivity

/-- Exact rational identities behind the upper bound; the only premise excludes
a zero denominator. -/
theorem rational_gap_identities (L : ℝ) (hL : L ≠ 0) :
    targetGap L = (9 - L) * polynomialP L / (72 * L^3) ∧
    targetGap L ^ 2 - envelopeVariance L =
      5 * (L - 9)^2 * polynomialQ L / (648 * L^3) := by
  unfold targetGap envelopeCenter envelopeVariance polynomialP polynomialQ
  constructor <;> field_simp <;> ring

/-- The rational 3+2+1 envelope is at most 98/3 on [1,9], with equality precisely
at the endpoint 9. This is only the algebraic envelope theorem; it does not
formalize the Lagrange-multiplier or phase-to-envelope arguments. -/
theorem sharp_envelope_bound (L : ℝ) (hlo : 1 ≤ L) (hhi : L ≤ 9) :
    envelopeCenter L + Real.sqrt (envelopeVariance L) ≤ 98 / 3 ∧
    (envelopeCenter L + Real.sqrt (envelopeVariance L) = 98 / 3 ↔ L = 9) := by
  have hL : 0 < L := lt_of_lt_of_le (by norm_num) hlo
  have ht : 0 ≤ L - 1 := sub_nonneg.mpr hlo
  have hpos := positive_polynomial_certificate (L - 1) ht
  have he : 1 + (L - 1) = L := by ring
  rw [he] at hpos
  rcases hpos with ⟨hp, hq⟩
  rcases rational_gap_identities L (ne_of_gt hL) with ⟨hg, hs⟩
  have hgap : 0 ≤ targetGap L := by
    rw [hg]
    exact div_nonneg (mul_nonneg (sub_nonneg.mpr hhi) hp.le) (by positivity)
  have hsq : envelopeVariance L ≤ targetGap L ^ 2 := by
    have hnonneg : 0 ≤ 5 * (L - 9)^2 * polynomialQ L / (648 * L^3) := by
      positivity
    linarith
  have hroot : Real.sqrt (envelopeVariance L) ≤ targetGap L :=
    (Real.sqrt_le_iff).mpr ⟨hgap, hsq⟩
  constructor
  · unfold targetGap at hroot
    linarith
  · constructor
    · intro heq
      by_contra hne
      have hstrict : 0 < 5 * (L - 9)^2 * polynomialQ L / (648 * L^3) := by
        have hz : 0 < (L - 9)^2 := sq_pos_of_ne_zero (sub_ne_zero.mpr hne)
        positivity
      have hgap_pos : 0 < targetGap L := by
        rw [hg]
        have hleft : 0 < 9 - L := sub_pos.mpr (lt_of_le_of_ne hhi hne)
        positivity
      have hroot_lt : Real.sqrt (envelopeVariance L) < targetGap L :=
        (Real.sqrt_lt' hgap_pos).mpr (by linarith)
      unfold targetGap at hroot_lt
      linarith
    · intro heq
      subst L
      norm_num [envelopeCenter, envelopeVariance]

end MUBSixPhasePolynomial
