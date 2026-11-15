module
public import MUBSunCubeGram
@[expose] public section
noncomputable section
namespace MUBNormalizerObstructions
open Matrix MUBSunCubeGram
set_option maxHeartbeats 4000000
set_option maxRecDepth 100000

def omega : ℂ := ⟨-1/2,Real.sqrt 3/2⟩

def fourier3 (x : Triple) : Triple :=
  ![x 0+x 1+x 2,
    x 0+omega*x 1+(starRingEnd ℂ) omega*x 2,
    x 0+(starRingEnd ℂ) omega*x 1+omega*x 2]

theorem omega_square : omega^2 = (starRingEnd ℂ) omega := by
  have hs : Real.sqrt 3 ^2=3 := Real.sq_sqrt (by norm_num)
  apply Complex.ext <;> norm_num [omega,pow_two,Complex.mul_re,Complex.mul_im]
  · nlinarith
  · ring

theorem omega_primitive : omega^3=1 ∧ omega≠1 := by
  have hs : Real.sqrt 3 ^2=3 := Real.sq_sqrt (by norm_num)
  constructor
  · rw [pow_succ,omega_square]
    apply Complex.ext <;> norm_num [omega,Complex.mul_re,Complex.mul_im]
    · nlinarith
    · ring
  · intro h
    have hr := congrArg Complex.re h
    norm_num [omega] at hr

theorem actual_fourier_parseval (x : Triple) :
    (∑ j, Complex.normSq (fourier3 x j)) = 3*(∑ j, Complex.normSq (x j)) := by
  have hs : Real.sqrt 3 ^2=3 := Real.sq_sqrt (by norm_num)
  norm_num [fourier3,omega,Fin.sum_univ_succ,Complex.normSq_apply,Complex.mul_re,Complex.mul_im]
  ring_nf
  rw [hs]
  ring

theorem shifted_unit_energy (w : Triple) (hw : UnitTriple w) :
    (∑ j, Complex.normSq (1+w j)) = 6+2*(∑ j, w j).re := by
  have hn (j : Fin 3) : Complex.normSq (w j)=1 := by
    apply Complex.ofReal_injective
    simpa only [Complex.mul_conj,Complex.ofReal_one] using hw j
  have h0 := hn 0
  have h1 := hn 1
  have h2 := hn 2
  norm_num [Fin.sum_univ_succ,Complex.normSq_apply] at h0 h1 h2 ⊢
  nlinarith

/-- The actual three-point DFT of 1+w cannot have all squared moduli six
when all three entries of w have unit modulus. -/
theorem actual_shared_chirp_obstruction (w : Triple) (hw : UnitTriple w) :
    ¬ (∀ j, Complex.normSq (fourier3 (fun k => 1+w k) j)=6) := by
  intro hflat
  have hp := actual_fourier_parseval (fun k => 1+w k)
  have he := shifted_unit_energy w hw
  have hf : (∑ j, Complex.normSq (fourier3 (fun k => 1+w k) j))=18 := by
    norm_num [hflat]
  have hr : (∑ j, w j).re=0 := by rw [hf,he] at hp; linarith
  have hsum : fourier3 (fun k => 1+w k) 0 = 3+∑ j, w j := by
    simp [fourier3,Fin.sum_univ_succ]
    ring
  have h0 := hflat 0
  rw [hsum] at h0
  have hn := Complex.normSq_nonneg (∑ j, w j)
  have hid : Complex.normSq (3+∑ j, w j) =
      9+6*(∑ j, w j).re+Complex.normSq (∑ j, w j) := by
    norm_num [Complex.normSq_apply]
    ring
  rw [hid,hr] at h0
  linarith

def qubitGram (V : Matrix (Fin 2) (Fin 3) ℂ) : Matrix (Fin 3) (Fin 3) ℂ :=
  fun a b => ∑ i, (starRingEnd ℂ) (V i a)*V i b

def qubitFrame (V : Matrix (Fin 2) (Fin 3) ℂ) : Matrix (Fin 2) (Fin 2) ℂ :=
  fun i j => ∑ a, V i a*(starRingEnd ℂ) (V j a)

/-- The exact squared Frobenius distance of the actual three-vector frame
operator from (3/2)I. -/
theorem actual_qubit_welch_identity (V : Matrix (Fin 2) (Fin 3) ℂ) :
    (∑ i, ∑ j, Complex.normSq (qubitFrame V i j - if i=j then 3/2 else 0)) =
      (∑ a, ∑ b, Complex.normSq (qubitGram V a b)) -
        3*(∑ a, ∑ i, Complex.normSq (V i a)) + 9/2 := by
  norm_num [qubitGram,qubitFrame,Fin.sum_univ_succ,Complex.normSq_apply,
    Complex.mul_re,Complex.mul_im]
  ring

/-- Three actual unit vectors in C2 cannot have all pairwise squared
inner products equal to 1/6. No rank or spectral inequality is assumed. -/
theorem actual_qubit_three_ray_obstruction (V : Matrix (Fin 2) (Fin 3) ℂ)
    (hunit : ∀ a, (∑ i, Complex.normSq (V i a))=1)
    (hcross : ∀ a b, a≠b → Complex.normSq (qubitGram V a b)=1/6) : False := by
  have hd (a : Fin 3) : qubitGram V a a = 1 := by
    calc
      _ = ((∑ i, Complex.normSq (V i a) : ℝ) : ℂ) := by
        simp only [qubitGram,Complex.ofReal_sum]
        apply Finset.sum_congr rfl
        intro i _
        rw [mul_comm,Complex.mul_conj]
      _ = _ := by rw [hunit]; norm_num
  have hn := actual_qubit_welch_identity V
  have hnonneg : 0 ≤ ∑ i, ∑ j, Complex.normSq (qubitFrame V i j - if i=j then 3/2 else 0) :=
    Finset.sum_nonneg (fun _ _ => Finset.sum_nonneg (fun _ _ => Complex.normSq_nonneg _))
  have hg : (∑ a, ∑ b, Complex.normSq (qubitGram V a b))=4 := by
    norm_num [Fin.sum_univ_succ,hd,hcross]
  have hsum : (∑ a, ∑ i, Complex.normSq (V i a))=3 := by norm_num [hunit]
  rw [hg,hsum] at hn
  linarith

end MUBNormalizerObstructions
