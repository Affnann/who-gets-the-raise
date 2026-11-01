# Analyses added after the main results were seen

Output of `code/04_extra_checks.py`. Not tests of the plan's hypotheses.

## X1. Wild cluster bootstrap (restricted, Rademacher, 9,999 draws)

| Model | Term | H0 | Side | Estimate | t | p, t(46) | p, wild bootstrap |
|---|---|---|---|---|---|---|---|
| H1 | trend | 0 | lt | -0.0399 | -16.168 | 0.0000 | 0.0000 |
| H2 | lnR | 1 | lt | -0.1034 | -2.758 | 0.0042 | 0.0116 |
| H2 | lnR | 0 | two | -0.1034 | -0.259 | 0.7972 | 0.8069 |
| H3 | lnM | 0 | gt | 0.9776 | 1.993 | 0.0261 | 0.0153 |
| H4 | lnR_G | 0 | gt | -0.1602 | -0.359 | 0.6393 | 0.6429 |

## X2. Pay per hour worked, including overtime pay

| Model | Term | H0 | Estimate | SE | 95% interval | p two-sided | p one-sided |
|---|---|---|---|---|---|---|---|
| H1 | trend | 0 | -0.0389 | 0.0024 | -0.044 to -0.034 | 0.0000 | 0.0000 |
| H2 | lnR | 1 | -0.1438 | 0.3910 | -0.931 to 0.643 | 0.0053 | 0.0027 |
| H2 | lnR | 0 | -0.1438 | 0.3910 | -0.931 to 0.643 | 0.7147 |  |
| H3 | lnR | 0 | -0.1687 | 0.3917 | -0.957 to 0.620 | 0.6687 |  |
| H3 | lnM | 0 | 0.8536 | 0.5872 | -0.328 to 2.036 | 0.1528 | 0.0764 |

- National growth of this pay measure, 2012-2019: 17.0%
- National growth of this pay measure, 2020-2025: 6.0%
- National growth of this pay measure, 2012-2025: 31.5%

## X3. Long differences, 2012-2025 (one observation per prefecture, HC1)

| Occupation | Slope on Δln R | SE | 95% interval | p | SD of Δln R | SD of Δln W |
|---|---|---|---|---|---|---|
| long difference, guards | -0.713 | 0.914 | -2.504 to 1.079 | 0.4355 | 0.0310 | 0.1461 |
| long difference, cleaners | -0.295 | 0.544 | -1.363 to 0.772 | 0.5875 | 0.0310 | 0.1435 |

## X4. Weighted correlation across prefectures in levels

| Year | ln R with guards' ln W | ln R with cleaners' ln W |
|---|---|---|
| 2012 | 0.433 | 0.689 |
| 2013 | 0.718 | 0.656 |
| 2014 | 0.606 | 0.783 |
| 2015 | 0.435 | 0.623 |
| 2016 | 0.570 | 0.798 |
| 2017 | 0.524 | 0.688 |
| 2018 | 0.573 | 0.754 |
| 2019 | 0.600 | 0.554 |
| 2020 | 0.615 | 0.522 |
| 2021 | 0.753 | 0.672 |
| 2022 | 0.536 | 0.620 |
| 2023 | 0.588 | 0.489 |
| 2024 | 0.276 | 0.776 |
| 2025 | 0.291 | 0.643 |
