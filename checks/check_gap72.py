"""Numerical check of the analytic energy gap E(psi) > 1/72 on the canonical product triple
(report Appendix "The analytic energy gap", Theorem thm:gap72, Lemma lem:energyid, Steps 1-4 of A.3,
Section 4.5 total-variation / distinguishing bounds).

DEFINITIONS.  U_r = A_r (x) B_r, A = [I2, H2, diag(1,i)H2], B = [I3, F3, D F3], D = diag(1,w,w), w = e^{2 pi i/3};
p_{r,k}(psi) = |<u_{r,k}, psi>|^2, E = sum (p - 1/6)^2.  Coordinates of A.1: psi = sum_k v_k (x) c_k, c_k the
columns of C = D^2 F3, n_k = |v_k|^2, X3 c_k = c_{k+1}, Z3 c_k = w^k c_k, W_r = X3 Z3^r, a_r, q_r, t_r, s, lambda =
(1-|a|)/2 as in the report.

WHAT IS TESTED (labels are the report's).
  A.1   the basis B_r consists of eigenvectors of W_r (distinct eigenvalues 1,w,w^2 once each).
  L1    Lemma lem:energyid  E = s + |a|^2/6 + |t|^2/3, and its two Parseval sub-identities
        sum_j (Q_rj-1/3)^2 = (2/3)|q_r|^2,  sum_j Delta_rj^2 = (a_r^2 + 2|t_r|^2)/3,  sum_r |q_r|^2 = 3 s.
  St1   lambda_min(rho_Q) = (1-|a|)/2.
  St2   n_h^2 <= 2 s (Weyl/Frobenius step) and n_h (lambda - n_h) <= s  (from lambda n_h <= n_h^2 + s).
  St3   n_i, n_j >= lambda - n_h and n_i n_j >= (lambda - n_h)(1 - lambda).
  St4   Fierz identity |m|^2 = 2 n_i n_j - |v_i^* v_j|^2, |R|^2 <= 4 n_h (1-n_h), |t| >= |m| - |R|, E >= |t|^2/3.
        These are the premise-free forms of the steps, tested on 200,000 Haar-random unit vectors.
  COND  The chain of A.3 is a contradiction argument, so its premises (s <= 1/72, |a|^2 <= 1/12) are almost
        never met by Haar samples.  We therefore also test the conclusions of Steps 2-4 verbatim
        (n_h < 9/200; n_i n_j > 3999/20000; |m|^2 > (31/50)^2; |R|^2 < (83/200)^2; |t| > 41/200;
        E >= |t|^2/3 > 1681/120000 > 1/72) on 200,000 targeted states that satisfy the premises
        s <= 1/72 and |a|^2 <= 1/12 (built from nearly orthogonal v_k and perturbations).
  EXACT all rational comparisons of Steps 2-4 in exact Fractions, and the endpoint-minimum claim of Step 2 on a grid.
  MIN   min E >= 0.0385 > 1/72 from 200 random-start BFGS minimizations (compared with (4-sqrt6)/40).
  TV    sum_x d_b(x)^2 <= 2 TV_b^2; max_b TV_b > 1/(12 sqrt3); success 1/2 + TV/2 > 1/2 + 1/(24 sqrt3);
        some outcome has |p - 1/6| > 1/36; on all Haar samples and on the 200 minimizers.
This is a numerical check in double precision, not a proof.
"""
import time
from fractions import Fraction as Fr
import numpy as np
from scipy.optimize import minimize

t0 = time.time()
rng = np.random.default_rng(72)
w = np.exp(2j * np.pi / 3)
H2 = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
A = [np.eye(2), H2, np.diag([1, 1j]) @ H2]
F = np.array([[w ** (j * k) for k in range(3)] for j in range(3)]) / np.sqrt(3)
D = np.diag([1, w, w])
B = [np.eye(3), F, D @ F]
U = [np.kron(A[r], B[r]) for r in range(3)]
Uall = np.concatenate(U, axis=1)           # 6 x 18, columns u_{r,(a,q)}, index 3a+q within basis r
for r in range(3):
    assert np.allclose(U[r].conj().T @ U[r], np.eye(6))
    for s_ in range(r + 1, 3):
        assert np.allclose(np.abs(U[r].conj().T @ U[s_]) ** 2, 1 / 6)
