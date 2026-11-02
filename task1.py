"""
Task 1 - Data Immersion & Wrangling
ApexPlanet Data Analytics Internship

Reads the raw Sales_Dataset sheet, profiles it, fixes the data quality
problems I found, adds a few useful columns and saves an analysis-ready file.

Setup: put the dataset next to this script (or inside a folder called data)
and run:  python task1.py
"""
import os
import pandas as pd
import numpy as np

# Paths are built from the script's own location, so it works from any folder
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Look for the dataset in ./data first, then next to the script.
# Both the original and the renamed file name are accepted.
RAW_FILE = None
for folder in (DATA_DIR, BASE):
    for name in ("raw_sales_dataset.xlsx", "ApexPlanet_DataAnalytics_Dataset.xlsx"):
        path = os.path.join(folder, name)
        if os.path.exists(path):
            RAW_FILE = path
            break
    if RAW_FILE:
        break
if RAW_FILE is None:
    raise FileNotFoundError(
        "Dataset not found. Put ApexPlanet_DataAnalytics_Dataset.xlsx in:\n  " + BASE
    )

CLEAN_CSV = os.path.join(DATA_DIR, "cleaned_sales_data.csv")
CLEAN_XLSX = os.path.join(DATA_DIR, "cleaned_sales_data.xlsx")

# ---------------------------------------------------------------
# 1. Load
# ---------------------------------------------------------------
raw = pd.read_excel(RAW_FILE, sheet_name="Sales_Dataset")
df = raw.copy()
print("Reading:", RAW_FILE)
print("Rows, columns:", df.shape)
print(df.dtypes, "\n")

# ---------------------------------------------------------------
# 2. Data quality assessment (profiling only, nothing changed yet)
# ---------------------------------------------------------------
print("---- Missing values ----")
print(df.isna().sum()[df.isna().sum() > 0], "\n")

print("---- Duplicates ----")
print("Fully duplicated rows :", df.duplicated().sum())
print("Repeated Order_IDs    :", df["Order_ID"].duplicated().sum())
print(df[df["Order_ID"].duplicated(keep=False)][["Order_ID", "Order_Date", "Customer_ID", "Product", "Total_Sales"]]
      .sort_values("Order_ID"), "\n")

print("---- Formatting checks ----")
for col in ["Order_ID", "Customer_ID", "Customer_Name", "Gender", "City", "Product", "Category"]:
    s = df[col].dropna().astype(str)
    print(col, "-> values with extra spaces:", (s != s.str.strip()).sum())
print("Order_Date stored as:", df["Order_Date"].map(type).value_counts().to_dict())
print("Cities:", sorted(df["City"].dropna().unique()))
print("Product/Category pairs:\n", df.groupby(["Product", "Category"]).size(), "\n")

print("---- Consistency: Quantity x Unit_Price vs Total_Sales ----")
calc_total = (df["Quantity"] * df["Unit_Price"]).round(2)
print("Mismatches:", (abs(calc_total - df["Total_Sales"]) > 0.01).sum(), "\n")

print("---- Outliers (IQR rule) ----")
def iqr_bounds(s):
    q1, q3 = s.quantile([0.25, 0.75])
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr

for col in ["Age", "Quantity", "Unit_Price", "Total_Sales"]:
    lo, hi = iqr_bounds(df[col].dropna())
    n = ((df[col] < lo) | (df[col] > hi)).sum()
    print(f"{col:12s} lower={lo:12.2f} upper={hi:12.2f} outliers={n}")
print()

print("---- Customer_ID consistency ----")
print("Unique Customer_IDs  :", df["Customer_ID"].nunique())
print("Unique Customer_Names:", df["Customer_Name"].nunique())
multi = df.groupby("Customer_ID")["Customer_Name"].nunique()
print("Customer_IDs with more than one name:", (multi > 1).sum(), "\n")

# ---------------------------------------------------------------
# 3. Cleaning
# ---------------------------------------------------------------

# 3.1 text columns - trim spaces and use proper case
for col in ["Customer_ID", "Customer_Name", "Gender", "City", "Product", "Category"]:
    df[col] = df[col].astype("string").str.strip()
df["Gender"] = df["Gender"].str.title()
df["City"] = df["City"].str.title()
df["Product"] = df["Product"].str.title()
df["Category"] = df["Category"].str.title()

# 3.2 dates - text to real datetime
df["Order_Date"] = pd.to_datetime(df["Order_Date"], format="%Y-%m-%d", errors="coerce")
print("Dates that failed to parse:", df["Order_Date"].isna().sum())

