# Hypothesis Testing Summary

ApexPlanet Data Analytics Internship - Task 4
Data: cleaned sales data (1,000 orders). H1 = Jan-Jun 2025 (499 orders), H2 = Jul 2025 - 1 Jan 2026 (501 orders).
Code: `task4.py`. Full results table: `task4_output/hypothesis_test_results.csv`.

## 1. Business question
In Task 2 I found that Mobile, the top product in the first half of 2025 (15.4M revenue), fell to last place in the second half (9.9M, down about 35%). In Task 2 I also saw a gap between male and female order values in the 25-34 age group and flagged it as "to be tested". This task checks whether these patterns are statistically real or could be random variation.

## 2. Primary hypotheses (Mobile)
| | Null hypothesis (H0) | Alternative (H1) |
|---|---|---|
| T1 | Mobile's share of all orders is the same in H1 and H2 | The share changed |
| T2 | Average Mobile order value is the same in H1 and H2 | The average order value differs |

Why two tests: revenue = number of orders x order value, so a revenue fall can come from fewer orders, smaller orders, or both. Testing both shows which one it is.

## 3. Supporting hypotheses
| | H0 |
|---|---|
| T3 | Product mix (share of orders by product) is the same in H1 and H2 |
| T4 | Male and female order values are equal in the 25-34 age group |
| T5 | Male and female average order values are equal (all ages) |
| T6 | Average order value is the same in Q3 and Q4 |
| T7 | Age group and product category are independent |

## 4. Methods
- **Two proportions (T1):** chi-square test for 2 proportions, with a 95% confidence interval for the difference.
- **Comparing averages (T2, T4, T5, T6):** Welch t-test (does not assume equal variance), with a 95% CI for the difference and Cohen's d. Total_Sales is right-skewed, so I also ran the Mann-Whitney test as a check that does not assume a normal distribution.
- **Independence (T3, T7):** chi-square test of independence, with Cramer's V as the effect size.
- Significance level: 0.05 for a single test. Because I ran 7 tests, a stricter Bonferroni limit of 0.05 / 7 = 0.0071 is also reported.

## 5. Results

| Test | Result | Difference (95% CI) | p-value | Significant at 5%? | After Bonferroni? |
|---|---|---|---|---|---|
| T1 Mobile share of orders | 21.2% (H1) vs 15.6% (H2) | 5.7 points (0.9 to 10.5) | 0.0206 | Yes | No |
| T2 Mobile order value | 145,268 vs 127,400 | 17,868 (-14,475 to 50,210), d = 0.16 | 0.277 | No | No |
| T3 Product mix H1 vs H2 | Cramer's V = 0.08 | - | 0.271 | No | No |
| T4 Male vs female, age 25-34 | 149,950 vs 108,975 | 40,975 (9,821 to 72,129), d = 0.35 | 0.0102 (Mann-Whitney 0.0695) | Yes (t-test only) | No |
| T5 Male vs female, all ages | 141,807 vs 136,883 | 4,924 (-9,232 to 19,080), d = 0.04 | 0.495 | No | No |
| T6 Q4 vs Q3 order value | 144,511 vs 128,163 | 16,349 (-3,570 to 36,267), d = 0.14 | 0.107 (Mann-Whitney 0.0723) | No | No |
| T7 Age group vs category | Cramer's V = 0.05 | - | 0.881 | No | No |

## 6. Interpretation

**Mobile (T1, T2).** Mobile made up 21.2% of orders in H1 (106 of 499) but 15.6% in H2 (78 of 501). A difference this large would happen by chance only about 2% of the time (p = 0.021), and the 95% confidence interval for the drop (0.9 to 10.5 points) does not include zero. The average value of a Mobile order did not change significantly (p = 0.277; the interval includes zero, and the effect is small, d = 0.16).
**Business conclusion:** the Mobile revenue decline is explained by fewer Mobile orders, not smaller orders. Customers who still buy Mobile spend about the same. The business should look at why Mobile orders dropped (stock, pricing, promotion, competition) rather than at order size.

**Product mix overall (T3).** The overall mix of products did not change significantly (p = 0.271). Mobile is the only product with a noticeable shift, and it is not strong enough to change the overall mix.

**Gender (T4, T5).** Across all ages there is no difference in spending (p = 0.495). In the 25-34 group the t-test shows a gap (p = 0.010), but the Mann-Whitney test, which is better suited to skewed data, gives p = 0.070, and the result does not survive the Bonferroni correction. I treat it as a possible pattern to re-check with more data, not a basis for targeting.

**Q4 vs Q3 (T6)** and **age vs category (T7)** show no significant differences.

## 7. Limitations
- **Post-hoc choice:** I picked Mobile after exploring the data (Task 2), which increases the chance of finding something that is only random. T1's p-value (0.021) is above the Bonferroni limit (0.0071), so it is moderate evidence, not proof. The next months of data can confirm it.
- **Multiple tests:** with 7 tests, about one significant result is expected by chance at the 5% level.
- **Observational data:** the tests show that the changes are unlikely to be random, but not why they happened.
- **Skewed data:** Total_Sales is right-skewed, which is why Mann-Whitney was used as a check.
- **Independence assumption:** orders are treated as independent; Customer_ID is unreliable (Task 1), so repeat buyers could not be taken into account.
- One year of data only, and no information about stock, prices or promotions that could explain the Mobile drop.
