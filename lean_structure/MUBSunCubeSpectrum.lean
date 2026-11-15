module
public import MUBSunCubeGram
public import Mathlib.LinearAlgebra.Matrix.Charpoly.Basic
public import Mathlib.Logic.Equiv.Fin.Basic
@[expose] public section
noncomputable section
namespace MUBSunCubeSpectrum
open Matrix Polynomial MUBSunCubeGram

def paritySplit : Fin 6 ≃ Fin 3 ⊕ Fin 3 where
  toFun := ![Sum.inl 0,Sum.inr 0,Sum.inl 1,Sum.inr 1,Sum.inl 2,Sum.inr 2]
  invFun := Sum.elim ![0,2,4] ![1,3,5]
  left_inv := by intro i; fin_cases i <;> rfl
  right_inv := by intro i; rcases i with i | i <;> fin_cases i <;> rfl

def ternaryBlock (t : ℝ) : Matrix (Fin 3) (Fin 3) ℂ :=
  !![6,6-6*(t:ℂ),6-6*(t:ℂ);
     6-6*(t:ℂ),6,6-6*(t:ℂ);
     6-6*(t:ℂ),6-6*(t:ℂ),6]

theorem actual_parity_split (t : ℝ) :
    Matrix.reindex paritySplit paritySplit (modelGram t) =
      Matrix.fromBlocks (ternaryBlock t) 0 0 (ternaryBlock t) := by
  ext i j
  rcases i with i | i <;> rcases j with j | j <;>
    fin_cases i <;> fin_cases j <;>
    norm_num [modelGram,correlationGram,ternaryBlock,Matrix.reindex_apply,
      paritySplit,Matrix.fromBlocks,map_ofNat]

theorem ternary_characteristic_polynomial (t : ℝ) :
    (ternaryBlock t).charpoly =
      (X-C (18-12*(t:ℂ))) * (X-C (6*(t:ℂ)))^2 := by
  simp [Matrix.charpoly,Matrix.det_fin_three,ternaryBlock,map_sub,map_mul,map_ofNat]
  ring

theorem model_characteristic_polynomial (t : ℝ) :
    (modelGram t).charpoly =
      (X-C (18-12*(t:ℂ)))^2 * (X-C (6*(t:ℂ)))^4 := by
  rw [← Matrix.charpoly_reindex paritySplit (modelGram t), actual_parity_split,
    Matrix.charpoly_fromBlocks_zero₁₂, ternary_characteristic_polynomial]
  ring

/-- The actual cube Gram characteristic polynomial, with repeated factors
combined automatically at q=1. No spectral multiplicities are a premise. -/
theorem actual_cube_characteristic_polynomial (u v : Triple)
    (hu : UnitTriple u) (hv : UnitTriple v)
    (hunit : (blockMatrix u v)ᴴ * blockMatrix u v = (6 : ℂ) • (1 : SixMatrix)) :
    ((entryCube (blockMatrix u v))ᴴ * entryCube (blockMatrix u v)).charpoly =
      (X-C (18-12*(q u:ℂ)))^2 * (X-C (6*(q u:ℂ)))^4 := by
  rw [actual_cube_gram u v hu hv hunit]
  exact model_characteristic_polynomial _

end MUBSunCubeSpectrum
