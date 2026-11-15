# Removing hypothesis (H): what is proved without the cited count 34,940 (exact team, phase 3)

Labels: [proved], [computer-assisted: rests on ...], [numerical], [cited], [read directly: URL], [could not verify].

## C. Literature on the count 34,940

- **Parisse, "Computing huge Groebner basis like cyclic10 over Q with Giac"** (arXiv:1903.12427) [read directly:
  https://arxiv.org/pdf/1903.12427, via a fetch summary].
  - The paper computes a rational Gröbner basis of cyclic10: 5,690 elements, about 2·10^7 monomials, about 10 days on
    36 cores.
  - The method is multimodular with rational reconstruction. The paper says reconstruction "is not checked on each
    basis element after each prime"; only a consistency check against the last prime is made.
  - It states neither the degree 34,940 nor zero-dimensionality.
  - So it is not a certified proof of (H), and I did not find the count stated there.
- I found no other published statement of a certified rational computation:
  - Faugère's cyclic-9 papers concern cyclic 9.
  - The Adrovic-Verschelde polyhedral papers (arXiv:1109.0241) are numerical.
  - I could not open Steel's Magma page.
  - Status: [could not verify] any rigorous source for (H).
- Note: (H) implies finiteness. Finiteness of biunimodular vectors of length 10 is the Björck-Saffari question for
  n = 10, which our literature notes record as open. A rigorous (H) would settle that case, and this should be checked
  before any claim is made.

## D. Best unconditional theorem

**Setting** [proved, sketch].
- Take Haagerup's bihomogeneous system in P^9 × P^9: f_k = x_k y_k − x_0 y_0 and h_k = a_k b_k − a_0 b_0 for
  k = 1..9, with a = F x and b = conj(F) y.
- Since Σ_k a_k b_k = Σ_k x_k y_k, a solution has either all x_k y_k = λ ≠ 0 ("proper") or x∘y = 0 = a∘b
  ("boundary").
- Proper solutions are exactly the cyclic 10-roots: y = λ/x, and Σ_k-constancy of a_k b_k is equivalent to g_s(x) = 0
  for all s ≠ 0, by the DFT. Near a proper point y is a local function of x, so our 34,940 certified simple roots are
  isolated points of the bihomogeneous intersection.
- The 18 forms of bidegree (1,1) are hyperplane sections of the Segre variety Σ ⊂ P^99, which has degree
  C(18,9) = 48,620.

**Refined Bézout** [cited from memory: Fulton, *Intersection Theory*, Example 8.4.6; to be checked].
- For subvarieties V_1, ..., V_r of P^N, the sum of deg(Z) over all irreducible components Z of ∩V_i is at most
  ∏ deg(V_i).
- Here it gives Σ_Z deg Z ≤ 48,620, summed over every component of the solution set, of any dimension.

**Boundary classification** [computer-assisted: float64 SVD rank decisions; the code asserts that no singular value
lies between 1e-12 and 1e-6; not exact]. Script: `code/boundary.py`.
- The boundary is the finite union, over supports (S, S'), of products P(V(S,S')) × P(W(S^c, S'^c)). Here
  V(S,S') = {x : supp x ⊆ S, supp Fx ⊆ S'}.
- The irreducible components are the maximal products.

| n | boundary components | types (dim P(A), dim P(B)) | Σ Segre degree |
|---|---|---|---|
| 4 | 4 | (0,0)×4 | 4 |
| 5 | 0 | none (Chebotarev, as for any prime) | 0 |
| 6 | 24 | (0,1)×12, (1,0)×12 | 24 |
| 10 | 920 | (0,0)×800, (0,3)×20, (3,0)×20, (1,2)×40, (2,1)×40 | 1,080 |

- Script `code/bdpoints.py`: exactly 800 of the candidate P^0×P^0 products have a nonsingular Jacobian (corank 0,
  with gap 0.11 versus 5e-10). These are presumably the 800 isolated boundary components, which are then transversal.
  I did not cross-match the two point lists.

**Theorem U** [computer-assisted: rests on Fulton's refined Bézout, the Krawczyk certificates, and the boundary
classification above]. Apart from the 34,940 certified simple roots, the cyclic-10 solution set has further
irreducible components of total degree at most

  48,620 − 34,940 − 1,080 = **12,600**.

Consequences:
- There are at most 12,600 further isolated cyclic 10-roots.
- Hence at most 12,600 biunimodular vectors of length 10 exist beyond the 3,040, or else a positive-dimensional
  component exists. Such a component is one of at most 12,600 components and itself uses up degree ≥ 1.
- Any further isolated vectors form a union of orbits of the order-1600 group.
- For n = 6 the same argument gives "at most 72 further", against the true value of 0. So the bound is valid but not
  sharp.

## A. Toward a proof of (H): exact excess contribution

- The true boundary contributions would have to total 48,620 − 34,940 = 13,680 for n = 10, and 96 for n = 6.
- The "clean" excess formula ∫_Z c(O(1,1)^{18}) c(N_Z X)^{-1} gives:
  - n = 10: 220 per (0,3) component, 370 per (1,2) component and 1 per point, totalling 39,200;
  - n = 6: 6 per component, totalling 144.
- Both overshoot the required values. So the components meet each other and/or the intersection scheme along them is
  non-reduced, and the contributions are not the clean ones.
- Computing the true equivalences is real work. It needs the scheme structure along the 120 positive-dimensional
  components and their intersections, for example via a blow-up or Segre-class computation. This was **not done**.
- If it gave exactly 13,680 − 800 = 12,880 for the positive-dimensional part, (H) would follow rigorously. The case
  n = 6 (target 96 from 24 lines) is the right first test.

## B. Tropical route: not attempted

- Facts recorded:
  - The cyclic formulation has deficiency MV − count = 1,000 (PHCpack: 1,000 paths at infinity).
  - In the bihomogeneous picture the deficiency is 13,680, of which our boundary components account for degree only
    1,080.
- Missing for a proof: an exact count of the roots lost at each tropism face, as Adrovic-Verschelde did for cyclic
  8, 9 and 12.

## Files

- `code/boundary.py`, `code/bdpoints.py`
- `unconditional/boundary_n{4,5,6,10}.json`, `unconditional/boundary10.log`
