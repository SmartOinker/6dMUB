# Running hide and seek on a real IBM quantum computer

Nine small circuits (at most 3 qubits and 8 two-qubit gates each), 4,000 shots apiece.

## Steps
1. `pip install qiskit qiskit-aer qiskit-ibm-runtime scipy matplotlib`
2. Create a free IBM Quantum account (Open Plan) and save your API key once, as IBM's setup guide describes:
   `QiskitRuntimeService.save_account(token="...", instance="...")`
3. From this folder:
   `python hardware_run.py ibm 4000 counts_ibm.json`      (picks the least busy device; prints a job id and waits)
   `python hardware_analyze.py counts_ibm.json fig4_hardware.png`

Rehearsal without an account: `python hardware_run.py fake:FakeFez 4000 counts_fake.json`

## What is measured
- `hider6`: the best-hiding qubit+qutrit state in the three local settings. Expected: clearly non-uniform.
- `ctrl6`: an eigenstate of setting 1, measured in settings 0 and 2. Ideal: exactly uniform. Shows how much bias the device fakes.
- `hider4`: the two-qubit perfect hider in ZZ, XX, YY. Ideal: exactly uniform.

## Rehearsal result (local noise model of ibm_fez, NOT hardware)
| group | chi-square | p | energy E | caught at 240 shots |
|---|---|---|---|---|
| qubit+qutrit best hider | 934 on 15 dof | 2e-189 | 0.0386 (ideal 0.0388) | 99.4% |
| qubit+qutrit control | 12 on 10 dof | 0.26 | 0.0001 | 0.3% |
| two-qubit perfect hider | 9 on 9 dof | 0.40 | 0.00002 | 0.2% |

## How to describe a hardware run honestly
- It illustrates the theorem; it cannot test it. The theorem is about pure states and ideal measurements, and no device prepares either.
- A real device may show small but significant bias in the controls at 4,000 shots. Report it; the comparison that matters is the size of E.
- Record the device name, date and job id (saved in the counts file).
