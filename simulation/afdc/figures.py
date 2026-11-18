"""Figures drawn at the final text width (6.5 in), so no text is scaled below 8 pt."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

TW = "state+czone"
INK = "#1f2933"
ACCENT = "#1d5f8a"
MUTED = "#8a99a8"
WARN = "#b5462f"

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Palatino", "Palatino Linotype", "TeX Gyre Pagella", "DejaVu Serif"],
    "font.size": 9, "axes.titlesize": 9.5, "axes.labelsize": 9, "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5, "legend.fontsize": 8.5, "axes.spines.top": False,
    "axes.spines.right": False, "axes.edgecolor": INK, "axes.labelcolor": INK,
    "xtick.color": INK, "ytick.color": INK, "savefig.dpi": 300,
})

ABBR = {"Alabama": "AL", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO",
        "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA", "Idaho": "ID",
        "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY",
        "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI",
        "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
        "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
        "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
        "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
        "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA",
        "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"}


def fig_moderation(R, path: Path, states: dict) -> None:
    st = states
    fig, axes = plt.subplots(1, 2, figsize=(6.5, 3.05), constrained_layout=True)
    ax = axes[0]
    x = np.array([v["tpr_1996"] for v in st.values()])
    y = np.array([v["tpr_2016"] for v in st.values()])
    names = list(st)
    ax.plot([0, 120], [0, 120], color=MUTED, lw=0.8, ls="--")
    ax.scatter(x, y, s=14, color=ACCENT, zorder=3)
    for n, xi, yi in zip(names, x, y):
        if ABBR[n] in {"MI", "WI", "PA", "OR", "CA", "MO", "NJ", "GA", "MN"}:
            off = {"WI": (-14, 4), "MI": (4, -6), "GA": (4, -3)}.get(ABBR[n], (3, 2))
            ax.annotate(ABBR[n], (xi, yi), xytext=off, textcoords="offset points", fontsize=8, color=INK)
    ax.set_xlim(25, 125)
    ax.set_ylim(0, 75)
    ax.set_xlabel("Families aided per 100 poor families, 1995–96")
    ax.set_ylabel("Families aided per 100 poor families, 2015–16")
    ax.set_title("(a) Cash assistance coverage by state", loc="left")
    ax.text(36, 52, "equal coverage", color=MUTED, fontsize=8, rotation=52)

    ax = axes[1]
    pr = R["primary"]
    b, g = pr["beta_at_mean"]["coef"], pr["gamma"]["coef"]
    V = np.array(pr["vcov_beta_gamma_twoway"])
    mbar = R["moderators"]["erosion"]["state_mean"]
    grid = np.linspace(R["moderators"]["erosion"]["min"], R["moderators"]["erosion"]["max"], 100)
    d = grid - mbar
    eff = b + g * d
    se = np.sqrt(V[0, 0] + d ** 2 * V[1, 1] + 2 * d * V[0, 1])
    q = 2.01  # t(47) two-sided 95%
    ax.fill_between(grid, eff - q * se, eff + q * se, color=ACCENT, alpha=0.15, lw=0)
    ax.plot(grid, eff, color=ACCENT, lw=1.4, label="Linear interaction (95% band)")
    for t in R["binned_terciles"]:
        lo, hi = t["ci95"]
        ax.errorbar(t["mean_erosion"], t["effect"], yerr=[[t["effect"] - lo], [hi - t["effect"]]],
                    fmt="o", color=INK, ms=4, capsize=2.5, lw=1, label="State terciles (95% CI)" if t["tercile"] == 1 else None)
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.set_xlabel("Erosion of the ratio, 1995–96 to 2015–16 (points)")
    ax.set_ylabel("Effect of shock on Republican share,\n2000–2016 (points per point)")
    ax.set_title("(b) Trade-shock effect by erosion", loc="left")
    ax.legend(frameon=False, loc="lower left")
    fig.savefig(path)
    plt.close(fig)


def fig_robustness(R, path: Path) -> None:
    rows = [R["robustness_rows"][k] for k in R["robustness_order"] if R["robustness_rows"][k]["group"] != "cbp"]
    rows = [(r["label"], r["coef"], r["ci95"][0], r["ci95"][1], r["group"]) for r in rows]

    n = len(rows)
    fig, ax = plt.subplots(figsize=(6.5, 0.24 * n + 0.9), constrained_layout=True)
    for i, (lab, c, lo, hi, grp) in enumerate(rows):
        yy = n - 1 - i
        col = ACCENT if grp == "main" else (WARN if grp == "placebo" else INK)
        ax.plot([lo, hi], [yy, yy], color=col, lw=1.2)
        ax.plot(c, yy, "o", color=col, ms=4)
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.set_yticks(range(n))
    ax.set_yticklabels([r[0] for r in rows][::-1])
    ax.set_xlabel("Interaction coefficient per state SD of the moderator (95% CI)")
    fig.savefig(path)
    plt.close(fig)


def fig_bridge(R, path: Path) -> None:
    br = R["bridge"]["counterfactuals"]
    fig, axes = plt.subplots(1, 3, figsize=(6.5, 2.5), constrained_layout=True, sharey=True)
    for ax, po in zip(axes, ["MI", "WI", "PA"]):
        for k, (lab, key) in enumerate([("Retain 1995–96\nratio", "retain_1996"),
                                        ("Least-eroded\nstate", "least_eroded_state")]):
            r = br[key]["states"][po]
            lo, hi = sorted(r["ci95"])
            ax.plot([k, k], [lo / 1000, hi / 1000], color=ACCENT, lw=1.6)
            ax.plot(k, r["net_dem_margin_change"] / 1000, "o", color=ACCENT, ms=4.5)
        m = br["retain_1996"]["states"][po]["trump_margin_fec"] / 1000
        ax.axhline(m, color=WARN, lw=1.1, ls="--")
        ax.axhline(0, color=MUTED, lw=0.8)
        ax.text(2.0, m + 10, "2016 margin", color=WARN, fontsize=8, va="bottom", ha="right")
        ax.set_xlim(-0.45, 2.05)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["Retain\n1995–96", "Least-\neroded"])
        ax.set_title({"MI": "Michigan", "WI": "Wisconsin", "PA": "Pennsylvania"}[po], loc="left")
    axes[0].set_ylabel("Net change in Democratic margin\n(thousands of votes)")
    fig.savefig(path)
    plt.close(fig)


def make_all(R, outdir: Path, states: dict) -> None:
    fig_moderation(R, outdir / "fig1_moderation.png", states)
    fig_robustness(R, outdir / "fig2_robustness.png")
    fig_bridge(R, outdir / "fig3_bridge.png")
