# Exploratory Data Analysis Report

ApexPlanet Data Analytics Internship - Task 2
Dataset: cleaned sales data from Task 1 (1,000 orders, 1 Jan 2025 - 1 Jan 2026)

All figures come from `task2.py`. Currency is not stated in the file, so values are shown as plain numbers. Charts are in `task2_output/charts/`.

## 1. Quick overview

| Measure | Value |
|---|---|
| Orders | 1,000 |
| Total revenue | 139,399,440 (139.4M) |
| Average order value (mean) | 139,399 |
| Median order value | 108,594 |
| Units sold | 5,435 |
| Products / categories / cities | 6 / 5 / 8 (plus 13 orders with unknown city) |

## 2. Univariate analysis

### Numerical columns

| Column | Mean | Median | Std | Min | Max | Skewness |
|---|---|---|---|---|---|---|
| Age | 41.3 | 41 | 13.7 | 18 | 65 | 0.04 |
| Quantity | 5.4 | 5 | 2.8 | 1 | 10 | 0.06 |
| Unit_Price | 25,487 | 25,399 | 14,179 | 145.78 | 49,997.53 | -0.03 |
| Total_Sales | 139,399 | 108,594 | 114,100 | 437.34 | 493,677.50 | 0.99 |

What I see (chart `01_histograms_numeric.png`, `02_boxplot_total_sales.png`):
- **Age, Quantity and Unit_Price are close to evenly spread** across their ranges, with mean and median almost the same and skewness near zero. There is no peak age group or favourite quantity.
- **Total_Sales is right-skewed** (skewness 0.99). The mean (139,399) is well above the median (108,594), so a minority of very large orders pull the average up. This is why the 19 high orders flagged in Task 1 appear as dots on the boxplot. It comes from Quantity x Unit_Price: a large quantity combined with a high price gives a large order.
- Total_Sales varies a lot (std 114,100, about 82% of the mean), so averages should always be read together with the median.

### Categorical columns (`03_bar_orders_by_category.png`, `04_bar_revenue_category_product.png`)

- **Category:** Electronics has 354 orders (35.4%) and 36.4% of revenue (50.8M), roughly double any other category. This is because Electronics holds two products (Mobile and Laptop); each of the other categories has one.
- **Product:** revenue is fairly even: Laptop 25.4M, Mobile 25.3M, Book 25.0M, Rice 22.2M, Chair 21.5M, Shoes 19.8M. Shoes is lowest in revenue (19.8M) and in average order value (127,153); Laptop is highest in average order value (149,665).
- **City:** Patna (19.3M), Kolkata (18.9M), Bengaluru (18.8M) and Mumbai (18.8M) lead. Gaya is lowest (14.4M). Bengaluru has the highest average order value (153,882) with fewer orders than Patna or Kolkata.
- **Gender:** 511 male and 489 female orders. Male revenue is 72.5M against 66.9M female; average order value is 141,807 vs 136,883 - a small gap.
- **Age group:** 35-44 has the highest revenue (32.8M) and 18-24 the lowest (21.2M). The 18-24 band covers only 7 ages while the others cover 10, so its lower total is partly just a narrower band (147 orders over 7 ages is about 21 per age, against about 22 per age for 35-44).
- **Time:** Q4 has the most revenue (37.4M) and Q3 the least (30.4M). Day of week is flat: Sunday has the most orders (153) and Tuesday the fewest (126), which is a small difference.

### Trend (`05_line_monthly_revenue.png`)
Monthly revenue moves between 9.2M and 13.1M. March (13.1M) and June (12.9M) are peaks. August (9.4M) and September (9.2M) are the weakest months, followed by a 36.2% jump in October. December has the most orders (98) but a low average order value (125,509). January 2026 is left out of the trend because it has only one day of data (5 orders).

## 3. SQL business questions
Seven questions were answered in SQL (SQLite) with filtering, aggregation, CTEs, window functions and joins across `orders`, `products` and `cities`. Full queries and results: `sql_queries_and_results.md`.

