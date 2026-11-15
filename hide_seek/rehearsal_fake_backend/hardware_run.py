"""Hide and seek on a real IBM quantum computer (or a local noise model of one).

  python3 hardware_run.py fake:FakeFez  4000 counts_fake.json      # rehearsal, no account needed
  python3 hardware_run.py ibm           4000 counts_ibm.json       # least-busy real device (needs a saved IBM account)
  python3 hardware_run.py ibm:<name>    4000 counts_ibm.json       # a named device

Nine small circuits, each run `shots` times:
  hider6_s0..s2   qubit+qutrit (3 qubits): best-hiding state, measured in the three local settings
  ctrl6_s0,s2     same 3 qubits: an eigenstate of setting 1, measured in settings 0 and 2 (ideal: exactly uniform)
  ctrl6_s1        the same state in its own setting (ideal: one certain outcome) -- sanity check of the circuits
  hider4_s0..s2   two qubits: the perfect hider (1,1,i,-i)/2 in ZZ, XX, YY (ideal: exactly uniform)
The controls measure how much non-uniformity the device itself fakes (readout bias, gate error).
"""
import json, sys, datetime
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import StatePreparation
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import SamplerV2
_argv = sys.argv[:]; sys.argv = sys.argv[:1]          # hide_seek.py reads argv at import; keep it out of the way
from hide_seek import SYSTEMS, A, B
sys.argv = _argv

which = sys.argv[1] if len(sys.argv) > 1 else "fake:FakeFez"
shots = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
out = sys.argv[3] if len(sys.argv) > 3 else "counts.json"

if which.startswith("fake:"):
    import qiskit_ibm_runtime.fake_provider as fp
    backend = getattr(fp, which.split(":")[1])()
else:
    from qiskit_ibm_runtime import QiskitRuntimeService
    service = QiskitRuntimeService()
    backend = service.backend(which.split(":")[1]) if ":" in which else service.least_busy(operational=True, simulator=False, min_num_qubits=3)
print("backend:", backend.name, flush=True)


def circuit(sys_, state, r, name):
    q = QuantumRegister(sys_["nq"], "q"); c = ClassicalRegister(sys_["nq"], "c")
    qc = QuantumCircuit(q, c, name=name)
    qc.append(StatePreparation(state), q)
    qc.barrier()
    for g, qq in sys_["meas"][r]:
        qc.append(g, [q[i] for i in qq])
    qc.measure(q, c)
    return qc


S6, S4 = SYSTEMS["d6"], SYSTEMS["d4"]
ctrl = np.zeros((2, 4), complex); ctrl[:, :3] = np.kron(A[1][:, 0], B[1][:, 0]).reshape(2, 3)      # |+> (x) F|0>, eigenstate of setting 1
ctrl = ctrl.reshape(8); ctrl3 = np.kron(A[1][:, 0], B[1][:, 0])
jobs = []
for r in range(3):
    jobs.append((f"hider6_s{r}", circuit(S6, S6["state"], r, f"hider6_s{r}"), S6["exact"][r], S6["valid"]))
for r in range(3):
    ideal = np.abs(np.kron(A[r], B[r]).conj().T @ ctrl3) ** 2
    jobs.append((f"ctrl6_s{r}", circuit(S6, ctrl, r, f"ctrl6_s{r}"), ideal, S6["valid"]))
for r in range(3):
    jobs.append((f"hider4_s{r}", circuit(S4, S4["state"], r, f"hider4_s{r}"), S4["exact"][r], S4["valid"]))

pm = generate_preset_pass_manager(backend=backend, optimization_level=3, seed_transpiler=7)
isa = [pm.run(qc) for _, qc, _, _ in jobs]
twoq = [sum(v for k, v in c.count_ops().items() if k in ("cx", "ecr", "cz", "rzz")) for c in isa]
sampler = SamplerV2(mode=backend)
job = sampler.run(isa, shots=shots)
print("job id:", job.job_id(), "- waiting for results", flush=True)
res = job.result()
rec = dict(backend=backend.name, shots=shots, job_id=str(job.job_id()), utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), circuits={})
for i, (name, qc, ideal, valid) in enumerate(jobs):
    cnt = res[i].data.c.get_counts()
    by_index = {int(k, 2): int(v) for k, v in cnt.items()}
    rec["circuits"][name] = dict(valid_counts=[by_index.get(v, 0) for v in valid], discarded=int(shots - sum(by_index.get(v, 0) for v in valid)),
                                 ideal=[float(x) for x in ideal], two_qubit_gates=int(twoq[i]), depth=int(isa[i].depth()))
    print(name, rec["circuits"][name]["valid_counts"], "discarded", rec["circuits"][name]["discarded"], "2q gates", twoq[i])
json.dump(rec, open(out, "w"), indent=1)
print("saved", out)
