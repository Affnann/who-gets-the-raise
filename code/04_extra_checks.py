"""Analyses added after the main results were seen (recorded in the change log of plan/analysis_plan.md and
labelled as such in the paper). None of them is a test of the plan's hypotheses.

X1  Wild cluster bootstrap p-values for the main tests of H1-H4 (restricted, Rademacher weights by prefecture,
    9,999 draws), as a check on the clustered t(46) inference with 47 clusters.
X2  Guards' pay per hour actually worked, including overtime pay: 8 * (C + B/12) / (H + O), where C is monthly
    contractual cash earnings (scheduled earnings plus overtime pay) and O overtime hours. H1-H3 re-estimated.
X3  Long differences, 2012 to 2025: the change in ln W on the change in ln R across the 47 prefectures, for guards
    and for building cleaners (weighted, heteroskedasticity-robust HC1 standard errors, t(45) critical values).
X4  Levels: the weighted correlation across prefectures between ln R and guards' ln W, and between ln R and
    building cleaners' ln W, in each year.
X5  Other protective service workers (MHLW occupation 1459, the occupation in which MHLW's definitions place
    traffic guards from 2020), 2020-2025, excluding position holders, weighted by their own average number:
    national growth of W against R; H1 (no 2020 dummy), H2 and H3; H4 against building cleaners and against
    security guards. Prefecture-years without figures are left out.
X6  Security guards and other protective service workers combined, 2020-2025 (worker-weighted S, B and H):
    national growth of W against R; H1 (no 2020 dummy), H2 and H3.

Inputs  results/panel.csv, data/pay_by_prefecture.csv
Outputs tables/extra_checks.csv, results/extra_checks.md

Usage: python code/04_extra_checks.py
"""

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("analysis", ROOT / "code" / "02_analysis.py")
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)

B_DRAWS = 9999
SEED = 20261101


def design(d, xs, fe_full, fe_part=None, drop_levels=()):
    X = d[xs].astype(float) if xs else pd.DataFrame(index=d.index)
    X = pd.concat([X, pd.get_dummies(d[fe_full].astype(str), prefix="a", prefix_sep=":", dtype=float)], axis=1)
    if fe_part is not None:
        D = pd.get_dummies(d[fe_part].astype(str), prefix="d", prefix_sep=":", dtype=float)
        D = D.drop(columns=[f"d:{lev}" for lev in drop_levels if f"d:{lev}" in D.columns])
        X = pd.concat([X, D], axis=1)
    return X


def wild(d, y, xs, term, null, side, fe_full, fe_part=None, drop_levels=(), weight=None, cluster="pref_code",
         draws=B_DRAWS, seed=SEED):
    """Restricted wild cluster bootstrap (WCR) p-value for H0: coef[term] = null, with Rademacher weights and the
    same CR1 clustered t-statistic as the main analysis. side: 'lt', 'gt' or 'two'."""
    X = design(d, xs, fe_full, fe_part, drop_levels)
    Xv = X.values
    Y = d[y].astype(float).values
    w = d[weight].astype(float).values if weight else np.ones(len(d))
    g = pd.factorize(d[cluster])[0]
    G, N, K = g.max() + 1, len(Y), Xv.shape[1]
    j = list(X.columns).index(term)
    cfac = G / (G - 1) * (N - 1) / (N - K)
    M_inv = np.linalg.inv(Xv.T @ (Xv * w[:, None]))
    A_mat = M_inv @ (Xv * w[:, None]).T          # b = A y
    h = (Xv * w[:, None]) @ M_inv[j]             # se_j^2 = c * sum_g (sum_{i in g} h_i e_i)^2

    def tstat(yv):
        b = A_mat @ yv
        e = yv - Xv @ b
        s = np.bincount(g, weights=h * e, minlength=G)
        return (b[j] - null) / np.sqrt(cfac * np.sum(s ** 2))

    t_obs = tstat(Y)
    # restricted model: impose the null, estimate the rest
    Xr = np.delete(Xv, j, axis=1)
    yr = Y - null * Xv[:, j]
    br = np.linalg.solve(Xr.T @ (Xr * w[:, None]), Xr.T @ (w * yr))
    fit_r = Xr @ br + null * Xv[:, j]
    u = Y - fit_r
    rng = np.random.default_rng(seed)
    V = rng.choice([-1.0, 1.0], size=(draws, G))
    tb = np.empty(draws)
    for r in range(draws):
        tb[r] = tstat(fit_r + V[r, g] * u)
    if side == "lt":
        p = np.mean(tb <= t_obs)
    elif side == "gt":
        p = np.mean(tb >= t_obs)
    else:
        p = np.mean(np.abs(tb) >= abs(t_obs))
    return t_obs, p