C = D @ D @ F
sig = [np.array([[1, 0], [0, -1]]), np.array([[0, 1], [1, 0]]), np.array([[0, -1j], [1j, 0]])]
X3 = np.roll(np.eye(3), 1, axis=0)
Z3 = np.diag([1, w, w ** 2])
W = [X3 @ np.linalg.matrix_power(Z3, r) for r in range(3)]

# ---- A.1: eigenvectors of W_r (operators defined in C-coordinates, transported to the standard basis)
for r in range(3):
    Wstd = C @ W[r] @ C.conj().T
    ev = []
    for j in range(3):
        beta = B[r][:, j]
        lam = np.vdot(beta, Wstd @ beta)
        assert np.linalg.norm(Wstd @ beta - lam * beta) < 1e-12, "B_r column not an eigenvector of W_r"
        ev.append(lam)
    k = sorted(int(round(np.angle(l) / (2 * np.pi / 3))) % 3 for l in ev)
    assert k == [0, 1, 2] and np.allclose(np.abs(ev), 1)
print("A.1: each basis B_r consists of eigenvectors of W_r with eigenvalues 1,w,w^2 once each: OK")


def quantities(psi):
    """psi: (n,6).  returns dict of arrays."""
    n = psi.shape[0]
    Mx = psi.reshape(n, 2, 3)
    V = Mx @ C.conj()                                   # V[n,a,k]
    p = np.abs(psi @ Uall.conj()) ** 2                  # n x 18
    d = p - 1 / 6
    E = (d ** 2).sum(1)
    nk = (np.abs(V) ** 2).sum(1)                        # n x 3
    G = np.einsum('nak,nal->nkl', V.conj(), V)          # G[k,l] = v_k^* v_l
    sgap = sum(np.abs(G[:, (k + 1) % 3, k]) ** 2 for k in range(3))
    rho = np.einsum('nak,nbk->nab', V, V.conj())
    a = np.stack([np.real(np.einsum('nab,ba->n', rho, sig[r])) for r in range(3)], 1)
    T = np.zeros((n, 3, 3), complex)                    # T[n,k,r] = w^{rk} v_{k+1}^* sigma_r v_k
    for k in range(3):
        for r in range(3):
            T[:, k, r] = w ** (r * k) * np.einsum('na,ab,nb->n', V[:, :, (k + 1) % 3].conj(), sig[r], V[:, :, k])
    t = T.sum(1)
    q = np.zeros((n, 3), complex)
    for r in range(3):
        q[:, r] = sum(w ** (r * k) * G[:, (k + 1) % 3, k] for k in range(3))
    return dict(p=p, d=d, E=E, V=V, nk=nk, G=G, s=sgap, rho=rho, a=a, T=T, t=t, q=q)


