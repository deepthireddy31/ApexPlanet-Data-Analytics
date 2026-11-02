# Data Dictionary

Source: `ApexPlanet_DataAnalytics_Dataset.xlsx` (sheet `Sales_Dataset`), 1,000 rows x 12 columns.
Every row is one sales order. Data covers 1 Jan 2025 to 1 Jan 2026.

## A. Original columns (from the raw file)

| # | Column | Type | Example | Meaning | Business relevance |
|---|--------|------|---------|---------|--------------------|
| 1 | Order_ID | Text | ORD100002 | Unique ID of the order | Primary key, used to count orders and join with other tables |
| 2 | Order_Date | Text in raw file (converted to Date) | 2025-02-25 | Date the order was placed | Trend, seasonality and monthly/quarterly reporting |
| 3 | Customer_ID | Text | CUST5529 | ID of the customer | Repeat customers, retention, customer lifetime value |
| 4 | Customer_Name | Text | Customer_227 | Name of the customer (anonymised) | Display only, not reliable for grouping (see quality report) |
| 5 | Age | Number (integer) | 30 | Age of the customer in years (18-65) | Age-group segmentation, targeted marketing |
| 6 | Gender | Text (2 values) | Female | Male / Female | Demographic split of buyers |
| 7 | City | Text (8 values) | Bengaluru | City the order came from | Regional performance, where to focus stock and promotions |
| 8 | Product | Text (6 values) | Rice | Product bought: Book, Chair, Laptop, Mobile, Rice, Shoes | Best and worst sellers |
| 9 | Category | Text (5 values) | Grocery | Product group: Education, Electronics, Fashion, Furniture, Grocery | Category level revenue and mix |
| 10 | Quantity | Number (integer) | 7 | Units bought in the order (1-10) | Volume, basket size |
| 11 | Unit_Price | Number (decimal) | 2829.77 | Price per unit, in rupees | Pricing analysis |
| 12 | Total_Sales | Number (decimal) | 19808.39 | Order revenue = Quantity x Unit_Price | Main revenue measure (KPI) |

## B. Columns added during cleaning

| # | Column | Type | How it is made | Why it is useful |
|---|--------|------|----------------|------------------|
| 13 | Order_ID_Original | Text | Copy of Order_ID before correction | Keeps an audit trail |
| 14 | Order_ID_Fixed_Flag | True/False | True where the Order_ID was repeated and had to be corrected | Lets anyone see exactly which 8 rows were changed |
| 15 | Order_Year | Number | Year of Order_Date | Year filter |
| 16 | Order_Quarter | Text | Q1-Q4 from Order_Date | Quarterly reporting |
| 17 | Order_Month | Number | Month number 1-12 | Sorting months correctly |
| 18 | Order_Month_Name | Text | Jan, Feb ... | Chart labels |
| 19 | Order_Day_Name | Text | Monday ... Sunday | Day of week patterns |
| 20 | Is_Weekend | True/False | True for Saturday and Sunday | Weekday vs weekend comparison |
| 21 | Age_Imputed_Flag | True/False | True where Age was blank in the raw file | Allows these rows to be excluded from age analysis |
| 22 | Age_Group | Text | 18-24, 25-34, 35-44, 45-54, 55-65 | Customer segmentation |
| 23 | Order_Value_Band | Text | Low / Medium / High / Very High using quartiles of Total_Sales | Quick order-size segmentation |
| 24 | Sales_Outlier_Flag | True/False | True if Total_Sales is outside 1.5 x IQR | Identifies unusually large orders |

Note: in the cleaned file `Order_ID` is the corrected key; `Order_ID_Original` is the raw value.
