# Investigation Findings

Date: July 22, 2026

## NIS in Total_Miles
- 837 rows, all California Highway Patrol
- Likely means "Not In Service"
- Decision: keep rows, treat mileage as null, document the reporting gap

## $23.8M Purchase Price
- Exact value $23,854,974 appears across dozens of CalFire rows
- Many have "Not Applicable" asset type and "Null" model year
- This is a data entry error, not a real vehicle price
- Decision: flag as anomaly, exclude from cost calculations

## Model_Year issues
- 2,033 rows have "Null" as model year
- 371 rows have years below 1950
- Values like 1, 2, 4, 6, 202 are clearly data entry errors
- Decision: null out years below 1900, flag years 1900-1950 for review

## Rows with no financial data
- 56,944 rows (10.4%) have no purchase price, no lease rate, no mileage
- Decision: keep in asset registry, exclude from cost analysis
