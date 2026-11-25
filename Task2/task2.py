"""
Task 2 - Exploratory Data Analysis (EDA) & Business Intelligence
ApexPlanet Data Analytics Internship

What this script does
  1. Descriptive statistics + univariate analysis (histograms, bar charts)
  2. SQL business questions (SQLite) - queries and results are saved
  3. Multivariate analysis (correlation heatmap, scatter plots, pair plot, heatmaps)
  4. Static dashboard mock-up (image) with the KPIs I propose to track
"""
import os
import json
import sqlite3
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")                      # save charts to files, no pop-up windows
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

# ---------------------------------------------------------------
# 0. Paths and settings
# ---------------------------------------------------------------
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "cleaned_sales_data.csv")
OUT_DIR = os.path.join(BASE, "task2_output")
CHART_DIR = os.path.join(OUT_DIR, "charts")
RESULT_DIR = os.path.join(OUT_DIR, "sql_results")

if not os.path.exists(DATA_FILE):
    raise FileNotFoundError("Cleaned data not found. Run task1.py first so that\n  "
                            + DATA_FILE + "\nexists.")
for folder in (OUT_DIR, CHART_DIR, RESULT_DIR):
    os.makedirs(folder, exist_ok=True)

sns.set_theme(style="whitegrid", font_scale=0.95)
BLUE, ORANGE, GREY = "#2F5D8C", "#E08A2E", "#8A8F98"

def millions(x, pos=None):
    if x == 0:
        return "0"
    return f"{x / 1e6:.1f}M" if abs(x) >= 1e6 else f"{x / 1e3:.0f}K"

def save_fig(name):
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, name), dpi=150, bbox_inches="tight")
    plt.close()