def check_all(psi, tag):
    Q = quantities(psi)
    n = psi.shape[0]
    a, t, s, nk, E = Q['a'], Q['t'], Q['s'], Q['nk'], Q['E']
    out = {}
    na = np.linalg.norm(a, axis=1)
    out['L1  |E - (s+|a|^2/6+|t|^2/3)|'] = np.abs(E - (s + na ** 2 / 6 + (np.abs(t) ** 2).sum(1) / 3)).max()
    out['L1b |sum|q_r|^2 - 3 s|'] = np.abs((np.abs(Q['q']) ** 2).sum(1) - 3 * s).max()
    # Parseval sub-identities from the actual probabilities
    p = Q['p'].reshape(n, 3, 2, 3)
    Qrj, Dr = p[:, :, 0, :] + p[:, :, 1, :], p[:, :, 0, :] - p[:, :, 1, :]
    out['L1c |sum_j (Q-1/3)^2 - (2/3)|q_r|^2|'] = np.abs(((Qrj - 1 / 3) ** 2).sum(2) - 2 / 3 * np.abs(Q['q']) ** 2).max()
    out['L1d |sum_j Delta^2 - (a_r^2+2|t_r|^2)/3|'] = np.abs((Dr ** 2).sum(2) - (a ** 2 + 2 * np.abs(t) ** 2) / 3).max()
    lam_min = np.linalg.eigvalsh(Q['rho'])[:, 0]
    lam = (1 - na) / 2
    out['St1 |lambda_min - (1-|a|)/2|'] = np.abs(lam_min - lam).max()
    h = nk.argmin(1)
    ar = np.arange(n)
    nh = nk[ar, h]
    i_, j_ = (h + 1) % 3, (h + 2) % 3
    ni, nj = nk[ar, i_], nk[ar, j_]
    out['St2a max(n_h^2 - 2 s)  (<=0)'] = (nh ** 2 - 2 * s).max()
    out['St2b max(n_h(lambda-n_h) - s)  (<=0)'] = (nh * (lam - nh) - s).max()
    out['St3a max((lambda-n_h) - min(n_i,n_j))  (<=0)'] = ((lam - nh) - np.minimum(ni, nj)).max()
    out['St3b max((lambda-n_h)(1-lambda) - n_i n_j)  (<=0)'] = ((lam - nh) * (1 - lam) - ni * nj).max()
    # Step 4: m = pair {i,j} = term k=h+1 ; R = terms k=h and k=h-1
    T = Q['T']
    m = T[ar, (h + 1) % 3, :]
    R = T[ar, h, :] + T[ar, (h + 2) % 3, :]
    nm2, nR2 = (np.abs(m) ** 2).sum(1), (np.abs(R) ** 2).sum(1)
    vij = np.abs(Q['G'][ar, i_, j_]) ** 2
    out['St4a |m|^2 - (2 n_i n_j - |v_i^*v_j|^2)'] = np.abs(nm2 - (2 * ni * nj - vij)).max()
    out['St4b max(|R|^2 - 4 n_h(1-n_h))  (<=0)'] = (nR2 - 4 * nh * (1 - nh)).max()
    nt = np.sqrt((np.abs(t) ** 2).sum(1))
    out['St4c max((|m|-|R|) - |t|)  (<=0)'] = (np.sqrt(nm2) - np.sqrt(nR2) - nt).max()
    out['St4d max(|t|^2/3 - E)  (<=0)'] = (nt ** 2 / 3 - E).max()
    out['St4e max(|v_i^*v_j|^2 - s)  (<=0)'] = (vij - s).max()
    # total variation family
    d = Q['d'].reshape(n, 3, 6)
    TV = 0.5 * np.abs(d).sum(2)
    out['TV1 max(sum d^2 - 2 TV^2)  (<=0)'] = ((d ** 2).sum(2) - 2 * TV ** 2).max()
    out['TV0 max|sum_x d_b(x)|  (=0)'] = np.abs(d.sum(2)).max()
    tvmax = TV.max(1)
    out['TV2 min_psi max_b TV_b  (> 1/(12 sqrt3))'] = tvmax.min()
    out['TV3 min_psi success 1/2+TV/2 (> 1/2+1/(24 sqrt3))'] = (0.5 + 0.5 * tvmax).min()
    out['TV4 min_psi max|p-1/6|  (> 1/36)'] = np.abs(Q['d']).max(1).min()
    out['min E'] = E.min()
    # report
    print(f"\n--- {tag}: {n} unit vectors ---")
    for k, v in out.items():
        print(f"  {k:58s} {v: .6e}")
    # asserts
    for k in ['L1  |E - (s+|a|^2/6+|t|^2/3)|', 'L1b |sum|q_r|^2 - 3 s|', 'L1c |sum_j (Q-1/3)^2 - (2/3)|q_r|^2|',
              'L1d |sum_j Delta^2 - (a_r^2+2|t_r|^2)/3|', 'St1 |lambda_min - (1-|a|)/2|',
              'St4a |m|^2 - (2 n_i n_j - |v_i^*v_j|^2)', 'TV0 max|sum_x d_b(x)|  (=0)']:
        assert out[k] < 1e-11, k
    for k in [k for k in out if k.endswith('(<=0)')]:
        assert out[k] <= 1e-12, k
    assert out['TV2 min_psi max_b TV_b  (> 1/(12 sqrt3))'] > 1 / (12 * np.sqrt(3))
    assert out['TV3 min_psi success 1/2+TV/2 (> 1/2+1/(24 sqrt3))'] > 0.5 + 1 / (24 * np.sqrt(3))
    assert out['TV4 min_psi max|p-1/6|  (> 1/36)'] > 1 / 36
    assert out['min E'] > 1 / 72
    return Q, out, dict(nh=nh, ni=ni, nj=nj, lam=lam, nm2=nm2, nR2=nR2, nt=nt, s=s, na=na, E=E)


