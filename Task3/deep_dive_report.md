# Deep-Dive Report: Segmentation Analysis

ApexPlanet Data Analytics Internship - Task 3

## 1. Why segmentation
Of the three suggested deep-dives, segmentation is the one this dataset supports.
- **Cohort analysis** needs customers who come back. Only 52 of 947 Customer_IDs have more than one order (and most have exactly two), and Customer_ID is not consistent with name, age or city (Task 1), so retention and lifetime value would not be reliable.
- **Funnel analysis** needs step-by-step user events (visit, cart, purchase). The data only has completed orders.
- **Segmentation** works with the order-level fields we have. Since every row is one order and Customer_ID is not reliable, the segments below are segments of *orders (buyers)*, not of unique customers.

## 2. Method
Task 2 showed that Total_Sales is driven about equally by Quantity (correlation 0.65) and Unit_Price (0.69), while Age has no effect (0.00). So each order was placed into one of four segments using two rules:
- Quantity: High if above 5 units, otherwise Low
- Unit price: High if above the median (25,398.74), otherwise Low

| Segment | Quantity | Unit price |
|---|---|---|
| Premium Bulk | High | High |
| Volume Buyers | High | Low |
| Premium Selective | Low | High |
| Budget Light | Low | Low |

I also ran K-Means (on Age, Quantity, Unit_Price, standardised) with k = 2 to 6 to check whether natural clusters exist.

## 3. Results

| Segment | Orders | % of orders | Revenue | % of revenue | Avg order value | Units / order | Avg unit price |
|---|---|---|---|---|---|---|---|
| Premium Bulk | 242 | 24.2% | 73.2M | 52.5% | 302,346 | 7.9 | 37,932 |
| Volume Buyers | 239 | 23.9% | 26.1M | 18.7% | 109,272 | 8.0 | 13,625 |
| Premium Selective | 258 | 25.8% | 29.5M | 21.1% | 114,176 | 3.1 | 37,361 |
| Budget Light | 261 | 26.1% | 10.7M | 7.6% | 40,836 | 3.1 | 13,072 |

(Charts: `01_segment_orders_vs_revenue.png`, `02_segment_avg_order_value.png`)

**Findings**
1. **Premium Bulk is the engine of the business.** It is about a quarter of orders (24.2%) but 52.5% of revenue. Its average order (302,346) is about 7.4 times that of Budget Light (40,836).
2. **Budget Light is the weakest segment.** It is the biggest segment by order count (26.1%) but brings only 7.6% of revenue.
3. **Volume Buyers and Premium Selective are worth the same per order (about 109K vs 114K) by different routes.** Volume Buyers buy about 8 units at a low price; Premium Selective buy about 3 units at a high price.
4. **Segments look alike in who buys.** Average age is 40-43 in all four, gender is close to 50/50 (Premium Bulk 45.5% female), and Electronics is the top category in every segment because it contains two products. The age mix shows small differences (Premium Bulk: 68% aged 35+; Volume Buyers: 26% aged 25-34), but with 240-260 orders per segment these are indicative only.
5. **K-Means found no natural clusters.** Silhouette scores are 0.24-0.30 for k = 2 to 6, well below 0.5, the level usually read as clear structure. Quantity, price and age are spread evenly with no groupings, so the rule-based segments are a practical business classification, not clusters discovered in the data (`05_kmeans_silhouette.png`).

## 4. Recommendations
- **Protect Premium Bulk:** it carries over half of revenue. Keep high-price items in stock and consider bulk-purchase offers or account follow-up for these buyers.
- **Move Budget Light up:** bundles or multi-buy offers could lift quantity, since these buyers order only about 3 units at low prices.
- **Encourage Premium Selective to buy more units:** their price level is already high, so quantity is the lever.
- **Track segment mix monthly** in the dashboard; a falling Premium Bulk share would be an early warning (Aug-Sep 2025 revenue dip is a good case to examine by segment, see `04_monthly_revenue_by_segment.png`).

## 5. Limitations
- Segments are of orders, not unique customers (Customer_ID issue from Task 1).
- Cut-offs (quantity 5, median price) are my choice; other cut-offs would change segment sizes but quartile-style rules like these keep the four groups similar in size.
- One year of data and no cost data, so revenue is analysed, not profit.
- The reasons behind the patterns (for example why Premium Bulk buys) cannot be found in this dataset.

## 6. Dashboard
The interactive dashboard (`task3_output/dashboard/index.html`) shows the five KPIs, monthly trend, segment share, category and city revenue and a segment table, with filters for month range, city, category, gender, age group and segment. See `dashboard_build_guide.md` for the Power BI / Looker Studio version.
