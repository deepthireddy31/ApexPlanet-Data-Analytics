# Data Quality Report

Dataset: 1,000 orders, 12 original columns. Checks were run in `scripts/data_cleaning.py` (output saved in `docs/cleaning_run_log.txt`).

## Summary of issues found

| # | Check | Result | Severity | Action taken |
|---|-------|--------|----------|--------------|
| 1 | Missing values - Age | 20 blanks (2.0%) | Medium | Filled with the median age of the same gender; flagged in `Age_Imputed_Flag` |
| 2 | Missing values - City | 13 blanks (1.3%) | Medium | Replaced with "Unknown" (a city cannot be guessed) |
| 3 | Missing values - other 10 columns | None | - | - |
| 4 | Fully duplicated rows | 0 | - | None needed |
| 5 | Repeated Order_ID | ORD100050 appears 9 times (8 extra rows) | High | Corrected, see below |
| 6 | Date format | Order_Date stored as text (YYYY-MM-DD), all 1,000 parse correctly | Low | Converted to real date type |
| 7 | Text formatting (spaces, case) | No leading/trailing spaces, categories are consistent (8 cities, 6 products, 5 categories, 2 genders) | - | Trim and proper-case applied anyway as a safeguard |
| 8 | Product vs Category mapping | Each product maps to exactly one category | - | None needed |
| 9 | Quantity x Unit_Price = Total_Sales | 0 mismatches | - | None needed (re-checked after cleaning) |
| 10 | Outliers - Age, Quantity, Unit_Price | 0 outliers by the 1.5 x IQR rule | - | None needed |
| 11 | Outliers - Total_Sales | 19 orders above the upper limit of 438,707 | Low | Kept, flagged in `Sales_Outlier_Flag` |
| 12 | Customer_ID vs Customer_Name | 947 unique IDs but only 425 unique names; 52 IDs are linked to more than one name | Medium | Not changed, reported (see below) |
| 13 | Date range | 5 orders are dated 2026-01-01, the rest are in 2025 | Low | Kept; use Order_Year when reporting "2025" |

## Details on the main decisions

**Repeated Order_ID (issue 5).** The IDs run from ORD100002 to ORD101001 in row order, so 1,000 rows should give 1,000 different IDs. Instead ORD100050 appears nine times and eight IDs are missing (ORD100120, 100240, 100360, 100480, 100600, 100720, 100840, 100960). The repeated rows are not copies of each other - they have different customers, dates, products and amounts - so they are separate real orders whose ID was overwritten. Deleting them would lose 8 valid orders worth about 1.3 million. Each extra row sits exactly at the position of one missing ID, so I gave it the ID that belongs to that position and kept the first ORD100050 as it was. The original value is kept in `Order_ID_Original`, and `Order_ID_Fixed_Flag` marks the 8 rows. After the fix there are 1,000 unique Order_IDs.

**Missing Age (issue 1).** Age looks evenly spread between 18 and 65 with mean 41.4 and median 41, so a median fill does not distort the distribution. I did not delete these rows because the sales information in them is complete.

**Outliers (issue 11).** The 19 high Total_Sales values are the result of high quantity with a high unit price, and the totals are arithmetically correct, so they are real large orders and not entry errors. I flagged instead of removing them, so the later EDA can show results with and without them.

**Customer fields (issue 12).** The same Customer_ID is sometimes attached to different names, ages and cities (for example CUST2515 appears 3 times with three different names). There is no way to tell from this file which one is correct, so I did not change them. For customer-level analysis later (retention, CLV) Customer_ID should be used as the identifier, with the caution that attributes like age and city may not be consistent per customer.

**Things I noticed but did not change.** Unit prices are spread from about 146 to 50,000 for every product, so a Laptop can be cheaper than a bag of Rice. That is not a statistical outlier, but it suggests the price column should be confirmed with the business before price analysis.

## Before and after

| Measure | Before | After |
|---------|--------|-------|
| Rows | 1,000 | 1,000 |
| Columns | 12 | 24 |
| Missing values | 33 (20 Age + 13 City) | 0 |
| Duplicate Order_IDs | 8 | 0 |
| Order_Date type | Text | Date |
| Total sales | 139,399,439.65 | 139,399,439.65 (unchanged) |
