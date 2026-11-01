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

**1 November 2026, after the plan was pushed to GitHub (05:02 UTC) and before any test was run.** Details the plan left open or got wrong, settled before the first result:

1. C9 said five prefectures carry FY2021 COVID-19 rates. MLIT's FY2021 table has eight, each in one grade (angle brackets in the source: Niigata A, Gifu B, Shizuoka B, Mie B, Tokushima A, Kagawa A, Ehime A, Kochi A). C9 drops those eight prefecture-years, as well as Iwate, Miyagi and Fukushima in every year. The README of japan-guard-price-panel v1.1.0 repeats the error; the data themselves are right.
2. What each check re-estimates. C1-C4, C6, C8, C9 and C11 re-estimate H1 to H4. C5 (2020-2025) and C7 (each sub-period) re-estimate H1 to H4 within the period, with no 2020 dummy in H1. C10 is one regression: Δln *W* on Δln *R* and Δln *M* with year effects, for 2013-2025. C12 adds ln *R*<sub>*p,t*+1</sub> to H2 and H3 and reports its coefficient, the coefficient on ln *R*<sub>*pt*</sub> and their difference with a 95 percent interval.
3. In H4, building cleaners follow each check's definition of pay where it applies to them (C3, C4, C5). The weights are those of section 3 in every check except C8. In C6, the combined pay of guards and gatekeepers is built from their worker-weighted means of *S*, *B* and *H*; in the five prefecture-years where MHLW publishes no figures for gatekeepers (Okinawa 2014 and 2018, Yamagata 2016, Niigata and Miyazaki 2019), from guards alone.
4. Standard errors: clustered by prefecture, with the finite-sample correction *G*/(*G*−1) · (*N*−1)/(*N*−*K*), where *K* counts every coefficient including the fixed effects, and *t*(*G*−1) critical values (*t*(46); *t*(43) in C9). The test of β = 0 in H2 is two-sided.

**1 November 2026, after the main results were seen.** Four analyses added (`code/04_extra_checks.py`), defined before they were run and reported as added later. None is a test of H1 to H4:

- X1. Wild cluster bootstrap p-values (restricted, Rademacher weights by prefecture, 9,999 draws) for the main tests of H1 to H4, as a check on the *t*(46) inference.
- X2. Guards' pay per hour actually worked, including overtime pay: 8 × (*C* + *B*/12) / (*H* + *O*), where *C* is contractual cash earnings (scheduled earnings plus overtime pay) and *O* overtime hours; H1 to H3 re-estimated.
- X3. Long differences: the change in ln *W* from 2012 to 2025 on the change in ln *R*, across the 47 prefectures, for guards and for building cleaners (weighted; HC1 standard errors).
- X4. Levels: the weighted correlation across prefectures between ln *R* and ln *W*, for guards and for building cleaners, in each year.

**1 November 2026, after the main results were seen: a correction, and two more analyses.** Checking MHLW's own explanations of its occupations showed that section 7 is wrong to say the data cover all security guards. From 2020, MHLW's occupation 1453 警備員 covers facility and personal guarding, and its explanations list traffic guards (交通誘導員), crowd guards (雑踏警備員) and construction site guides (建設現場誘導員) under 1459 その他の保安職業従事者, other protective service workers (令和３年 survey, 役職及び職種解説, page 15). To 2019, MHLW's definition of 警備員 describes guarding facilities, cash and valuables in transit and people, by employees of certified security businesses, and does not mention traffic or crowd guarding (令和元年 survey, page 12). By MHLW's definitions, then, *W* is the pay of security guards other than traffic guards; how employers actually classified traffic guards cannot be told from the tables. The planned analysis is unchanged and is reported as planned, with this correction stated.

The data are updated to japan-guard-price-panel v1.2.0 (https://doi.org/10.5281/zenodo.23852751), which adds other protective service workers for 2020-2025; the rows used by the planned analysis are identical to v1.1.0. Two analyses are added, defined before they were run:

- X5. Other protective service workers, 2020-2025, excluding position holders, with *W* defined as in section 3 and each prefecture weighted by its own average number of these workers: the national growth of *W* against *R*; H1 (without the 2020 dummy), H2 and H3 re-estimated; and H4 re-estimated twice, against building cleaners and against security guards. Prefecture-years without figures (Ishikawa 2020; Shimane 2020, 2023 and 2024) are left out.
- X6. Security guards and other protective service workers combined, 2020-2025 (worker-weighted means of *S*, *B* and *H*, weights as in X5 for the combined count): the national growth of *W* against *R*; H1 (without the 2020 dummy), H2 and H3 re-estimated. In the four prefecture-years without figures for other protective service workers, guards alone.

**1 November 2026, two more corrections to the plan's description (no change to any test).** Section 1 says MLIT states that the rates do not bind the wages paid to workers. MLIT's releases said so, for subcontract labor rates and for wages, from FY2012 to FY2016; from FY2017 they say only that the rates are for estimating the cost of public works, and from FY2026 they add that the rates are the basis of the "appropriate labor cost" to be secured in construction contracts under the standard for labor costs that the Central Construction Industry Council recommended in December 2025 under the amended Construction Business Act. H4 describes building cleaners as an occupation with no MLIT rate. They have none in the design labor rates, but MLIT also sets building maintenance labor rates (建築保全業務労務単価) for cleaners and facility guards in maintenance contracts at government buildings, by region.

**1 November 2026, after an independent check of every number in the paper (no change to any test of H1 to H4).** The data are updated to japan-guard-price-panel v1.2.1 (https://doi.org/10.5281/zenodo.23856290), which corrects two national weighted averages of the minimum wage that had been truncated instead of rounded: FY2017 (848 yen, not 847) and FY2026 (1,177, not 1,176). Only the national series uses them, and the change moves Japan's ratio of guards' pay to eight hours at the minimum wage in 2018 from 1.551 to 1.550; no estimate changes. The intervals in X3 now use *t*(45) critical values, as every other interval does, instead of normal ones (guards: −2.55 to 1.13, not −2.50 to 1.08; building cleaners: −1.39 to 0.80, not −1.36 to 0.77). Figure 2 now labels the seven prefectures with the most guards, with leader lines, because two of its labels sat next to other prefectures' circles.

**1 November 2026, after an independent check of the sources (no change to any test).** Two descriptions above are made more precise. The correction of Section 1: the FY2012 release says that the rates do not bind subcontract labor rates or wages, and from FY2013 to FY2016 the releases say the same of the rates plus the employer's costs; from FY2019 the releases also say that leaving the employer's costs out of a subcontract price, or discounting them from it, is an unfair practice; and the design rates have been the basis of the "appropriate labor cost" since December 2025, when the standard for labor costs was recommended and the amended act came fully into force, not only from FY2026. The definitions in Section 3: *H* (所定内実労働時間数) counts hours actually worked within scheduled hours, so *W* is pay per 8 scheduled hours worked and rises when more paid leave is taken; and excluding position holders in every year keeps their treatment the same, but MHLW's occupation of security guards was itself redefined in 2020, taking in gatekeepers (守衛), the reason for check C6.
