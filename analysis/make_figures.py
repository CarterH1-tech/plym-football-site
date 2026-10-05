#!/usr/bin/env python3
"""Generate the paper's figures from the analysis outputs."""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
FIG = os.path.join(HERE, "..", "paper", "figures")
os.makedirs(FIG, exist_ok=True)

GREEN = "#054e39"
LIME = "#9ccb3b"
GREY = "#8a938e"


def load(name):
    return list(csv.DictReader(open(os.path.join(OUT, name))))


def fig_production_by_major():
    rows = load("major_summary.csv")
    rows = [r for r in rows if r["major"] not in ("Not reported",)]
    rows.sort(key=lambda r: float(r["mean_z"]))
    labels = [r["major"] for r in rows]
    vals = [float(r["mean_z"]) for r in rows]
    ns = [int(r["with_stats"]) for r in rows]
    colors = [GREEN if r["major"] == "Business, Finance & Accounting" else GREY for r in rows]

    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    bars = ax.barh(labels, vals, color=colors)
    for b, n in zip(bars, ns):
        x = b.get_width()
        ax.text(x + (0.05 if x >= 0 else -0.05), b.get_y() + b.get_height() / 2,
                f"n={n}", va="center", ha="left" if x >= 0 else "right",
                fontsize=8, color="#333")
    ax.axvline(0, color="#444", linewidth=0.8)
    ax.set_xlabel("Mean position-normalised production (z-score)")
    ax.set_title("Production per player by major\n(2026 MASCAC opponents with published majors)",
                 fontsize=11)
    ax.grid(axis="x", color="#e6e9e7", linewidth=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.margins(x=0.18)
    fig.tight_layout()
    path = os.path.join(FIG, "fig1_production_by_major.png")
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print("wrote", path)


def fig_business_vs_wins():
    rows = load("team_mix.csv")
    x = [float(r["business_pct"]) for r in rows]
    y = [float(r["conf_pct"]) * 100 for r in rows]
    labels = [r["team"] for r in rows]

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.scatter(x, y, s=70, color=GREEN, zorder=3)
    offsets = {
        "Framingham St.": (6, 4),
        "Worcester St.": (6, 4),
        "Westfield St.": (6, 4),
        "Plymouth St.": (7, 6),
        "Mass.-Dartmouth": (-12, -14),
        "Fitchburg St.": (-8, 8),
        "Dean": (6, 4),
    }
    for xi, yi, lab in zip(x, y, labels):
        ax.annotate(lab, (xi, yi), textcoords="offset points",
                    xytext=offsets.get(lab, (6, 4)), fontsize=8)
    ax.set_xlabel("Share of declared-major roster in Business, Finance & Accounting (%)")
    ax.set_ylabel("Conference win %")
    ax.set_title("Roster major mix vs. conference results\n(7 teams, side note — n is small, not causal)",
                 fontsize=11)
    ax.grid(color="#e6e9e7", linewidth=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_xlim(0, 55)
    ax.set_ylim(-10, 110)
    fig.tight_layout()
    path = os.path.join(FIG, "fig2_business_vs_wins.png")
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print("wrote", path)


if __name__ == "__main__":
    fig_production_by_major()
    fig_business_vs_wins()
