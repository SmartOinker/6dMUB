module
public import MUBQuantumTransport
@[expose] public section
noncomputable section
namespace MUBMixedTransport
open Matrix MUBTensorFrame MUBQuantumTransport
variable {n : Type*} [Fintype n] [DecidableEq n]

def mixedOperator (A B : Matrix n n ℂ) : Matrix n n ℂ :=
  let V := repetition n
  let F := repeatedFrame A
  let G := repeatedFrame B
  partialTrace12 ((V * Vᴴ) * (F * Fᴴ) * (G * Gᴴ))

theorem repeated_frame_overlap (A B : Matrix n n ℂ) :
    (repeatedFrame A)ᴴ * repeatedFrame B = cube (Aᴴ * B) := by
  have he (U : Matrix n n ℂ) (a b i j : n) :
      repeatedFrame U (a,b,i) j = U a j * U b j * U i j := by
    rw [repeatedFrame, repetition_mul_right]
    rfl
  ext i j
  change _ = ((Aᴴ * B) i j)^3
  simp only [Matrix.mul_apply, Matrix.conjTranspose_apply,
    Fintype.sum_prod_type, he, star_mul]
  simp only [pow_succ, pow_zero, Finset.sum_mul, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro a ha
  apply Finset.sum_congr rfl
  intro b hb
  apply Finset.sum_congr rfl
  intro c hc
  ring

theorem mixed_projector_factorization (A B : Matrix n n ℂ) :
    let V := repetition n
    let F := repeatedFrame A
    let G := repeatedFrame B
    (V * Vᴴ) * (F * Fᴴ) * (G * Gᴴ) =
      V * (cube A * cube (Aᴴ * B)) * Gᴴ := by
  dsimp only
  have hc : (repetition n)ᴴ * repeatedFrame A = cube A := by
    rw [repeatedFrame, ← Matrix.mul_assoc, repetition_compression]
    rfl
  calc
    _ = repetition n * (((repetition n)ᴴ * repeatedFrame A) *
        ((repeatedFrame A)ᴴ * repeatedFrame B)) * (repeatedFrame B)ᴴ := by
      simp only [Matrix.mul_assoc]
    _ = _ := by rw [hc, repeated_frame_overlap]

theorem mixed_partial_trace (A B : Matrix n n ℂ) :
    mixedOperator A B = transport B (cube A * cube (Aᴴ * B)) := by
  dsimp only [mixedOperator]
  rw [mixed_projector_factorization]
  exact partial_trace_repetition_frame B _

theorem mixed_trace (A B : Matrix n n ℂ) :
    Matrix.trace (mixedOperator A B) =
      Matrix.trace (cube A * cube (Aᴴ * B) * (cube B)ᴴ) := by
  rw [mixed_partial_trace]
  simp only [transport, Matrix.trace, Matrix.diag_apply, Matrix.mul_apply,
    Matrix.of_apply, Matrix.conjTranspose_apply, cube, star_pow]
  apply Finset.sum_congr rfl
  intro i hi
  apply Finset.sum_congr rfl
  intro j hj
  ring

theorem centered_mixed_transport (A B : Matrix n n ℂ)
    (hunit : B ∈ Matrix.unitaryGroup n ℂ)
    (hflat : ∀ i j, Complex.normSq (B i j) = 1/6) :
    mixedOperator A B - (1/36 : ℂ) • (1 : Matrix n n ℂ) =
      transport B (cube A * cube (Aᴴ * B) - cube B) := by
  rw [mixed_partial_trace, ← transport_cube B hunit hflat]
  unfold transport
  rw [← Matrix.sub_mul]
  congr 1
  ext i j
  simp [Matrix.of_apply, sub_mul]

theorem centered_mixed_norm (A B : Matrix n n ℂ)
    (hunit : B ∈ Matrix.unitaryGroup n ℂ)
    (hflat : ∀ i j, Complex.normSq (B i j) = 1/6) :
    let D := mixedOperator A B - (1/36 : ℂ) • (1 : Matrix n n ℂ)
    let R := cube A * cube (Aᴴ * B) - cube B
    Matrix.trace (Dᴴ * D) = Matrix.trace (Rᴴ * R)/36 := by
  dsimp only
  rw [centered_mixed_transport A B hunit hflat]
  exact transport_gram_trace B _ hunit hflat
end MUBMixedTransport
