import pandas as pd
import numpy as np

# --------------------------------------------------
# LOAD RAW DATA
# --------------------------------------------------
df = pd.read_csv("data/california-state-fleet-2015-2025.csv", encoding="latin-1")
print(f"Raw data loaded: {len(df)} rows, {len(df.columns)} columns")

# --------------------------------------------------
# FIX 1: Strip whitespace from column names
# --------------------------------------------------
df.columns = df.columns.str.strip()
print("Column names stripped of whitespace")

# --------------------------------------------------
# FIX 2: Convert "Null" text strings to actual NaN
# Handles both "Null" and "Null " (trailing space)
# --------------------------------------------------
null_variants = ["Null", "Null ", "null", "NULL"]
for col in df.columns:
    mask = df[col].isin(null_variants)
    count = mask.sum()
    if count > 0:
        df.loc[mask, col] = np.nan
        print(f"  Converted {count} null strings in {col}")

# --------------------------------------------------
# FIX 3: Handle "NIS" in Total_Miles
# 837 rows, all CHP. Means "Not In Service"
# Keep the rows, convert NIS to NaN for mileage
# --------------------------------------------------
nis_count = (df["Total_Miles"] == "NIS").sum()
df.loc[df["Total_Miles"] == "NIS", "Total_Miles"] = np.nan
print(f"Converted {nis_count} NIS values in Total_Miles to NaN")

# --------------------------------------------------
# FIX 4: Fix inconsistent casing in Disposed
# "Yes" (54,975) vs "yes" (19)
# --------------------------------------------------
df["Disposed"] = df["Disposed"].str.strip().str.title()
disposed_counts = df["Disposed"].value_counts()
print(f"Standardized Disposed column: {disposed_counts.to_dict()}")

# --------------------------------------------------
# FIX 5: Convert financial columns to numeric
# --------------------------------------------------
financial_cols = [
    "Purchase_Price", "Annual_Lease_Rate",
    "Acquisition_Mileage", "Disposition_Mileage",
    "Disposition_Sold_Amount", "Total_Miles"
]
for col in financial_cols:
    before_valid = pd.to_numeric(df[col], errors="coerce").notna().sum()
    df[col] = pd.to_numeric(df[col], errors="coerce")
    after_valid = df[col].notna().sum()
    print(f"  {col}: {after_valid} valid numeric values")

# --------------------------------------------------
# FIX 6: Convert Model_Year to numeric, fix bad values
# Values like 1, 2, 4, 6, 202 are data entry errors
# --------------------------------------------------
df["Model_Year"] = pd.to_numeric(df["Model_Year"], errors="coerce")
bad_years = df["Model_Year"] < 1900
bad_year_count = bad_years.sum()
df.loc[bad_years, "Model_Year"] = np.nan
print(f"Nulled {bad_year_count} Model_Year values below 1900")

# --------------------------------------------------
# FIX 7: Flag the $23.8M CalFire anomaly
# Create a column to mark these, do not silently delete
# --------------------------------------------------
calfire_anomaly = df["Purchase_Price"] == 23854974.0
df["Price_Anomaly_Flag"] = False
df.loc[calfire_anomaly, "Price_Anomaly_Flag"] = True
print(f"Flagged {calfire_anomaly.sum()} rows with $23.8M CalFire price anomaly")

# --------------------------------------------------
# FIX 8: Flag negative mileage values
# --------------------------------------------------
neg_acq = df["Acquisition_Mileage"] < 0
neg_disp = df["Disposition_Mileage"] < 0
df["Mileage_Anomaly_Flag"] = False
df.loc[neg_acq | neg_disp, "Mileage_Anomaly_Flag"] = True
print(f"Flagged {(neg_acq | neg_disp).sum()} rows with negative mileage")

# --------------------------------------------------
# VALIDATION: Check the cleaned data
# --------------------------------------------------
print("\n=== POST-CLEANING VALIDATION ===")
print(f"Total rows: {len(df)}")
print(f"Rows with valid Purchase_Price: {df['Purchase_Price'].notna().sum()}")
print(f"Rows with valid Total_Miles: {df['Total_Miles'].notna().sum()}")
print(f"Rows flagged as price anomaly: {df['Price_Anomaly_Flag'].sum()}")
print(f"Rows flagged as mileage anomaly: {df['Mileage_Anomaly_Flag'].sum()}")
print(f"Model_Year range: {df['Model_Year'].min():.0f} to {df['Model_Year'].max():.0f}")
print(f"Purchase_Price range (excluding anomalies): "
      f"${df.loc[~df['Price_Anomaly_Flag'], 'Purchase_Price'].min():,.0f} to "
      f"${df.loc[~df['Price_Anomaly_Flag'], 'Purchase_Price'].max():,.0f}")

# Confirm no "Null" strings remain anywhere
null_remaining = 0
for col in df.columns:
    if df[col].dtype == "object":
        remaining = df[col].isin(null_variants).sum()
        null_remaining += remaining
print(f"Remaining 'Null' strings in text columns: {null_remaining}")

# --------------------------------------------------
# SAVE CLEANED DATA
# --------------------------------------------------
df.to_csv("data/california-fleet-cleaned.csv", index=False)
print(f"\nCleaned data saved: data/california-fleet-cleaned.csv")
print(f"Final shape: {df.shape[0]} rows, {df.shape[1]} columns")
