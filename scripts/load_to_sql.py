import pandas as pd
import sqlite3

# Load cleaned data
df = pd.read_csv("data/california-fleet-cleaned.csv")
print(f"Loaded cleaned data: {len(df)} rows, {len(df.columns)} columns")

# Connect to SQLite database (creates the file if it doesn't exist)
conn = sqlite3.connect("data/fleet.db")

# Write the dataframe to a SQL table
df.to_sql("fleet_assets", conn, if_exists="replace", index=False)

# Verify it worked
cursor = conn.execute("SELECT COUNT(*) FROM fleet_assets")
row_count = cursor.fetchone()[0]
print(f"Loaded into fleet_assets table: {row_count} rows")

# Check the table structure
cursor = conn.execute("PRAGMA table_info(fleet_assets)")
columns = cursor.fetchall()
print(f"\nTable structure ({len(columns)} columns):")
for col in columns:
    print(f"  {col[1]:35} {col[2]}")

conn.close()
print("\nDatabase saved: data/fleet.db")
