Rehearsal on a fake-backend noise model only. No hardware run was performed. Not cited as evidence in the report.

These files are a kit for running the hide-and-seek test on a real IBM device. They were exercised only against
Qiskit's `FakeFez` noise model (`python3 hardware_run.py fake:FakeFez 4000 counts_fake.json`, then
`python3 hardware_analyze.py counts_fake.json fig4_rehearsal_fake_fez.png`). `counts_fake.json`,
`counts_fake_analysis.json` and `fig4_rehearsal_fake_fez.png` are outputs of that rehearsal, not measurements.
`HARDWARE.md` describes the intended real-device run; it has not been carried out.
