import sqlite3

conn = sqlite3.connect("data/fleet.db")

def run_query(title, sql):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    cursor = conn.execute(sql)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    
    header = " | ".join(f"{c:>25}" for c in columns)
    print(header)
    print("-" * len(header))
    
    for row in rows:
        formatted = []
        for val in row:
            if val is None:
                formatted.append(f"{'N/A':>25}")
            elif isinstance(val, float):
                formatted.append(f"{val:>25,.2f}")
            else:
                formatted.append(f"{str(val):>25}")
        print(" | ".join(formatted))
    print(f"\n({len(rows)} rows returned)")


# -----------------------------------------------
# QUERY 1: Fleet size by agency, top 10
# "How big is each agency's fleet?"
# -----------------------------------------------
run_query("TOP 10 AGENCIES BY ACTIVE FLEET SIZE", """
    SELECT 
        Agency,
        COUNT(*) as total_vehicles,
        SUM(CASE WHEN Disposed = 'No' THEN 1 ELSE 0 END) as active_vehicles,
        SUM(CASE WHEN Disposed = 'Yes' THEN 1 ELSE 0 END) as disposed_vehicles
    FROM fleet_assets
    WHERE Report_Year = 2024
    GROUP BY Agency
    ORDER BY active_vehicles DESC
    LIMIT 10
""")


# -----------------------------------------------
# QUERY 2: Average purchase price by vehicle type
# "What do different vehicle types actually cost?"
# -----------------------------------------------
run_query("AVERAGE PURCHASE PRICE BY VEHICLE TYPE (2024)", """
    SELECT 
        Asset_Type,
        COUNT(*) as vehicle_count,
        ROUND(AVG(Purchase_Price), 0) as avg_price,
        ROUND(MIN(Purchase_Price), 0) as min_price,
        ROUND(MAX(Purchase_Price), 0) as max_price
    FROM fleet_assets
    WHERE Report_Year = 2024
        AND Purchase_Price IS NOT NULL
        AND Price_Anomaly_Flag = 0
        AND Purchase_Price > 0
    GROUP BY Asset_Type
    HAVING vehicle_count >= 50
    ORDER BY avg_price DESC
""")


# -----------------------------------------------
# QUERY 3A: Cost per lifetime mile (disposed vehicles only)
# Uses Disposition_Mileage which is the odometer at disposal
# -----------------------------------------------
run_query("COST PER LIFETIME MILE - DISPOSED VEHICLES", """
    SELECT
        Asset_Type,
        COUNT(*) as vehicle_count,
        ROUND(AVG(Purchase_Price), 0) as avg_purchase_price,
        ROUND(AVG(Disposition_Mileage), 0) as avg_lifetime_miles,
        ROUND(AVG(Purchase_Price) / NULLIF(AVG(Disposition_Mileage), 0), 2) as cost_per_mile
    FROM fleet_assets
    WHERE Disposed = 'Yes'
        AND Purchase_Price IS NOT NULL
        AND Disposition_Mileage IS NOT NULL
        AND Purchase_Price > 0
        AND Disposition_Mileage > 100
        AND Disposition_Mileage < 500000
        AND Price_Anomaly_Flag = 0
    GROUP BY Asset_Type
    HAVING vehicle_count >= 20
    ORDER BY cost_per_mile DESC
""")


# -----------------------------------------------
# QUERY 3B: Cost per lifetime mile using summed annual miles
# Sums Total_Miles across all years per vehicle
# Uses MAX(Purchase_Price) because some vehicles have
# changing prices across years (likely depreciated values)
# -----------------------------------------------
run_query("COST PER LIFETIME MILE - ALL VEHICLES (SUMMED ANNUAL)", """
    SELECT
        sub.Asset_Type,
        COUNT(*) as vehicle_count,
        ROUND(AVG(sub.purchase_price), 0) as avg_purchase_price,
        ROUND(AVG(sub.lifetime_miles), 0) as avg_lifetime_miles,
        ROUND(AVG(sub.purchase_price) / NULLIF(AVG(sub.lifetime_miles), 0), 2) as cost_per_mile
    FROM (
        SELECT
            Equipment_Number,
            Asset_Type,
            MAX(Purchase_Price) as purchase_price,
            SUM(Total_Miles) as lifetime_miles
        FROM fleet_assets
        WHERE Purchase_Price IS NOT NULL
            AND Total_Miles IS NOT NULL
            AND Purchase_Price > 0
            AND Price_Anomaly_Flag = 0
        GROUP BY Equipment_Number, Asset_Type
    ) sub
    WHERE sub.lifetime_miles > 100
        AND sub.lifetime_miles < 500000
    GROUP BY sub.Asset_Type
    HAVING vehicle_count >= 20
    ORDER BY cost_per_mile DESC
""")


