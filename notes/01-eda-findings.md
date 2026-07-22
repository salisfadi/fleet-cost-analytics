# EDA Findings - California State Fleet Data

Date: July 21, 2026
Source: California State Fleet CSV, 2015-2025
Rows: 545,011 | Columns: 34 | Agencies: 69

## Data quality issues found

1. "Null" stored as text string, not actual null, across all financial columns
2. Disposed column has inconsistent casing: "Yes" (54,975) vs "yes" (19)
3. Acquisition_Mileage has two versions of null: "Null " (trailing space) and "Null"
4. Total_Miles contains unknown value "NIS", need to check data dictionary
5. Negative mileage values in Acquisition_Mileage (-18) and Disposition_Mileage (-1)
6. Purchase_Price max is $23.8M, needs investigation against asset category
7. Model_Year has 158 unique values, should have roughly 50, non-year values likely present
8. Column names in raw CSV have leading/trailing spaces

## Financial column coverage

- Purchase_Price: 460,028 valid numeric values out of 545,011 rows
- Annual_Lease_Rate: 24,525 valid (very sparse, most vehicles are purchased not leased)
- Disposition_Sold_Amount: 36,196 valid (only disposed vehicles)
- Total_Miles: 288,191 valid
- No maintenance cost or fuel spend data exists in this dataset
