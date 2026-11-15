"""Finite-sample detection theorem (report, Theorem "A finite-sample detection guarantee"): numerical and exact checks.

Setting.  Three measurement settings r = 1,2,3, six outcomes each, N independent shots per setting, counts n_{r,k}.
    C_r = sum_k n_{r,k}(n_{r,k}-1) / (N(N-1))      (collision estimator, unbiased for sum_k p_{r,k}^2)
    T   = C_1 + C_2 + C_3 - 1/2                    (unbiased for the energy E = sum_{r,k} (p_{r,k} - 1/6)^2)
    Pearson's statistic satisfies  X^2 = 15 + 6(N-1) T  exactly.
Theorem.  Fix 0 < t < 1 and decide "not white noise" when T >= t*gamma.
  (i)  If all 18 outcome probabilities are 1/6:   P(T >= t gamma) <= 1 / (1 + (6/5) t^2 gamma^2 N(N-1)).
  (ii) If E >= gamma:  P(T < t gamma) <= V/(V + (1-t)^2 gamma^2),  V = (4/N) gamma (1/6 + sqrt(gamma)) + 3/(2N(N-1)).
Both are Cantelli (one-sided Chebyshev) bounds from the exact variance of the collision U-statistic.

This script (1) verifies the mean, the variance formula and X^2 = 15 + 6(N-1)T EXACTLY (rational arithmetic, full
enumeration of all outcome sequences) for N = 2,3,4 on random rational distributions; (2) tests the variance bound
used in (ii) on 200,000 random triples of distributions; (3) prints the shot counts the theorem gives;
(4) Monte Carlo at the theorem's N for the minimum-energy state of the canonical product triple, for random pure
states, and for white noise.  Checks, not proofs: the proof is in the report.
"""
import itertools, sys, numpy as np
from fractions import Fraction as Fr
rng = np.random.default_rng(2026)

# ---------- (1) exact enumeration ----------
def exact_moments(p, N):
    """exact E[C], Var[C] of the collision estimator for one setting, distribution p (Fractions), N shots."""
    m1 = Fr(0); m2 = Fr(0)
    for seq in itertools.product(range(6), repeat=N):
        w = Fr(1)
        for k in seq: w *= p[k]
        if w == 0: continue
        cnt = [seq.count(k) for k in range(6)]
        C = Fr(sum(c*(c-1) for c in cnt), N*(N-1))
        X2 = sum(Fr(6, N)*(Fr(c) - Fr(N, 6))**2 for c in cnt)
        assert X2 == 5 + 6*(N-1)*(C - Fr(1, 6))            # Pearson identity, per setting
        m1 += w*C; m2 += w*C*C
    return m1, m2 - m1*m1
def formula(p, N):
    th = sum(q*q for q in p); s3 = sum(q**3 for q in p)
    return th, Fr(2, N*(N-1))*(2*(N-2)*(s3 - th*th) + th - th*th)
for N in (2, 3, 4):
    for trial in range(3):
        w = [Fr(int(x)) for x in rng.integers(1, 9, size=6)]; p = [x/sum(w) for x in w]
        assert exact_moments(p, N) == formula(p, N)
    u = [Fr(1, 6)]*6
    assert exact_moments(u, N) == (Fr(1, 6), Fr(5, 18*N*(N-1)))
print("(1) exact: mean, variance formula, uniform variance 5/(18N(N-1)) and X^2 = 5 + 6(N-1)(C - 1/6) hold for N = 2,3,4")

# ---------- (2) the variance bound ----------
def var_T(P, N):      # P: 3 x 6 array of probabilities; exact variance of T
    th = (P**2).sum(1); s3 = (P**3).sum(1)
    return float((2/(N*(N-1))*(2*(N-2)*(s3 - th**2) + th - th**2)).sum())
def var_bound(E, N): return 4/N*E*(1/6 + np.sqrt(E)) + 3/(2*N*(N-1))
worst = 0.0
for _ in range(200000):
    a = rng.choice([0.3, 1.0, 5.0, 50.0])
    P = rng.dirichlet(np.full(6, a), size=3); E = float(((P - 1/6)**2).sum()); N = int(rng.integers(2, 5000))
    worst = max(worst, var_T(P, N)/var_bound(E, N))
print("(2) variance bound: max of Var(T)/bound over 200,000 random triples =", worst)
assert worst <= 1.0

# ---------- (3) shot counts from the theorem ----------
# Certified energy bounds, rounded down: cert/verify.py proves E > 0.03849999999 (canonical product triple) and
# E > 0.02349999999 (second product triple); d6_fourier proves E > 0.0234999999946 for all 16 Fourier-pair triples.
def false_alarm(g, N, t=0.5): return 1/(1 + 1.2*(t*g)**2*N*(N-1))
def miss(g, N, t=0.5):
    V = var_bound(g, N); return V/(V + ((1-t)*g)**2)
def shots(g, beta, alpha):
    """smallest N for which some threshold t*g gives miss <= beta and false alarm <= alpha; returns (N, t)."""
    N = 2
    while True:
        tmin = np.sqrt((1/alpha - 1)*5/(6*N*(N-1)))/g; tmax = 1 - np.sqrt(var_bound(g, N)*(1/beta - 1))/g
        if tmin <= tmax:
            t = np.floor(tmax*1e5)/1e5                      # a 5-digit threshold inside the feasible interval
            if t >= tmin and miss(g, N, t) <= beta and false_alarm(g, N, t) <= alpha: return N, float(t)
        N += 1
