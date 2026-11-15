"""Hide-and-seek: can a pure state look like white noise to three mutually unbiased LOCAL measurements?

  d = 4 (two qubits, settings Z(x)Z, X(x)X, Y(x)Y): yes. psi4 = (1,1,i,-i)/2 is uniform in all three.
  d = 6 (qubit (x) qutrit, canonical product triple): no. Certified: E(psi) >= 0.0385 for every pure state
        (degree-six certificate, cert/verify.py), where E = sum over the 18 outcomes of (p - 1/6)^2.

The hider prepares the state that is hardest to catch; the referee takes N shots in each of the three
settings and runs Pearson's chi-square test for uniformity (3(d-1) degrees of freedom). The statistic has
mean shift (noncentrality) d*N*E, so the minimum-energy state is the best hider and E is the detectability
per shot.

Same conventions as src/visibility/t5_sim.py: circuits transpiled to {cx,u}; depolarising error r on cx and
r/10 on u; exact outcome probabilities from Aer's density-matrix method; shot noise by multinomial sampling
from those probabilities. A simulator repeats linear algebra and proves nothing: its job here is to turn
E into shots and gate-error requirements. The embedding differs from t5_sim on purpose: the qubit is one
physical qubit and the qutrit is two (level |11> unused), so every measurement setting is LOCAL -- no gate
between the qubit and the qutrit is needed to measure.
"""
import json, sys, time
import numpy as np
from scipy.stats import chi2, ncx2
from scipy.optimize import brentq
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import UnitaryGate, StatePreparation
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
P4_BASES = sys.argv[2] if len(sys.argv) > 2 else None        # results/visibility/bases_d6_P4.npy
SIM_JSON = sys.argv[3] if len(sys.argv) > 3 else None        # results/visibility/sim.json
E_CERT = 0.0385                                              # certified lower bound, canonical triple
rng = np.random.default_rng(2026)
w = np.exp(2j * np.pi / 3)
H2 = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
A = [np.eye(2, dtype=complex), H2.astype(complex), np.diag([1, 1j]) @ H2]      # Z, X, Y eigenbases
F = np.array([[w ** (j * k) for k in range(3)] for j in range(3)]) / np.sqrt(3)
Dg = np.diag([1, w, w])
B = [np.eye(3, dtype=complex), F, Dg @ F]
C = Dg @ Dg @ F


def hider_d6():
    """Closed-form minimum-energy state of the structure paper (first version) eq. (20); E = (4 - sqrt 6)/40."""
    h = np.sqrt((3 + np.sqrt(3)) / 6); l = np.sqrt((3 - np.sqrt(3)) / 6); eta = (1 + 1j) / np.sqrt(2)
    qm = np.array([l, eta * h]); qp = np.array([-h, eta * l])
    u = np.sqrt(3) / 2; v = np.sqrt((11 - 4 * np.sqrt(6)) / 20)
    x = ((u - v) / 2) ** 2; y = ((u + v) / 2) ** 2; z = (7 + 2 * np.sqrt(6)) / 20
    psi = (np.sqrt(x) * np.exp(1j * np.pi / 3) * np.kron(qm, C[:, 0]) + np.sqrt(y) * np.exp(2j * np.pi / 3) * np.kron(qm, C[:, 1])
           + np.sqrt(z) * np.kron(qp, C[:, 2]))
    return psi / np.linalg.norm(psi)


SYSTEMS = {}
# ---- d = 6: index 3a+q  ->  embedded index 4a+q (qubit 2 = a, qubits 1,0 = q; q = 3 unused)
psi6 = hider_d6()
emb6 = np.zeros((2, 4), complex); emb6[:, :3] = psi6.reshape(2, 3)
pad4 = lambda M: np.block([[M, np.zeros((3, 1))], [np.zeros((1, 3)), np.ones((1, 1))]])
SYSTEMS["d6"] = dict(d=6, nq=3, state=emb6.reshape(8), valid=[0, 1, 2, 4, 5, 6],
                     exact=np.array([np.abs(np.kron(A[r], B[r]).conj().T @ psi6) ** 2 for r in range(3)]),
                     meas=[[(UnitaryGate(A[r].conj().T), [2]), (UnitaryGate(pad4(B[r].conj().T)), [0, 1])] for r in range(3)])
# ---- d = 4: index 2a+b (qubit 1 = a, qubit 0 = b)
psi4 = np.array([1, 1, 1j, -1j]) / 2
SYSTEMS["d4"] = dict(d=4, nq=2, state=psi4, valid=[0, 1, 2, 3],
                     exact=np.array([np.abs(np.kron(A[r], A[r]).conj().T @ psi4) ** 2 for r in range(3)]),
                     meas=[[(UnitaryGate(A[r].conj().T), [1]), (UnitaryGate(A[r].conj().T), [0])] for r in range(3)])


