"""
Task 4 - Data Storytelling & Statistical Validation
ApexPlanet Data Analytics Internship

What this script does
  1. Runs the hypothesis tests I planned (t-test, Mann-Whitney, chi-square)
  2. Calculates p-values, 95% confidence intervals and effect sizes
  3. Saves a results table, charts and the numbers used in the final presentation

"""
import os
import json
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "cleaned_sales_data.csv")
OUT = os.path.join(BASE, "task4_output")
CHARTS = os.path.join(OUT, "charts")
if not os.path.exists(DATA_FILE):
    raise FileNotFoundError("Run task1.py first, cleaned data not found at:\n  " + DATA_FILE)
os.makedirs(CHARTS, exist_ok=True)

BLUE, ORANGE, GREY = "#2F5D8C", "#E08A2E", "#8A8F98"
ALPHA = 0.05

df = pd.read_csv(DATA_FILE, parse_dates=["Order_Date"])
# H1 = Jan-Jun 2025, H2 = Jul 2025 - 1 Jan 2026 (same split I used in Task 2)
df["Half"] = np.where(df["Order_Date"] < "2025-07-01", "H1", "H2")
print("Orders:", len(df), "| H1:", (df["Half"] == "H1").sum(), "| H2:", (df["Half"] == "H2").sum())

