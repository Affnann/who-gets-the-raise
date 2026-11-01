"""Figures 1-3 of the paper (plan/analysis_plan.md, section 6).

Usage: python code/03_figures.py (after code/01_build_panel.py and code/02_analysis.py)
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
INK = "#222222"
ACCENT = "#8B2E2E"
GREY = "#9A9A9A"
yen = matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}")

panel = pd.read_csv(ROOT / "results" / "panel.csv", dtype={"pref_code": str})
nat = pd.read_csv(ROOT / "tables" / "national_series.csv", index_col="year")
pr = panel[panel["pref_code"] != "00"].copy()

# Figure 1: national official rate and guards' pay per 8 hours
fig, ax = plt.subplots(figsize=(6.5, 3.6))
ax.plot(nat.index, nat["R"], color=ACCENT, lw=2, marker="o", ms=3.5)
for seg in (nat.loc[:2019], nat.loc[2020:]):
    ax.plot(seg.index, seg["W_guards"], color=INK, lw=2, marker="o", ms=3.5)
ax.axvline(2019.5, color=GREY, lw=1, ls="--")
ax.text(2019.6, 2500, "MHLW survey\nchanged in 2020", fontsize=7.5, color="#555555", va="bottom")
ax.text(2025.25, nat.loc[2025, "R"], f"Official rate\n{nat.loc[2025, 'R']:,.0f}", fontsize=8, color=ACCENT, va="center")
ax.text(2025.25, nat.loc[2025, "W_guards"], f"Guards' pay\n{nat.loc[2025, 'W_guards']:,.0f}", fontsize=8, color=INK,
        va="center")
ax.text(2011.75, nat.loc[2012, "R"] - 900, f"{nat.loc[2012, 'R']:,.0f}", fontsize=8, color=ACCENT, ha="left", va="top")
ax.text(2011.75, nat.loc[2012, "W_guards"] + 700, f"{nat.loc[2012, 'W_guards']:,.0f}", fontsize=8, color=INK, ha="left",
        va="bottom")
ax.set_xlim(2011.5, 2027.4)
ax.set_xticks(range(2012, 2026, 2))
ax.set_ylim(0, 20000)  # from zero, so neither rise is exaggerated
ax.yaxis.set_major_formatter(yen)
ax.set_ylabel("Yen per 8 hours")
ax.grid(axis="y", color="#E5E5E5", lw=0.8)
fig.tight_layout()
fig.savefig(FIG / "fig1_national.png", dpi=300)
plt.close(fig)

# Figure 2: change in the official rate against change in guards' pay, by prefecture, 2012-2025
a = pr[pr["year"] == 2012].set_index("pref_code")
b = pr[pr["year"] == 2025].set_index("pref_code")
dR = 100 * (b["R"] / a["R"] - 1)
dW = 100 * (b["g_W"] / a["g_W"] - 1)
w = a["w_guard"]
fig, ax = plt.subplots(figsize=(6.5, 5.4))
ax.plot((0, 100), (0, 100), color=GREY, lw=1, ls="--")
ax.text(60, 66, "Pay rose by as much as the rate", fontsize=7.5, color="#555555", rotation=45, rotation_mode="anchor",
        ha="center", va="bottom", transform_rotates_text=True)
ax.axhline(0, color="#CCCCCC", lw=0.8)
ax.scatter(dR, dW, s=w / w.max() * 180 + 8, color=ACCENT, alpha=0.55, edgecolor="white", lw=0.5)
names = a["prefecture"]
OFFSET = {"13": (12, -10, "left"), "27": (-10, 6, "right")}  # Tokyo and Osaka sit on top of each other
for code in ("13", "27", "23", "01", "40", "47", "04"):
    dx, dy, ha = OFFSET.get(code, (5, 3, "left"))
    ax.annotate(names[code], (dR[code], dW[code]), fontsize=7, xytext=(dx, dy), textcoords="offset points", ha=ha,
                arrowprops=dict(arrowstyle="-", lw=0.5, color="#555555", shrinkA=0, shrinkB=3) if code in OFFSET else None)
ax.set_xlim(0, 140)
ax.set_ylim(-20, 100)
ax.set_aspect("equal")  # the same scale on both axes, so the distance below the dashed line is not distorted
ax.set_xticks(range(0, 141, 20))
ax.set_yticks(range(-20, 101, 20))
ax.set_xlabel("Change in the official rate for traffic guards, FY2012 to FY2025 (%)")
ax.set_ylabel("Change in security guards' pay per 8 hours,\n2012 to 2025 (%)")
ax.grid(color="#EEEEEE", lw=0.6)
fig.tight_layout()
fig.savefig(FIG / "fig2_prefectures.png", dpi=300)
plt.close(fig)

# Figure 3: guards' pay relative to eight hours at the minimum wage
pr["ratio"] = pr["g_W"] / (8 * pr["M"])
q = pr.groupby("year")["ratio"].quantile([0.1, 0.9]).unstack()
fig, ax = plt.subplots(figsize=(6.5, 3.4))
for lo, hi in ((2012, 2019), (2020, 2025)):
    yrs = range(lo, hi + 1)
    ax.fill_between(list(yrs), q.loc[lo:hi, 0.1], q.loc[lo:hi, 0.9], color=GREY, alpha=0.25, lw=0)
    ax.plot(list(yrs), nat.loc[lo:hi, "W_over_8M"], color=INK, lw=2, marker="o", ms=3.5)
ax.axvline(2019.5, color=GREY, lw=1, ls="--")
ax.axhline(1, color=ACCENT, lw=1)
ax.text(2012, 1.03, "Eight hours at the minimum wage", fontsize=7.5, color=ACCENT, va="bottom")
ax.text(2025.2, nat.loc[2025, "W_over_8M"], "Japan", fontsize=8, va="center")
ax.text(2025.2, q.loc[2025, 0.9] + 0.05, "Prefectures,\n10th to 90th\npercentile", fontsize=7.5, color="#555555",
        va="bottom")
ax.set_xlim(2011.5, 2027.4)
ax.set_xticks(range(2012, 2026, 2))
ax.set_ylim(0, 2.2)
ax.set_ylabel("Guards' pay per 8 hours /\n8 hours at the minimum wage")
ax.grid(axis="y", color="#E5E5E5", lw=0.8)
fig.tight_layout()
fig.savefig(FIG / "fig3_minimum_wage.png", dpi=300)
plt.close(fig)

print("figures written:", sorted(p.name for p in FIG.glob("*.png")))
print(f"Figure 2 ranges: rate change {dR.min():.1f} to {dR.max():.1f}%, pay change {dW.min():.1f} to {dW.max():.1f}%")
print(f"Figure 3 band 2025: {q.loc[2025, 0.1]:.2f} to {q.loc[2025, 0.9]:.2f}; max ratio {pr['ratio'].max():.2f}")
