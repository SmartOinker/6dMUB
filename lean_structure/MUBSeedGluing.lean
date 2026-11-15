module
public import Mathlib.Data.Fintype.Perm
public import Mathlib.Data.Fintype.Prod
public import Mathlib.Algebra.BigOperators.Group.Finset.Basic
public import Mathlib.Logic.Relation
public import Mathlib.Data.Finset.Card
public import Mathlib.GroupTheory.Perm.Basic
public import Mathlib.Tactic.FinCases
public import Mathlib.Tactic.NormNum
@[expose] public section
namespace MUBSeedGluing
abbrev RootPerm := Equiv.Perm (Fin 3)
abbrev Face := RootPerm × RootPerm
abbrev Edge := Fin 6

def step (e : Edge) (f : Face) : Face :=
  match e.val with
  | 0 => (f.1, Equiv.swap 1 2 * f.2)
  | 1 => (Equiv.swap 0 1 * f.1, f.2)
  | 2 => (f.1, Equiv.swap 0 2 * f.2)
  | 3 => (Equiv.swap 1 2 * f.1, f.2)
  | 4 => (f.1, Equiv.swap 0 1 * f.2)
  | _ => (Equiv.swap 0 2 * f.1, f.2)

def nextEdge (e : Edge) : Edge := ⟨(e.val+1)%6, Nat.mod_lt _ (by decide)⟩
def edgeOrbit (e : Edge) (f : Face) : Finset Face := {f,step e f}
def cornerOrbit (e : Edge) (f : Face) : Finset Face :=
  {f,step e f,step (nextEdge e) f,step e (step (nextEdge e) f)}
def edgeCount : ℕ := ∑ e : Edge, (Finset.univ.image (edgeOrbit e)).card
def vertexCount : ℕ := ∑ e : Edge, (Finset.univ.image (cornerOrbit e)).card

def rootLetter (i : Fin 4) : RootPerm :=
  match i.val with
  | 0 => 1
  | 1 => Equiv.swap 0 1
  | 2 => Equiv.swap 0 2
  | _ => Equiv.swap 1 2

set_option maxRecDepth 200000
set_option maxHeartbeats 20000000

theorem face_count : Fintype.card Face = 36 := by decide +kernel

theorem edge_involution (e : Edge) (f : Face) :
    step e (step e f) = f ∧ step e f ≠ f := by
  revert e f
  decide +kernel

theorem adjacent_steps_commute (e : Edge) (f : Face) :
    step e (step (nextEdge e) f) = step (nextEdge e) (step e f) := by
  revert e f
  decide +kernel

theorem actual_orbit_sizes (e : Edge) (f : Face) :
    (edgeOrbit e f).card = 2 ∧ (cornerOrbit e f).card = 4 := by
  revert e f
  decide +kernel

theorem actual_cell_counts : edgeCount = 108 ∧ vertexCount = 54 := by
  decide +kernel

/-- Every permutation of the three actual root labels is a product of at
most two of the three gluing transpositions, allowing an identity step. -/
theorem two_root_letters_cover (p : RootPerm) :
    ∃ a b : Fin 4, rootLetter a * rootLetter b = p := by
  revert p
  decide +kernel

/-- The actual six edge colors realize all three transpositions on each
factor independently; this is the finite algebra behind connected gluing. -/
theorem letters_are_edge_moves (a : Fin 4) (f : Face) :
    ((rootLetter a * f.1, f.2) = f ∨ ∃ e : Edge, step e f = (rootLetter a * f.1,f.2)) ∧
    ((f.1, rootLetter a * f.2) = f ∨ ∃ e : Edge, step e f = (f.1,rootLetter a * f.2)) := by
  revert a f
  decide +kernel

/-- The finite cell count gives Euler characteristic minus eighteen.
Its identification with a continuous surface is not a hypothesis here,
and is not proved by this arithmetic statement. -/
theorem cell_euler_characteristic :
    (vertexCount : ℤ) - edgeCount + Fintype.card Face = -18 := by
  rw [actual_cell_counts.1, actual_cell_counts.2, face_count]
  norm_num
def adjacent (f g : Face) : Prop := ∃ e : Edge, step e f = g

/-- The actual 36-face gluing graph is connected. This proves reachability
by its explicit edge maps, not only transitivity of an abstract action. -/
theorem gluing_graph_connected (f g : Face) :
    Relation.ReflTransGen adjacent f g := by
  have left (h : Face) (a : Fin 4) :
      Relation.ReflTransGen adjacent h (rootLetter a * h.1,h.2) := by
    rcases (letters_are_edge_moves a h).1 with he | he
    · rw [he]
    · exact Relation.ReflTransGen.single he
  have right (h : Face) (a : Fin 4) :
      Relation.ReflTransGen adjacent h (h.1,rootLetter a * h.2) := by
    rcases (letters_are_edge_moves a h).2 with he | he
    · rw [he]
    · exact Relation.ReflTransGen.single he
  obtain ⟨a,b,hab⟩ := two_root_letters_cover (g.1 * f.1⁻¹)
  obtain ⟨c,d,hcd⟩ := two_root_letters_cover (g.2 * f.2⁻¹)
  have hl := (left f b).trans (left _ a)
  have hr := (right (g.1,f.2) d).trans (right _ c)
  have h1 : rootLetter a * (rootLetter b * f.1) = g.1 := by
    rw [← mul_assoc,hab,mul_assoc,inv_mul_cancel, mul_one]
  have h2 : rootLetter c * (rootLetter d * f.2) = g.2 := by
    rw [← mul_assoc,hcd,mul_assoc,inv_mul_cancel, mul_one]
  simp only [h1] at hl
  simp only [h2] at hr
  exact hl.trans hr
end MUBSeedGluing
