# Degree-six certificate: energy gap for the product MUB triples in dimension six

Computer-assisted lower bounds on E(psi) = sum over the 18 outcomes of (probability - 1/6)^2, for every unit psi in C^6.

| Triple | Certified | Numerical minimum |
|---|---|---|
| T0: Z(x)I, X(x)F, Y(x)DF (the canonical triple of xinrui.pdf) | E > 0.038499999998 | 0.0387627564 = (4 - sqrt 6)/40 |
| T1: as T0, but third basis is 0_y (x) DF together with 1_y (x) D^2F | E > 0.023499999997 | 0.0238354 |

## Check it
    pip install python-flint numpy
    python3 verify.py 0.0385 Q_T0_gamma0.0385.npy T0
    python3 verify.py 0.0235 Q_T1_gamma0.0235.npy T1
    python3 verify_sets.py <repo>/results/visibility/bases_d6_delta.npy <repo>/results/visibility/bases_d6_P4.npy

`verify.py` is the proof checker; its docstring states the argument. It trusts Arb (python-flint) and itself.
`build.py` (needs cvxpy) only searches for the matrices and is not part of the proof.

## Consequences (verify_sets.py prints these)
With c = 3 sqrt6/(sqrt6+1)^2 and any orthonormal basis G added to a triple with E >= g:
- some overlap of G with the triple has | |<u,g>|^2 - 1/6 | >= sqrt(g/18);
- the four-basis game score falls short of the four-MUB value by at least c*g/72
  (from sqrt p <= 1/sqrt6 + (sqrt6/2)(p - 1/6) - c (p - 1/6)^2 on [0,1]).

## Not established
- T1 was written down from memory of McNulty-Weigert's classification; check it against their paper.
- Nothing here is in Lean, and no second person or program has reviewed verify.py.
- The bounds concern quadruples containing an exact product triple, not all quadruples.