def haar(n):
    z = rng.normal(size=(n, 6)) + 1j * rng.normal(size=(n, 6))
    return z / np.linalg.norm(z, axis=1, keepdims=True)


# ---------------- Haar samples ----------------
agg = None
for c in range(10):
    psi = haar(20000)
    if c == 0:
        Q, out, aux = check_all(psi, "Haar-random unit vectors (chunk 1 of 10, detailed)")
    else:
        import io, contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            Q, out, aux = check_all(psi, "chunk")
    agg = out if agg is None else {k: (max(agg[k], out[k]) if (k.endswith('(<=0)') or k.startswith(('L1', 'St1', 'St4a', 'TV0'))) else
                                       (min(agg[k], out[k]) if k.startswith(('TV2', 'TV3', 'TV4', 'min E')) else agg[k]))
                                   for k in agg}
print("\n=== aggregated over all 200,000 Haar samples (10 chunks of 20,000): worst values ===")
for k, v in agg.items():
    print(f"  {k:58s} {v: .6e}")
print("  (all assertions in the chunks passed)")

# ---------------- premise (targeted) states ----------------
def targeted(n):
    psis, V = [], []
    while len(V) < n:
        m = 4000
        # orthonormal pair e,f in C^2 and random third direction
        g = rng.normal(size=(m, 2)) + 1j * rng.normal(size=(m, 2))
        e = rng.normal(size=(m, 2)) + 1j * rng.normal(size=(m, 2)); e /= np.linalg.norm(e, axis=1, keepdims=True)
        f = np.stack([-np.conj(e[:, 1]), np.conj(e[:, 0])], 1)
        wgt = rng.dirichlet([2, 2, 0.1], size=m)
        coef = np.sqrt(wgt)
        vk = np.stack([coef[:, 0, None] * e, coef[:, 1, None] * f, coef[:, 2, None] * g / np.linalg.norm(g, axis=1, keepdims=True)], 1)
        noise = (rng.normal(size=vk.shape) + 1j * rng.normal(size=vk.shape)) * (10.0 ** rng.uniform(-3, -0.7, size=(m, 1, 1)))
        vk = vk + noise
        perm = np.array([rng.permutation(3) for _ in range(m)])
        vk = np.take_along_axis(vk, perm[:, :, None], 1)         # (m, k, a)
        Vm = vk.transpose(0, 2, 1)                              # (m, a, k)
        Vm = Vm / np.sqrt((np.abs(Vm) ** 2).sum((1, 2)))[:, None, None]
        # psi[a,q] = sum_k V[a,k] C[q,k]
        psi = np.einsum('nak,qk->naq', Vm, C).reshape(m, 6)
        Qt = quantities(psi)
        ok = (Qt['s'] <= 1 / 72) & ((Qt['a'] ** 2).sum(1) <= 1 / 12)
        psis.append(psi[ok]); V.extend([1] * int(ok.sum()))
    return np.concatenate(psis)[:n]


psiT = targeted(200000)
QT, outT, auxT = check_all(psiT, "targeted premise states (s<=1/72 and |a|^2<=1/12)")
nh, ni, nj, lam = auxT['nh'], auxT['ni'], auxT['nj'], auxT['lam']
print("\nCOND: verbatim conclusions of Steps 1-4 on the premise states")
cond = {
    'lambda > 71/200': (lam.min(), lam.min() > 71 / 200),
    'St2: n_h < 9/200  (max n_h)': (nh.max(), nh.max() < 9 / 200),
    'St3: n_i n_j > 3999/20000  (min)': ((ni * nj).min(), (ni * nj).min() > 3999 / 20000),
    'St4: |m|^2 > (31/50)^2 (min |m|^2)': (auxT['nm2'].min(), auxT['nm2'].min() > (31 / 50) ** 2),
    'St4: |R|^2 < (83/200)^2 (max |R|^2)': (auxT['nR2'].max(), auxT['nR2'].max() < (83 / 200) ** 2),
    'St4: |t| > 41/200 (min |t|)': (auxT['nt'].min(), auxT['nt'].min() > 41 / 200),
    'final: E >= |t|^2/3 > 1681/120000 > 1/72 (min E)': (auxT['E'].min(), auxT['E'].min() > 1681 / 120000 > 1 / 72),
}
for k, (v, ok) in cond.items():
    print(f"  {k:55s} {v:.6f}   {'holds' if ok else 'FAILS'}")
    assert ok, k
