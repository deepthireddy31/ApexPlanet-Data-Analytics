# SQL business questions - queries and results

Database: SQLite (`task2_output/sales.db`), tables `orders`, `products`, `cities`.

## Q1. Top 5 products by revenue in the last 6 months

```sql
SELECT p.product_name,
       p.category,
       COUNT(*)                         AS orders,
       SUM(o.quantity)                  AS units_sold,
       ROUND(SUM(o.total_sales), 2)     AS revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
WHERE o.order_date >= DATE((SELECT MAX(order_date) FROM orders), '-6 months')
GROUP BY p.product_name, p.category
ORDER BY revenue DESC
LIMIT 5;
```

| product_name | category | orders | units_sold | revenue |
|---|---|---|---|---|
| Laptop | Electronics | 88 | 501 | 13,009,494.74 |
| Book | Education | 92 | 542 | 12,739,832.53 |
| Chair | Furniture | 87 | 467 | 11,560,952.45 |
| Shoes | Fashion | 81 | 453 | 11,149,392.03 |
| Rice | Grocery | 75 | 394 | 10,215,563.97 |

## Q2. Monthly revenue, orders and month-on-month growth

```sql
WITH monthly AS (
    SELECT STRFTIME('%Y-%m', order_date) AS month,
           COUNT(*)                      AS orders,
           ROUND(SUM(total_sales), 2)    AS revenue,
           ROUND(AVG(total_sales), 2)    AS avg_order_value
    FROM orders
    WHERE order_date < '2026-01-01'      -- Jan 2026 has only 1 day of data, so it is left out
    GROUP BY STRFTIME('%Y-%m', order_date)
)
SELECT month, orders, revenue, avg_order_value,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
             / LAG(revenue) OVER (ORDER BY month), 1) AS mom_growth_pct
FROM monthly
ORDER BY month;
```

| month | orders | revenue | avg_order_value | mom_growth_pct |
|---|---|---|---|---|
| 2025-01 | 76 | 10,096,190.73 | 132,844.61 | nan |
| 2025-02 | 86 | 11,511,181.46 | 133,850.95 | 14.00 |
| 2025-03 | 89 | 13,059,899.94 | 146,740.45 | 13.50 |
| 2025-04 | 80 | 12,222,700.17 | 152,783.75 | -6.40 |
| 2025-05 | 85 | 10,984,689.25 | 129,231.64 | -10.10 |
| 2025-06 | 83 | 12,912,332.64 | 155,570.27 | 17.50 |
| 2025-07 | 83 | 11,746,226.80 | 141,520.80 | -9.00 |
| 2025-08 | 75 | 9,448,471.22 | 125,979.62 | -19.60 |
| 2025-09 | 79 | 9,179,896.29 | 116,201.22 | -2.80 |
| 2025-10 | 84 | 12,500,936.50 | 148,820.67 | 36.20 |
| 2025-11 | 77 | 12,627,620.22 | 163,995.07 | 1.00 |
| 2025-12 | 98 | 12,299,904.44 | 125,509.23 | -2.60 |

## Q3. Category performance and share of total revenue

```sql
SELECT p.category,
       COUNT(*)                                                   AS orders,
       SUM(o.quantity)                                            AS units_sold,
       ROUND(SUM(o.total_sales), 2)                               AS revenue,
       ROUND(AVG(o.total_sales), 2)                               AS avg_order_value,
       ROUND(100.0 * SUM(o.total_sales)
             / (SELECT SUM(total_sales) FROM orders), 1)          AS revenue_share_pct
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY revenue DESC;
```

| category | orders | units_sold | revenue | avg_order_value | revenue_share_pct |
|---|---|---|---|---|---|
| Electronics | 354 | 1978 | 50,778,581.70 | 143,442.32 | 36.40 |
| Education | 178 | 977 | 25,031,689.40 | 140,627.47 | 18.00 |
| Grocery | 153 | 826 | 22,231,711.28 | 145,305.30 | 15.90 |
| Furniture | 159 | 855 | 21,521,561.48 | 135,355.73 | 15.40 |
| Fashion | 156 | 799 | 19,835,895.79 | 127,153.18 | 14.20 |

## Q4. Top 5 cities by revenue (unknown city excluded)

```sql
SELECT c.city_name,
       COUNT(*)                       AS orders,
       ROUND(SUM(o.total_sales), 2)   AS revenue,
       ROUND(AVG(o.total_sales), 2)   AS avg_order_value
FROM orders o
JOIN cities c ON o.city_id = c.city_id
WHERE c.city_name <> 'Unknown'
GROUP BY c.city_name
ORDER BY revenue DESC
LIMIT 5;
```