def main():
    panel = pd.read_csv(ROOT / "results" / "panel.csv", dtype={"pref_code": str})
    rows = []
    d = A.sample(panel, {"label": ""})

    # X1: wild cluster bootstrap for the main tests
    tests = [
        ("H1", "gap", ["trend", "post"], "trend", 0.0, "lt", dict(fe_full="pref_code"), d, "wg"),
        ("H2", "lnW", ["lnR"], "lnR", 1.0, "lt", dict(fe_full="pref_code", fe_part="year", drop_levels=["2012"]), d, "wg"),
        ("H2", "lnW", ["lnR"], "lnR", 0.0, "two", dict(fe_full="pref_code", fe_part="year", drop_levels=["2012"]), d, "wg"),
        ("H3", "lnW", ["lnR", "lnM"], "lnM", 0.0, "gt", dict(fe_full="pref_code", fe_part="year", drop_levels=["2012"]), d, "wg"),
    ]
    s = A.stack(d)
    tests.append(("H4", "y", ["lnR", "lnR_G", "lnM_G", "lnM_C"], "lnR_G", 0.0, "gt",
                  dict(fe_full="occ_pref", fe_part="occ_year", drop_levels=["guard_2012", "cleaner_2012"]), s, "w"))
    for model, y, xs, term, null, side, fe, data, wcol in tests:
        res, G = A.fit(data, y, xs, fe["fe_full"], fe.get("fe_part"), fe.get("drop_levels", ()), weight=wcol)
        c = A.coef(res, G, term, null=null, side=None if side == "two" else side)
        t_obs, p = wild(data, y, xs, term, null, side, weight=wcol, **fe)
        assert np.isclose(t_obs, c["t"]), (model, t_obs, c["t"])
        rows.append(dict(check="X1", model=model, term=term, null=null, side=side, coef=c["coef"], t=c["t"],
                         p_t46=c["p_one"] if side != "two" else c["p_two"], p_wild=p, draws=B_DRAWS, n_obs=len(data)))

    # X2: pay per hour worked including overtime
    pay = pd.read_csv(ROOT / "data" / "pay_by_prefecture.csv", dtype={"pref_code": str})
    g = pay[(pay["occupation"] == "security_guards") & (pay["position_holders"] == "excluded") & (pay["sex"] == "total")]
    g = g.set_index(["pref_code", "survey_year"])
    wt = 8 * (g["contractual_earnings_kyen"] * 1000 + g["annual_bonus_kyen"] * 1000 / 12) / (g["scheduled_hours"] + g["overtime_hours"])
    p2 = panel.set_index(["pref_code", "year"]).copy()
    p2["gt_W"] = wt.reindex(p2.index).values
    p2 = p2.reset_index()
    assert p2.loc[p2["pref_code"] != "00", "gt_W"].notna().all()
    dx = A.sample(p2, {"label": "", "guard": "gt_W"})
    res, G = A.fit(dx, "gap", ["trend", "post"], "pref_code", weight="wg")
    rows.append(dict(check="X2", model="H1", **{k: v for k, v in A.coef(res, G, "trend", side="lt").items()
                                                  if k in ("term", "coef", "se", "ci_low", "ci_high", "p_one", "p_two", "null")}, n_obs=len(dx)))
    res, G = A.fit(dx, "lnW", ["lnR"], "pref_code", "year", drop_levels=["2012"], weight="wg")
    for null, side in ((1.0, "lt"), (0.0, None)):
        c = A.coef(res, G, "lnR", null=null, side=side)
        rows.append(dict(check="X2", model="H2", **{k: v for k, v in c.items()
                                                      if k in ("term", "coef", "se", "ci_low", "ci_high", "p_one", "p_two", "null")}, n_obs=len(dx)))
    res, G = A.fit(dx, "lnW", ["lnR", "lnM"], "pref_code", "year", drop_levels=["2012"], weight="wg")
    for term, side in (("lnR", None), ("lnM", "gt")):
        c = A.coef(res, G, term, side=side)
        rows.append(dict(check="X2", model="H3", **{k: v for k, v in c.items()
                                                      if k in ("term", "coef", "se", "ci_low", "ci_high", "p_one", "p_two", "null")}, n_obs=len(dx)))
    nat = p2[p2["pref_code"] == "00"].set_index("year")
    x2_growth = {f"{a}-{b}": 100 * (nat.loc[b, "gt_W"] / nat.loc[a, "gt_W"] - 1) for a, b in ((2012, 2019), (2020, 2025), (2012, 2025))}

    # X3: long differences 2012-2025
    pr = panel[panel["pref_code"] != "00"]
    a, b = pr[pr["year"] == 2012].set_index("pref_code"), pr[pr["year"] == 2025].set_index("pref_code")
    dlr = np.log(b["R"]) - np.log(a["R"])
    for occ, col, wcol in (("guards", "g_W", "w_guard"), ("cleaners", "c_W", "w_cleaner")):
        dlw = np.log(b[col]) - np.log(a[col])
        r = sm.WLS(dlw.values, sm.add_constant(dlr.values), weights=a[wcol].values).fit(cov_type="HC1", use_t=True)
        q = stats.t.ppf(0.975, r.df_resid)   # t(45), like every other interval in the paper
        rows.append(dict(check="X3", model=f"long difference, {occ}", term="dlnR", null=0.0, coef=r.params[1], se=r.bse[1],
                         ci_low=r.params[1] - q * r.bse[1], ci_high=r.params[1] + q * r.bse[1], p_two=r.pvalues[1],
                         n_obs=len(dlw), sd_dlnR=float(np.std(dlr, ddof=1)), sd_dlnW=float(np.std(dlw, ddof=1))))

    # X4: correlation in levels across prefectures, by year (weighted)
    def wcorr(x, y, w):
        mx, my = np.average(x, weights=w), np.average(y, weights=w)
        cov = np.average((x - mx) * (y - my), weights=w)
        return cov / np.sqrt(np.average((x - mx) ** 2, weights=w) * np.average((y - my) ** 2, weights=w))

    for year, sub in pr.groupby("year"):
        rows.append(dict(check="X4", model=str(year), term="corr(ln R, ln W)",
                         coef=wcorr(np.log(sub["R"]), np.log(sub["g_W"]), sub["w_guard"]),
                         coef_cleaners=wcorr(np.log(sub["R"]), np.log(sub["c_W"]), sub["w_cleaner"]), n_obs=len(sub)))

    # X5 and X6: other protective service workers, 2020-2025
    def occ_vars(occ, prefix):
        o = pay[(pay["occupation"] == occ) & (pay["position_holders"] == "excluded") & (pay["sex"] == "total")
                & (pay["survey_year"] >= 2020)].set_index(["pref_code", "survey_year"])
        return pd.DataFrame({f"{prefix}_S": o["scheduled_earnings_kyen"] * 1000, f"{prefix}_B": o["annual_bonus_kyen"] * 1000,
                             f"{prefix}_H": o["scheduled_hours"], f"{prefix}_n": o["workers_tens"] * 10})
    q = occ_vars("other_protective", "o").join(occ_vars("security_guards", "s"))
    q["o_W"] = 8 * (q["o_S"] + q["o_B"] / 12) / q["o_H"]
    has_o = q[["o_S", "o_B", "o_H", "o_n"]].notna().all(axis=1)
    no = q["o_n"].where(has_o, 0.0)
    for v in ("S", "B", "H"):
        q[f"b_{v}"] = (q[f"s_{v}"] * q["s_n"] + q[f"o_{v}"].where(has_o, 0.0) * no) / (q["s_n"] + no)
    q["b_n"] = q["s_n"] + no
    q["b_W"] = 8 * (q["b_S"] + q["b_B"] / 12) / q["b_H"]
    q.index = q.index.set_names(["pref_code", "year"])
    p5 = panel[panel["year"] >= 2020].set_index(["pref_code", "year"]).join(q[["o_W", "o_n", "b_W", "b_n"]]).reset_index()
    pr5 = p5[p5["pref_code"] != "00"]
    p5 = p5.merge(pr5.groupby("pref_code")["o_n"].mean().rename("w_o"), on="pref_code", how="left")
    p5 = p5.merge(pr5.groupby("pref_code")["b_n"].mean().rename("w_b"), on="pref_code", how="left")
    natq = p5[p5["pref_code"] == "00"].set_index("year")
    x56_growth = {k: 100 * (natq.loc[2025, c] / natq.loc[2020, c] - 1)
                  for k, c in (("R", "R"), ("security guards", "g_W"), ("other protective", "o_W"),
                               ("combined", "b_W"), ("building cleaners", "c_W"))}
    x56_levels = {k: (natq.loc[2020, c], natq.loc[2025, c]) for k, c in
                  (("R", "R"), ("other protective", "o_W"), ("combined", "b_W"), ("security guards", "g_W"))}
    dropped = pr5.loc[pr5["o_W"].isna(), ["prefecture", "year"]].values.tolist()
    assert sorted(map(tuple, dropped)) == [("Ishikawa", 2020), ("Shimane", 2020), ("Shimane", 2023), ("Shimane", 2024)], dropped
    keep_cols = ("term", "coef", "se", "ci_low", "ci_high", "p_one", "p_two", "null")

    def add(check, model, c, n):
        rows.append(dict(check=check, model=model, **{k: v for k, v in c.items() if k in keep_cols}, n_obs=n))

    for check, wcol, wname in (("X5", "o_W", "w_o"), ("X6", "b_W", "w_b")):
        dd = p5[(p5["pref_code"] != "00") & p5[wcol].notna()].copy()
        dd["lnR"], dd["lnM"], dd["lnW"] = np.log(dd["R"]), np.log(dd["M"]), np.log(dd[wcol])
        dd["trend"] = dd["year"] - 2012
        dd["gap"] = dd["lnW"] - dd["lnR"]
        res, G = A.fit(dd, "gap", ["trend"], "pref_code", weight=wname)
        add(check, "H1", A.coef(res, G, "trend", side="lt"), len(dd))
        res, G = A.fit(dd, "lnW", ["lnR"], "pref_code", "year", drop_levels=["2020"], weight=wname)
        add(check, "H2", A.coef(res, G, "lnR", null=1.0, side="lt"), len(dd))
        add(check, "H2", A.coef(res, G, "lnR", null=0.0), len(dd))
        res, G = A.fit(dd, "lnW", ["lnR", "lnM"], "pref_code", "year", drop_levels=["2020"], weight=wname)
        add(check, "H3", A.coef(res, G, "lnR"), len(dd))
        add(check, "H3", A.coef(res, G, "lnM", side="gt"), len(dd))
        if check == "X5":
            for other, ocol, owt in (("building cleaners", "c_W", "w_cleaner"), ("security guards", "g_W", "w_guard")):
                base = p5[p5["pref_code"] != "00"].copy()
                a1 = base[base["o_W"].notna()].assign(occ="op", G=1.0, y=lambda z: np.log(z["o_W"]), w=lambda z: z["w_o"])
                a0 = base.assign(occ="other", G=0.0, y=lambda z: np.log(z[ocol]), w=lambda z: z[owt])
                st = pd.concat([a1, a0], ignore_index=True)
                st["lnR"], st["lnM"] = np.log(st["R"]), np.log(st["M"])
                st["lnR_G"], st["lnM_G"], st["lnM_C"] = st["lnR"] * st["G"], st["lnM"] * st["G"], st["lnM"] * (1 - st["G"])
                st["occ_pref"] = st["occ"] + "_" + st["pref_code"]
                st["occ_year"] = st["occ"] + "_" + st["year"].astype(str)
                res, G = A.fit(st, "y", ["lnR", "lnR_G", "lnM_G", "lnM_C"], "occ_pref", "occ_year",
                               drop_levels=["op_2020", "other_2020"], weight="w")
                add(check, f"H4 against {other}", A.coef(res, G, "lnR_G", side="gt"), len(st))

    out = pd.DataFrame(rows)
    out.to_csv(ROOT / "tables" / "extra_checks.csv", index=False, float_format="%.6g")
    L = ["# Analyses added after the main results were seen", "", "Output of `code/04_extra_checks.py`. Not tests of the plan's hypotheses.", ""]
    L += ["## X1. Wild cluster bootstrap (restricted, Rademacher, 9,999 draws)", "", "| Model | Term | H0 | Side | Estimate | t | p, t(46) | p, wild bootstrap |", "|---|---|---|---|---|---|---|---|"]
    for r in out[out["check"] == "X1"].itertuples():
        L.append(f"| {r.model} | {r.term} | {r.null:g} | {r.side} | {r.coef:.4f} | {r.t:.3f} | {r.p_t46:.4f} | {r.p_wild:.4f} |")
    L += ["", "## X2. Pay per hour worked, including overtime pay", "", "| Model | Term | H0 | Estimate | SE | 95% interval | p two-sided | p one-sided |", "|---|---|---|---|---|---|---|---|"]
    for r in out[out["check"] == "X2"].itertuples():
        L.append(f"| {r.model} | {r.term} | {r.null:g} | {r.coef:.4f} | {r.se:.4f} | {r.ci_low:.3f} to {r.ci_high:.3f} | {r.p_two:.4f} | "
                 f"{'' if pd.isna(r.p_one) else f'{r.p_one:.4f}'} |")
    L += [""] + [f"- National growth of this pay measure, {k}: {v:.1f}%" for k, v in x2_growth.items()]
    L += ["", "## X3. Long differences, 2012-2025 (one observation per prefecture, HC1, t(45))", "",
          "| Occupation | Slope on Δln R | SE | 95% interval | p | SD of Δln R | SD of Δln W |", "|---|---|---|---|---|---|---|"]
    for r in out[out["check"] == "X3"].itertuples():
        L.append(f"| {r.model} | {r.coef:.3f} | {r.se:.3f} | {r.ci_low:.3f} to {r.ci_high:.3f} | {r.p_two:.4f} | {r.sd_dlnR:.4f} | {r.sd_dlnW:.4f} |")
    L += ["", "## X4. Weighted correlation across prefectures in levels", "", "| Year | ln R with guards' ln W | ln R with cleaners' ln W |", "|---|---|---|"]
    for r in out[out["check"] == "X4"].itertuples():
        L.append(f"| {r.model} | {r.coef:.3f} | {r.coef_cleaners:.3f} |")
    L += ["", "## X5 and X6. Other protective service workers (includes traffic guards), and combined with security guards, 2020-2025", ""]
    L += [f"- National growth 2020-2025: " + "; ".join(f"{k} {v:.1f}%" for k, v in x56_growth.items())]
    L += [f"- National levels, 2020 and 2025 (yen per 8 hours): " + "; ".join(f"{k} {a:,.0f} and {b:,.0f}" for k, (a, b) in x56_levels.items())]
    L += [f"- Prefecture-years left out of X5 (no figures): {', '.join(f'{p} {y}' for p, y in dropped)}", "",
          "| Analysis | Model | Term | H0 | Estimate | SE | 95% interval | p two-sided | p one-sided | N |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in out[out["check"].isin(["X5", "X6"])].itertuples():
        L.append(f"| {r.check} | {r.model} | {r.term} | {r.null:g} | {r.coef:.4f} | {r.se:.4f} | {r.ci_low:.3f} to {r.ci_high:.3f} | "
                 f"{r.p_two:.4f} | {'' if pd.isna(r.p_one) else f'{r.p_one:.4f}'} | {r.n_obs} |")
    (ROOT / "results" / "extra_checks.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