for name, g in (("canonical product triple, gamma = 0.0384999", 0.0384999),
                ("second product triple and all 16 Fourier-pair triples, gamma = 0.0234999", 0.0234999)):
    for beta, alpha in ((0.05, 1e-3), (0.01, 1e-3)):
        N, t = shots(g, beta, alpha)
        print("(3) %s: N = %d shots per setting, threshold %.5f*gamma: miss <= %.5f, false alarm <= %.3e" % (name, N, t, miss(g, N, t), false_alarm(g, N, t)))
    N = 2
    while miss(g, N) > 0.05: N += 1
    print("(3) %s: with the fixed threshold gamma/2: N = %d, miss <= %.5f, false alarm <= %.3e" % (name, N, miss(g, N), false_alarm(g, N)))

# ---------- (4) Monte Carlo ----------
def triple():
    w = np.exp(2j*np.pi/3); H = np.array([[1, 1], [1, -1]])/np.sqrt(2)
    F = np.array([[1, 1, 1], [1, w, w*w], [1, w*w, w]])/np.sqrt(3); D = np.diag([1, w, w])
    A = [np.eye(2), H, np.diag([1, 1j]) @ H]; B = [np.eye(3), F, D @ F]
    return [np.kron(A[r], B[r]) for r in range(3)]
U = triple()
def probs(psi): return np.array([np.abs(Ur.conj().T @ psi)**2 for Ur in U])
def energy(psi): return float(((probs(psi) - 1/6)**2).sum())
def minimise():
    from scipy.optimize import minimize
    best = None
    f = lambda x: energy((x[:6] + 1j*x[6:])/np.linalg.norm(x))
    for _ in range(20):
        r = minimize(f, rng.normal(size=12), method="BFGS")
        if best is None or r.fun < best.fun: best = r
    x = best.x; return (x[:6] + 1j*x[6:])/np.linalg.norm(x)
def T_samples(P, N, trials):
    out = np.empty(trials)
    for t in range(trials):
        n = np.array([rng.multinomial(N, P[r]/P[r].sum()) for r in range(3)])
        out[t] = (n*(n - 1)).sum()/(N*(N - 1)) - 0.5
    return out
g = 0.0384999; N, t = shots(g, 0.05, 1e-3); thr_T = t*g; trials = 20000
hider = minimise(); Eh = energy(hider)
print("(4) minimum-energy state found numerically: E = %.10f  ((4 - sqrt6)/40 = %.10f)" % (Eh, (4 - np.sqrt(6))/40))
Th = T_samples(probs(hider), N, trials)
print("    N = %d: mean of T = %.5f (E = %.5f); empirical variance %.3e, exact %.3e, bound %.3e" % (N, Th.mean(), Eh, Th.var(), var_T(probs(hider), N), var_bound(Eh, N)))
print("    missed detections (T < %.5f*gamma): %d of %d   [theorem: <= %.3f]" % (t, (Th < thr_T).sum(), trials, miss(g, N, t)))
m = 0
for _ in range(200):
    z = rng.normal(size=6) + 1j*rng.normal(size=6); z /= np.linalg.norm(z)
    m += (T_samples(probs(z), N, 100) < thr_T).sum()
print("    200 random pure states x 100 runs: missed %d of 20000 (random states have energy well above the minimum, so this is a weak test)" % m)
m2 = 0
for _ in range(200):
    z = hider + 0.03*(rng.normal(size=6) + 1j*rng.normal(size=6)); z /= np.linalg.norm(z)
    m2 += (T_samples(probs(z), N, 100) < thr_T).sum()
print("    200 states near the minimiser (perturbation 0.03) x 100 runs: missed %d of 20000" % m2)
Tu = T_samples(np.full((3, 6), 1/6), N, trials)
print("    white noise: false alarms (T >= %.5f*gamma): %d of %d   [theorem: <= %.2e]; empirical variance %.3e, exact %.3e" % (t, (Tu >= thr_T).sum(), trials, false_alarm(g, N, t), Tu.var(), 5/(6*N*(N-1))))

# ---------- (5) the large-sample (chi-square) rule at N = 239, for comparison ----------
from scipy.stats import chi2, ncx2
thr = chi2.isf(1e-3, 15)
def pearson_power(P, N, trials):
    T = T_samples(P, N, trials); return float(((15 + 6*(N - 1)*T) > thr).mean())
print("(5) Pearson test, false alarm 0.1%%, threshold %.3f. Noncentral chi-square prediction with 6*N*0.0385:" % thr)
for N5 in (50, 100, 126, 239):
    print("    N = %3d: prediction %.4f; simulated, minimum-energy state: %.4f (20,000 trials)" % (N5, ncx2.sf(thr, 15, 6*N5*0.0385), pearson_power(probs(hider), N5, 20000)))
lo = 1.0
for _ in range(50):
    z = rng.normal(size=6) + 1j*rng.normal(size=6); z /= np.linalg.norm(z)
    lo = min(lo, pearson_power(probs(z), 239, 2000))
print("    N = 239, 50 random pure states (2,000 trials each): smallest simulated detection rate %.4f" % lo)
print("    white noise at N = 239: simulated false-alarm rate %.5f (100,000 trials)" % pearson_power(np.full((3, 6), 1/6), 239, 100000))
assert (Th < thr_T).mean() <= miss(g, N, t) and (Tu >= thr_T).mean() <= false_alarm(g, N, t) + 3e-3
print("OK")
