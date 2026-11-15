"""Numerical check of the cube-rank / cubic-cap identities for order-six complex Hadamard matrices
(report Section 4.1-4.2, Proposition "Cubic norm cap", eqs. eq:VV, eq:fourier27, eq:BK).

DEFINITIONS (as in the report).  H is 6x6, |H_ij| = 1, H*H = 6I.  M = entrywise cube of H.  V is the 20x6 matrix
V_{I,j} = prod_{a in I} H_{aj} over 3-subsets I of {0..5}.  K = V V* (20x20).  B_{IJ} = 2|I n J| - 3.
CLAIMS TESTED.
  (VV)   V*V = 18 I + M*M/3.  Derived from column orthogonality alone, so claimed for EVERY Hadamard H.
  (F27)  eq:fourier27: sum_j prod_{a in I} H_aj prod_{b not in I} conj(H_bj) = 0 for every 3-set I, i.e.
         K_{I,I^c} = 0.  Claimed (cited result) for every H NOT equivalent to the cubic Tao matrix.
  (BK)   B o K = 24 I - K (o = Schur product).  The derivation uses row orthogonality and (F27), so it is
         claimed only for H satisfying (F27).
  (CAP)  ||M||_op^2 <= 18; rank M >= 2; tr((M*M)^2) <= 648 with equality iff rank M = 2; rank M = 2 implies
         ||M||_op^2 = 18.  Claimed for H satisfying (F27).
  (RANK) cube rank <= 2 iff H is Fourier-family, transposed Fourier-family or the cubic Tao matrix.
FAMILIES.  (a) Fourier family F6(a,b) of Tadej-Zyczkowski (random a,b, 60 matrices) and the report's family
H(z)_{(t,a),(s,b)} = w^{ts} (-1)^{ab} z_t^b (60 matrices); their transposes; (b) Tao's matrix S6 as defined in the
report (exponent vectors in Section 4) and 20 random standard equivalents; (c) Dita's D6; (d) >= 200 numerical
"generic" Hadamard matrices from random unimodular starts, Gauss-Newton on the 15 complex orthogonality
equations, accepted when ||H*H - 6I||_F < 1e-11.  Each matrix is also tested after a random standard
equivalence (row/column permutations and unimodular rephasing) in the Fourier and generic classes.
This is a numerical check (double precision), not a proof; rank uses singular values with tolerance 1e-8.
"""
import itertools, time
import numpy as np

t0 = time.time()
rng = np.random.default_rng(2026)
w = np.exp(2j * np.pi / 3)
w6 = np.exp(2j * np.pi / 6)
subs = list(itertools.combinations(range(6), 3))
idx = {s: i for i, s in enumerate(subs)}
comp = [idx[tuple(sorted(set(range(6)) - set(s)))] for s in subs]
Bm = np.array([[2 * len(set(I) & set(J)) - 3 for J in subs] for I in subs], float)


def hadamard_err(H):
    return np.linalg.norm(H.conj().T @ H - 6 * np.eye(6))


def analyse(H):
    M = H ** 3
    V = np.array([[np.prod(H[list(I), j]) for j in range(6)] for I in subs])
    K = V @ V.conj().T
    G = M.conj().T @ M
    vv = np.abs(V.conj().T @ V - 18 * np.eye(6) - G / 3).max()
    f27 = max(abs(K[i, comp[i]]) for i in range(20))
    bk = np.abs(Bm * K - 24 * np.eye(20) + K).max()
    ev = np.linalg.eigvalsh(G)
    sv = np.linalg.svd(M, compute_uv=False)
    rk = int((sv > 1e-8).sum())
    tr2 = float((G @ G).trace().real)
    return dict(vv=vv, f27=f27, bk=bk, n2=ev.max(), rk=rk, tr2=tr2, K24=ev.max())


def equiv(H):
    P, Q = rng.permutation(6), rng.permutation(6)
    D1 = np.diag(np.exp(2j * np.pi * rng.random(6)))
    D2 = np.diag(np.exp(2j * np.pi * rng.random(6)))
    return D1 @ H[P][:, Q] @ D2


# ---------------- families ----------------
F6 = np.array([[w6 ** (j * k) for k in range(6)] for j in range(6)])
fam = {}


def TZ(a, b):
    R = np.zeros((6, 6))
    for r in (1, 3, 5):
        R[r, [1, 4]] = a
        R[r, [2, 5]] = b
    return F6 * np.exp(1j * R)


def report_family(z):  # rows (t,a), cols (s,b); index = t + 3a ... any fixed bijection
    H = np.zeros((6, 6), complex)
    for t in range(3):
        for a in range(2):
            for s in range(3):
                for b in range(2):
                    H[t + 3 * a, s + 3 * b] = w ** (t * s) * (-1) ** (a * b) * z[t] ** b
    return H