def energy(P):
    d = P.shape[1]
    return float(((P - 1 / d) ** 2).sum())


def circuits(sys_):
    out = []
    for r in range(3):
        qc = QuantumCircuit(sys_["nq"])
        qc.append(StatePreparation(sys_["state"]), range(sys_["nq"]))
        qc.barrier()
        for g, q in sys_["meas"][r]:
            qc.append(g, q)
        out.append(qc)
    return out


def noise_model(r):
    nm = NoiseModel(basis_gates=["cx", "u"])
    nm.add_all_qubit_quantum_error(depolarizing_error(r, 2), ["cx"])
    nm.add_all_qubit_quantum_error(depolarizing_error(r / 10, 1), ["u"])
    return nm


dm = AerSimulator(method="density_matrix")


def probabilities(tc, sys_, r):
    """Exact outcome distributions: returns (post-selected 3 x d matrix, raw 3 x (d+1) with leakage last)."""
    cs = [c.copy() for c in tc]
    for c in cs:
        c.save_probabilities()
    res = dm.run(cs, noise_model=noise_model(r) if r > 0 else None).result()
    raw = np.array([np.array(res.data(i)["probabilities"]) for i in range(3)])
    val = raw[:, sys_["valid"]]
    leak = 1 - val.sum(axis=1)
    return val / val.sum(axis=1, keepdims=True), np.column_stack([val, np.clip(leak, 0, None)])


def statistic(counts):
    """Pearson chi-square for uniformity, summed over the three settings. counts: trials x 3 x d (valid outcomes)."""
    m = counts.sum(axis=2, keepdims=True); d = counts.shape[2]
    e = np.maximum(m / d, 1e-300)
    return (((counts - e) ** 2) / e).sum(axis=(1, 2))


def detect_rate(raw, N, thr, trials):
    cnt = np.stack([rng.multinomial(N, raw[r] / raw[r].sum(), size=trials) for r in range(3)], axis=1)   # trials x 3 x (d+1)
    return float((statistic(cnt[:, :, :-1]) > thr).mean())


def shots_needed(E, d, alpha, power):
    """Shots per setting so that the chi-square test at false-alarm alpha detects with the given power (noncentral chi-square)."""
    df = 3 * (d - 1); thr = chi2.isf(alpha, df)
    if E <= 0:
        return float("inf")
    f = lambda N: ncx2.sf(thr, df, d * N * E) - power
    return float(brentq(f, 1e-3, 1e12))


