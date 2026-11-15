# Degree-six certificate: energy gap for the product MUB triples in dimension six

Computer-assisted lower bounds on E(psi) = sum over the 18 outcomes of (probability - 1/6)^2, for every unit psi in C^6.

| Triple | Certified | Numerical minimum |
|---|---|---|
| T0: Z(x)I, X(x)F, Y(x)DF (the canonical triple of the structure paper (first version)) | E > 0.03849999999 (S <= 2.189e-12) | 0.0387627564 = (4 - sqrt 6)/40 |
| T1: as T0, but third basis is 0_y (x) DF together with 1_y (x) D^2F | E > 0.02349999999 (S <= 2.807e-12) | 0.0238354 |

## Check it
    pip install python-flint numpy
    python3 verify.py 0.0385 Q_T0_gamma0.0385.npy T0
    python3 verify.py 0.0235 Q_T1_gamma0.0235.npy T1
    python3 verify_sets.py <repo>/results/visibility/bases_d6_delta.npy <repo>/results/visibility/bases_d6_P4.npy

`verify.py` is the proof checker; its docstring states the argument. It trusts Arb (python-flint) and itself.
The printed bound is rounded DOWN to 11 decimals. The values `S` and `||R||_F` are printed with `%.3e` (round to nearest): `S` is
2.18857e-12 (T0) and 2.80694e-12 (T1) and prints as 2.189e-12 and 2.807e-12 (up); `||R||_F` is 9.55013e-15 and 7.83125e-15 and prints
as 9.550e-15 and 7.831e-15 (down by less than 3e-19; no conclusion depends on it).
`build.py` (needs cvxpy) only searches for the matrices and is not part of the proof.

## Consequences (verify_sets.py prints these; upper bounds rounded up, lower bounds rounded down)
bias <= 0.030223873 and shortfall <= 0.0002357826 (second set), bias <= 0.040598666 (second set), shortfall <= 0.0006180870 (first set);
T0: delta > 0.046248, shortfall > 0.0003302291; T1: delta > 0.036132, shortfall > 0.0002015684.
With c = 3 sqrt6/(sqrt6+1)^2 and any orthonormal basis G added to a triple with E >= g:
- some overlap of G with the triple has | |<u,g>|^2 - 1/6 | >= sqrt(g/18);
- the four-basis game score falls short of the four-MUB value by at least c*g/72
  (from sqrt p <= 1/sqrt6 + (sqrt6/2)(p - 1/6) - c (p - 1/6)^2 on [0,1]).

## Not established
- That T1 is the second class of the McNulty-Weigert classification is cited (eq. 7.19 of their review), not re-verified; that T1 is a mutually
  unbiased triple is checked in ball arithmetic (`verify.py` asserts the orthonormality and unbiasedness of the 18 projectors).
- The certificate itself is not in Lean (the Lean project at the repository root covers the square-root lemma and the array form of the
  bridge theorem only). A second implementation, `checks/check_cert_pointwise.py`, tests the identity numerically, not in ball arithmetic;
  no second rigorous checker exists.
- The bounds concern quadruples containing an exact product triple, not all quadruples.
