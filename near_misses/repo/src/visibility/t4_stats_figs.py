"""Task 4 (statistics), results.json assembly, Task 6 figures. Reads opt_*.json, sim.json, checks.json."""
import json, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from common import *

L = lambda f: json.load(open(f"{OUT}/{f}"))
o6, o5, o7, oD, sim, chk = L('opt_d6_P4.json'), L('opt_d5_P4.json'), L('opt_d7_P4.json'), L('opt_d6_D2.json'), L('sim.json'), L('checks.json')
pm = P_bound(6); pb = o6['P_n']; delta = pm - pb
R = {}
R['checks'] = chk
R['optimisation'] = {
  'd6_P4_best': pb, 'd6_MUB_value_exact': pm, 'gap_to_MUB': delta, 'literature_best_known_P4': 0.703888,
  'literature_MUB': 0.704124, 'diff_vs_literature_P4': pb - 0.703888,
  'd6_pairwise_P': o6['pairwise_P'], 'd6_D2_of_P4_set': o6['D2_of_this_set'],
  'n_runs_d6_P': o6['n_runs'], 'best_from_random': o6['best_random'], 'best_from_seeded3MUB': o6['best_seeded'],
  'd6_D2_best': oD['D2_n'], 'literature_D2': 0.99829, 'diff_vs_literature_D2': oD['D2_n'] - 0.99829,
  'd6_D2_pairwise': oD['pairwise_D2'], 'd6_P_of_D2_set': oD['P_of_this_set'],
  'd5_best': o5['best'], 'd5_bound': P_bound(5), 'd5_diff': o5['best'] - P_bound(5), 'd5_runs': o5['n_runs'],
  'd7_best': o7['best'], 'd7_bound': P_bound(7), 'd7_diff': o7['best'] - P_bound(7), 'd7_runs': o7['n_runs'],
  'note': 'numerical lower bound on the optimum: the true optimum is at least this; nothing here proves an upper bound'}
# ---- Task 4
def N_needed(p0, p1, z):
    D = abs(p0 - p1)
    one = z**2 * p0 * (1 - p0) / D**2                     # data from p1-world lies z sigma from p0 (null sigma)
    two = z**2 * (np.sqrt(p0 * (1 - p0)) + np.sqrt(p1 * (1 - p1)))**2 / D**2   # both hypotheses z sigma from threshold
    return one, two
st = {'formula_one_sided': 'N = z^2 p0(1-p0)/(p0-p1)^2  (separation of mean from p0 equals z binomial sigma)',
      'formula_two_hypothesis': 'N = z^2 (sqrt(p0 q0)+sqrt(p1 q1))^2/(p0-p1)^2  (threshold z sigma from both)',
      'p_MUB': pm, 'p_best': pb, 'delta': delta}
for z in (3, 5):
    a, b = N_needed(pm, pb, z); st[f'N_{z}sigma'] = a; st[f'N_{z}sigma_two_hyp'] = b
eps = delta / (pm - 1 / 6)
st['eps_budget'] = eps
st['eps_formula'] = 'P_noisy=(1-eps)P+eps/d  =>  eps=(P_MUB-p_best)/(P_MUB-1/d)'
# depolarising on message also shrinks the gap itself: gap_noisy=(1-eps)*gap
st['note_eps'] = ('This is the tolerable UNCERTAINTY/size of un-modelled message noise: a known eps could be corrected for. '
                  'Noise also scales the gap by (1-eps), negligible here.')
# two-qubit gate-error equivalents from simulation (deficit ~ linear in rate)
cr = {}
for key in ('separate', 'fused'):
    r = sim['noise'][key]['6']['rates']; slope = r['1e-06']['deficit'] / 1e-6
    cr[key] = dict(deficit_per_unit_rate=slope, rate_at_which_deficit_equals_gap=delta / slope)
st['gate_error_equiv'] = cr
st['D2'] = {'gap_1_minus_D2': 1 - oD['D2_n'], 'comment': 'D^2 is a property of the bases, not a game probability; no direct round-count. Its 1.7e-3 gap '
            'is ~7x larger than the P gap but is not an observable; the P-game numbers above are what an experiment sees.'}
R['statistics'] = st
R['simulation'] = sim
json.dump(R, open(f"{OUT}/results.json", 'w'), indent=1, default=float)
print(json.dumps(st, indent=1, default=float))

# ---- Figures
plt.rcParams.update({'font.size': 13, 'axes.spines.top': False, 'axes.spines.right': False})
col = {5: '#1b6ca8', 6: '#c8501f', 7: '#2a8f5b'}
fig, ax = plt.subplots(figsize=(7.5, 5))
ds = [5, 6, 7]; floor = 1e-16
gaps = [max(abs(sim[f'd{d}']['gap_sim']), floor) for d in ds]
bars = ax.bar([str(d) for d in ds], gaps, color=[col[d] for d in ds], width=0.55)
for b, d, g in zip(bars, ds, gaps):
    ax.text(b.get_x() + b.get_width() / 2, g * (1.6 if g <= floor else 0.45), '0 (< 1e-15)' if g <= floor else f'{g:.2e}', ha='center', fontsize=12, color='k' if g <= floor else 'white')
for N, ls in ((10**6, '--'), (10**8, ':')):
    s = sim['shots']['6'][str(N)]['binomial_sigma']
    ax.axhline(s, color='k', ls=ls, lw=1.3); ax.text(-0.55, s * 1.25, f'1$\\sigma$ shot noise, N={N:.0e}', ha='left', fontsize=11)
ax.set_yscale('log'); ax.set_ylim(1e-17, 1e-1)
ax.set_xlabel('local dimension d'); ax.set_ylabel(r'MUB bound $-$ best $P_4$  (log scale)')
ax.set_xlim(-0.6, 2.6)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1_gap.png", dpi=300); plt.close(fig)

fig, ax = plt.subplots(figsize=(7.5, 5))
rates = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2]
for d in ds:
    for key, ls in (('separate', '-'), ('fused', '--')):
        r = sim['noise'][key][str(d)]['rates']
        y = [P_bound(d) - r[str(x)]['P4_noisy_est'] for x in rates]
        ax.plot(rates, y, ls, marker='o', color=col[d], label=f'd={d}' if key == 'separate' else None)
ax.plot([], [], 'k-', label='solid: prep and measurement as separate 8x8 unitaries'); ax.plot([], [], 'k--', label='dashed: fused into one unitary')
ax.axhline(delta, color='k', lw=1.5); ax.text(2e-3, delta * 0.55, f'd=6 anomaly: {delta:.2e}', fontsize=12)
ax.set_xscale('log'); ax.set_yscale('log')
ax.set_xlabel('two-qubit depolarising error rate (1-qubit = 1/10 of it)'); ax.set_ylabel(r'MUB bound $-$ $P_4$ (noisy)')
ax.legend(fontsize=10, frameon=False, loc='upper left')
fig.tight_layout(); fig.savefig(f"{OUT}/fig2_noise.png", dpi=300); plt.close(fig)
