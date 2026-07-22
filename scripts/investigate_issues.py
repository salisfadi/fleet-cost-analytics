import pandas as pd

df = pd.read_csv("data/california-state-fleet-2015-2025.csv", encoding="latin-1")
df.columns = df.columns.str.strip()

# 1. What is NIS in Total_Miles?
print("=== NIS IN TOTAL_MILES ===")
nis_rows = df[df["Total_Miles"] == "NIS"]
print(f"Count: {len(nis_rows)}")
print("Sample of NIS rows:")
print(nis_rows[["Agency", "Asset_Type", "Model_Year", "Fuel_Type", "Total_Miles"]].head(10))

# 2. What is the $23.8M vehicle?
print("\n=== HIGH PURCHASE PRICES (over $1M) ===")
df["Purchase_Price_Num"] = pd.to_numeric(df["Purchase_Price"], errors="coerce")
expensive = df[df["Purchase_Price_Num"] > 1_000_000].sort_values("Purchase_Price_Num", ascending=False)
print(f"Count over $1M: {len(expensive)}")
print(expensive[["Agency", "Asset_Type", "Asset_Category", "Make_Model", 
                  "Model_Year", "Purchase_Price_Num"]].head(20))

# 3. What non-year values are in Model_Year?
print("\n=== NON-YEAR VALUES IN MODEL_YEAR ===")
model_year_num = pd.to_numeric(df["Model_Year"], errors="coerce")
non_year = df[model_year_num.isna() & df["Model_Year"].notna()]
print(f"Count: {len(non_year)}")
print("Unique values:", non_year["Model_Year"].unique())

# Also check: years that exist but seem wrong
print("\n=== SUSPICIOUS YEAR VALUES ===")
valid_years = model_year_num.dropna()
print("Years below 1950:", (valid_years < 1950).sum())
print("Years above 2026:", (valid_years > 2026).sum())
print("Smallest years:", sorted(valid_years.unique())[:10])

# 4. Bonus: how many rows have ALL financial fields as "Null"?
print("\n=== ROWS WITH NO FINANCIAL DATA AT ALL ===")
financial_cols = ["Purchase_Price", "Annual_Lease_Rate", "Total_Miles"]
all_null = df[
    (df["Purchase_Price"].isin(["Null", "Null "])) &
    (df["Annual_Lease_Rate"].isin(["Null", "Null "])) &
    (df["Total_Miles"].isin(["Null", "Null ", "NIS"]))
]
print(f"Rows with no purchase price, no lease rate, and no mileage: {len(all_null)}")
print(f"That is {len(all_null)/len(df)*100:.1f}% of the dataset")
