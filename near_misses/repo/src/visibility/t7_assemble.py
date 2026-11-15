"""Task 7 assembly: add key worst_case_bias to results.json; copy bases_d6_delta JSON."""
import json, numpy as np
from common import *
L = lambda f: json.load(open(f"{OUT}/{f}"))
d6, fx, d5, d7 = L('delta_d6_delta.json'), L('delta_d6_delta_fixedtriple.json'), L('delta_d5_delta.json'), L('delta_d7_delta.json')
sh = lambda dl: 25 * (1 / 6) * (5 / 6) / dl ** 2       # N = z^2 p0 (1-p0)/delta^2, z=5, p0=1/6
p4, d2 = L('opt_d6_P4.json'), L('opt_d6_D2.json')
W = dict(label='numerical upper bound on the minimum: explicit bases achieve this delta; nothing proves a lower bound',
  best_delta=d6['best_delta'], pair_max=d6['pair_max'], n_active_overlaps_1em6=d6['n_active_within_1em6'], n_overlaps=216,
  structure=d6['structure'], P_4=d6['P_n'], D2=d6['D2_n'], n_starts=d6['n_starts_run'], delta_by_start_kind=d6['delta_by_kind'],
  delta_of_P4_optimal_set=0.0406, delta_of_D2_optimal_set=0.0423,
  calibration=dict(d5_best=d5['best_delta'], d5_starts=d5['n_starts_run'], d5_starts_below_1em9=d5['n_starts_below_1em9'],
                   d7_best=d7['best_delta'], d7_starts=d7['n_starts_run'], d7_starts_below_1em9=d7['n_starts_below_1em9'],
                   note='calib mode: cheap p=2 pre-screen, polish only runs already <1e-3; random starts only'),
  fixed_exact_triple=dict(best_delta=fx['best_delta'], pair_max=fx['pair_max'], n_active=fx['n_active_within_1em6'],
                          structure=fx['structure'], P_4=fx['P_n'], D2=fx['D2_n'], n_starts=fx['n_starts_run']),
  shots_5sigma_single_setting=dict(delta=d6['best_delta'], N=sh(d6['best_delta']), formula='N=25*(1/6)(5/6)/delta^2 (null p0=1/6)',
                                   N_for_fixed_triple_fourth=sh(fx['best_delta'])))
R = L('results.json'); R['worst_case_bias'] = W
json.dump(R, open(f"{OUT}/results.json", 'w'), indent=1, default=float)
B = np.load(f"{OUT}/bases_d6_delta.npy")
json.dump(dict(re=[b.real.tolist() for b in B], im=[b.imag.tolist() for b in B]), open(f"{OUT}/bases_d6_delta.json", 'w'))
# independent re-verification from the saved bases
Bs = list(B); dev = np.concatenate([(np.abs(Bs[a].conj().T @ Bs[b])**2 - 1/6).ravel() for a in range(4) for b in range(a+1, 4)])
print('verify delta', np.abs(dev).max(), 'unitary', all(is_unitary(b, 1e-12) for b in Bs), 'P4', P_n(Bs), 'D2', D2_n(Bs))
print(json.dumps(W, indent=1, default=float)[:2500])
