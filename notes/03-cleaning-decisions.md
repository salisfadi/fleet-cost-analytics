# Data Cleaning Decisions

Date: July 22, 2026
Script: scripts/clean_data.py
Input: california-state-fleet-2015-2025.csv (545,011 rows, 34 columns)
Output: california-fleet-cleaned.csv (545,011 rows, 36 columns)

## Why 36 columns instead of 34
Two flag columns were added during cleaning:
- Price_Anomaly_Flag: marks the $23.8M CalFire data entry error
- Mileage_Anomaly_Flag: marks negative mileage values

## Cleaning rules applied, in order

### 1. Column name whitespace
Several column names had leading or trailing spaces in the raw CSV.
Stripped all column names with df.columns.str.strip().
Without this, any code referencing these columns by name would silently fail.

### 2. "Null" text strings converted to actual NaN
The source system exported missing values as the literal word "Null" instead
of leaving cells empty. Found in 11 columns. Total conversions:
- Purchase_Price: 84,983
- Annual_Lease_Rate: 520,486
- Total_Miles: 255,983
- Acquisition_Mileage: 271,019
- Disposition_Mileage: 514,181
- Disposition_Sold_Amount: 508,815
- And several non-financial columns

### 3. "NIS" in Total_Miles
837 rows, all California Highway Patrol vehicles.
Means "Not In Service." Converted to NaN.
Rows kept because the vehicles are real, only the mileage is unreported.

### 4. Disposed column casing
19 rows had "yes" instead of "Yes". Standardized using .str.title().
Confirmed: 54,975 + 19 = 54,994 total Yes values after fix.

### 5. Financial and mileage columns converted to numeric
Six columns converted from text to numeric type:
- Purchase_Price: 460,028 valid values
- Annual_Lease_Rate: 24,525 valid values
- Acquisition_Mileage: 273,992 valid values
- Disposition_Mileage: 30,830 valid values
- Disposition_Sold_Amount: 36,196 valid values
- Total_Miles: 288,191 valid values

### 6. Model_Year cleanup
Converted to numeric. 2,033 "Null" strings already handled in step 2.
10 additional rows had years below 1900 (values like 1, 2, 4, 6).
These were set to NaN. Years 1900-1950 kept but may need review.

### 7. CalFire price anomaly flagged
42 rows with exact value $23,854,974, all from Department of Forestry
and Fire Protection. Flagged with Price_Anomaly_Flag = True.
Not deleted. Any cost analysis should filter where Price_Anomaly_Flag = False.

### 8. Negative mileage flagged
29 rows with negative values in Acquisition_Mileage or Disposition_Mileage.
Flagged with Mileage_Anomaly_Flag = True. Not deleted.

## What was NOT changed
- No rows were deleted. All 545,011 rows remain.
- "Not Applicable" values in categorical columns were kept as-is.
- The $17M max purchase price (after excluding anomalies) was not investigated yet.
- Years 1900-1950 were kept, may be legitimate historic vehicles.

## Key principle
Flag, don't delete. Anomalous data is marked with flag columns so that
any downstream analysis can exclude it explicitly. The decision to exclude
is visible and reversible, not hidden inside a cleaning step.
