"""Tests of the estimator in code/02_analysis.py on simulated data (no real data are used).

1. With known coefficients, WLS with prefecture and year dummies recovers them.
2. The clustered standard errors equal a sandwich computed by hand with the correction
   G/(G-1) * (N-1)/(N-K), K counting every coefficient including the fixed effects.
3. p-values and intervals use t(G-1).
4. In the stacked model (H4), lnR + lnR_G equals the guards-only coefficient, as it must when every other
   coefficient is specific to the occupation.

Usage: python tests/test_estimator.py
"""

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("analysis", ROOT / "code" / "02_analysis.py")
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)


def simulate(seed=1, beta=0.3, gamma=0.5, beta_c=0.1, gamma_c=0.7):
    rng = np.random.default_rng(seed)
    prefs = [f"{i:02d}" for i in range(1, 48)]
    years = range(2012, 2026)
    a = dict(zip(prefs, rng.normal(9, 0.1, 47)))
    ac = dict(zip(prefs, rng.normal(8.9, 0.1, 47)))
    d = dict(zip(years, np.cumsum(rng.normal(0.02, 0.01, 14))))
    rows = []
    for p in prefs:
        lr0, lm0 = rng.normal(9.1, 0.05), rng.normal(6.7, 0.05)
        for t in years:
            k = t - 2012
            lnR = lr0 + 0.05 * k + rng.normal(0, 0.03)
            lnM = lm0 + 0.025 * k + rng.normal(0, 0.01)
            e = rng.normal(0, 0.02)  # common within prefecture-year, so the clusters matter
            rows.append(dict(pref_code=p, year=t, lnR=lnR, lnM=lnM,
                             lnW=a[p] + d[t] + beta * lnR + gamma * lnM + e + rng.normal(0, 0.02),
                             lnWc=ac[p] + 0.5 * d[t] + beta_c * lnR + gamma_c * lnM + e + rng.normal(0, 0.02),
                             wg=rng.uniform(1, 50), wc=rng.uniform(1, 50)))
    return pd.DataFrame(rows)


def manual(d, y, xs, wcol):
    X = pd.concat([d[xs], pd.get_dummies(d["pref_code"], dtype=float),
                   pd.get_dummies(d["year"].astype(str), dtype=float).drop(columns="2012")], axis=1).values
    Y, w = d[y].values, d[wcol].values
    XtWX = X.T @ (X * w[:, None])
    b = np.linalg.solve(XtWX, X.T @ (w * Y))
    e = Y - X @ b
    meat = np.zeros_like(XtWX)
    for g in d["pref_code"].unique():
        m = (d["pref_code"] == g).values
        s = X[m].T @ (w[m] * e[m])
        meat += np.outer(s, s)
    N, K, G = X.shape[0], X.shape[1], d["pref_code"].nunique()
    inv = np.linalg.inv(XtWX)
    V = G / (G - 1) * (N - 1) / (N - K) * inv @ meat @ inv
    return b[: len(xs)], np.sqrt(np.diag(V))[: len(xs)]


def main():
    d = simulate()
    res, G = A.fit(d, "lnW", ["lnR", "lnM"], "pref_code", "year", drop_levels=["2012"], weight="wg")
    assert G == 47
    b, se = manual(d, "lnW", ["lnR", "lnM"], "wg")
    assert np.allclose(res.params[["lnR", "lnM"]].values, b, rtol=1e-8), (res.params[["lnR", "lnM"]], b)
    assert np.allclose(res.bse[["lnR", "lnM"]].values, se, rtol=1e-8), (res.bse[["lnR", "lnM"]], se)
    c = A.coef(res, G, "lnR")
    assert np.isclose(c["p_two"], float(res.pvalues["lnR"])), "statsmodels does not use t(G-1)"
    assert np.isclose(c["ci_low"], float(res.conf_int().loc["lnR", 0]))
    assert np.isclose(c["p_two"], 2 * stats.t.sf(abs(c["t"]), 46))
    print(f"1-3. beta {res.params['lnR']:.3f} (true 0.3), gamma {res.params['lnM']:.3f} (true 0.5); "
          f"SEs equal the hand-computed sandwich; p-values use t(46)")

    # recovery over many draws: mean estimates near the truth, intervals cover about 95% of the time
    bs, cover = [], 0
    for s in range(200):
        dd = simulate(seed=100 + s)
        r, G = A.fit(dd, "lnW", ["lnR", "lnM"], "pref_code", "year", drop_levels=["2012"], weight="wg")
        cc = A.coef(r, G, "lnR")
        bs.append(cc["coef"])
        cover += cc["ci_low"] <= 0.3 <= cc["ci_high"]
    print(f"   200 draws: mean beta {np.mean(bs):.4f} (true 0.3); 95% interval covers the truth in {cover / 2:.0f}% of draws")
    assert abs(np.mean(bs) - 0.3) < 0.01 and 0.90 <= cover / 200 <= 0.99

    # stacked model
    dd = d.copy()
    s = A.stack(dd)
    r4, G4 = A.fit(s, "y", ["lnR", "lnR_G", "lnM_G", "lnM_C"], "occ_pref", "occ_year",
                   drop_levels=["guard_2012", "cleaner_2012"], weight="w")
    rg, _ = A.fit(dd, "lnW", ["lnR", "lnM"], "pref_code", "year", drop_levels=["2012"], weight="wg")
    rc, _ = A.fit(dd, "lnWc", ["lnR", "lnM"], "pref_code", "year", drop_levels=["2012"], weight="wc")
    assert np.isclose(r4.params["lnR"] + r4.params["lnR_G"], rg.params["lnR"])
    assert np.isclose(r4.params["lnR"], rc.params["lnR"])
    assert np.isclose(r4.params["lnM_G"], rg.params["lnM"]) and np.isclose(r4.params["lnM_C"], rc.params["lnM"])
    print(f"4. stacked: theta {r4.params['lnR_G']:.3f} (true 0.2); lnR + lnR_G equals the guards-only coefficient")
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
