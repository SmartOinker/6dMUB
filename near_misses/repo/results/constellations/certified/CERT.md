# Certified local minima of the constellation misfit

Setting: f(x)=|r(x)|^2/2, r as in `src/constellations/search.py` (phases of vectors 1..m-1 free, v_0=(1,...,1)), n=5(m-1) unknowns. Let c be the 256-bit rounding of the 40-digit phases x0 in `polished.jsonl` (|c-x0|<2e-77).

**Theorem (shape [4,4,1], n=40).** Let X=c+[-1e-9,1e-9]^40. Then g=grad f has exactly one zero x* in X (Krawczyk test passes, also for 1e-8). In X, H=Hess f is positive definite with lambda_min(H(x)) >= 7.70e-5 for all x in X; hence x* is a strict local minimum (indeed the unique minimizer of f on X). Moreover |x*-c|_inf <= 8.51e-23, and
|r(x*)| in [0.0010249768385195336910, 0.0010249768385195336990], f(x*) in [5.2528875975074912e-7, 5.2528875975074913e-7] > 0,
F_BW(x*) in [2.91815079034540594e-8, 2.91815079034540600e-8] < 1e-7.
No zero of r (exact solution) lies within Euclidean distance 1.67e-4 of x* (Lipschitz bound with interval-Jacobian norm 6.13 on a box of half-width 1.78e-4; the global constant L=sqrt(20 n_same+60 n_cross)=40.99 gives 2.50e-5).

**Theorem (shape [5,3,1], n=40).** Same statement with X=c+[-1e-8,1e-8]^40 (T1 also passes at 1e-7), lambda_min(H) >= 5.70e-7 on X, |x*-c|_inf <= 1.44e-25, |r(x*)| in [7.32788656303687804426e-4, 7.32788656303687804437e-4], f(x*) in [2.6848960740368214609e-7, 2.6848960740368214611e-7], F_BW in [1.49149429273738542e-8, 1.49149429273738544e-8] < 1e-7; exclusion radius 1.21e-4 (global-L: 1.81e-5).

Shapes [4,3,2] (misfit 0.004988...) and [4,4,2] also pass T1-T4 (F_BW = 6.9e-7, 1.56e-6, not < 1e-7); see `certificate.json`, which holds all enclosures as decimal strings.

**Method.** Every inequality is evaluated in python-flint (Arb) ball arithmetic at 256 bits over the whole box: T1 Krawczyk with Y = midpoint of the ball inverse of H(c); T3 Gershgorin on B=Q^T H(X) Q with Q the float64 eigenvector matrix converted exactly, ||Q^TQ-I||_inf<1e-14 so Q is nonsingular. The reported lambda bound is (min Gershgorin bound of B)/(1+||Q^TQ-I||_inf), a rigorous lower bound on lambda_min(H(x)) for all x in X.

**Assumed:** correctness of python-flint 0.9/Arb and of `certify.py` (r, J, H validated against search.py to 1e-15 / 3e-10 relative at random points; this validation is not itself rigorous).

**Not proved:** the statements concern one local minimum each. They do not show that the misfit has no zero elsewhere, nor that no zero exists beyond the stated exclusion radius, nor anything about other shapes.
