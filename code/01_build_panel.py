"""Build the prefecture-year panel used in the analysis (plan/analysis_plan.md, section 3).

Inputs (copied unchanged from japan-guard-price-panel v1.1.0, https://doi.org/10.5281/zenodo.23852300)
  data/guard_rates_by_prefecture.csv    MLIT design labor rates for traffic guards A and B, FY2012-FY2026
  data/pay_by_prefecture.csv            MHLW Basic Survey on Wage Structure, survey years 2012-2025
  data/minimum_wage_by_prefecture.csv   MHLW prefecture minimum wages, FY2002-FY2026

Output
  results/panel.csv   one row per prefecture (and Japan, pref_code 00) and survey year 2012-2025

Definitions, for prefecture p and survey year t
  R   official rate: mean of the guard A and guard B daily rates in MLIT's table for fiscal year t
      (in force in June of t, the month the wage survey measures); R_prev and R_next use table years t-1 and t+1
  W   pay per 8 scheduled hours including bonuses: 8 * (S + B/12) / H, in yen, where S is scheduled monthly
      earnings in June, B the previous calendar year's bonuses and other special earnings and H scheduled
      hours worked in June. W_nb = 8 * S / H leaves out bonuses (check C3).
  M   prefecture minimum wage in force on 30 June of t: the fiscal year t-1 amount, yen per hour
  Weights: each prefecture's average estimated number of workers over 2012-2025 (both sexes, excluding position
      holders), held fixed across years; one weight for guards, one for building cleaners.

Usage: python code/01_build_panel.py
"""

import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"
YEARS = list(range(2012, 2026))
PREFS = [f"{i:02d}" for i in range(1, 48)]


def pay_variables(pay, occupation, positions, sex, prefix):
    """S, B, H, workers and W for one occupation and coverage, by pref_code and survey_year."""
    d = pay[(pay["occupation"] == occupation) & (pay["position_holders"] == positions) & (pay["sex"] == sex)]
    d = d.set_index(["pref_code", "survey_year"])
    out = pd.DataFrame({
        f"{prefix}_S": d["scheduled_earnings_kyen"] * 1000,
        f"{prefix}_B": d["annual_bonus_kyen"] * 1000,
        f"{prefix}_H": d["scheduled_hours"],
        f"{prefix}_n": d["workers_tens"] * 10,
    })
    out[f"{prefix}_W"] = 8 * (out[f"{prefix}_S"] + out[f"{prefix}_B"] / 12) / out[f"{prefix}_H"]
    out[f"{prefix}_Wnb"] = 8 * out[f"{prefix}_S"] / out[f"{prefix}_H"]
    return out


