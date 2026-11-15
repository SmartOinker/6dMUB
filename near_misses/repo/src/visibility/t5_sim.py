"""Task 5: Qiskit Aer simulation of the 2->1 d-level QRAC embedded in 3 qubits.
(a) exact noiseless probabilities for ALL settings (pair, x1, x2, y) -> P_4
(b) shot-noise: multinomial/binomial sampling from those exact probabilities (no per-shot circuits)
(c) depolarising noise on transpiled circuits (basis cx,u), SAMPLED settings (fixed seed), exact noisy
    probabilities from Aer density-matrix simulation (save_probabilities), so no shot noise there.
    Estimator: P_noisy = P_exact(formula) - mean over sampled settings of (p_noiseless - p_noisy)  [paired difference]."""
import json, time, numpy as np
from itertools import combinations
from scipy.linalg import qr
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import UnitaryGate
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from common import *

rng = np.random.default_rng(2026)
NQ = 3; D8 = 8
def pad(M):
    d = M.shape[0]; P = np.eye(D8, dtype=complex); P[:d, :d] = M; return P

def optimal_state(A, B, i, j):
    d = A.shape[0]
    M = np.outer(A[:, i], A[:, i].conj()) + np.outer(B[:, j], B[:, j].conj())
    w, V = np.linalg.eigh(M); return V[:, -1]

def prep_unitary(psi, d):
    v = np.zeros(D8, complex); v[:d] = psi
    Z = np.eye(D8, dtype=complex); Z[:, 0] = v
    Q, R = qr(Z); Q = Q.astype(complex)
    Q[:, 0] = v                      # fix global phase: column 0 exactly psi
    assert np.abs(Q.conj().T @ Q - np.eye(D8)).max() < 1e-12
    return Q

def meas_unitary(B):                  # maps basis vector b_i -> |i>, identity on unused levels
    return pad(B.conj().T)

def settings_all(n, d):
    return [(a, b, x1, x2, y) for a, b in combinations(range(n), 2) for x1 in range(d) for x2 in range(d) for y in (0, 1)]

def build(Bs, d, s, fused):
    a, b, x1, x2, y = s
    psi = optimal_state(Bs[a], Bs[b], x1, x2)
    U = prep_unitary(psi, d); V = meas_unitary(Bs[a] if y == 0 else Bs[b])
    qc = QuantumCircuit(NQ)
    if fused: qc.append(UnitaryGate(V @ U), [0, 1, 2])
    else:
        qc.append(UnitaryGate(U), [0, 1, 2]); qc.barrier(); qc.append(UnitaryGate(V), [0, 1, 2])
    target = x1 if y == 0 else x2
    return qc, target

def run_all(Bs, d, settings, fused, sim, noise_model=None, tcache=None):
    circs, targets = [], []
    for s in settings:
        qc, t = build(Bs, d, s, fused); circs.append(qc); targets.append(t)
    if tcache is None: tc = circs
    else: tc = tcache
    tc = [c.copy() for c in tc]
    for c in tc: c.save_probabilities()
    r = sim.run(tc, noise_model=noise_model).result()
    p = np.array([np.array(r.data(i)['probabilities'])[t] for i, t in enumerate(targets)])
    return p, circs

def get_sets():
    Bs = {}
    M5, M7 = mubs_prime(5), mubs_prime(7)
    Bs[5] = M5[:4]; Bs[7] = M7[:4]
    Bs[6] = list(np.load(f"{OUT}/bases_d6_P4.npy"))
    return Bs

