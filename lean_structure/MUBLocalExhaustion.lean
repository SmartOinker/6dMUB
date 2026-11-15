module

public import Mathlib.Analysis.Calculus.ImplicitFunction.ProdDomain

@[expose] public section
noncomputable section

namespace MUBLocalExhaustion

open Filter
open scoped Topology

variable {E Y W Z : Type*}
  [NormedAddCommGroup E] [NormedSpace ℝ E] [CompleteSpace E]
  [NormedAddCommGroup Y] [NormedSpace ℝ Y] [CompleteSpace Y]
  [NormedAddCommGroup W] [NormedSpace ℝ W] [CompleteSpace W]
  [Zero Z]

/-- If selected equations have an invertible partial derivative and a continuous
seed graph supplies full solutions at every nearby free coordinate, then the full
zero set is locally exactly that graph. Uniqueness and exhaustion are conclusions
of Mathlib's implicit-function theorem, not hypotheses. -/
theorem local_graph_exhaustion
    (F : E × Y → Z) (G : E × Y → W) (u : E × Y)
    (G' : E × Y →L[ℝ] W) (seed : E → Y)
    (hG : HasStrictFDerivAt G G' u)
    (hinv : (G' ∘L ContinuousLinearMap.inr ℝ E Y).IsInvertible)
    (hzero : G u = 0)
    (hselect : ∀ p, F p = 0 → G p = 0)
    (hseed_cont : ContinuousAt seed u.1)
    (hseed_anchor : seed u.1 = u.2)
    (hseed_full : ∀ᶠ q in 𝓝 u.1, F (q, seed q) = 0) :
    ∀ᶠ p in 𝓝 u, F p = 0 ↔ p.2 = seed p.1 := by
  let ψ := hG.implicitFunctionOfProdDomain hinv
  have hchart : ∀ᶠ p in 𝓝 u, G p = G u ↔ ψ p.1 = p.2 :=
    hG.eventually_apply_eq_iff_implicitFunctionOfProdDomain hinv
  have hgraph_cont : ContinuousAt (fun q => (q, seed q)) u.1 :=
    continuousAt_id.prodMk hseed_cont
  have hgraph : Tendsto (fun q => (q, seed q)) (𝓝 u.1) (𝓝 u) := by
    simpa only [hseed_anchor, Prod.mk.eta] using hgraph_cont.tendsto
  have hseed_eq : ∀ᶠ q in 𝓝 u.1, ψ q = seed q := by
    filter_upwards [hgraph.eventually hchart, hseed_full] with q hq hf
    apply hq.mp
    rw [hzero]
    exact hselect (q, seed q) hf
  have hfst : Tendsto (Prod.fst : E × Y → E) (𝓝 u) (𝓝 u.1) :=
    continuousAt_fst.tendsto
  filter_upwards [hchart, hfst.eventually hseed_eq, hfst.eventually hseed_full]
    with p hc he hf
  constructor
  · intro hp
    have hy : ψ p.1 = p.2 := hc.mp (by rw [hzero]; exact hselect p hp)
    exact hy.symm.trans he
  · intro hy
    simpa only [← hy, Prod.mk.eta] using hf

/-- Every property holding on the nearby seed graph transfers to every nearby
full solution. In particular this applies to one or several residual-zero
identities. The concrete derivative and seed hypotheses remain explicit. -/
theorem local_property_transfer
    (F : E × Y → Z) (G : E × Y → W) (u : E × Y)
    (G' : E × Y →L[ℝ] W) (seed : E → Y) (P : E × Y → Prop)
    (hG : HasStrictFDerivAt G G' u)
    (hinv : (G' ∘L ContinuousLinearMap.inr ℝ E Y).IsInvertible)
    (hzero : G u = 0)
    (hselect : ∀ p, F p = 0 → G p = 0)
    (hseed_cont : ContinuousAt seed u.1)
    (hseed_anchor : seed u.1 = u.2)
    (hseed_full : ∀ᶠ q in 𝓝 u.1, F (q, seed q) = 0)
    (hseed_property : ∀ᶠ q in 𝓝 u.1, P (q, seed q)) :
    ∀ᶠ p in 𝓝 u, F p = 0 → P p := by
  have hexhaust := local_graph_exhaustion F G u G' seed hG hinv hzero hselect
    hseed_cont hseed_anchor hseed_full
  have hfst : Tendsto (Prod.fst : E × Y → E) (𝓝 u) (𝓝 u.1) :=
    continuousAt_fst.tendsto
  filter_upwards [hexhaust, hfst.eventually hseed_property] with p he hp
  intro hf
  have hy : p.2 = seed p.1 := he.mp hf
  simpa only [← hy, Prod.mk.eta] using hp

end MUBLocalExhaustion
