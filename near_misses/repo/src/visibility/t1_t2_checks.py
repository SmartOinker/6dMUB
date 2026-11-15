"""Tasks 1,2 (+ gradient check): derivation check, MUB sanity, gradient correctness."""
import numpy as np, json
from common import *
rng = np.random.default_rng(1)
res = {}

# Task 1: brute force. For each (i,j) the optimal state is top eigenvector of |e_i><e_i|+|f_j><f_j|;
# success = 1/(2 d^2) * sum_{ij} (<e_i|psi|e_i> + <f_j|psi|f_j>) averaged = P
def brute(A, B):
    d = A.shape[0]; tot = 0
    for i in range(d):
        for j in range(d):
            M = np.outer(A[:, i], A[:, i].conj()) + np.outer(B[:, j], B[:, j].conj())
            w, V = np.linalg.eigh(M); psi = V[:, -1]
            tot += abs(np.vdot(A[:, i], psi)) ** 2 + abs(np.vdot(B[:, j], psi)) ** 2
    return tot / (2 * d * d)
res['task1'] = {}
for d in (3, 6):
    errs = [abs(brute(haar(d, rng), haar(d, rng)) - 0) for _ in range(0)]
    errs = []
    for _ in range(20):
        A, B = haar(d, rng), haar(d, rng)
        errs.append(abs(brute(A, B) - P_pair(A, B)))
    res['task1'][f'd{d}_max_abs_err_20_random_pairs'] = max(errs)
    print('task1 d', d, max(errs))

# Task 2
res['task2'] = {}
for d in (5, 7):
    M = mubs_prime(d)
    for B in M: assert is_unitary(B)
    from itertools import combinations as C
    worst = 0
    for quad in C(range(d + 1), 4):
        worst = max(worst, abs(P_n([M[i] for i in quad]) - P_bound(d)))
    res['task2'][f'd{d}_max_dev_over_all_4subsets'] = worst
    print('d', d, 'max |P4-bound|', worst)
M6 = mubs_d6()
for B in M6: assert is_unitary(B)
res['task2']['d6_P3_minus_bound'] = P_n(M6) - P_bound(6)
res['task2']['d6_D2_3mubs'] = D2_n(M6)
print('d6 P3-bound', P_n(M6) - P_bound(6), 'D2', D2_n(M6))

# gradient check (finite differences), both objectives, d=6, n=4
for kind in 'PD':
    d, n = 6, 4
    fg = make_fg(d, n, kind, 1e-3)
    x = rng.standard_normal(3 * make_index(d)[1]) * 0.5
    f0, g = fg(x)
    num = np.zeros_like(x)
    for i in range(len(x)):
        e = np.zeros_like(x); e[i] = 1e-6
        num[i] = (fg(x + e)[0] - fg(x - e)[0]) / 2e-6
    res['task2'][f'gradcheck_{kind}_max_abs_diff'] = np.abs(num - g).max()
    print('gradcheck', kind, np.abs(num - g).max(), np.abs(g).max())
# round trip x<->U
U = haar(6, rng); x = x_from_unitary(U, 6); U2 = unitary_and_cache(x, 6)[0]
res['task2']['param_roundtrip_err'] = np.abs(U - U2).max()
print('roundtrip', np.abs(U - U2).max())
json.dump(res, open(OUT + '/checks.json', 'w'), indent=1)