| # | Question | Answer in short |
|---|---|---|
| Q1 | Top 5 products by revenue, last 6 months | Laptop 13.0M, Book 12.7M, Chair 11.6M, Shoes 11.1M, Rice 10.2M |
| Q2 | Monthly revenue and growth | Range 9.2M-13.1M; largest fall Aug 2025 (-19.6%), largest rise Oct 2025 (+36.2%) |
| Q3 | Category performance | Electronics 36.4% of revenue, Education 18.0%, Grocery 15.9%, Furniture 15.4%, Fashion 14.2% |
| Q4 | Top 5 cities | Patna, Kolkata, Bengaluru, Mumbai, Hyderabad |
| Q5 | Revenue by age group and gender | Largest gap is in 25-34: male 16.9M vs female 10.6M (average order value 149,950 vs 108,975) |
| Q6 | Repeat customers | 52 customer IDs have more than one order (most have exactly 2) |
| Q7 | Best product in each city | Kolkata: Mobile, Patna: Book, Mumbai: Laptop, Hyderabad: Book, Bengaluru: Shoes, Delhi: Mobile, Gaya: Rice, Pune: Laptop |

**Worth noting - Mobile:** Mobile was the top product in Jan-Jun 2025 (15.4M) but fell to last place in Jul-Dec 2025 (9.9M), down about 35%, which is why it is missing from the Q1 top 5. No other product dropped like this. The reason cannot be found in this dataset and should be checked with the business (stock, pricing, competition, a seasonal effect).

**Caution on Q5 and Q6:** each age-and-gender group has only about 65-125 orders, so the 25-34 gap could be chance and should be tested before acting on it (Task 4). The repeat-customer result depends on Customer_ID, which Task 1 showed is not consistent with name/age/city, so treat it as indicative only.

## 4. Multivariate analysis

### Correlation (`06_heatmap_correlation.png`)

| | Age | Quantity | Unit_Price | Total_Sales |
|---|---|---|---|---|
| Age | 1.00 | -0.03 | -0.01 | 0.00 |
| Quantity | -0.03 | 1.00 | 0.02 | 0.65 |
| Unit_Price | -0.01 | 0.02 | 1.00 | 0.69 |
| Total_Sales | 0.00 | 0.65 | 0.69 | 1.00 |

- Total_Sales is moderately-to-strongly correlated with both Unit_Price (0.69) and Quantity (0.65). This is expected because Total_Sales = Quantity x Unit_Price. Neither factor alone explains it, and the two are unrelated to each other (0.02), so both drive revenue about equally.
- **Age has no relationship** with Quantity, Unit_Price or Total_Sales (all within +/-0.03). Customer age does not predict how much a customer spends.

### Scatter, pair plot and heatmaps (`07`-`11`)
- The unit price vs total sales scatter shows straight lines, one for each quantity from 1 to 10, because Total_Sales is exactly Quantity x Unit_Price. The age scatter shows no pattern.
- The pair plot confirms the same: no clear separation between categories on any numeric column.
- City x category heatmap: revenue is spread across all combinations without one dominant pairing; Electronics is the top category in all 8 cities, again because it has two products.
- Age group x category heatmap: order counts are fairly even, so no age group has a clearly different product preference.
- Average order value by category is similar (127K-145K); Fashion is lowest and Grocery highest.

## 5. Key insights

1. Revenue is balanced across products, cities and age groups; the business does not depend on a single product or city. Electronics leads only because it has two products.
2. Average order value is pushed up by a small number of large orders, so median should be tracked alongside mean.
3. Mobile revenue fell about 35% from the first half to the second half of 2025, the only clear decline among products.
4. Revenue dipped in Aug-Sep 2025 and recovered strongly in Oct 2025; Q4 was the strongest quarter.
5. Customer age does not influence spending, so age-based targeting is unlikely to help; product, price and quantity matter more.
6. Repeat purchasing looks low (5.5% of customer IDs), but data quality of Customer_ID limits this conclusion.

## 6. Dashboard mock-up and proposed KPIs
See `dashboard_mockup.pptx` (slide 1: layout, slide 2: KPI definitions) and `task2_output/dashboard_mockup.png`. Proposed KPIs: Total Revenue, Total Orders, Average Order Value, Month-on-Month Growth, Revenue Share by Category, Repeat Customer Rate.

## 7. Limitations
- One year of data, with only one day in January 2026.
- No cost, marketing or customer-master data, so profit and marketing-spend analysis was not possible.
- Customer_ID is not consistent with the other customer fields (see Task 1 quality report).
- Unit prices are spread from about 146 to 50,000 for every product; these should be confirmed with the business.