print(f"  states with n_h-premises: |a|^2 range [{(auxT['na']**2).min():.4f},{(auxT['na']**2).max():.4f}], s range [{auxT['s'].min():.2e},{auxT['s'].max():.4f}]")

# ---------------- exact rational comparisons ----------------
print("\nEXACT (fractions):")
e1 = Fr(9, 200) * (Fr(71, 200) - Fr(9, 200)); e2 = Fr(1, 6) * (Fr(71, 200) - Fr(1, 6))
print("  9/200*(71/200-9/200) =", e1, " 1/6*(71/200-1/6) =", e2, " min >1/72:", min(e1, e2) > Fr(1, 72))
assert e1 == Fr(279, 20000) and e2 == Fr(113, 3600) and min(e1, e2) > Fr(1, 72)
n3 = (Fr(71, 200) - Fr(9, 200)) * (1 - Fr(71, 200)); print("  (62/200)(129/200) =", n3)
assert n3 == Fr(3999, 20000)
m2 = 2 * n3 - Fr(1, 72); print("  2*3999/20000 - 1/72 =", float(m2), "> (31/50)^2 =", float(Fr(31, 50) ** 2)); assert m2 > Fr(31, 50) ** 2
R2 = 4 * Fr(9, 200) * Fr(191, 200); print("  4*9/200*191/200 =", R2, "< (83/200)^2 =", Fr(83, 200) ** 2); assert R2 == Fr(1719, 10000) and R2 < Fr(83, 200) ** 2
assert Fr(31, 50) - Fr(83, 200) == Fr(41, 200)
fin = Fr(1, 3) * Fr(41, 200) ** 2; print("  (1/3)(41/200)^2 =", fin, "> 1/72:", fin > Fr(1, 72)); assert fin == Fr(1681, 120000) and fin > Fr(1, 72)
assert Fr(29, 100) ** 2 > Fr(1, 12); assert (1 - Fr(29, 100)) / 2 == Fr(71, 200); assert Fr(1, 6) ** 2 * 2 >= 0
assert Fr(1, 12) < Fr(29, 100) ** 2 and Fr(1, 72) * 2 == Fr(1, 36)
# Step 2 endpoint claim on a grid: for lambda in (71/200, 1/2], n in [9/200,1/6], n(lambda-n) > min(...) > 1/72
worst = min(n * (l - n) for l in np.linspace(71 / 200, 0.5, 301)[1:] for n in np.linspace(9 / 200, 1 / 6, 301))
print("  grid min of n(lambda-n) over lambda in (71/200,1/2], n in [9/200,1/6]:", worst, "> 1/72 =", 1 / 72)
assert worst > 1 / 72
print("  4n(1-n) increasing on [0,1/2): derivative 4(1-2n) > 0 -> value at 9/200 is the max for n_h < 9/200: OK")

# ---------------- minimization ----------------
def f(x):
    psi = x[:6] + 1j * x[6:]
    psi = psi / np.linalg.norm(psi)
    return float((((np.abs(Uall.conj().T @ psi) ** 2) - 1 / 6) ** 2).sum())


mins, endpoints = [], []
for _ in range(200):
    r = minimize(f, rng.normal(size=12), method="BFGS", options={"gtol": 1e-12})
    mins.append(r.fun)
    psi = r.x[:6] + 1j * r.x[6:]
    endpoints.append(psi / np.linalg.norm(psi))
mins = np.array(mins)
print(f"\nMIN: 200 random-start BFGS minimizations of E: smallest {mins.min():.10f}, largest local value {mins.max():.6f}")
print(f"     claimed exact min (4-sqrt6)/40 = {(4 - np.sqrt(6)) / 40:.10f}; 0.0385 ; 1/72 = {1 / 72:.8f}")
print(f"     starts within 1e-8 of the smallest: {(mins < mins.min() + 1e-8).sum()}")
assert mins.min() >= 0.0385 and mins.min() > 1 / 72
# bounds on the 200 minimizer endpoints
check_all(np.array(endpoints), "200 minimizer endpoints (worst cases)")
print(f"\nruntime {time.time() - t0:.1f} s")
print("OK")
