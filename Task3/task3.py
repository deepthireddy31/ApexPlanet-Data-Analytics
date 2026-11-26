"""
Task 3 - Deep-Dive Analysis & Interactive Dashboarding
ApexPlanet Data Analytics Internship

Deep-dive chosen: SEGMENTATION ANALYSIS (business rules, checked with K-Means)

What this script does
  1. Calculates the 5 core KPIs
  2. Segments the orders with business rules (quantity x unit price) and profiles each segment
  3. Checks with K-Means whether the data has natural clusters (silhouette score)
  4. Exports a dashboard-ready file for Power BI / Looker Studio / Tableau
  5. Builds the interactive HTML dashboard (dashboard_template.html -> index.html)

Setup:   pip install pandas matplotlib seaborn scikit-learn
Files:   put task3.py and dashboard_template.html next to task1.py / task2.py
Run:     python task3.py
"""
import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "cleaned_sales_data.csv")
TEMPLATE = os.path.join(BASE, "dashboard_template.html")
OUT = os.path.join(BASE, "task3_output")
CHARTS = os.path.join(OUT, "charts")
DASH = os.path.join(OUT, "dashboard")

if not os.path.exists(DATA_FILE):
    raise FileNotFoundError("Run task1.py first, cleaned data not found at:\n  " + DATA_FILE)
for f in (OUT, CHARTS, DASH):
    os.makedirs(f, exist_ok=True)

sns.set_theme(style="whitegrid", font_scale=0.95)
BLUE, ORANGE = "#2F5D8C", "#E08A2E"
SEG_ORDER = ["Premium Bulk", "Volume Buyers", "Premium Selective", "Budget Light"]
SEG_COLORS = {"Premium Bulk": "#2F5D8C", "Volume Buyers": "#5B8DB8",
              "Premium Selective": "#E08A2E", "Budget Light": "#8A8F98"}

def millions(x, pos=None):
    if x == 0:
        return "0"
    return f"{x / 1e6:.1f}M" if abs(x) >= 1e6 else f"{x / 1e3:.0f}K"

def save_fig(name):
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS, name), dpi=150, bbox_inches="tight")
    plt.close()

df = pd.read_csv(DATA_FILE, parse_dates=["Order_Date"])
print("Loaded", len(df), "orders")

# ---------------------------------------------------------------
# 1. Core KPIs
# ---------------------------------------------------------------
# Each KPI is defined in docs/KPI_definitions.md. Here is how they are calculated.
total_revenue = df["Total_Sales"].sum()
orders = len(df)
aov = total_revenue / orders
units_per_order = df["Quantity"].sum() / orders

# Jan 2026 has only one day of data, so it is left out of the growth calculation
monthly = (df[df["Order_Date"] < "2026-01-01"]
           .groupby(df["Order_Date"].dt.to_period("M"))["Total_Sales"].sum())
mom_growth = monthly.pct_change() * 100
latest_month = str(monthly.index[-1])
latest_growth = mom_growth.iloc[-1]

# ---------------------------------------------------------------
# 2. Segmentation with business rules
# ---------------------------------------------------------------
# Task 2 showed that revenue depends about equally on Quantity and Unit_Price
# (correlations 0.65 and 0.69) and that Age does not matter. So I split every
# order by those two drivers: quantity above 5 = High, unit price above the
# median = High.
qty_cut = 5
price_cut = df["Unit_Price"].median()
print(f"\nCut-offs -> Quantity > {qty_cut}, Unit_Price > {price_cut:,.2f} (median)")

def segment(row):
    high_q = row["Quantity"] > qty_cut
    high_p = row["Unit_Price"] > price_cut
    if high_q and high_p:
        return "Premium Bulk"
    if high_q:
        return "Volume Buyers"
    if high_p:
        return "Premium Selective"
    return "Budget Light"

df["Segment"] = df.apply(segment, axis=1)

# Each row is one order and Customer_ID is not reliable (Task 1), so these are
# segments of ORDERS / buyers, not of unique customers.
def top_value(s):
    return s.value_counts().index[0]

