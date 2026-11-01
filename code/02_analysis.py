"""The analysis set out in plan/analysis_plan.md (written 1 November 2026, before any test was run):
hypotheses H1-H4 and checks C1-C12, with the details settled in the plan's change log before the first result.

Input   results/panel.csv (from code/01_build_panel.py)
Outputs results/estimates.csv      every coefficient the analysis estimates
        tables/national_series.csv national official rate, guards' pay and minimum wage, 2012-2025
        tables/summary_stats.csv   summary statistics, prefecture-years
        tables/hypotheses.csv      H1-H4
        tables/checks.csv          C1-C12
        results/main_results.md    every number, in one file

Estimation: weighted least squares with the fixed effects as dummy variables; standard errors clustered by
prefecture with the finite-sample correction G/(G-1) * (N-1)/(N-K), K counting every coefficient including the
fixed effects, and t(G-1) critical values.

Usage: python code/02_analysis.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
TABLES = ROOT / "tables"
BASE_YEAR = 2012

# Each check: which columns hold guards' pay, building cleaners' pay and the official rate, the years, weights
# and rows dropped. Guards' and cleaners' pay columns are W = 8 * (S + B/12) / H in yen (see 01_build_panel.py).
SPECS = {
    "main": dict(label="Main specification"),
    "C1": dict(label="C1. Guard A's rate", rate="rate_A"),
    "C2": dict(label="C2. Guard B's rate", rate="rate_B"),
    "C3": dict(label="C3. Pay without bonuses, 8S/H", guard="g_Wnb", cleaner="c_Wnb"),
    "C4": dict(label="C4. Men only", guard="gm_W", cleaner="cm_W"),
    "C5": dict(label="C5. 2020-2025, including position holders", guard="gi_W", cleaner="ci_W", years=(2020, 2025)),
    "C6": dict(label="C6. 2020 definition throughout (guards and gatekeepers combined to 2019)", guard="gk_W"),
    "C7a": dict(label="C7. 2012-2019 only", years=(2012, 2019)),
    "C7b": dict(label="C7. 2020-2025 only", years=(2020, 2025)),
    "C8": dict(label="C8. Unweighted", weighted=False),
    "C9": dict(label="C9. Without Iwate, Miyagi, Fukushima and the FY2021 COVID-19 rates", drop_special=True),
    "C11": dict(label="C11. Previous year's rate (2013-2025)", rate="R_prev", years=(2013, 2025)),
}


def fit(d, y, xs, fe_full, fe_part=None, drop_levels=(), weight=None, cluster="pref_code"):
    """WLS of d[y] on d[xs], a full set of dummies for fe_full (no constant) and dummies for fe_part without
    the levels in drop_levels. Standard errors clustered by `cluster`."""
    X = d[xs].astype(float) if xs else pd.DataFrame(index=d.index)
    X = pd.concat([X, pd.get_dummies(d[fe_full].astype(str), prefix="a", prefix_sep=":", dtype=float)], axis=1)
    if fe_part is not None:
        D = pd.get_dummies(d[fe_part].astype(str), prefix="d", prefix_sep=":", dtype=float)
        D = D.drop(columns=[f"d:{lev}" for lev in drop_levels if f"d:{lev}" in D.columns])
        X = pd.concat([X, D], axis=1)
    assert np.linalg.matrix_rank(X.values) == X.shape[1], "design matrix is not of full rank"
    groups = pd.factorize(d[cluster])[0]
    w = d[weight].astype(float).values if weight else np.ones(len(d))
    res = sm.WLS(d[y].astype(float).values, X, weights=w).fit(
        cov_type="cluster", cov_kwds={"groups": groups, "use_correction": True, "df_correction": True}, use_t=True)
    return res, int(len(np.unique(groups)))


def coef(res, G, term, null=0.0, side=None):
    """Estimate, standard error, t, two-sided p and 95% interval for one coefficient, with t(G-1) inference;
    `side` 'lt' or 'gt' adds a one-sided p-value for H0: coefficient >= null (lt) or <= null (gt)."""
    b, se = float(res.params[term]), float(res.bse[term])
    df = G - 1
    t = (b - null) / se
    q = stats.t.ppf(0.975, df)
    out = dict(term=term, coef=b, se=se, null=null, t=t, df=df, p_two=2 * stats.t.sf(abs(t), df),
               ci_low=b - q * se, ci_high=b + q * se, p_one=np.nan, side=side or "")
    if side == "lt":
        out["p_one"] = stats.t.cdf(t, df)
    elif side == "gt":
        out["p_one"] = stats.t.sf(t, df)
    return out


def contrast(res, G, plus, minus, name):
    """plus - minus, with its standard error from the clustered covariance matrix and t(G-1) inference."""
    V = res.cov_params()
    b = float(res.params[plus] - res.params[minus])
    se = float(np.sqrt(V.loc[plus, plus] + V.loc[minus, minus] - 2 * V.loc[plus, minus]))
    df = G - 1
    t = b / se
    q = stats.t.ppf(0.975, df)
    return dict(term=name, coef=b, se=se, null=0.0, t=t, df=df, p_two=2 * stats.t.sf(abs(t), df),
                ci_low=b - q * se, ci_high=b + q * se, p_one=np.nan, side="")


def sample(panel, spec):
    d = panel[panel["pref_code"] != "00"].copy()
    lo, hi = spec.get("years", (2012, 2025))
    d = d[(d["year"] >= lo) & (d["year"] <= hi)]
    if spec.get("drop_special"):
        d = d[~d["prefecture"].isin(["Iwate", "Miyagi", "Fukushima"]) & ~d["covid"]]
    rate = spec.get("rate", "R")
    d["lnR"] = np.log(d[rate])
    d["lnW"] = np.log(d[spec.get("guard", "g_W")])
    d["lnWc"] = np.log(d[spec.get("cleaner", "c_W")])
    d["lnM"] = np.log(d["M"])
    d["trend"] = d["year"] - BASE_YEAR
    d["post"] = (d["year"] >= 2020).astype(float)
    d["gap"] = d["lnW"] - d["lnR"]
    if spec.get("weighted", True):
        d["wg"], d["wc"] = d["w_guard"], d["w_cleaner"]
    else:
        d["wg"], d["wc"] = 1.0, 1.0
    assert d[["lnR", "lnW", "lnWc", "lnM"]].notna().all().all()
    return d


def stack(d):
    """Guards (G = 1) and building cleaners (G = 0) in one data set, for H4."""
    g = d.assign(occ="guard", G=1.0, y=d["lnW"], w=d["wg"])
    c = d.assign(occ="cleaner", G=0.0, y=d["lnWc"], w=d["wc"])
    s = pd.concat([g, c], ignore_index=True)
    s["lnR_G"] = s["lnR"] * s["G"]
    s["lnM_G"] = s["lnM"] * s["G"]
    s["lnM_C"] = s["lnM"] * (1 - s["G"])
    s["occ_pref"] = s["occ"] + "_" + s["pref_code"]
    s["occ_year"] = s["occ"] + "_" + s["year"].astype(str)
    return s


def run(panel, name, spec):
    d = sample(panel, spec)
    first = int(d["year"].min())
    rows = []

    def add(model, res, G, items, n):
        for it in items:
            rows.append(dict(spec=name, label=spec["label"], model=model, n_obs=n, clusters=G, **it))

    # H1: ln(W/R) = a_p + tau (t - 2012) + kappa 1[t >= 2020]
    both = d["year"].min() < 2020 <= d["year"].max()
    xs = ["trend", "post"] if both else ["trend"]
    res, G = fit(d, "gap", xs, "pref_code", weight="wg")
    items = [coef(res, G, "trend", side="lt")] + ([coef(res, G, "post")] if both else [])
    add("H1", res, G, items, len(d))

    # H2: ln W = beta ln R + a_p + d_t
    res, G = fit(d, "lnW", ["lnR"], "pref_code", "year", drop_levels=[str(first)], weight="wg")
    b1 = coef(res, G, "lnR", null=1.0, side="lt")
    b0 = coef(res, G, "lnR", null=0.0)
    b0["term"] = "lnR (test of 0)"
    add("H2", res, G, [b1, b0], len(d))

    # H3: ln W = beta ln R + gamma ln M + a_p + d_t
    res, G = fit(d, "lnW", ["lnR", "lnM"], "pref_code", "year", drop_levels=[str(first)], weight="wg")
    add("H3", res, G, [coef(res, G, "lnR"), coef(res, G, "lnM", side="gt"),
                       contrast(res, G, "lnM", "lnR", "lnM - lnR")], len(d))

    # H4: stacked with building cleaners
    s = stack(d)
    res, G = fit(s, "y", ["lnR", "lnR_G", "lnM_G", "lnM_C"], "occ_pref", "occ_year",
                 drop_levels=[f"guard_{first}", f"cleaner_{first}"], weight="w")
    add("H4", res, G, [coef(res, G, "lnR"), coef(res, G, "lnR_G", side="gt"), coef(res, G, "lnM_G"),
                       coef(res, G, "lnM_C")], len(s))
    return rows


def run_c10(panel):
    """C10: first differences, d ln W on d ln R and d ln M with year effects, 2013-2025."""
    d = sample(panel, {"label": ""}).sort_values(["pref_code", "year"])
    for v in ("lnW", "lnR", "lnM"):
        d["D" + v] = d.groupby("pref_code")[v].diff()
    d = d[d["year"] >= 2013]
    assert d[["DlnW", "DlnR", "DlnM"]].notna().all().all() and len(d) == 47 * 13
    res, G = fit(d, "DlnW", ["DlnR", "DlnM"], "year", weight="wg")
    lab = "C10. First differences with year effects (2013-2025)"
    return [dict(spec="C10", label=lab, model="FD", n_obs=len(d), clusters=G, **coef(res, G, "DlnR")),
            dict(spec="C10", label=lab, model="FD", n_obs=len(d), clusters=G, **coef(res, G, "DlnM"))]


def run_c12(panel):
    """C12: add next year's rate ln R_{p,t+1} to H2 and H3."""
    d = sample(panel, {"label": ""})
    d["lnR_next"] = np.log(d["R_next"])
    lab = "C12. Adding next year's rate"
    rows = []
    for model, xs in (("H2", ["lnR", "lnR_next"]), ("H3", ["lnR", "lnR_next", "lnM"])):
        res, G = fit(d, "lnW", xs, "pref_code", "year", drop_levels=["2012"], weight="wg")
        items = [coef(res, G, "lnR"), coef(res, G, "lnR_next"), contrast(res, G, "lnR_next", "lnR", "lnR_next - lnR")]
        if "lnM" in xs:
            items.append(coef(res, G, "lnM"))
        rows += [dict(spec="C12", label=lab, model=model, n_obs=len(d), clusters=G, **it) for it in items]
    return rows


