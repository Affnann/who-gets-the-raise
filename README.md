# who-gets-the-raise

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23852892.svg)](https://doi.org/10.5281/zenodo.23852892)

Replication package for Kazi Affnann Azom (2026), "Who Gets the Raise? Japan's Public Works Pay Rates and the Wages of Security Guards." Preprint, Zenodo. [10.5281/zenodo.23852894](https://doi.org/10.5281/zenodo.23852894)

Every year Japan's Ministry of Land, Infrastructure, Transport and Tourism (MLIT) sets the public works design labor rates (公共工事設計労務単価), the daily wage that cost estimates for public works assume for each trade in each prefecture, including traffic guards employed by security companies. The rates are estimates of cost: from FY2012 to FY2016 MLIT's releases stated that they did not bind the labor rates in subcontracts or the wages paid to workers. This package compares the official rate for traffic guards with what guards were actually paid, by prefecture, from 2012 to 2025.

## Main results

- **The official rate doubled; guards' pay rose by under a third.** From FY2012 to FY2025 the official rate for traffic guards (the mean of grades A and B, averaged across the 47 prefectures with each prefecture's number of guards as its weight) rose by 107.7%, from ¥8,326 to ¥17,292 a day. Security guards' pay per 8 scheduled hours, including bonuses, rose by 29.2%, from ¥9,491 to ¥12,259, less than building cleaners' pay (33.8%) and the minimum wage (43.1%). In 2012 guards were paid 14% more than the official rate; in 2025, 29% less, and less than the rate in every prefecture.
- **H1 holds: within prefectures, the gap widened by about 4% a year** (τ = -0.040, 95% interval -0.045 to -0.035), in every check.
- **H2: pay rose by less than the rate, and no more where the rate rose more.** With prefecture and year effects, β = -0.10 (95% interval -0.91 to 0.70): below one (one-sided p = 0.004) but not different from zero. The rate rose by similar proportions everywhere (the standard deviation of its 2012-2025 log change across prefectures is 0.031, against 0.146 for pay), so this test has little power.
- **H3: guards' pay moved with the minimum wage** (γ = 0.98, 95% interval -0.01 to 1.97, one-sided p = 0.026), but not in every check: not within either sub-period, unweighted, with gatekeepers included before 2020, or including position holders.
- **H4 fails: the rate is no more closely tied to guards' pay than to the pay of building cleaners**, an occupation the design labor rates do not cover (θ = -0.16, 95% interval -1.06 to 0.74), in every check.
- **By MHLW's own definitions, its security guards are not traffic guards** (see "Read this first"). In analyses added after the main results were seen, the occupation that includes traffic guards, other protective service workers, published from 2020, saw its pay per 8 hours rise by 5.1% from 2020 to 2025, while the official rate rose by 28.6%; within prefectures its gap with the rate widened by 3.7% a year.

The analysis plan was written before any test was run and is the first commit of this repository: [`plan/analysis_plan.md`](plan/analysis_plan.md). Its change log records the details settled after it was pushed and before the first result, the six analyses added after the main results were seen, and three corrections to statements in the plan, made after the main results were seen. None of the corrections changes a test.

## What is in this repository

| Path | Contents |
|---|---|
| [`plan/analysis_plan.md`](plan/analysis_plan.md) | The dated analysis plan: question, data, definitions, hypotheses H1-H4, checks C1-C12, change log |
| [`data/`](data/) | The three data files from japan-guard-price-panel v1.2.1 (see [`data/README.md`](data/README.md)) |
| [`code/01_build_panel.py`](code/01_build_panel.py) | Builds the prefecture-year panel (`results/panel.csv`) with the plan's definitions |
| [`code/02_analysis.py`](code/02_analysis.py) | H1-H4 and checks C1-C12, as set out in the plan |
| [`code/03_figures.py`](code/03_figures.py) | The three figures |
| [`code/04_extra_checks.py`](code/04_extra_checks.py) | Six analyses (X1-X6) added after the main results were seen, labelled as such in the paper |
| [`tests/test_estimator.py`](tests/test_estimator.py) | Tests of the estimator on simulated data: it recovers known coefficients, and its clustered standard errors equal a sandwich computed by hand |
| [`results/`](results/) | The panel, every planned estimate (`estimates.csv`), and every number in one file each for the planned analysis (`main_results.md`) and the added ones (`extra_checks.md`) |
| [`tables/`](tables/) | National series, summary statistics, hypotheses, checks and added analyses |
| [`figures/`](figures/) | The figures (300 dpi) |

## Reproduce it

Needs Python 3.10 or later. The results were produced with Python 3.13, pandas 3.0.5, NumPy 2.5.3, SciPy 1.18.1, statsmodels 0.15.0 and Matplotlib 3.11.2.

```
pip install -r requirements.txt
python code/01_build_panel.py
python code/02_analysis.py
python code/03_figures.py
python code/04_extra_checks.py
python tests/test_estimator.py
```

## Definitions

For prefecture *p* and survey year *t*:

- **Official rate** *R*: the mean of the guard A and guard B daily rates in MLIT's table for fiscal year *t*, in force in June of *t*. Guard A holds a first- or second-grade qualification in traffic guarding; guard B is any other security company guard directing traffic.
- **Guards' pay** *W* = 8 × (*S* + *B*/12) / *H*: pay per 8 scheduled hours, including bonuses, of security guards (both sexes, general workers, excluding position holders), where *S* is scheduled monthly earnings in June, *B* the previous calendar year's bonuses and *H* scheduled hours in June. Like the rate, it includes basic pay, regular allowances and bonuses and excludes overtime pay.
- **Minimum wage** *M*: the prefecture minimum wage in force on 30 June, that is, the previous fiscal year's amount.
- **Weights**: each prefecture's average estimated number of guards over 2012-2025.

## Read this first

- **MHLW's security guards are not traffic guards.** By MHLW's definitions, its occupation 警備員 covers guarding facilities and people. From 2020 MHLW lists traffic guards (交通誘導員), crowd guards and construction site guides under 1459 その他の保安職業従事者, other protective service workers; up to 2019 its definition of 警備員 describes facility, cash-in-transit and personal guarding and does not mention traffic or crowd guarding. How employers actually classified their traffic guards cannot be told from the published tables. The planned analysis uses security guards for 2012-2025, as the plan set out; other protective service workers enter in the analyses added later (X5, X6), for 2020-2025 only.
- **The rates are estimates of cost.** MLIT sets them from a survey of wages paid on public works in October of the year before, in which security companies' guards are included. They exclude the security company's overheads. From FY2012 to FY2016 MLIT's releases stated that they did not bind subcontract labor rates or wages. From FY2026, under the standard for labor costs recommended in December 2025 under the amended Construction Business Act, they are also the basis of the "appropriate labor cost" that construction contracts are expected to secure, which is after the period studied here.
- **Building cleaners** are not covered by the design labor rates, but MLIT sets separate building maintenance labor rates (建築保全業務労務単価) for cleaners and facility guards in maintenance contracts at government buildings, by region.
- **The 2020 break.** In 2020 MHLW changed its occupation list, began to include position holders in occupation figures, and changed its estimation method. The main series excludes position holders in every year, so the coverage is the same; the remaining break is absorbed by year effects, or by a shift from 2020 in H1.
- **Associations, not effects.** MLIT sets each prefecture's rate from its own survey of wages, so the regressions measure how pay and the rate move together, not the effect of the rate on pay.

## Data sources

All three files come from japan-guard-price-panel v1.2.1 ([10.5281/zenodo.23856290](https://doi.org/10.5281/zenodo.23856290)). The plan names v1.1.0 ([10.5281/zenodo.23852300](https://doi.org/10.5281/zenodo.23852300)); the prefecture rows used by the planned analysis are identical in the two, and v1.2.1 corrects two national averages of the minimum wage (see [`data/README.md`](data/README.md)). The data set compiles them from:

- 「公共工事設計労務単価」（国土交通省）, https://www.mlit.go.jp/totikensangyo/const/1_6_bt_000217.html, used under the Public Data License 1.0. The tables are edited from MLIT's files (「公共工事設計労務単価」（国土交通省）を加工して作成) and are not an official MLIT product.
- 「賃金構造基本統計調査」（厚生労働省）, via e-Stat, https://www.e-stat.go.jp/stat-search/files?toukei=00450091&tstat=000001011429, used under e-Stat's terms of use (compatible with CC BY 4.0). The tables are edited from these files and are not an official MHLW product.
- 「平成14年度から令和８年度までの地域別最低賃金改定状況」（厚生労働省）, https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/koyou_roudou/roudoukijun/minimumichiran/, used under the Public Data License 1.0. The table is edited from MHLW's file and is not an official MHLW product.

## How to cite

Azom, Kazi Affnann (2026). *who-gets-the-raise: replication package for 'Who Gets the Raise? Japan's Public Works Pay Rates and the Wages of Security Guards'* (Version v1.0.0) [Software]. Zenodo. https://doi.org/10.5281/zenodo.23852892

To cite the paper:

Azom, Kazi Affnann (2026). *Who Gets the Raise? Japan's Public Works Pay Rates and the Wages of Security Guards* [Preprint]. Zenodo. https://doi.org/10.5281/zenodo.23852894

See also `CITATION.cff`.

## License

Code: MIT (see [`LICENSE`](LICENSE)). Data, text, plan, results, tables and figures: CC BY 4.0 (see [`LICENSE-DATA`](LICENSE-DATA)), with the source credits above.