| city_name | orders | revenue | avg_order_value |
|---|---|---|---|
| Patna | 135 | 19,285,966.89 | 142,859.01 |
| Kolkata | 133 | 18,884,349.57 | 141,987.59 |
| Bengaluru | 122 | 18,773,574.32 | 153,881.76 |
| Mumbai | 131 | 18,757,050.17 | 143,183.59 |
| Hyderabad | 125 | 17,166,766.87 | 137,334.13 |

## Q5. Revenue by age group and gender

```sql
SELECT age_group,
       gender,
       COUNT(*)                       AS orders,
       ROUND(SUM(total_sales), 2)     AS revenue,
       ROUND(AVG(total_sales), 2)     AS avg_order_value
FROM orders
GROUP BY age_group, gender
ORDER BY age_group, gender;
```

| age_group | gender | orders | revenue | avg_order_value |
|---|---|---|---|---|
| 18-24 | Female | 65 | 10,674,345.02 | 164,220.69 |
| 18-24 | Male | 82 | 10,551,139.10 | 128,672.43 |
| 25-34 | Female | 97 | 10,570,552.13 | 108,974.76 |
| 25-34 | Male | 113 | 16,944,315.31 | 149,949.69 |
| 35-44 | Female | 124 | 17,130,053.48 | 138,145.59 |
| 35-44 | Male | 101 | 15,670,659.78 | 155,155.05 |
| 45-54 | Female | 87 | 12,399,196.96 | 142,519.51 |
| 45-54 | Male | 108 | 14,924,889.26 | 138,193.42 |
| 55-65 | Female | 116 | 16,161,741.43 | 139,325.36 |
| 55-65 | Male | 107 | 14,372,547.18 | 134,322.87 |

## Q6. Repeat customers - top 10 by total spend

```sql
SELECT customer_id,
       COUNT(*)                       AS orders,
       ROUND(SUM(total_sales), 2)     AS total_spent,
       MIN(order_date)                AS first_order,
       MAX(order_date)                AS last_order
FROM orders
GROUP BY customer_id
HAVING COUNT(*) > 1
ORDER BY total_spent DESC
LIMIT 10;
```

| customer_id | orders | total_spent | first_order | last_order |
|---|---|---|---|---|
| CUST9510 | 2 | 867,333.24 | 2025-03-17 | 2025-05-10 |
| CUST6845 | 2 | 769,479.75 | 2025-09-04 | 2026-01-01 |
| CUST6532 | 2 | 610,981.74 | 2025-03-16 | 2025-08-22 |
| CUST6082 | 2 | 548,416.39 | 2025-05-19 | 2025-10-24 |
| CUST3689 | 2 | 542,484.08 | 2025-04-16 | 2025-06-07 |
| CUST3730 | 2 | 538,633.97 | 2025-05-19 | 2025-07-18 |
| CUST4706 | 2 | 528,036.44 | 2025-10-13 | 2026-01-01 |
| CUST9693 | 2 | 511,421.86 | 2025-03-27 | 2025-04-12 |
| CUST7374 | 2 | 511,309.40 | 2025-01-10 | 2025-02-23 |
| CUST9089 | 2 | 469,247.10 | 2025-03-02 | 2025-12-16 |

## Q7. Best-selling product (by revenue) in each city

```sql
WITH city_product AS (
    SELECT c.city_name,
           p.product_name,
           COUNT(*)                       AS orders,
           ROUND(SUM(o.total_sales), 2)   AS revenue
    FROM orders o
    JOIN cities   c ON o.city_id    = c.city_id
    JOIN products p ON o.product_id = p.product_id
    WHERE c.city_name <> 'Unknown'
    GROUP BY c.city_name, p.product_name
),
ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY city_name ORDER BY revenue DESC) AS rnk
    FROM city_product
)
SELECT city_name, product_name AS top_product, orders, revenue
FROM ranked
WHERE rnk = 1
ORDER BY revenue DESC;
```

| city_name | top_product | orders | revenue |
|---|---|---|---|
| Kolkata | Mobile | 35 | 4,921,494.03 |
| Patna | Book | 26 | 4,567,627.61 |
| Mumbai | Laptop | 25 | 4,349,872.27 |
| Hyderabad | Book | 34 | 4,045,423.51 |
| Bengaluru | Shoes | 27 | 4,042,713.46 |
| Delhi | Mobile | 27 | 3,984,503.40 |
| Gaya | Rice | 24 | 3,232,818.98 |
| Pune | Laptop | 19 | 3,191,860.47 |