def main():
    rates = pd.read_csv(DATA / "guard_rates_by_prefecture.csv", dtype={"pref_code": str})
    pay = pd.read_csv(DATA / "pay_by_prefecture.csv", dtype={"pref_code": str})
    mw = pd.read_csv(DATA / "minimum_wage_by_prefecture.csv", dtype={"pref_code": str})

    # ---- official rates
    r = rates.pivot_table(index=["pref_code", "table_year"], columns="grade", values="daily_rate_yen", aggfunc="first")
    r.columns = [f"rate_{g}" for g in r.columns]
    special = rates.assign(
        covid=rates["special_rate"].eq("yes") & rates["note"].str.contains("COVID", na=False),
        tohoku=rates["special_rate"].eq("yes") & rates["note"].str.contains("Iwate", na=False),
    ).groupby(["pref_code", "table_year"])[["covid", "tohoku"]].any()
    r = r.join(special)
    r["R"] = (r["rate_A"] + r["rate_B"]) / 2
    assert r.index.get_level_values("table_year").min() == 2012 and r.index.get_level_values("table_year").max() == 2026
    assert len(r) == 47 * 15 and r[["rate_A", "rate_B"]].notna().all().all()
    # every table year's rates took effect before June of that year
    eff = rates.groupby("table_year")["effective_from"].agg(["min", "max"])
    for y, (lo, hi) in eff.iterrows():
        assert f"{y}-02" <= lo and hi <= f"{y}-04", (y, lo, hi)

    # ---- pay
    parts = [
        pay_variables(pay, "security_guards", "excluded", "total", "g"),
        pay_variables(pay, "security_guards", "excluded", "male", "gm"),
        pay_variables(pay, "security_guards", "included", "total", "gi"),
        pay_variables(pay, "gatekeepers", "excluded", "total", "k"),
        pay_variables(pay, "building_cleaners", "excluded", "total", "c"),
        pay_variables(pay, "building_cleaners", "excluded", "male", "cm"),
        pay_variables(pay, "building_cleaners", "included", "total", "ci"),
    ]
    p = pd.concat(parts, axis=1)
    p.index = p.index.set_names(["pref_code", "year"])

    # C6: guards and gatekeepers combined for 2012-2019 (worker-weighted means of S, B and H); 2020 on, guards
    has_k = p["k_S"].notna() & p["k_B"].notna() & p["k_H"].notna() & p["k_n"].notna()
    nk = p["k_n"].where(has_k, 0.0)
    for v in ("S", "B", "H"):
        p[f"gk_{v}"] = (p[f"g_{v}"] * p["g_n"] + p[f"k_{v}"].where(has_k, 0.0) * nk) / (p["g_n"] + nk)
    p["gk_n"] = p["g_n"] + nk
    p["gk_W"] = 8 * (p["gk_S"] + p["gk_B"] / 12) / p["gk_H"]
    late = p.index.get_level_values("year") >= 2020
    for v in ("S", "B", "H", "n", "W"):
        p.loc[late, f"gk_{v}"] = p.loc[late, f"g_{v}"]
    p["gk_guards_only"] = ~has_k & ~late

    # ---- minimum wage in force on 30 June of t: FY t-1 amount
    mw = mw.set_index(["pref_code", "fiscal_year"])
    rows = []
    for code in ["00"] + PREFS:
        for t in YEARS:
            prev, cur = mw.loc[(code, t - 1)], mw.loc[(code, t)]
            if code != "00":
                june30 = datetime.date(t, 6, 30)
                assert datetime.date.fromisoformat(prev["effective_date"]) <= june30, (code, t)
                assert (cur["hourly_yen"] == prev["hourly_yen"]
                        or datetime.date.fromisoformat(cur["effective_date"]) > june30), (code, t)
            rows.append({"pref_code": code, "year": t, "M": float(prev["hourly_yen"])})
    m = pd.DataFrame(rows).set_index(["pref_code", "year"])

    # ---- assemble
    panel = p.join(m, how="left")
    panel = panel[panel.index.get_level_values("year").isin(YEARS)]
    rr = r.copy()
    rr.index = rr.index.set_names(["pref_code", "year"])
    panel = panel.join(rr, how="left")
    prev = r[["R", "rate_A", "rate_B"]].rename(columns=lambda c: c + "_prev")
    prev.index = pd.MultiIndex.from_arrays([prev.index.get_level_values(0), prev.index.get_level_values(1) + 1],
                                           names=["pref_code", "year"])
    nxt = r[["R", "rate_A", "rate_B"]].rename(columns=lambda c: c + "_next")
    nxt.index = pd.MultiIndex.from_arrays([nxt.index.get_level_values(0), nxt.index.get_level_values(1) - 1],
                                          names=["pref_code", "year"])
    panel = panel.join(prev, how="left").join(nxt, how="left")

    # weights: average estimated workers over 2012-2025, prefectures only
    pref_rows = panel.index.get_level_values("pref_code") != "00"
    wg = panel.loc[pref_rows, "g_n"].groupby(level="pref_code").mean()
    wc = panel.loc[pref_rows, "c_n"].groupby(level="pref_code").mean()
    panel["w_guard"] = panel.index.get_level_values("pref_code").map(wg)
    panel["w_cleaner"] = panel.index.get_level_values("pref_code").map(wc)

    # national official rate: weighted mean of the 47 prefectures (guard weights)
    for col in ("R", "rate_A", "rate_B", "R_prev", "R_next"):
        nat = (panel.loc[pref_rows, col] * panel.loc[pref_rows, "w_guard"]).groupby(level="year").sum(min_count=1) / \
              panel.loc[pref_rows, "w_guard"].groupby(level="year").sum()
        for t, v in nat.items():
            panel.loc[("00", t), col] = v

    names = rates.drop_duplicates("pref_code").set_index("pref_code")["prefecture_en"].to_dict()
    names["00"] = "Japan"
    panel = panel.reset_index().sort_values(["pref_code", "year"])
    panel.insert(1, "prefecture", panel["pref_code"].map(names))
    for c in ("covid", "tohoku"):
        panel[c] = panel[c].fillna(False).astype(bool)

    # ---- checks of the build
    pr = panel[panel["pref_code"] != "00"]
    assert len(pr) == 47 * len(YEARS)
    need = ["g_W", "gm_W", "c_W", "cm_W", "gk_W", "R", "R_next", "M", "w_guard", "w_cleaner"]
    assert pr[need].notna().all().all(), pr[need].isna().sum()
    assert pr.loc[pr["year"] >= 2013, "R_prev"].notna().all()
    assert pr.loc[pr["year"] >= 2020, ["gi_W", "ci_W"]].notna().all().all()
    assert pr["covid"].sum() == 8 and (pr.loc[pr["covid"], "year"] == 2021).all()
    assert set(pr.loc[pr["tohoku"], "prefecture"]) == {"Iwate", "Miyagi", "Fukushima"}
    assert int(pr["gk_guards_only"].sum()) == 5
    assert panel.loc[panel["pref_code"] == "00", "g_W"].notna().sum() == len(YEARS)

    RESULTS.mkdir(exist_ok=True)
    panel.to_csv(RESULTS / "panel.csv", index=False, float_format="%.6f")
    print(f"panel: {len(panel)} rows ({len(pr)} prefecture-years and {len(YEARS)} national rows) -> results/panel.csv")


if __name__ == "__main__":
    main()
