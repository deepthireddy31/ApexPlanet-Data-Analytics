# Core KPIs

Based on the Task 2 findings: revenue depends about equally on quantity and unit price, age has no effect, and a few large orders lift the average. The KPIs below track those drivers.

| # | KPI | Formula | Business rationale | Current value |
|---|-----|---------|--------------------|---------------|
| 1 | Total Revenue | SUM(Total_Sales) | Headline measure of business performance; every other KPI is read against it | 139.4M |
| 2 | Average Order Value (AOV) | Total Revenue / Number of Orders | Shows how much each order is worth. Raising AOV (bundles, upsell) grows revenue without needing more orders | 139,399 |
| 3 | Units per Order | SUM(Quantity) / Number of Orders | Measures basket size. Quantity is one of the two drivers of revenue (correlation 0.65) | 5.44 |
| 4 | Month-on-Month (MoM) Revenue Growth % | (Revenue this month - Revenue last month) / Revenue last month x 100 | Catches seasonality and dips early (Aug-Sep 2025 fell sharply, Oct 2025 recovered +36.2%) | -2.6% (Dec 2025) |
| 5 | Premium Bulk Revenue Share % | Revenue from Premium Bulk orders / Total Revenue x 100 | Shows how dependent the business is on its best segment (high quantity and high unit price) | 52.5% |

Notes
- Number of Orders = COUNT of Order_ID (1,000).
- January 2026 has only one day of data, so it is counted in the totals but not used for MoM growth.
- Repeat Customer Rate was proposed in Task 2 but is not used here, because Customer_ID is not consistent with other customer fields (Task 1 quality report).