profile = df.groupby("Segment").agg(
    orders=("Order_ID", "count"),
    revenue=("Total_Sales", "sum"),
    avg_order_value=("Total_Sales", "mean"),
    units_per_order=("Quantity", "mean"),
    avg_unit_price=("Unit_Price", "mean"),
    avg_age=("Age", "mean"),
    female_pct=("Gender", lambda s: (s == "Female").mean() * 100),
    top_category=("Category", top_value),
    top_city=("City", lambda s: s[s != "Unknown"].value_counts().index[0]),
).reindex(SEG_ORDER)
profile.insert(1, "order_share_pct", profile["orders"] / orders * 100)
profile.insert(3, "revenue_share_pct", profile["revenue"] / total_revenue * 100)
profile = profile.round(1)
profile.to_csv(os.path.join(OUT, "segment_profile.csv"))
print("\n===== SEGMENT PROFILE =====")
print(profile.to_string())

premium_share = profile.loc["Premium Bulk", "revenue_share_pct"]

kpi_table = pd.DataFrame([
    ["Total Revenue", round(total_revenue, 2)],
    ["Average Order Value", round(aov, 2)],
    ["Units per Order", round(units_per_order, 2)],
    [f"MoM Revenue Growth % ({latest_month})", round(latest_growth, 1)],
    ["Premium Bulk Revenue Share %", premium_share],
], columns=["KPI", "Value"])
kpi_table.to_csv(os.path.join(OUT, "kpi_summary.csv"), index=False)
print("\n===== KPIs =====")
print(kpi_table.to_string(index=False))

# segment x category / age group / city (revenue) for the report
seg_cat = df.pivot_table(index="Segment", columns="Category", values="Total_Sales",
                         aggfunc="sum").reindex(SEG_ORDER) / 1e6
seg_age = pd.crosstab(df["Segment"], df["Age_Group"], normalize="index").reindex(SEG_ORDER) * 100
seg_cat.round(2).to_csv(os.path.join(OUT, "segment_by_category.csv"))
seg_age.round(1).to_csv(os.path.join(OUT, "segment_by_age_group.csv"))
print("\nShare of each segment's orders by age group (%):\n", seg_age.round(1).to_string())

# chart 1: orders share vs revenue share per segment
fig, ax = plt.subplots(figsize=(9, 5))
x = np.arange(len(SEG_ORDER))
ax.bar(x - 0.2, profile["order_share_pct"], 0.4, label="% of orders", color="#8A8F98")
ax.bar(x + 0.2, profile["revenue_share_pct"], 0.4, label="% of revenue", color=BLUE)
for i, seg in enumerate(SEG_ORDER):
    ax.text(i - 0.2, profile.loc[seg, "order_share_pct"] + 0.8, f"{profile.loc[seg, 'order_share_pct']:.0f}%", ha="center", fontsize=9)
    ax.text(i + 0.2, profile.loc[seg, "revenue_share_pct"] + 0.8, f"{profile.loc[seg, 'revenue_share_pct']:.0f}%", ha="center", fontsize=9)
ax.set_xticks(x)
ax.set_xticklabels(SEG_ORDER)
ax.set_ylabel("Share (%)")
ax.set_title("Share of orders vs share of revenue by segment")
ax.legend()
save_fig("01_segment_orders_vs_revenue.png")

# chart 2: average order value by segment
plt.figure(figsize=(8, 4.5))
plt.bar(SEG_ORDER, profile["avg_order_value"], color=[SEG_COLORS[s] for s in SEG_ORDER])
for i, v in enumerate(profile["avg_order_value"]):
    plt.text(i, v + 4000, f"{v:,.0f}", ha="center", fontsize=9)
plt.title("Average order value by segment")
plt.gca().yaxis.set_major_formatter(mtick.FuncFormatter(millions))
save_fig("02_segment_avg_order_value.png")

# chart 3: segment x category revenue heatmap
plt.figure(figsize=(9, 4.5))
sns.heatmap(seg_cat, annot=True, fmt=".1f", cmap="Blues", linewidths=0.5,
            cbar_kws={"label": "Revenue (millions)"})