def national(panel):
    n = panel[panel["pref_code"] == "00"].set_index("year")
    t = pd.DataFrame({
        "rate_A": n["rate_A"], "rate_B": n["rate_B"], "R": n["R"],
        "W_guards": n["g_W"], "W_over_R": n["g_W"] / n["R"],
        "S_guards": n["g_S"], "B_guards": n["g_B"], "H_guards": n["g_H"],
        "M": n["M"], "W_over_8M": n["g_W"] / (8 * n["M"]),
        "W_cleaners": n["c_W"], "Wc_over_8M": n["c_W"] / (8 * n["M"]),
    })
    return t


def growth(t):
    out = {}
    for a, b in ((2012, 2019), (2020, 2025), (2012, 2025)):
        for v in ("R", "W_guards", "W_cleaners", "M"):
            out[f"{v} {a}-{b}"] = 100 * (t.loc[b, v] / t.loc[a, v] - 1)
    return out


def summary(panel):
    d = panel[panel["pref_code"] != "00"].copy()
    d["W_over_R"] = d["g_W"] / d["R"]
    d["W_over_8M"] = d["g_W"] / (8 * d["M"])
    cols = {"rate_A": "Official rate, guard A (yen per day)", "rate_B": "Official rate, guard B (yen per day)",
            "R": "Official rate R, mean of A and B (yen per day)",
            "g_S": "Guards' scheduled monthly earnings S (yen)", "g_B": "Guards' annual bonuses B (yen)",
            "g_H": "Guards' scheduled monthly hours H", "g_W": "Guards' pay per 8 hours W (yen)",
            "W_over_R": "W / R", "M": "Minimum wage M (yen per hour)", "W_over_8M": "W / (8M)",
            "c_W": "Building cleaners' pay per 8 hours (yen)", "g_n": "Guards, estimated number",
            "c_n": "Building cleaners, estimated number"}
    rows = []
    for c, lab in cols.items():
        for period, sub in (("2012-2025", d), ("2012", d[d["year"] == 2012]), ("2025", d[d["year"] == 2025])):
            x = sub[c]
            rows.append(dict(variable=c, description=lab, period=period, n=int(x.notna().sum()), mean=x.mean(),
                             sd=x.std(), min=x.min(), max=x.max()))
    return pd.DataFrame(rows)


