# mub10: searches for mutually unbiased bases in C^10

This folder is shared between a cloud Claude session (which orchestrates the research and writes code and
job files here) and a Claude Code session on this PC (which runs them on the RTX 5070).

- `CLAUDE.md`: role and rules for the local Claude Code session.
- `docs/`: shared definitions and the literature summary.
- `handoff/`: the message channel between the two sessions (`python handoff/chan.py log` shows the traffic).
- `code/<team>/`: scripts. `jobs/`: queue, records and logs. `results/<team>/`: output data.
- `worker/`: an optional unattended job runner (`powershell -ExecutionPolicy Bypass -File worker\start_worker.ps1`).