# ---------------------------------------------------------------
# helper functions
# ---------------------------------------------------------------
def welch(a, b, label_a, label_b):
    """Welch t-test (does not assume equal variance) + Mann-Whitney as a check,
    because Total_Sales is right-skewed."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    t, p = stats.ttest_ind(a, b, equal_var=False)
    diff = a.mean() - b.mean()
    va, vb = a.var(ddof=1) / len(a), b.var(ddof=1) / len(b)
    se = np.sqrt(va + vb)
    dof = (va + vb) ** 2 / (va ** 2 / (len(a) - 1) + vb ** 2 / (len(b) - 1))
    tcrit = stats.t.ppf(0.975, dof)
    pooled_sd = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2))
    mw_p = stats.mannwhitneyu(a, b, alternative="two-sided").pvalue
    return {"test": "Welch t-test", "n": f"{len(a)} / {len(b)}",
            "estimate": f"{label_a} {a.mean():,.0f} vs {label_b} {b.mean():,.0f}",
            "difference": round(diff, 1), "ci_low": round(diff - tcrit * se, 1), "ci_high": round(diff + tcrit * se, 1),
            "statistic": round(t, 3), "p_value": p, "effect_size": f"Cohen d = {diff / pooled_sd:.2f}",
            "check_p_mannwhitney": mw_p}

def two_proportions(x1, n1, x2, n2, label1, label2):
    """Chi-square test for two proportions + 95% CI of the difference."""
    table = np.array([[x1, n1 - x1], [x2, n2 - x2]])
    chi2, p, _, _ = stats.chi2_contingency(table, correction=False)
    p1, p2 = x1 / n1, x2 / n2
    se = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    diff = p1 - p2
    return {"test": "Chi-square (2 proportions)", "n": f"{n1} / {n2}",
            "estimate": f"{label1} {p1 * 100:.1f}% vs {label2} {p2 * 100:.1f}%",
            "difference": round(diff * 100, 1), "ci_low": round((diff - 1.96 * se) * 100, 1),
            "ci_high": round((diff + 1.96 * se) * 100, 1), "statistic": round(chi2, 3),
            "p_value": p, "effect_size": "diff in percentage points", "check_p_mannwhitney": np.nan}

def chi_square(table, label):
    chi2, p, dof, _ = stats.chi2_contingency(table)
    n = table.values.sum()
    v = np.sqrt(chi2 / (n * (min(table.shape) - 1)))
    return {"test": f"Chi-square independence (df={dof})", "n": str(n), "estimate": label,
            "difference": np.nan, "ci_low": np.nan, "ci_high": np.nan, "statistic": round(chi2, 3),
            "p_value": p, "effect_size": f"Cramer's V = {v:.2f}", "check_p_mannwhitney": np.nan}

# ---------------------------------------------------------------
# the tests (decided before looking at the p-values)
# ---------------------------------------------------------------
mobile = df[df["Product"] == "Mobile"]
n_h1, n_h2 = (df["Half"] == "H1").sum(), (df["Half"] == "H2").sum()
m1, m2 = (mobile["Half"] == "H1"), (mobile["Half"] == "H2")

tests = []
def add(tid, hypothesis, result):
    tests.append({"id": tid, "hypothesis": hypothesis, **result})

add("T1", "H0: Mobile's share of orders is the same in H1 and H2. H1: it changed.",
    two_proportions(m1.sum(), n_h1, m2.sum(), n_h2, "H1", "H2"))
add("T2", "H0: Average Mobile order value is the same in H1 and H2. H1: it differs.",
    welch(mobile.loc[m1, "Total_Sales"], mobile.loc[m2, "Total_Sales"], "H1", "H2"))
add("T3", "H0: Product mix (share of orders per product) is the same in H1 and H2.",
    chi_square(pd.crosstab(df["Product"], df["Half"]), "Order counts by product, H1 vs H2"))
g = df[df["Age_Group"] == "25-34"]
add("T4", "H0: Male and female order values are equal in the 25-34 age group.",
    welch(g.loc[g["Gender"] == "Male", "Total_Sales"], g.loc[g["Gender"] == "Female", "Total_Sales"], "Male", "Female"))
add("T5", "H0: Male and female average order values are equal (all ages).",
    welch(df.loc[df["Gender"] == "Male", "Total_Sales"], df.loc[df["Gender"] == "Female", "Total_Sales"], "Male", "Female"))
add("T6", "H0: Average order value is the same in Q3 and Q4.",
    welch(df.loc[df["Order_Quarter"] == "Q4", "Total_Sales"], df.loc[df["Order_Quarter"] == "Q3", "Total_Sales"], "Q4", "Q3"))
add("T7", "H0: Age group and product category are independent.",
    chi_square(pd.crosstab(df["Age_Group"], df["Category"]), "Age group x Category"))

res = pd.DataFrame(tests)
bonferroni = ALPHA / len(res)      # stricter limit because I ran several tests
res["significant_at_5%"] = np.where(res["p_value"] < ALPHA, "Yes", "No")
res["significant_after_bonferroni"] = np.where(res["p_value"] < bonferroni, "Yes", "No")
res_out = res.copy()
res_out["p_value"] = res_out["p_value"].map(lambda v: round(v, 4))
res_out["check_p_mannwhitney"] = res_out["check_p_mannwhitney"].map(lambda v: round(v, 4) if pd.notna(v) else v)
res_out.to_csv(os.path.join(OUT, "hypothesis_test_results.csv"), index=False)

print(f"\nAlpha = {ALPHA}, Bonferroni limit for {len(res)} tests = {bonferroni:.4f}\n")
for _, r in res_out.iterrows():
    print(f"{r['id']} | {r['test']}\n   {r['hypothesis']}\n   {r['estimate']} | p = {r['p_value']} | "
          f"diff = {r['difference']} [{r['ci_low']}, {r['ci_high']}] | {r['effect_size']} | "
          f"5%: {r['significant_at_5%']} | Bonferroni: {r['significant_after_bonferroni']}")
    if pd.notna(r["check_p_mannwhitney"]):
        print(f"   Mann-Whitney check p = {r['check_p_mannwhitney']}")

# ---------------------------------------------------------------
# charts
# ---------------------------------------------------------------
# 1. Mobile share of orders
t1 = res.iloc[0]
p1, p2 = m1.sum() / n_h1 * 100, m2.sum() / n_h2 * 100
se1 = np.sqrt(p1 / 100 * (1 - p1 / 100) / n_h1) * 196
se2 = np.sqrt(p2 / 100 * (1 - p2 / 100) / n_h2) * 196
plt.figure(figsize=(6, 4.5))
plt.bar(["H1 (Jan-Jun)", "H2 (Jul-Dec)"], [p1, p2], yerr=[se1, se2], capsize=8, color=[BLUE, ORANGE])
for i, v in enumerate([p1, p2]):
    plt.text(i, v / 2, f"{v:.1f}%", ha="center", color="white", fontsize=12, fontweight="bold")
plt.ylabel("Mobile as % of all orders")
plt.title(f"Mobile share of orders (p = {t1['p_value']:.3f}, bars = 95% CI)")
plt.tight_layout(); plt.savefig(os.path.join(CHARTS, "01_mobile_share_h1_h2.png"), dpi=150); plt.close()

# 2. Mobile monthly revenue and orders
mm = mobile.groupby(mobile["Order_Date"].dt.to_period("M")).agg(revenue=("Total_Sales", "sum"), orders=("Order_ID", "count"))
fig, ax = plt.subplots(figsize=(10, 4.5))
ax.bar(mm.index.astype(str), mm["revenue"] / 1e6, color=BLUE)
ax.set_ylabel("Mobile revenue (millions)")
ax2 = ax.twinx()
ax2.plot(mm.index.astype(str), mm["orders"], color=ORANGE, marker="o")
ax2.set_ylabel("Mobile orders")
ax2.set_ylim(0, mm["orders"].max() * 1.2)
plt.title("Mobile: monthly revenue (bars) and number of orders (line)")
plt.setp(ax.get_xticklabels(), rotation=45)
plt.tight_layout(); plt.savefig(os.path.join(CHARTS, "02_mobile_monthly.png"), dpi=150); plt.close()

# 3. all p-values against the limits
plt.figure(figsize=(8, 4.5))
colors = [BLUE if p < ALPHA else GREY for p in res["p_value"]]
plt.bar(res["id"], res["p_value"], color=colors)
plt.axhline(ALPHA, color=ORANGE, linestyle="--", label="0.05")
plt.axhline(bonferroni, color="red", linestyle=":", label=f"Bonferroni {bonferroni:.4f}")
plt.ylabel("p-value")
plt.title("p-values of all tests")
plt.legend()
plt.tight_layout(); plt.savefig(os.path.join(CHARTS, "03_p_values.png"), dpi=150); plt.close()

# 4. Male vs female order value, age 25-34, with 95% CI
plt.figure(figsize=(6, 4.5))
for i, gname in enumerate(["Male", "Female"]):
    v = g.loc[g["Gender"] == gname, "Total_Sales"]
    ci = stats.t.ppf(0.975, len(v) - 1) * v.std(ddof=1) / np.sqrt(len(v))
    plt.bar(gname, v.mean(), yerr=ci, capsize=8, color=[BLUE, ORANGE][i])
plt.ylabel("Average order value")
plt.title(f"Age 25-34: average order value by gender (p = {res.iloc[3]['p_value']:.3f})")
plt.tight_layout(); plt.savefig(os.path.join(CHARTS, "04_gender_25_34.png"), dpi=150); plt.close()

# ---------------------------------------------------------------
# numbers for the presentation
# ---------------------------------------------------------------
prod_half = df.pivot_table(index="Product", columns="Half", values="Total_Sales", aggfunc="sum")
key = {
    "total_revenue": round(df["Total_Sales"].sum(), 2), "orders": len(df),
    "aov": round(df["Total_Sales"].mean(), 2), "units_per_order": round(df["Quantity"].mean(), 2),
    "monthly": {str(k): round(v, 2) for k, v in df[df["Order_Date"] < "2026-01-01"]
                .groupby(df["Order_Date"].dt.to_period("M"))["Total_Sales"].sum().items()},
    "product_h1": {k: round(v, 2) for k, v in prod_half["H1"].items()},
    "product_h2": {k: round(v, 2) for k, v in prod_half["H2"].items()},
    "mobile_share_h1": round(p1, 1), "mobile_share_h2": round(p2, 1),
    "bonferroni": round(bonferroni, 4),
    "tests": res_out[["id", "hypothesis", "test", "estimate", "difference", "ci_low", "ci_high", "p_value",
                      "significant_at_5%", "significant_after_bonferroni"]].fillna("").to_dict("records"),
}
with open(os.path.join(OUT, "key_numbers_task4.json"), "w") as f:
    json.dump(key, f, indent=2)
print("\nDone. Everything is saved in:", OUT)