ab = rng.uniform(0, 2 * np.pi, (60, 2))
fam['Fourier F6(a,b) [Tadej-Zyczkowski]'] = [TZ(a, b) for a, b in ab]
fam['transpose of F6(a,b)'] = [TZ(a, b).T for a, b in ab]
zs = np.exp(2j * np.pi * rng.random((60, 3)))
fam['report family H(z) (w^{ts}(-1)^{ab} z_t^b)'] = [report_family(z) for z in zs]
fam['transpose of H(z)'] = [report_family(z).T for z in zs]
fam['F6 standard equivalents (random perm/phases)'] = [equiv(TZ(a, b)) for a, b in ab[:30]]

tao_exp = np.array([(0, 0, 0, 0, 0, 0), (0, 0, 1, 1, 2, 2), (0, 1, 0, 2, 1, 2), (0, 1, 2, 0, 2, 1),
                    (0, 2, 1, 2, 0, 1), (0, 2, 2, 1, 1, 0)])  # columns
S6 = (w ** tao_exp).T
fam['Tao S6 (report definition)'] = [S6]
fam['Tao S6 standard equivalents'] = [equiv(S6) for _ in range(20)]
i_ = 1j
D6 = np.array([[1, 1, 1, 1, 1, 1], [1, -1, i_, -i_, -i_, i_], [1, i_, -1, i_, -i_, -i_],
               [1, -i_, i_, -1, i_, -i_], [1, -i_, -i_, i_, -1, i_], [1, i_, -i_, -i_, i_, -1]], complex)
fam['Dita D6'] = [D6]


# generic numerical Hadamard matrices
def gauss_newton(phi):
    for it in range(200):
        H = np.exp(1j * phi.reshape(6, 6))
        G = H.conj().T @ H
        pairs = [(j, k) for j in range(6) for k in range(j + 1, 6)]
        r = np.array([G[j, k] for j, k in pairs])
        res = np.concatenate([r.real, r.imag])
        if np.linalg.norm(res) < 1e-14:
            break
        J = np.zeros((15, 36), complex)
        for p, (j, k) in enumerate(pairs):
            for a in range(6):
                J[p, 6 * a + j] += -1j * np.conj(H[a, j]) * H[a, k]
                J[p, 6 * a + k] += 1j * np.conj(H[a, j]) * H[a, k]
        Jr = np.vstack([J.real, J.imag])
        step = np.linalg.lstsq(Jr, res, rcond=1e-12)[0]
        nrm = np.linalg.norm(step)
        phi = phi - step * (1.0 if nrm < 1.0 else 1.0 / nrm)
    return phi


gen, tried = [], 0
while len(gen) < 700 and time.time() - t0 < 110:
    tried += 1
    phi = gauss_newton(rng.uniform(0, 2 * np.pi, 36))
    H = np.exp(1j * phi.reshape(6, 6))
    if hadamard_err(H) < 1e-11:
        gen.append(H)
print(f"generic search: {len(gen)} Hadamard matrices accepted (||H*H-6I||_F<1e-11) from {tried} random starts "
      f"({time.time() - t0:.0f} s)")
assert len(gen) >= 200


def invariant(H):  # equivalence-invariant multiset of 4-point products H_ij H_kl conj(H_il H_kj)
    v = []
    for i in range(6):
        for k in range(i + 1, 6):
            for j in range(6):
                for l in range(j + 1, 6):
                    v.append(H[i, j] * H[k, l] * np.conj(H[i, l] * H[k, j]))
    v = np.array(v)
    return np.sort_complex(np.round(v.real, 6) + 1j * np.abs(np.round(v.imag, 6)) + 0.0)  # |Im|: row order flips conjugation


inv_tao = invariant(S6)
split = {'generic: cube rank 1': [], 'generic: cube rank 2': [], 'generic: cube rank >= 3': []}
for H in gen:
    rk = analyse(H)['rk']
    split['generic: cube rank 1' if rk == 1 else 'generic: cube rank 2' if rk == 2 else 'generic: cube rank >= 3'].append(H)
ntao_inv = sum(np.abs(invariant(H) - inv_tao).max() < 1e-5 for H in split['generic: cube rank 1'])
print(f"generic search split: rank1 {len(split['generic: cube rank 1'])} (of which share Tao's 4-point invariant: {ntao_inv}), "
      f"rank2 {len(split['generic: cube rank 2'])}, rank>=3 {len(split['generic: cube rank >= 3'])}")
assert ntao_inv == len(split['generic: cube rank 1'])
fam.pop('generic numerical Hadamard (random starts)', None)
for k, v in split.items():
    if v:
        fam[k + ' (random-start numerical Hadamard)'] = v

