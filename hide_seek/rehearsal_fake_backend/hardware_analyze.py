"""Analyse counts from hardware_run.py: uniformity tests, detectability, and a figure.
  python3 hardware_analyze.py counts_ibm.json fig4_hardware.png"""
import json, sys
import numpy as np
from scipy.stats import chi2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

src = sys.argv[1]; fig_out = sys.argv[2] if len(sys.argv) > 2 else "fig4_hardware.png"
R = json.load(open(src)); C = R["circuits"]; rng = np.random.default_rng(2026)
INK, INK2, GRID, SURF, C4, C6 = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb", "#1b6ca8", "#c8501f"


def group(names):
    cnt = np.array([C[n]["valid_counts"] for n in names], float)
    m = cnt.sum(axis=1, keepdims=True); d = cnt.shape[1]; f = cnt / m
    stat = float((((cnt - m / d) ** 2) / (m / d)).sum()); dof = len(names) * (d - 1)
    E_raw = float(((f - 1 / d) ** 2).sum()); E_corr = E_raw - float(((d - 1) / (d * m)).sum())   # remove sampling bias
    # how often would 240 shots per setting catch this distribution at a 0.1% false-alarm rate?
    thr = chi2.isf(1e-3, dof); n = 240
    sub = np.stack([rng.multinomial(n, f[i], size=20000) for i in range(len(names))], axis=1)
    caught = float(((((sub - n / d) ** 2) / (n / d)).sum(axis=(1, 2)) > thr).mean())
    return dict(counts=cnt, freq=f, shots=m.ravel(), chi2=stat, dof=dof, p=float(chi2.sf(stat, dof)), E=E_corr,
                max_bias=float(np.abs(f - 1 / d).max()), caught_at_240=caught, discarded=[C[x]["discarded"] for x in names],
                twoq=[C[x]["two_qubit_gates"] for x in names])


G = dict(hider6=group([f"hider6_s{r}" for r in range(3)]), ctrl6=group(["ctrl6_s0", "ctrl6_s2"]), hider4=group([f"hider4_s{r}" for r in range(3)]))
sanity = max(C["ctrl6_s1"]["valid_counts"]) / max(1, sum(C["ctrl6_s1"]["valid_counts"]))
print(f"backend {R['backend']}, {R['shots']} shots per circuit, job {R['job_id']}")
for k, lab in (("hider6", "qubit+qutrit best hider"), ("ctrl6", "qubit+qutrit control (ideal: uniform)"), ("hider4", "two-qubit perfect hider (ideal: uniform)")):
    g = G[k]
    print(f"{lab:42s} chi2 = {g['chi2']:8.1f} on {g['dof']:2d} dof, p = {g['p']:.2e}; E = {g['E']:.5f}; max bias = {g['max_bias']:.4f}; "
          f"caught at 240 shots: {100*g['caught_at_240']:.1f}%; 2-qubit gates {g['twoq']}; discarded {g['discarded']}")
print(f"circuit sanity (eigenstate in its own setting): {100*sanity:.1f}% on the expected outcome")
print("ideal E for the best hider: 0.03876")

plt.rcParams.update({"font.size": 11.5, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK, "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF})
fig, axs = plt.subplots(2, 3, figsize=(12.5, 6.6), sharey="row")
rows = (("hider6", [f"hider6_s{r}" for r in range(3)], ["qubit Z, qutrit computational", "qubit X, qutrit Fourier", "qubit Y, qutrit shifted Fourier"], C6, 6, "qubit + qutrit: best hider"),
        ("hider4", [f"hider4_s{r}" for r in range(3)], ["ZZ", "XX", "YY"], C4, 4, "two qubits: perfect hider"))
rowtext = []
for i, (k, names, titles, col, d, rowlab) in enumerate(rows):
    g = G[k]
    for r in range(3):
        ax = axs[i, r]; f = g["freq"][r]; n = g["shots"][r]; x = np.arange(d)
        ax.bar(x, f, width=0.62, color=col, zorder=3, label="measured")
        ax.errorbar(x, f, yerr=np.sqrt(f * (1 - f) / n), fmt="none", ecolor=INK, elinewidth=1, capsize=2.5, zorder=4)
        ax.plot(x, C[names[r]]["ideal"], "D", ms=6, mfc=SURF, mec=INK, mew=1.4, zorder=5, label="ideal state")
        ax.axhline(1 / d, color=INK2, lw=1, ls="--", zorder=2, label="white noise")
        ax.set_xticks(x); ax.set_xticklabels([str(j) for j in x]); ax.set_title(titles[r], fontsize=11.5, loc="left")
        ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True); ax.set_ylim(0, 0.34 if d == 4 else 0.27)
        if r == 0:
            ax.set_ylabel("outcome frequency")
        if i == 0 and r == 0:
            handles, labels = ax.get_legend_handles_labels()
        if i == 1:
            ax.set_xlabel("outcome")
    verdict = f"p = {g['p']:.1e}" if g["p"] < 1e-3 else f"p = {g['p']:.2f}"
    rowtext.append(f"{rowlab}:  χ² = {g['chi2']:.0f} on {g['dof']} degrees of freedom, {verdict}")
fig.tight_layout(rect=(0, 0, 1, 0.90), h_pad=5.0)
fig.text(0.012, 0.965, f"Hide and seek on {R['backend']}, {R['shots']} shots per setting", fontsize=13.5, ha="left")
fig.legend(handles, labels, frameon=False, fontsize=10.5, loc="upper right", ncol=3, bbox_to_anchor=(0.995, 0.99))
for i in range(2):
    y = axs[i, 0].get_position().y1 + 0.052
    fig.text(0.012, y, rowtext[i], fontsize=11.5, ha="left", color=INK, weight="bold")
fig.savefig(fig_out, dpi=200)
json.dump({k: {a: (b.tolist() if hasattr(b, "tolist") else b) for a, b in g.items()} for k, g in G.items()} | {"backend": R["backend"], "shots": R["shots"], "job_id": R["job_id"]},
          open(src.replace(".json", "_analysis.json"), "w"), indent=1)
print("saved", fig_out)