# 3.3 duplicate Order_IDs
# Order_IDs run ORD100002 .. ORD101001 in row order, so a 1000 row file should
# have every number exactly once. 8 IDs were missing and 8 rows repeated ORD100050.
# The repeated rows are completely different orders (different customer, date,
# product, amount) so they are NOT duplicate records - their IDs were just
# overwritten. I keep the first ORD100050 and give the other rows the ID that
# belongs to their row position. The old value is kept in Order_ID_Original.
df["Order_ID_Original"] = df["Order_ID"]
expected_ids = pd.Series([f"ORD{100002 + i}" for i in range(len(df))], index=df.index)
dup_mask = df["Order_ID"].duplicated(keep="first")
missing_ids = set(expected_ids) - set(df["Order_ID"])
assert set(expected_ids[dup_mask]) == missing_ids, "Repeated IDs do not line up with the missing IDs"
df["Order_ID_Fixed_Flag"] = dup_mask
df.loc[dup_mask, "Order_ID"] = expected_ids[dup_mask]
assert df["Order_ID"].is_unique
print("Order_IDs corrected:", int(dup_mask.sum()))

# 3.4 missing values
# City: 13 blanks. Cannot be guessed, so label them Unknown.
df["City"] = df["City"].fillna("Unknown")

# Age: 20 blanks. Fill with the median age of the same gender (Age is
# roughly uniform 18-65 so the median is a safe middle value) and keep a flag
# so these rows can be excluded later if needed.
df["Age_Imputed_Flag"] = df["Age"].isna()
df["Age"] = df["Age"].fillna(df.groupby("Gender")["Age"].transform("median"))
df["Age"] = df["Age"].round().astype(int)

# 3.5 data types
df["Quantity"] = df["Quantity"].astype(int)
df["Unit_Price"] = df["Unit_Price"].round(2)
df["Total_Sales"] = df["Total_Sales"].round(2)

# ---------------------------------------------------------------
# 4. Transformations / feature engineering
# ---------------------------------------------------------------
df["Order_Year"] = df["Order_Date"].dt.year
df["Order_Month"] = df["Order_Date"].dt.month
df["Order_Month_Name"] = df["Order_Date"].dt.strftime("%b")
df["Order_Quarter"] = "Q" + df["Order_Date"].dt.quarter.astype(str)
df["Order_Day_Name"] = df["Order_Date"].dt.day_name()
df["Is_Weekend"] = df["Order_Date"].dt.dayofweek >= 5

df["Age_Group"] = pd.cut(
    df["Age"], bins=[17, 24, 34, 44, 54, 65],
    labels=["18-24", "25-34", "35-44", "45-54", "55-65"],
).astype("string")

# Order size bands using quartiles of Total_Sales
q1, q2, q3 = df["Total_Sales"].quantile([0.25, 0.5, 0.75])
df["Order_Value_Band"] = pd.cut(
    df["Total_Sales"], bins=[-np.inf, q1, q2, q3, np.inf],
    labels=["Low", "Medium", "High", "Very High"],
).astype("string")

# Sales outliers: kept (Quantity x Unit_Price matches, so they are real big
# orders) but flagged so they can be handled in the analysis.
lo, hi = iqr_bounds(df["Total_Sales"])
df["Sales_Outlier_Flag"] = (df["Total_Sales"] < lo) | (df["Total_Sales"] > hi)

# Final check - recomputed total should match given total
assert (abs((df["Quantity"] * df["Unit_Price"]).round(2) - df["Total_Sales"]) <= 0.01).all()

# ---------------------------------------------------------------
# 5. Final column order and save
# ---------------------------------------------------------------
df = df[[
    "Order_ID", "Order_ID_Original", "Order_ID_Fixed_Flag", "Order_Date",
    "Order_Year", "Order_Quarter", "Order_Month", "Order_Month_Name",
    "Order_Day_Name", "Is_Weekend",
    "Customer_ID", "Customer_Name", "Age", "Age_Imputed_Flag", "Age_Group",
    "Gender", "City", "Product", "Category",
    "Quantity", "Unit_Price", "Total_Sales", "Order_Value_Band", "Sales_Outlier_Flag",
]]

df.to_csv(CLEAN_CSV, index=False, date_format="%Y-%m-%d")
with pd.ExcelWriter(CLEAN_XLSX, engine="openpyxl", datetime_format="yyyy-mm-dd") as xw:
    df.to_excel(xw, sheet_name="Cleaned_Sales", index=False)
    ws = xw.sheets["Cleaned_Sales"]
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for col in ws.columns:
        width = max(len(str(c.value)) if c.value is not None else 0 for c in col)
        ws.column_dimensions[col[0].column_letter].width = min(width + 2, 28)

# ---------------------------------------------------------------
# 6. Before / after summary
# ---------------------------------------------------------------
print("\n================ SUMMARY ================")
print("Rows before / after      :", len(raw), "/", len(df))
print("Columns before / after   :", raw.shape[1], "/", df.shape[1])
print("Missing values after     :", int(df.isna().sum().sum()))
print("Duplicate Order_IDs after:", int(df["Order_ID"].duplicated().sum()))
print("Total sales before       :", round(raw["Total_Sales"].sum(), 2))
print("Total sales after        :", round(df["Total_Sales"].sum(), 2))
print("Age imputed rows         :", int(df["Age_Imputed_Flag"].sum()))
print("Sales outliers flagged   :", int(df["Sales_Outlier_Flag"].sum()))
print("Saved:", CLEAN_CSV, "and", CLEAN_XLSX)