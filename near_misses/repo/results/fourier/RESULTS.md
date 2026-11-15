# Dimension 6: the pair {I, Fourier}
Script: src/fourier/fourier_case.py (about 5 min). Question: which unit vectors of C^6 are unbiased to both I and Fourier, and do they give a fourth MU basis?

| claim | value | how supported |
|---|---|---|
| Solutions found (4000 random starts, last new at start 219) | 48 | numerical (not a proof) |
| Each solution is the unique zero of equations j=1..5 in a box of radius 1e-3 (Krawczyk, 320-bit) | 48 of 48 | certified by interval arithmetic |
| Dropped equation j=0 equals minus the sum of the others (Parseval) | holds exactly | exact |
| The 48 are pairwise distinct (min phase distance 1.196) | yes | certified by interval arithmetic |
| Distinct complex roots of cyclic 6-roots, each isolated | 156 | certified by interval arithmetic |
| Mixed volume (bound on roots; float qhull, error 1e-10) | 156 | numerical (not a proof) |
| Roots proved non-unimodular / the 48 vectors | 108 / 48 | certified by interval arithmetic |
| No other vector exists | follows if the mixed volume is exactly 156 | cited (Grassl 2004) |
| Orthogonal pairs (enclosure contains 0, width < 1e-78) | 300 | numerical (not a proof) |
| Smallest |<u,v>|/6 over non-orthogonal pairs | 0.1547 | certified by interval arithmetic |
| Orthonormal bases (6-cliques) | 16 | numerical (not a proof) |
| Bases through each vector | 2, so no partition of the 48 | exact |
| MU pairs among the 16 bases | 0 of 120 | certified by interval arithmetic |
| Smallest over pairs of the largest deviation | 1/6 | certified by interval arithmetic |
| Vectors of the 48 unbiased to some B_a | 0; min max-deviation 1/6 | certified by interval arithmetic |
| Best max-deviation of any unit v vs {I, Fourier, B_a} | 0.0515 overall (per triple 0.0515, 0.0555 or 0.0591) | numerical (not a proof; upper bound on the minimum) |

Notes
- Completeness has two parts. The 156 distinct roots are rigorous. The upper bound of 156 uses the Bernstein-Kushnirenko theorem with a floating-point mixed volume (155.9999999999). A Groebner-basis attempt in sympy did not finish in 15 minutes.
- Orthogonality, and therefore the 16 bases, rests on enclosures containing 0. Exact zero was not proved.
- If the 48 are all the vectors, {I, Fourier} lies in no set of four MU bases.
