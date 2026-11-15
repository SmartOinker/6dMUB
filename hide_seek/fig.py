"""Figures for the hide-and-seek simulation. Reads hide_seek.json, writes fig3_hide_seek.png (+ one file per panel)."""
import json, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
R = json.load(open(f"{OUT}/hide_seek.json"))
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
C4, C6 = "#1b6ca8", "#c8501f"            # same hues as the d=5 / d=6 series of fig1, fig2 (validated pair)
plt.rcParams.update({"font.size": 12, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": INK2,
                     "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF})


def panel_a(ax):
    c6, c4, cert = R["d6"]["curves"], R["d4"]["curves"], R["certified"]
    N = np.array(c6["0.0"]["N"]); keep = N <= 1000
    ax.plot(np.array(cert["N"])[keep], np.array(cert["detect_floor"])[keep], color=INK, lw=1.2, zorder=2,
            label="certified floor, any pure state")
    ax.plot(N[keep], np.array(c6["0.0"]["detect"])[keep], "o", ms=6.5, color=C6, mec=SURF, mew=1.2, zorder=4,
            label="qubit + qutrit, no noise")
    ax.plot(N[keep], np.array(c6["0.01"]["detect"])[keep], "--", lw=2, color=C6, zorder=3,
            label="qubit + qutrit, 1% gate error")
    ax.plot(N[keep], np.array(c4["0.0"]["detect"])[keep], "-s", ms=5.5, lw=2, color=C4, mec=SURF, mew=1.2, zorder=3,
            label="two qubits")
    ax.set_xscale("log"); ax.set_xlim(9, 1100); ax.set_ylim(-0.03, 1.05)
    ax.set_xlabel("shots per measurement setting"); ax.set_ylabel("probability the referee catches the state")
    ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=10.5, loc="upper left", bbox_to_anchor=(0.0, 0.97), handlelength=2.2)
    n99 = cert["shots_per_setting_alpha1em3_99pct"]
    ax.annotate(f"caught 99% of the time\nby {n99:.0f} shots", xy=(n99, 0.99), xytext=(270, 0.66), fontsize=10.5, color=INK2,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
    ax.annotate("never caught: stays at the\n0.1% false-alarm rate", xy=(400, 0.004), xytext=(120, 0.16), fontsize=10.5, color=INK2,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
    ax.set_title("Hide and seek against three local measurements", fontsize=12.5, loc="left", pad=10)


def panel_b(ax):
    sc = [s for s in R["d6"]["scan"] if s["rate"] > 0]; g = R["game"]
    q = np.array([s["rate"] for s in sc]); tot = 3 * np.array([s["shots_per_setting_5sigma_50pct"] for s in sc])
    ax.plot(q, tot, "-", lw=2, color=C6, zorder=3)
    qs = g["rate_where_noise_loss_equals_gap_separate"]
    ax.plot([q.min(), qs], [g["rounds_5sigma"]] * 2, "-", lw=2, color=INK2, zorder=3)
    ax.plot([qs], [g["rounds_5sigma"]], "x", ms=9, mew=2, color=INK2, zorder=4)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(7e-7, 1.5e-1); ax.set_ylim(1e2, 3e9)
    ax.set_xlabel("two-qubit gate error rate (one-qubit = 1/10 of it)"); ax.set_ylabel("repetitions needed for 5σ")
    ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.text(1e-6, g["rounds_5sigma"] * 2.2, f"guessing game: {g['rounds_5sigma']:.1e} rounds".replace("e+07", "×10⁷"), fontsize=10.5, color=INK)
    ax.text(qs * 1.5, g["rounds_5sigma"] * 0.2, f"gate noise costs more than the\ngap beyond {qs:.1e}".replace("e-05", "×10⁻⁵"), fontsize=10.5, color=INK2, va="top")
    ax.text(1e-6, tot[0] * 2.0, f"hide and seek: {tot[0]:.0f} shots", fontsize=10.5, color=INK)
    ax.text(1e-1, tot[-1] * 1.9, f"still {tot[-1]:,.0f} shots\nat 10% gate error", fontsize=10.5, color=INK2, va="bottom", ha="right")
    ax.set_title("What each experiment needs", fontsize=12.5, loc="left", pad=10)


fig, axs = plt.subplots(1, 2, figsize=(13.2, 5.0))
panel_a(axs[0]); panel_b(axs[1])
fig.tight_layout(w_pad=3.0)
fig.savefig(f"{OUT}/fig3_hide_seek.png", dpi=200)
for name, fn in (("a", panel_a), ("b", panel_b)):
    f, ax = plt.subplots(figsize=(7.2, 5.0)); fn(ax); f.tight_layout(); f.savefig(f"{OUT}/fig3{name}_hide_seek.png", dpi=200); plt.close(f)
print("ok")