plt.title("Revenue by segment and category (millions)")
save_fig("03_heatmap_segment_category.png")

# chart 4: monthly revenue by segment
seg_month = (df[df["Order_Date"] < "2026-01-01"]
             .pivot_table(index=df["Order_Date"].dt.to_period("M").astype(str), columns="Segment",
                          values="Total_Sales", aggfunc="sum")[SEG_ORDER])
seg_month.plot(kind="bar", stacked=True, figsize=(11, 5), color=[SEG_COLORS[s] for s in SEG_ORDER])
plt.title("Monthly revenue by segment (2025)")
plt.xlabel("")
plt.gca().yaxis.set_major_formatter(mtick.FuncFormatter(millions))
plt.xticks(rotation=45)
save_fig("04_monthly_revenue_by_segment.png")

# ---------------------------------------------------------------
# 3. K-Means check (are there natural clusters?)
# ---------------------------------------------------------------
try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import silhouette_score

    X = StandardScaler().fit_transform(df[["Age", "Quantity", "Unit_Price"]])
    rows = []
    for k in range(2, 7):
        labels = KMeans(n_clusters=k, n_init=10, random_state=42).fit_predict(X)
        rows.append([k, round(silhouette_score(X, labels), 3)])
    sil = pd.DataFrame(rows, columns=["k", "silhouette"])
    sil.to_csv(os.path.join(OUT, "kmeans_silhouette.csv"), index=False)
    print("\n===== K-MEANS silhouette scores (Age, Quantity, Unit_Price) =====")
    print(sil.to_string(index=False))

    plt.figure(figsize=(7, 4))
    plt.plot(sil["k"], sil["silhouette"], marker="o", color=BLUE)
    plt.axhline(0.5, color=ORANGE, linestyle="--", label="0.5 = clear structure")
    plt.ylim(0, 0.7)
    plt.xlabel("Number of clusters (k)")
    plt.ylabel("Silhouette score")
    plt.title("K-Means: silhouette score by k")
    plt.legend()
    save_fig("05_kmeans_silhouette.png")
except ImportError:
    print("\nscikit-learn is not installed, skipping the K-Means check (pip install scikit-learn)")

# ---------------------------------------------------------------
# 4. Export for the BI tool
# ---------------------------------------------------------------
bi = df[["Order_ID", "Order_Date", "Order_Month_Name", "Order_Quarter", "Customer_ID", "Age", "Age_Group",
         "Gender", "City", "Product", "Category", "Quantity", "Unit_Price", "Total_Sales",
         "Order_Value_Band", "Segment"]].copy()
bi["Order_Month"] = bi["Order_Date"].dt.strftime("%Y-%m")
bi.to_csv(os.path.join(OUT, "dashboard_data.csv"), index=False, date_format="%Y-%m-%d")
print("\nSaved dashboard_data.csv (use this file in Power BI / Looker Studio / Tableau)")

# ---------------------------------------------------------------
# 5. Interactive HTML dashboard
# ---------------------------------------------------------------
if os.path.exists(TEMPLATE):
    records = [{"d": r.Order_Date.strftime("%Y-%m-%d"), "c": r.City, "k": r.Category, "p": r.Product,
                "g": r.Gender, "a": r.Age_Group, "s": r.Segment, "q": int(r.Quantity),
                "u": float(r.Unit_Price), "t": float(r.Total_Sales)} for r in df.itertuples()]
    html = open(TEMPLATE, encoding="utf-8").read().replace("/*DATA*/[]", json.dumps(records, separators=(",", ":")))
    with open(os.path.join(DASH, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("Dashboard saved:", os.path.join(DASH, "index.html"))
else:
    print("dashboard_template.html not found next to task3.py, dashboard not built")

with open(os.path.join(OUT, "key_numbers_task3.json"), "w") as f:
    json.dump({"total_revenue": round(total_revenue, 2), "aov": round(aov, 2),
               "units_per_order": round(units_per_order, 2), "latest_month": latest_month,
               "latest_growth": round(latest_growth, 1), "premium_share": premium_share}, f, indent=2)
print("\nDone. Everything is saved in:", OUT)
