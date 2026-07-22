import pandas as pd

df = pd.read_csv("data/california-state-fleet-2015-2025.csv", encoding="latin-1")

# Strip whitespace from column names
df.columns = df.columns.str.strip()

# The columns we care about most
financial_cols = ["Purchase_Price", "Annual_Lease_Rate", "Disposition_Sold_Amount"]
usage_cols = ["Acquisition_Mileage", "Disposition_Mileage", "Total_Miles"]
identity_cols = ["Model_Year", "Asset_Category", "Asset_Type", "Fuel_Type"]

print("=== FINANCIAL COLUMNS ===")
for col in financial_cols:
    print(f"\n--- {col} ---")
    print("Unique non-numeric values:", df[col][pd.to_numeric(df[col], errors="coerce").isna() & df[col].notna()].unique()[:10])
    print("Null count:", df[col].isna().sum())
    numeric_vals = pd.to_numeric(df[col], errors="coerce")
    print("Valid numeric count:", numeric_vals.notna().sum())
    print("Min:", numeric_vals.min(), "Max:", numeric_vals.max(), "Median:", numeric_vals.median())

print("\n=== USAGE COLUMNS ===")
for col in usage_cols:
    print(f"\n--- {col} ---")
    print("Unique non-numeric values:", df[col][pd.to_numeric(df[col], errors="coerce").isna() & df[col].notna()].unique()[:10])
    numeric_vals = pd.to_numeric(df[col], errors="coerce")
    print("Valid numeric count:", numeric_vals.notna().sum())
    print("Min:", numeric_vals.min(), "Max:", numeric_vals.max(), "Median:", numeric_vals.median())

print("\n=== KEY CATEGORICAL COLUMNS ===")
for col in identity_cols:
    print(f"\n--- {col} ---")
    print("Unique values:", df[col].nunique())
    print("Top 10:")
    print(df[col].value_counts().head(10))

print("\n=== DATASET SHAPE ===")
print("Unique agencies:", df["Agency"].nunique())
print("Year range:", df["Report_Year"].min(), "to", df["Report_Year"].max())
print("Disposed breakdown:")
print(df["Disposed"].value_counts())