if __name__ == "__main__":
    t0 = time.time(); R = {"conventions": "cx depolarising rate r, u rate r/10; chi-square uniformity test over 3 settings"}
    ALPHA = 1e-3; ALPHA5 = 2.866515718791933e-07       # one-sided 5 sigma
    Ns = np.unique(np.round(np.logspace(1, np.log10(5000), 28)).astype(int))
    rates_curve = [0.0, 1e-3, 1e-2]
    rates_scan = [0.0] + list(np.logspace(-6, -1, 21))
    TR = 20000
    for name, S in SYSTEMS.items():
        d = S["d"]; df = 3 * (d - 1); thr = chi2.isf(ALPHA, df)
        qcs = circuits(S)
        tc = transpile(qcs, basis_gates=["cx", "u"], optimization_level=3, seed_transpiler=7)
        meas_only = []
        for r in range(3):
            q = QuantumCircuit(S["nq"])
            for g, qq in S["meas"][r]:
                q.append(g, qq)
            meas_only.append(transpile(q, basis_gates=["cx", "u"], optimization_level=3, seed_transpiler=7))
        rec = dict(d=d, dof=df, threshold_alpha_1em3=float(thr),
                   cx_total=[int(c.count_ops().get("cx", 0)) for c in tc],
                   cx_measurement_only=[int(c.count_ops().get("cx", 0)) for c in meas_only],
                   u_total=[int(c.count_ops().get("u", 0)) for c in tc])
        P0, raw0 = probabilities(tc, S, 0.0)
        rec["noiseless_circuit_vs_exact_max_dev"] = float(np.abs(P0 - S["exact"]).max())
        rec["E_exact"] = energy(S["exact"]); rec["max_bias_exact"] = float(np.abs(S["exact"] - 1 / d).max())
        # false-alarm calibration under exact uniformity
        uni = np.ones((3, d + 1)); uni[:, -1] = 0
        rec["false_alarm_measured"] = {int(N): detect_rate(uni, int(N), thr, 200000) for N in (10, 30, 100, 1000)}
        # detection curves
        rec["curves"] = {}
        for r in rates_curve:
            P, raw = probabilities(tc, S, r)
            rec["curves"][str(r)] = dict(E=energy(P), leak=float(raw[:, -1].mean()), N=[int(n) for n in Ns],
                                         detect=[detect_rate(raw, int(n), thr, TR) for n in Ns],
                                         theory=[float(ncx2.sf(thr, df, d * n * energy(P))) if energy(P) > 1e-14 else ALPHA for n in Ns])
            print(name, "rate", r, "E", rec["curves"][str(r)]["E"], "leak", rec["curves"][str(r)]["leak"], flush=True)
        # noise scan
        scan = []
        for r in rates_scan:
            P, raw = probabilities(tc, S, r); E = energy(P)
            scan.append(dict(rate=float(r), E=E, max_bias=float(np.abs(P - 1 / d).max()), leak=float(raw[:, -1].mean()),
                             shots_per_setting_5sigma_50pct=shots_needed(E, d, ALPHA5, 0.5) if E > 1e-12 else None,
                             shots_per_setting_alpha1em3_99pct=shots_needed(E, d, ALPHA, 0.99) if E > 1e-12 else None))
        rec["scan"] = scan
        # sampled-shot validation with real per-shot simulation
        val = {}
        for r in (0.0, 1e-2):
            cs = [c.copy() for c in tc]
            for c in cs:
                c.measure_all()
            shots = 200000
            res = dm.run(cs, noise_model=noise_model(r) if r > 0 else None, shots=shots, seed_simulator=11).result()
            _, raw = probabilities(tc, S, r); worst = 0.0
            for i in range(3):
                cnts = res.get_counts(i); f = np.zeros(2 ** S["nq"])
                for k, v in cnts.items():
                    f[int(k, 2)] = v / shots
                full = np.zeros(2 ** S["nq"]); full[S["valid"]] = raw[i, :-1]
                sig = np.sqrt(np.maximum(full * (1 - full), 1e-12) / shots)
                worst = max(worst, float((np.abs(f - full)[S["valid"]] / sig[S["valid"]]).max()))
            val[str(r)] = dict(shots_per_setting=shots, worst_deviation_in_sigma=worst)
        rec["sampled_shot_validation"] = val
        R[name] = rec
        print(name, "cx", rec["cx_total"], "meas-only cx", rec["cx_measurement_only"], "dev", rec["noiseless_circuit_vs_exact_max_dev"],
              "E", rec["E_exact"], "false alarm", rec["false_alarm_measured"], "validation", val, flush=True)
    # certified floor for any pure state against the canonical triple (noiseless)
    df = 15; thr = chi2.isf(ALPHA, df)
    R["certified"] = dict(E_lower_bound=E_CERT, N=[int(n) for n in Ns],
                          detect_floor=[float(ncx2.sf(thr, df, 6 * n * E_CERT)) for n in Ns],
                          shots_per_setting_alpha1em3_99pct=shots_needed(E_CERT, 6, ALPHA, 0.99),
                          shots_per_setting_5sigma_50pct=shots_needed(E_CERT, 6, ALPHA5, 0.5),
                          shots_per_setting_5sigma_99pct=shots_needed(E_CERT, 6, ALPHA5, 0.99),
                          note="chi-square (large-N) approximation of the test; the bound on E itself is certified")
    # the guessing game, for comparison (numbers recomputed from the saved bases and sim.json)
    if P4_BASES and SIM_JSON:
        Bs = np.load(P4_BASES); mu = 0.5 + 0.5 / np.sqrt(6)
        P4 = np.mean([0.5 + np.abs(Bs[a].conj().T @ Bs[b]).sum() / 72 for a in range(4) for b in range(a + 1, 4)])
        gap = mu - P4; sim = json.load(open(SIM_JSON))
        g = dict(P4=float(P4), gap=float(gap), rounds_5sigma=float(25 * mu * (1 - mu) / gap ** 2))
        for key in ("separate", "fused"):
            slope = sim["noise"][key]["6"]["rates"]["1e-06"]["deficit"] / 1e-6
            g[f"rate_where_noise_loss_equals_gap_{key}"] = float(gap / slope)
        R["game"] = g; print("game", g)
    R["elapsed_s"] = time.time() - t0
    json.dump(R, open(f"{OUT}/hide_seek.json", "w"), indent=1)
    print("certified", {k: v for k, v in R["certified"].items() if k.startswith("shots")})