def to_markdown(table):
    """small markdown table writer (so I don't need the tabulate package)"""
    cols = list(table.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, row in table.iterrows():
        lines.append("| " + " | ".join(f"{v:,.2f}" if isinstance(v, float) else str(v) for v in row) + " |")
    return "\n".join(lines)

# ---------------------------------------------------------------
# 1. Load the cleaned data from Task 1
# ---------------------------------------------------------------
df = pd.read_csv(DATA_FILE, parse_dates=["Order_Date"])
print("Loaded", df.shape[0], "rows and", df.shape[1], "columns")

num_cols = ["Age", "Quantity", "Unit_Price", "Total_Sales"]
total_revenue = df["Total_Sales"].sum()

# ---------------------------------------------------------------
# 2. Descriptive statistics & univariate analysis
# ---------------------------------------------------------------
print("\n===== NUMERICAL SUMMARY =====")
desc = df[num_cols].describe().T
desc["median"] = df[num_cols].median()
desc["skewness"] = df[num_cols].skew()
desc["cv_%"] = desc["std"] / desc["mean"] * 100       # variation relative to the mean
desc = desc[["count", "mean", "median", "std", "min", "25%", "75%", "max", "skewness", "cv_%"]].round(2)
print(desc.to_string())
desc.to_csv(os.path.join(OUT_DIR, "numerical_summary.csv"))

print("\n===== CATEGORICAL SUMMARY =====")
cat_cols = ["Gender", "City", "Product", "Category", "Age_Group", "Order_Quarter", "Order_Day_Name"]
cat_tables = []
for col in cat_cols:
    t = df[col].value_counts().rename("orders").to_frame()
    t["share_%"] = (t["orders"] / len(df) * 100).round(1)
    t["revenue"] = df.groupby(col)["Total_Sales"].sum().round(2)
    t.insert(0, "column", col)
    t.index.name = "value"
    cat_tables.append(t.reset_index())
    print(f"\n{col}\n", t.drop(columns="column").to_string())
pd.concat(cat_tables).to_csv(os.path.join(OUT_DIR, "categorical_summary.csv"), index=False)

# 2a. histograms of the numeric columns
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
for ax, col in zip(axes.ravel(), num_cols):
    sns.histplot(df[col], bins=25, color=BLUE, edgecolor="white", ax=ax)
    ax.axvline(df[col].mean(), color=ORANGE, linestyle="--", label=f"Mean {df[col].mean():,.0f}")
    ax.axvline(df[col].median(), color="green", linestyle=":", label=f"Median {df[col].median():,.0f}")
    ax.set_title(f"Distribution of {col}")
    ax.legend(fontsize=8)
save_fig("01_histograms_numeric.png")

# 2b. boxplot of Total_Sales (shows the outliers flagged in Task 1)
plt.figure(figsize=(9, 3))
sns.boxplot(x=df["Total_Sales"], color=BLUE, flierprops={"markerfacecolor": ORANGE})
plt.title("Total_Sales - boxplot (dots = outliers by the 1.5 x IQR rule)")
plt.gca().xaxis.set_major_formatter(mtick.FuncFormatter(millions))
save_fig("02_boxplot_total_sales.png")

# 2c. bar charts for categorical columns (number of orders)
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
for ax, col in zip(axes.ravel(), ["Category", "Product", "City", "Gender", "Age_Group", "Order_Day_Name"]):
    counts = df[col].value_counts()
    if col == "Age_Group":
        counts = counts.sort_index()
    elif col == "Order_Day_Name":
        counts = counts.reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    sns.barplot(x=counts.values, y=counts.index, color=BLUE, ax=ax)
    for i, v in enumerate(counts.values):
        ax.text(v + 1, i, str(v), va="center", fontsize=8)
    ax.set_title(f"Orders by {col}")
    ax.set_xlabel("Number of orders")
    ax.set_ylabel("")
save_fig("03_bar_orders_by_category.png")

# 2d. revenue by category and product
fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
for ax, col in zip(axes, ["Category", "Product"]):
    rev = df.groupby(col)["Total_Sales"].sum().sort_values()
    ax.barh(rev.index, rev.values, color=BLUE)
    for i, v in enumerate(rev.values):
        ax.text(v, i, f" {v / 1e6:.1f}M ({v / total_revenue * 100:.0f}%)", va="center", fontsize=8)
    ax.set_title(f"Revenue by {col}")
    ax.xaxis.set_major_formatter(mtick.FuncFormatter(millions))
    ax.set_xlim(0, rev.max() * 1.25)
save_fig("04_bar_revenue_category_product.png")

# 2e. monthly trend (Jan 2026 only has 1 day of data so it is left out of the chart)
monthly = df.groupby(df["Order_Date"].dt.to_period("M")).agg(revenue=("Total_Sales", "sum"),
                                                              orders=("Order_ID", "count"))
monthly = monthly[monthly.index < "2026-01"]
fig, ax = plt.subplots(figsize=(11, 4.5))
ax.plot(monthly.index.astype(str), monthly["revenue"], marker="o", color=BLUE)
ax.set_title("Monthly revenue, 2025")
ax.set_ylim(0, monthly["revenue"].max() * 1.15)
ax.yaxis.set_major_formatter(mtick.FuncFormatter(millions))
ax.set_ylabel("Revenue")
plt.xticks(rotation=45)
save_fig("05_line_monthly_revenue.png")

# ---------------------------------------------------------------
# 3. SQL for business questions (SQLite)
# ---------------------------------------------------------------
# Task 2 asks for multi-table joins, but the data is one flat file, so I split it
# into three tables like a small database: orders, products and cities.
products = df[["Product", "Category"]].drop_duplicates().sort_values("Product").reset_index(drop=True)
products.insert(0, "product_id", products.index + 1)
products.columns = ["product_id", "product_name", "category"]

cities = pd.DataFrame({"city_name": sorted(df["City"].unique())})
cities.insert(0, "city_id", cities.index + 1)

orders = (df.merge(products, left_on="Product", right_on="product_name")
            .merge(cities, left_on="City", right_on="city_name"))
orders = pd.DataFrame({
    "order_id": orders["Order_ID"],
    "order_date": orders["Order_Date"].dt.strftime("%Y-%m-%d"),
    "customer_id": orders["Customer_ID"],
    "age": orders["Age"],
    "age_group": orders["Age_Group"],
    "gender": orders["Gender"],
    "city_id": orders["city_id"],
    "product_id": orders["product_id"],
    "quantity": orders["Quantity"],
    "unit_price": orders["Unit_Price"],
    "total_sales": orders["Total_Sales"],
    "is_weekend": orders["Is_Weekend"].astype(int),
})

conn = sqlite3.connect(os.path.join(OUT_DIR, "sales.db"))
orders.to_sql("orders", conn, if_exists="replace", index=False)
products.to_sql("products", conn, if_exists="replace", index=False)
cities.to_sql("cities", conn, if_exists="replace", index=False)

queries = {}

queries["Q1. Top 5 products by revenue in the last 6 months"] = """
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
"""

queries["Q2. Monthly revenue, orders and month-on-month growth"] = """
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
"""

queries["Q3. Category performance and share of total revenue"] = """
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
"""

queries["Q4. Top 5 cities by revenue (unknown city excluded)"] = """
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
"""

queries["Q5. Revenue by age group and gender"] = """
SELECT age_group,
       gender,
       COUNT(*)                       AS orders,
       ROUND(SUM(total_sales), 2)     AS revenue,
       ROUND(AVG(total_sales), 2)     AS avg_order_value
FROM orders
GROUP BY age_group, gender
ORDER BY age_group, gender;
"""

queries["Q6. Repeat customers - top 10 by total spend"] = """
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
"""

queries["Q7. Best-selling product (by revenue) in each city"] = """
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
"""

sql_file = ["-- ApexPlanet Data Analytics Internship - Task 2: business questions",
            "-- Tables: orders(order_id, order_date, customer_id, age, age_group, gender, city_id,",
            "--         product_id, quantity, unit_price, total_sales, is_weekend)",
            "--         products(product_id, product_name, category)   cities(city_id, city_name)", ""]
md_file = ["# SQL business questions - queries and results", "",
           "Database: SQLite (`task2_output/sales.db`), tables `orders`, `products`, `cities`.", ""]
sql_results = {}

for title, q in queries.items():
    result = pd.read_sql_query(q, conn)
    sql_results[title] = result
    print(f"\n===== {title} =====")
    print(result.to_string(index=False))
    short = title.split(".")[0]
    result.to_csv(os.path.join(RESULT_DIR, f"{short}.csv"), index=False)
    sql_file += [f"-- {title}", q.strip(), ""]
    md_file += [f"## {title}", "", "```sql", q.strip(), "```", "", to_markdown(result), ""]

with open(os.path.join(OUT_DIR, "business_queries.sql"), "w", encoding="utf-8") as f:
    f.write("\n".join(sql_file))
with open(os.path.join(OUT_DIR, "sql_queries_and_results.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md_file))
conn.close()

# ---------------------------------------------------------------
# 4. Multivariate analysis & correlation
# ---------------------------------------------------------------
print("\n===== CORRELATION MATRIX (Pearson) =====")
corr = df[num_cols].corr()
print(corr.round(3).to_string())
corr.round(3).to_csv(os.path.join(OUT_DIR, "correlation_matrix.csv"))

# 4a. correlation heatmap
plt.figure(figsize=(6.5, 5))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1, linewidths=0.5)
plt.title("Correlation between numeric columns")
save_fig("06_heatmap_correlation.png")

# 4b. scatter plots
fig, axes = plt.subplots(1, 3, figsize=(17, 5))
sns.scatterplot(data=df, x="Unit_Price", y="Total_Sales", hue="Category", alpha=0.6, s=25, ax=axes[0])
axes[0].set_title("Unit price vs Total sales")
sns.stripplot(data=df, x="Quantity", y="Total_Sales", color=BLUE, alpha=0.4, size=3, ax=axes[1])
axes[1].set_title("Quantity vs Total sales")
sns.scatterplot(data=df, x="Age", y="Total_Sales", color=GREY, alpha=0.5, s=25, ax=axes[2])
axes[2].set_title("Age vs Total sales")
for ax in axes:
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(millions))
save_fig("07_scatter_plots.png")

# 4c. pair plot
pair = sns.pairplot(df[num_cols + ["Category"]], hue="Category", corner=True,
                    plot_kws={"alpha": 0.5, "s": 15}, height=2.2)
pair.fig.suptitle("Pair plot of numeric columns by category", y=1.02)
pair.savefig(os.path.join(CHART_DIR, "08_pairplot.png"), dpi=120, bbox_inches="tight")
plt.close("all")

# 4d. revenue heatmap: city x category
city_cat = df[df["City"] != "Unknown"].pivot_table(index="City", columns="Category",
                                                   values="Total_Sales", aggfunc="sum") / 1e6
plt.figure(figsize=(9, 6))
sns.heatmap(city_cat, annot=True, fmt=".1f", cmap="Blues", linewidths=0.5,
            cbar_kws={"label": "Revenue (millions)"})
plt.title("Revenue by city and category (millions)")
save_fig("09_heatmap_city_category.png")

# 4e. age group vs product category (number of orders)
age_cat = pd.crosstab(df["Age_Group"], df["Category"])
plt.figure(figsize=(8, 5))
sns.heatmap(age_cat, annot=True, fmt="d", cmap="Oranges", linewidths=0.5)
plt.title("Number of orders: age group vs category")
save_fig("10_heatmap_age_category.png")

# 4f. Total_Sales by category
plt.figure(figsize=(9, 5))
sns.boxplot(data=df, x="Category", y="Total_Sales", color=BLUE)
plt.gca().yaxis.set_major_formatter(mtick.FuncFormatter(millions))
plt.title("Total_Sales by category")
save_fig("11_boxplot_sales_by_category.png")

print("\nAverage order value by category:")
print(df.groupby("Category")["Total_Sales"].mean().round(0).sort_values(ascending=False).to_string())
print("\nAverage order value by gender:")
print(df.groupby("Gender")["Total_Sales"].mean().round(0).to_string())

# ---------------------------------------------------------------
# 5. Static dashboard mock-up
# ---------------------------------------------------------------
orders_n = len(df)
aov = df["Total_Sales"].mean()
units = int(df["Quantity"].sum())
cat_rev = df.groupby("Category")["Total_Sales"].sum().sort_values(ascending=False)
city_rev = df[df["City"] != "Unknown"].groupby("City")["Total_Sales"].sum().sort_values(ascending=False)
age_rev = df.groupby("Age_Group")["Total_Sales"].sum().sort_index()
repeat_pct = (df["Customer_ID"].value_counts() > 1).mean() * 100

kpis = [(f"{total_revenue / 1e6:.1f}M", "Total Revenue"),
        (f"{orders_n:,}", "Total Orders"),
        (f"{aov:,.0f}", "Avg Order Value"),
        (f"{units:,}", "Units Sold"),
        (cat_rev.index[0], f"Top Category ({cat_rev.iloc[0] / total_revenue * 100:.0f}% of revenue)"),
        (f"{repeat_pct:.1f}%", "Customer IDs with 2+ orders")]

fig = plt.figure(figsize=(16, 10), facecolor="#F4F6F9")
gs = fig.add_gridspec(3, 6, height_ratios=[0.7, 2.6, 2.6], hspace=0.5, wspace=0.7,
                      top=0.87, bottom=0.08, left=0.05, right=0.97)
fig.text(0.05, 0.955, "Sales Performance Dashboard  (static mock-up)", fontsize=21,
         fontweight="bold", color="#1F2D3D")
fig.text(0.05, 0.923, "Period: 1 Jan 2025 - 1 Jan 2026   |   Source: cleaned_sales_data.csv   |   "
         "Proposed filters: Date, City, Category, Gender, Age group", fontsize=10.5, color=GREY)

for i, (value, label) in enumerate(kpis):
    ax = fig.add_subplot(gs[0, i])
    ax.set_facecolor("white")
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_edgecolor("#D5DBE3")
    ax.text(0.5, 0.65, value, ha="center", va="center", fontsize=18, fontweight="bold", color=BLUE)
    ax.text(0.5, 0.2, label, ha="center", va="center", fontsize=8.5, color=GREY)

ax1 = fig.add_subplot(gs[1, 0:3])
ax1.plot(monthly.index.astype(str), monthly["revenue"], marker="o", color=BLUE)
ax1.set_title("Monthly revenue (2025)", loc="left", fontweight="bold")
ax1.set_ylim(0, monthly["revenue"].max() * 1.15)
ax1.yaxis.set_major_formatter(mtick.FuncFormatter(millions))
ax1.tick_params(axis="x", rotation=45)

ax2 = fig.add_subplot(gs[1, 3:6])
ax2.barh(cat_rev.index[::-1], cat_rev.values[::-1], color=BLUE)
ax2.set_title("Revenue by category", loc="left", fontweight="bold")
ax2.xaxis.set_major_formatter(mtick.FuncFormatter(millions))

ax3 = fig.add_subplot(gs[2, 0:3])
top_cities = city_rev.head(8)
ax3.bar(top_cities.index, top_cities.values, color=BLUE)
ax3.set_title("Revenue by city", loc="left", fontweight="bold")
ax3.yaxis.set_major_formatter(mtick.FuncFormatter(millions))
ax3.tick_params(axis="x", rotation=30)

ax4 = fig.add_subplot(gs[2, 3:6])
ax4.bar(age_rev.index, age_rev.values, color=ORANGE)
ax4.set_title("Revenue by age group", loc="left", fontweight="bold")
ax4.yaxis.set_major_formatter(mtick.FuncFormatter(millions))

fig.savefig(os.path.join(OUT_DIR, "dashboard_mockup.png"), dpi=150, facecolor=fig.get_facecolor())
plt.close()

# numbers saved for the slides / report
key_numbers = {
    "total_revenue": round(total_revenue, 2), "orders": orders_n, "aov": round(aov, 2), "units": units,
    "repeat_customer_pct": round(repeat_pct, 1),
    "monthly": {str(k): round(v, 2) for k, v in monthly["revenue"].items()},
    "category": {k: round(v, 2) for k, v in cat_rev.items()},
    "city": {k: round(v, 2) for k, v in city_rev.items()},
    "age_group": {k: round(v, 2) for k, v in age_rev.items()},
}
with open(os.path.join(OUT_DIR, "key_numbers.json"), "w") as f:
    json.dump(key_numbers, f, indent=2)

print("\nDone. Everything is saved in:", OUT_DIR)