# random standard equivalents of the generic non-Tao matrices
fam['generic rank>=3, random standard equivalents'] = [equiv(H) for H in split['generic: cube rank >= 3'][:100]]
# ---------------- evaluation ----------------
CLAIM_F27 = {'Tao S6 (report definition)': False, 'Tao S6 standard equivalents': False}
tab = []
warn = []
print("\nHadamard defect max per family, then identity violations (max over family):")
hdr = f"{'family':50s} {'n':>4s} {'|H*H-6I|':>9s} {'VV':>9s} {'F27':>9s} {'BK':>9s} {'max||M||^2':>10s} {'max tr2':>9s}  cube ranks"
print(hdr)
for name, Hs in fam.items():
    res = [analyse(H) for H in Hs]
    herr = max(hadamard_err(H) for H in Hs)
    assert herr < 1e-11, (name, herr)
    vv = max(r['vv'] for r in res); f27 = max(r['f27'] for r in res); bk = max(r['bk'] for r in res)
    n2 = max(r['n2'] for r in res); tr2 = max(r['tr2'] for r in res)
    ranks = {}
    for r in res:
        ranks[r['rk']] = ranks.get(r['rk'], 0) + 1
    print(f"{name:50s} {len(Hs):4d} {herr:9.1e} {vv:9.1e} {f27:9.1e} {bk:9.1e} {n2:10.5f} {tr2:9.3f}  {dict(sorted(ranks.items()))}")
    tab.append((name, ranks))
    is_tao = name.startswith('Tao') or 'cube rank 1' in name
    # claims
    if vv > 1e-9:
        warn.append(f"!!! WARNING: (VV) V*V=18I+M*M/3 fails for '{name}', max violation {vv:.3e} (claimed for all H)")
    if not is_tao:
        if f27 > 1e-9:
            warn.append(f"!!! WARNING: (F27) fails for non-Tao '{name}', max |K_(I,I^c)| = {f27:.3e}")
        if bk > 1e-9:
            warn.append(f"!!! WARNING: (BK) B o K = 24I - K fails for non-Tao '{name}', max violation {bk:.3e}")
        if n2 > 18 + 1e-9:
            warn.append(f"!!! WARNING: cap ||M||^2<=18 fails for '{name}': {n2:.6f}")
        if tr2 > 648 + 1e-7:
            warn.append(f"!!! WARNING: tr((M*M)^2)<=648 fails for '{name}': {tr2:.6f}")
        if min(ranks) < 2:
            warn.append(f"!!! WARNING: cube rank < 2 for non-Tao '{name}'")
    # per-matrix equality / implication checks (non-Tao)
    if not is_tao:
        for r in res:
            if (abs(r['tr2'] - 648) < 1e-7) != (r['rk'] == 2):
                warn.append(f"!!! WARNING: trace equality <-> rank 2 fails in '{name}': tr2={r['tr2']}, rank={r['rk']}")
                break
        for r in res:
            if r['rk'] == 2 and abs(r['n2'] - 18) > 1e-7:
                warn.append(f"!!! WARNING: rank 2 but ||M||^2 = {r['n2']} != 18 in '{name}'")
                break
    else:
        print(f"    note (Tao, not claimed): (F27) violation {f27:.3e}; (BK) violation {bk:.3e}; ||M||^2 = {n2:.4f} "
              f"(M is the all-ones matrix, ||M||^2 = 36 > 18); tr((M*M)^2) = {tr2:.1f} > 648; cube rank {sorted(ranks)}")

# rank(M) <= 2 iff Fourier/transposed/Tao: every generic matrix must have cube rank >= 3, or be Fourier-type
gen_ranks = {}
for r in map(analyse, gen):
    gen_ranks[r['rk']] = gen_ranks.get(r['rk'], 0) + 1
print("\ncube-rank histogram of the generic numerical matrices:", dict(sorted(gen_ranks.items())))
low = [H for H in gen if analyse(H)['rk'] <= 2]
print("generic matrices with cube rank <= 2 (Fourier-type expected):", len(low))

# near-extremal check: largest ||M||^2 over everything non-Tao
allmax = max(analyse(H)['n2'] for name, Hs in fam.items() if not (name.startswith('Tao') or 'cube rank 1' in name) for H in Hs)
print(f"largest ||M||_op^2 over all non-Tao matrices tested: {allmax:.10f} (cap 18)")

print("\nTable: family -> cube rank (count of matrices)")
for name, ranks in tab:
    print(f"  {name:50s} {dict(sorted(ranks.items()))}")
print(f"\nruntime {time.time() - t0:.1f} s")
if warn:
    print("\n".join(warn))
    raise SystemExit("DISCREPANCIES FOUND")
print("OK")