# -----------------------------------------------
# QUERY 4: Fleet age distribution
# "How old is our fleet? Are we replacing on time?"
# -----------------------------------------------
run_query("FLEET AGE DISTRIBUTION (ACTIVE VEHICLES, 2024)", """
    SELECT
        CASE
            WHEN (2024 - Model_Year) <= 3 THEN '0-3 years'
            WHEN (2024 - Model_Year) <= 6 THEN '4-6 years'
            WHEN (2024 - Model_Year) <= 10 THEN '7-10 years'
            WHEN (2024 - Model_Year) <= 15 THEN '11-15 years'
            ELSE 'Over 15 years'
        END as age_group,
        COUNT(*) as vehicle_count,
        ROUND(AVG(Purchase_Price), 0) as avg_purchase_price,
        ROUND(AVG(Total_Miles), 0) as avg_annual_miles
    FROM fleet_assets
    WHERE Report_Year = 2024
        AND Disposed = 'No'
        AND Model_Year IS NOT NULL
    GROUP BY age_group
    ORDER BY 
        CASE age_group
            WHEN '0-3 years' THEN 1
            WHEN '4-6 years' THEN 2
            WHEN '7-10 years' THEN 3
            WHEN '11-15 years' THEN 4
            WHEN 'Over 15 years' THEN 5
        END
""")


# -----------------------------------------------
# QUERY 5: Disposal recovery rate
# "How much do we recover when we sell old vehicles?"
# -----------------------------------------------
run_query("DISPOSAL VALUE RECOVERY BY VEHICLE TYPE", """
    SELECT
        Asset_Type,
        COUNT(*) as disposed_count,
        ROUND(AVG(Purchase_Price), 0) as avg_purchase_price,
        ROUND(AVG(Disposition_Sold_Amount), 0) as avg_sold_amount,
        ROUND(AVG(Disposition_Sold_Amount) * 100.0 / 
              NULLIF(AVG(Purchase_Price), 0), 1) as recovery_rate_pct,
        ROUND(AVG(Disposition_Mileage), 0) as avg_miles_at_disposal
    FROM fleet_assets
    WHERE Disposed = 'Yes'
        AND Purchase_Price IS NOT NULL
        AND Disposition_Sold_Amount IS NOT NULL
        AND Purchase_Price > 0
        AND Disposition_Sold_Amount > 0
        AND Price_Anomaly_Flag = 0
    GROUP BY Asset_Type
    HAVING disposed_count >= 20
    ORDER BY recovery_rate_pct DESC
""")


# -----------------------------------------------
# QUERY 6: Year over year fleet cost trends
# "Is our fleet getting more expensive?"
# -----------------------------------------------
run_query("FLEET COST TRENDS BY YEAR", """
    SELECT
        Report_Year,
        COUNT(*) as total_vehicles,
        SUM(CASE WHEN Purchase_Price IS NOT NULL AND Price_Anomaly_Flag = 0 
            THEN 1 ELSE 0 END) as vehicles_with_price,
        ROUND(AVG(CASE WHEN Price_Anomaly_Flag = 0 
            THEN Purchase_Price END), 0) as avg_purchase_price,
        ROUND(SUM(CASE WHEN Price_Anomaly_Flag = 0 
            THEN Purchase_Price ELSE 0 END), 0) as total_fleet_value
    FROM fleet_assets
    GROUP BY Report_Year
    ORDER BY Report_Year
""")


# -----------------------------------------------
# QUERY 7: Data quality dashboard
# "How trustworthy is our data?"
# -----------------------------------------------
run_query("DATA QUALITY SUMMARY BY YEAR", """
    SELECT
        Report_Year,
        COUNT(*) as total_rows,
        ROUND(SUM(CASE WHEN Purchase_Price IS NOT NULL THEN 1 ELSE 0 END) 
              * 100.0 / COUNT(*), 1) as pct_has_price,
        ROUND(SUM(CASE WHEN Total_Miles IS NOT NULL THEN 1 ELSE 0 END) 
              * 100.0 / COUNT(*), 1) as pct_has_mileage,
        ROUND(SUM(CASE WHEN Model_Year IS NOT NULL THEN 1 ELSE 0 END) 
              * 100.0 / COUNT(*), 1) as pct_has_year,
        SUM(Price_Anomaly_Flag) as price_anomalies,
        SUM(Mileage_Anomaly_Flag) as mileage_anomalies
    FROM fleet_assets
    GROUP BY Report_Year
    ORDER BY Report_Year
""")

conn.close()
