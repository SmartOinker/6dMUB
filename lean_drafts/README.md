# Lean 4 draft of the vector-to-basis bridge lemma: UNBUILT

**Status: this file has never been compiled. It is a draft. No claim in the report is Lean-verified by it.**

`BridgeLemma.lean` states, and gives proof scripts for, the square-root lemma and the array form of the
vector-to-basis theorem (report, Section "From a vector to a basis"):

| declaration | claim in the report | difference |
|---|---|---|
| `MUB6Bridge.cstar`, `cstar_eq` | the constant c* = 3 sqrt6/(sqrt6+1)^2 = (21 sqrt6 - 36)/25 | none |
| `sqrt_le_quadratic_cap` | Lemma (quadratic cap on the square root) | none |
| `bias_bound` | Theorem, part (a) | stated for 18 real numbers, not for vectors |
| `pair_sum_bound` | inequality (pair sum) in the proof of part (b) | stated for a 6 x 6 array with entries in [0,1] and total 6 |
| `game_bound` | Theorem, part (b), the three pairs (triple basis, fourth basis) | array form; the step from orthonormal bases to arrays (Parseval) is on paper only |
| `numbers_T0`, `numbers_T1` | Corollary (numbers for the two product triples) | uses the certified values 0.038499999998 and 0.023499999997 |

Why it is unbuilt: no Lean toolchain or Mathlib could be installed in the workspace where the report was assembled,
and the Open Math OS platform, where a build was requested through its API (`tools/mathos_client.py`), had no free
agent slot at the time (the request is recorded in the chat "CLAUDE: bridge-lemma Lean build" of the team project).
The proof scripts were written without compiler feedback, so some tactic calls will probably need repair.

To try it: Lean v4.35.0 with Mathlib v4.35.0 (the competition's pinned versions), then
`lake env lean lean_drafts/BridgeLemma.lean` from a project that depends on Mathlib. If it builds, add
`#print axioms` for each declaration and record the log before making any Lean claim.

This directory is deliberately outside any lake project so that an automated Lean build of the repository does not
pick it up.
