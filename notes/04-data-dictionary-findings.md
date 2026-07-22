# Data Dictionary Findings

Date: July 22, 2026

## Critical finding: Total_Miles is ANNUAL, not lifetime

Total_Miles = "Total miles driven by the asset during the calendar year of the observation"

This means:
- Each row's Total_Miles is one year of driving, not cumulative
- Cost per mile calculations using Purchase_Price / Total_Miles are wrong
  because they divide a one-time cost by one year of usage
- To get true lifetime miles, sum Total_Miles across all Report_Years
  for the same Equipment_Number, or use Disposition_Mileage for disposed vehicles

## Other key definitions

- Acquisition_Mileage: odometer at purchase (not miles driven in year one)
- Disposition_Mileage: odometer at disposal (this IS lifetime miles at end of life)
- Purchase_Price: nominal dollars (not inflation-adjusted)
- Equipment_Number: unique ID per vehicle, consistent across its lifetime

## Impact on existing queries

Query 3 (cost per mile) needs to be rewritten. Either:
1. Sum Total_Miles across years per vehicle to get lifetime miles
2. Use Disposition_Mileage for disposed vehicles only
3. Calculate annual cost per mile (Purchase_Price / expected_life / Total_Miles)
   which requires knowing expected vehicle lifespan
