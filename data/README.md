# Data

The three files in this folder are copied unchanged from `data/clean/` of japan-guard-price-panel v1.2.1 (commit `5325e10`, [10.5281/zenodo.23856290](https://doi.org/10.5281/zenodo.23856290)). That data set documents how each file was built from the official tables, the checks run on it and the meaning of every column; this folder only records which version is used here.

| File | Rows (excluding header) | SHA-256 | Contents |
|---|---|---|---|
| `guard_rates_by_prefecture.csv` | 1,410 | `63949d2256ca35a487651e59a77785921697970b44d39dbb668ccc1d7756cc0d` | MLIT's guard A and guard B daily rates by prefecture, FY2012-FY2026 tables |
| `minimum_wage_by_prefecture.csv` | 1,200 | `2194b93f49cbbba33182147d9813e00bc9a74efbdf10c3563af3df7049687cf2` | Prefecture minimum wages and their effective dates, FY2002-FY2026 |
| `pay_by_prefecture.csv` | 7,872 | `4c686a74f1ef5f30fc56ce1e976f85582c7dfc3b89f530585928b25e5802a489` | MHLW wage survey figures by prefecture, survey years 2012-2025: security guards, building cleaners, gatekeepers (to 2019) and other protective service workers (from 2020) |

The analysis plan names v1.1.0 ([10.5281/zenodo.23852300](https://doi.org/10.5281/zenodo.23852300)). Against v1.1.0:

- The rate file is identical.
- All 6,144 rows of the v1.1.0 pay file are unchanged; v1.2.0 adds 1,728 rows for other protective service workers (2020-2025), which only the analyses added after the main results were seen (X5 and X6 in `code/04_extra_checks.py`) use.
- The minimum wage file differs in two rows: v1.2.1 corrects the national weighted averages for FY2017 (848 yen, not 847) and FY2026 (1,177, not 1,176), which had been truncated instead of rounded. No prefecture value changes. Of the two, only FY2017 is used here, in the national series for 2018.

## Sources and terms

- 「公共工事設計労務単価」（国土交通省）, https://www.mlit.go.jp/totikensangyo/const/1_6_bt_000217.html. Public Data License 1.0. Edited from MLIT's files (「公共工事設計労務単価」（国土交通省）を加工して作成); not an official MLIT product.
- 「賃金構造基本統計調査」（厚生労働省）, via e-Stat, https://www.e-stat.go.jp/stat-search/files?toukei=00450091&tstat=000001011429. e-Stat terms of use (compatible with CC BY 4.0). Edited from these files; not an official MHLW product.
- 「平成14年度から令和８年度までの地域別最低賃金改定状況」（厚生労働省）, https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/koyou_roudou/roudoukijun/minimumichiran/. Public Data License 1.0. Edited from MHLW's file; not an official MHLW product.

The compiled files are published in japan-guard-price-panel under CC BY 4.0, with these credits.