if __name__ == '__main__':
    t0 = time.time(); n = 4; sets = get_sets(); out = {}
    sv = AerSimulator(method='statevector')
    # (a) exact noiseless, ALL settings
    allp = {}
    for d in (5, 6, 7):
        S = settings_all(n, d)
        p, _ = run_all(sets[d], d, S, False, sv)
        # P_4 = mean over settings (uniform pair, x1,x2,y)
        P = p.mean()
        out[f'd{d}'] = dict(P4_sim=float(P), P4_formula=float(P_n(sets[d])), bound=float(P_bound(d)),
                            gap_sim=float(P_bound(d) - P), n_settings=len(S))
        allp[d] = (S, p); print('exact', d, P, P_bound(d) - P, flush=True)
    # (b) shot noise (sampling from exact per-setting probabilities; stratified multinomial over settings)
    shot = {}
    for d in (5, 6, 7):
        S, p = allp[d]; shot[d] = {}
        for N in (10**4, 10**6, 10**8):
            ests = []
            for rep in range(200 if N <= 10**6 else 20):
                cnt = rng.multinomial(N, np.ones(len(S)) / len(S))
                ests.append(rng.binomial(cnt, p).sum() / N)
            ests = np.array(ests); pb = P_bound(d)
            shot[d][N] = dict(mean=float(ests.mean()), sd_over_reps=float(ests.std(ddof=1)),
                              binomial_sigma=float(np.sqrt(pb * (1 - pb) / N)), n_reps=len(ests),
                              mean_minus_bound=float(ests.mean() - pb))
            print('shots', d, N, shot[d][N], flush=True)
    out['shots'] = {str(d): {str(N): v for N, v in shot[d].items()} for d in shot}
    # (c) transpile + depolarising noise
    NS = 200
    rates = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2]
    dm = AerSimulator(method='density_matrix')
    noise = {}
    for fused in (False, True):
        key = 'fused' if fused else 'separate'
        noise[key] = {}
        for d in (5, 6, 7):
            S, p_all = allp[d]
            idx = rng.choice(len(S), NS, replace=False)       # fixed-seed sample of settings
            Ssub = [S[i] for i in idx]
            circs = [build(sets[d], d, s, fused)[0] for s in Ssub]
            targets = [(s[2] if s[4] == 0 else s[3]) for s in Ssub]
            tc = transpile(circs, basis_gates=['cx', 'u'], optimization_level=(3 if fused else 1), seed_transpiler=7)
            cx = [c.count_ops().get('cx', 0) for c in tc]; u1 = [c.count_ops().get('u', 0) for c in tc]  # (before save instr.)
            # sanity: noiseless transpiled circuits still give the right probabilities
            tc = [c.copy() for c in tc]
            for c in tc: c.save_probabilities()   # added after transpilation (not a basis gate)
            r0 = dm.run(tc).result()
            p0 = np.array([np.array(r0.data(i)['probabilities'])[t] for i, t in enumerate(targets)])
            ref = np.array([p_all[i] for i in idx])
            err0 = float(np.abs(p0 - ref).max())
            rec = dict(cx_mean=float(np.mean(cx)), cx_max=int(np.max(cx)), cx_min=int(np.min(cx)),
                       u_mean=float(np.mean(u1)), noiseless_transpile_max_dev=err0, n_sampled_settings=NS, rates={})
            for r2 in rates:
                nm = NoiseModel(basis_gates=['cx', 'u'])
                nm.add_all_qubit_quantum_error(depolarizing_error(r2, 2), ['cx'])
                nm.add_all_qubit_quantum_error(depolarizing_error(r2 / 10, 1), ['u'])
                rr = dm.run(tc, noise_model=nm).result()
                pn = np.array([np.array(rr.data(i)['probabilities'])[t] for i, t in enumerate(targets)])
                diff = ref - pn
                deficit = float(diff.mean()); se = float(diff.std(ddof=1) / np.sqrt(NS))
                Pn = float(P_n(sets[d]) - deficit)
                rec['rates'][str(r2)] = dict(deficit=deficit, deficit_se=se, P4_noisy_est=Pn,
                                             P4_noisy_minus_MUBbound=Pn - P_bound(d))
                print(key, d, r2, rec['rates'][str(r2)], flush=True)
            noise[key][str(d)] = rec
            print(key, d, 'cx mean', rec['cx_mean'], 'max', rec['cx_max'], 'noiseless dev', err0, flush=True)
    out['noise'] = noise; out['elapsed_s'] = time.time() - t0
    json.dump(out, open(f"{OUT}/sim.json", 'w'), indent=1)