def fmt(x, nd=3):
    return f"{x:.{nd}f}".replace("-", "−") if pd.notna(x) else ""


def main():
    panel = pd.read_csv(RESULTS / "panel.csv", dtype={"pref_code": str})
    TABLES.mkdir(exist_ok=True)

    rows = []
    for name, spec in SPECS.items():
        rows += run(panel, name, spec)
    rows += run_c10(panel)
    rows += run_c12(panel)
    est = pd.DataFrame(rows)
    est.to_csv(RESULTS / "estimates.csv", index=False, float_format="%.6g")

    nat = national(panel)
    nat.to_csv(TABLES / "national_series.csv", float_format="%.4f")
    gr = growth(nat)
    summ = summary(panel)
    summ.to_csv(TABLES / "summary_stats.csv", index=False, float_format="%.4f")

    main_rows = est[est["spec"] == "main"]
    main_rows.to_csv(TABLES / "hypotheses.csv", index=False, float_format="%.6g")
    keep = {("H1", "trend"), ("H2", "lnR"), ("H3", "lnR"), ("H3", "lnM"), ("H4", "lnR_G"), ("H4", "lnR"),
            ("FD", "DlnR"), ("FD", "DlnM"), ("H2", "lnR_next"), ("H2", "lnR_next - lnR"),
            ("H3", "lnR_next"), ("H3", "lnR_next - lnR")}
    checks = est[[(m, t) in keep for m, t in zip(est["model"], est["term"])]]
    checks.to_csv(TABLES / "checks.csv", index=False, float_format="%.6g")

    # ---- every number, in one file
    pr = panel[panel["pref_code"] != "00"]
    a, b = pr[pr["year"] == 2012].set_index("pref_code"), pr[pr["year"] == 2025].set_index("pref_code")
    fell = int(((b["g_W"] / b["R"]) < (a["g_W"] / a["R"])).sum())
    L = ["# Main results", "", "Output of `code/02_analysis.py`. Plan: [`plan/analysis_plan.md`](../plan/analysis_plan.md).", "",
         "## National series (Japan's W from MHLW's national row; R as the weighted mean of the 47 prefectures)", "",
         "| Year | Rate A | Rate B | R | Guards' W | W/R | M (FY t−1) | W/(8M) | Cleaners' W |",
         "|---|---|---|---|---|---|---|---|---|"]
    for y, r in nat.iterrows():
        L.append(f"| {y} | {r.rate_A:,.0f} | {r.rate_B:,.0f} | {r.R:,.0f} | {r.W_guards:,.0f} | {r.W_over_R:.3f} | "
                 f"{r.M:,.0f} | {r.W_over_8M:.3f} | {r.W_cleaners:,.0f} |")
    L += ["", "Growth, national (%):", ""]
    L += [f"- {k}: {v:.1f}" for k, v in gr.items()]
    L += ["", f"- Prefectures where W/R was lower in 2025 than in 2012: {fell} of 47.", ""]

    def line(r):
        p1 = f", one-sided p = {r.p_one:.4f}" if pd.notna(r.p_one) else ""
        nul = f" (test of {r.null:g})" if r.null not in (0, 0.0) else ""
        return (f"| {r.model} | {r.term}{nul} | {fmt(r.coef)} | {fmt(r.se)} | {fmt(r.ci_low)} to {fmt(r.ci_high)} | "
                f"{r.p_two:.4f}{p1} | {r.n_obs} | {r.clusters} |")

    for name in est["spec"].unique():
        sub = est[est["spec"] == name]
        L += [f"## {sub['label'].iloc[0]}", "", "| Model | Term | Estimate | SE | 95% interval | p (two-sided; one-sided where the plan sets a direction) | N | Clusters |",
              "|---|---|---|---|---|---|---|---|"]
        L += [line(r) for r in sub.itertuples()]
        L.append("")
    L += ["## Summary statistics, prefecture-years", "", "| Variable | Period | N | Mean | SD | Min | Max |", "|---|---|---|---|---|---|---|"]
    for r in summ.itertuples():
        L.append(f"| {r.description} | {r.period} | {r.n} | {r.mean:,.3f} | {r.sd:,.3f} | {r.min:,.3f} | {r.max:,.3f} |")
    L.append("")
    (RESULTS / "main_results.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:40]))
    print(f"... {len(est)} estimates -> results/estimates.csv, results/main_results.md, tables/")


if __name__ == "__main__":
    main()
