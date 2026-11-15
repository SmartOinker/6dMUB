module

public import MUBIdentities
public import Mathlib.Data.Fin.VecNotation
public import Mathlib.Algebra.BigOperators.Fin
public import Mathlib.Tactic.FinCases
public import Mathlib.Tactic.NormNum

@[expose] public section

noncomputable section

namespace MUBQuantum

abbrev Qubit := Fin 2 → ℂ
abbrev Coefficients := Fin 3 → Qubit

def innerQ (u v : Qubit) : ℂ := star (u 0) * v 0 + star (u 1) * v 1
def weight (v : Coefficients) (k : Fin 3) : ℝ :=
  Complex.normSq (v k 0) + Complex.normSq (v k 1)
def totalNorm (v : Coefficients) : ℝ := ∑ k, weight v k
def overlap (v : Coefficients) (k : Fin 3) : ℂ :=
  if k = 0 then innerQ (v 1) (v 0)
  else if k = 1 then innerQ (v 2) (v 1)
  else innerQ (v 0) (v 2)
def overlapEnergy (v : Coefficients) : ℝ := ∑ k, Complex.normSq (overlap v k)

/-- Three cube-root phases in real coordinates, with r²=3 supplied to lemmas. -/
def phase (r : ℝ) (j : Fin 3) : ℂ :=
  if j = 0 then 1 else if j = 1 then ⟨-1 / 2, r / 2⟩ else ⟨-1 / 2, -r / 2⟩

/-- Matrix elements of Z, X, Y in that order. -/
def pauliForm (b : Fin 3) (u v : Qubit) : ℂ :=
  if b = 0 then star (u 0) * v 0 - star (u 1) * v 1
  else if b = 1 then star (u 0) * v 1 + star (u 1) * v 0
  else -Complex.I * star (u 0) * v 1 + Complex.I * star (u 1) * v 0

def imbalance (v : Coefficients) (b : Fin 3) : ℝ :=
  (∑ k, pauliForm b (v k) (v k)).re

def correlation (r : ℝ) (v : Coefficients) (b : Fin 3) : ℂ :=
  pauliForm b (v 1) (v 0) +
    phase r b * pauliForm b (v 2) (v 1) +
    star (phase r b) * pauliForm b (v 0) (v 2)

/-- The unnormalized qutrit eigenbasis amplitude for X Z^b. Dividing by √3
gives a normalized measurement amplitude when r²=3. -/
def amplitude (r : ℝ) (v : Coefficients) (b j : Fin 3) : Qubit := fun a =>
  v 0 a + phase r j * v 1 a + star (phase r b) * star (phase r j) * v 2 a

/-- Born probabilities for Z, X, Y qubit measurements after the qutrit
eigenbasis transform. The denominators incorporate amplitude normalizations. -/
def probability (r : ℝ) (v : Coefficients) (b j : Fin 3) (a : Fin 2) : ℝ :=
  let w := amplitude r v b j
  if b = 0 then Complex.normSq (w a) / 3
  else if b = 1 then
    if a = 0 then Complex.normSq (w 0 + w 1) / 6
    else Complex.normSq (w 0 - w 1) / 6
  else
    if a = 0 then Complex.normSq (w 0 - Complex.I * w 1) / 6
    else Complex.normSq (w 0 + Complex.I * w 1) / 6

/-- The homogeneous energy becomes the usual 18-probability error on unit states. -/
def measurementEnergy (r : ℝ) (v : Coefficients) : ℝ :=
  ∑ b, ∑ j, ∑ a, (probability r v b j a - totalNorm v / 6) ^ 2

theorem probability_nonnegative (r : ℝ) (v : Coefficients) (b j : Fin 3) (a : Fin 2) :
    0 ≤ probability r v b j a := by
  unfold probability
  split_ifs <;> exact div_nonneg (Complex.normSq_nonneg _) (by norm_num)

theorem pauli_diagonal_real (b : Fin 3) (v : Qubit) :
    (pauliForm b v v).im = 0 := by
  fin_cases b <;>
    simp [pauliForm, Complex.mul_im, Complex.mul_re,
      Complex.star_def, Complex.conj_re, Complex.conj_im] <;> ring


#print axioms probability_nonnegative
#print axioms pauli_diagonal_real

end MUBQuantum
