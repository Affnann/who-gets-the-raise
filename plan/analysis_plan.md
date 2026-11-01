# Analysis plan: Who Gets the Raise? Japan's Public Works Pay Rates and the Wages of Security Guards

Kazi Affnann Azom. Written 1 November 2026, before any of the tests below was run.

This plan is the first commit of this repository. Anything added after the first results were seen is recorded in the change log at the end and labelled as added later wherever it is reported.

## 0. What had been seen before this plan was written

The data were built and checked in japan-guard-price-panel v1.1.0 (https://doi.org/10.5281/zenodo.23852300). Building them meant looking at national series one at a time: the average official rate for traffic guards across the 47 prefectures roughly doubled between FY2012 and FY2025, and the national monthly scheduled earnings of security guards rose by about a quarter between 2012 and 2025. No comparison of rates and pay by prefecture, no regression and no test in this plan had been run. Because the national direction of the gap in H1 was seen in advance, H1's national comparison is descriptive; its test is the prefecture-level trend below.

## 1. Question

Every year Japan's Ministry of Land, Infrastructure, Transport and Tourism (MLIT) sets the public works design labor rates (公共工事設計労務単価), the daily wage that cost estimates for public works assume for each trade in each prefecture, including traffic guards (交通誘導警備員A and B). MLIT states that the rates are for estimating costs and do not bind the wages paid to workers. When the official rate for guards rises, how much of the rise shows up in what security guards are actually paid?

## 2. Data

All from japan-guard-price-panel v1.1.0 (CC BY 4.0), copied unchanged into `data/`:

- `guard_rates_by_prefecture.csv`: MLIT daily rates for guards A and B, 47 prefectures, table years FY2012-FY2026.
- `pay_by_prefecture.csv`: MHLW Basic Survey on Wage Structure (賃金構造基本統計調査), general (full-time) workers, survey years 2012-2025, security guards (警備員), building cleaners (ビル清掃員 / ビル・建物清掃員) and, to 2019, gatekeepers (守衛).
- `minimum_wage_by_prefecture.csv`: MHLW prefecture minimum wages and effective dates, FY2002-FY2026.

## 3. Definitions

For prefecture *p* and survey year *t* (2012-2025):

- **Official rate** *R*<sub>*pt*</sub>: the mean of the guard A and guard B daily rates in MLIT's table for fiscal year *t*. Every table year's rates took effect between February and April of calendar year *t*, so they are the rates in force in June of *t*, the month the wage survey measures. Special rates in the source (post-earthquake rates for Iwate, Miyagi and Fukushima; the FY2021 COVID-19 measure) are kept as published.
- **Guards' pay** *W*<sub>*pt*</sub>: pay per 8 scheduled hours, including bonuses, of security guards, both sexes, excluding position holders (the coverage MHLW used for occupations before 2020):

  *W* = 8 × (*S* + *B*/12) / *H*

  where *S* is scheduled monthly earnings for June (所定内給与額), *B* the previous calendar year's bonuses and other special earnings (年間賞与その他特別給与額), and *H* scheduled hours worked in June (所定内実労働時間数). MLIT's rate covers basic pay, regular allowances, bonuses and pay in kind for 8 scheduled hours and excludes overtime pay, so *W* is built to cover the same elements.
- **Minimum wage** *M*<sub>*pt*</sub>: the prefecture's minimum wage in force on 30 June of year *t*, that is, the fiscal year *t*−1 amount (every revision took effect by 31 March of *t*), in yen per hour.
- **Building cleaners' pay**: defined as *W*, for building cleaners.
- **Weights**: each prefecture's average estimated number of guards (both sexes, excluding position holders) over 2012-2025, held fixed across years. For building cleaners, their own average.
- **National series**: Japan's *W* from MHLW's national row; Japan's *R* as the weighted mean of the prefecture rates.

## 4. Hypotheses and tests

All regressions are weighted, with standard errors clustered by prefecture (47 clusters) and *t*(46) critical values. One-sided tests at the 5 percent level where a hypothesis has a direction; 95 percent intervals reported throughout.

**H1. The official rate rose faster than guards' pay.** Prefecture-level trend in the gap:

ln(*W*<sub>*pt*</sub>/*R*<sub>*pt*</sub>) = α<sub>*p*</sub> + τ(*t* − 2012) + κ·1[*t* ≥ 2020] + ε<sub>*pt*</sub>

H1 predicts τ < 0. The dummy for 2020 onwards absorbs the change in MHLW's survey that year. Reported alongside: the national ratio *W*/*R* each year, and the growth of *R* and *W* from 2012 to 2019 and from 2020 to 2025.

**H2. Pay rises by less than the rate.** Within prefectures over time:

ln *W*<sub>*pt*</sub> = β ln *R*<sub>*pt*</sub> + α<sub>*p*</sub> + δ<sub>*t*</sub> + ε<sub>*pt*</sub>

H2 predicts β < 1. Also reported: the test of β = 0. Because MLIT sets each prefecture's rate from its own survey of wages paid on public works, β measures how far guards' pay and the rate move together across prefectures, not the causal effect of the rate.

**H3. Guards' pay follows the minimum wage.** Adding the minimum wage:

ln *W*<sub>*pt*</sub> = β ln *R*<sub>*pt*</sub> + γ ln *M*<sub>*pt*</sub> + α<sub>*p*</sub> + δ<sub>*t*</sub> + ε<sub>*pt*</sub>

H3 predicts γ > 0. Also reported: γ − β with its interval.

**H4. Comparison with building cleaners.** If the official rate moves guards' pay, it should be more closely tied to guards' pay than to the pay of building cleaners in the same prefecture and year, whose work has no MLIT rate. Stacking the two occupations *o*:

ln *W*<sub>*opt*</sub> = β<sub>c</sub> ln *R*<sub>*pt*</sub> + θ ln *R*<sub>*pt*</sub>·*G*<sub>*o*</sub> + γ<sub>*o*</sub> ln *M*<sub>*pt*</sub> + α<sub>*op*</sub> + δ<sub>*ot*</sub> + ε<sub>*opt*</sub>

where *G*<sub>*o*</sub> = 1 for guards. H4 is supported if θ > 0. A θ near zero would mean the link between the rate and guards' pay in H2 is no stronger than for an occupation the rate does not cover, that is, it reflects local labor markets rather than the rate.

## 5. Checks (all set in advance)

- C1. Guard A's rate instead of the mean of A and B.
- C2. Guard B's rate instead.
- C3. Pay without bonuses: hourly scheduled pay *S*/*H*.
- C4. Men only (MHLW publishes women guards separately only from 2020).
- C5. 2020-2025 including position holders.
- C6. The 2020 definition throughout: for 2012-2019, guards and gatekeepers combined, weighted by workers, since MHLW counts gatekeepers as security guards from 2020.
- C7. 2012-2019 and 2020-2025 separately.
- C8. Unweighted.
- C9. Without Iwate, Miyagi and Fukushima, and without the five prefectures' FY2021 COVID-19 rates.
- C10. First differences: Δln *W* on Δln *R* and Δln *M*, with year effects.
- C11. The previous year's rate *R*<sub>*p,t*−1</sub> instead of *R*<sub>*pt*</sub> (2013-2025).
- C12. Direction: adding the next year's rate *R*<sub>*p,t*+1</sub>, which MLIT sets from its survey of October of year *t*. If rates follow wages rather than lead them, the next year's rate should be tied to this year's pay more closely than this year's rate is.

## 6. Planned outputs

- Figure 1: national official rate and guards' pay per 8 hours, 2012-2025.
- Figure 2: change in the official rate against change in guards' pay by prefecture, 2012-2025.
- Figure 3: guards' pay relative to eight hours at the minimum wage, 2012-2025.
- Tables: sources; summary statistics; H1-H3; H4; checks.

## 7. How the results will be read

- H1 and H2 together describe whether the rise in the official rate reached guards' pay; neither identifies a causal effect.
- The data cover all security guards, not only traffic guards on public works, and say nothing directly about the security companies' revenue or margins. If guards' pay has not kept up with the rate, the paper will say where the difference could have gone and what data would be needed to tell, not which it was.
- A failed hypothesis is reported as failed.

## Change log

(Empty at the first commit.)
