import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, isnull, lit, current_timestamp
from pyspark.sql.types import StringType

def run_data_cleaning():
    spark = SparkSession.builder \
        .appName("UrbanTransit_DQ_Cleaning") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()
        
    raw_dir = "raw_data"
    clean_dir = "processed_data/clean"
    quarantine_dir = "processed_data/quarantine"
    
    os.makedirs(clean_dir, exist_ok=True)
    os.makedirs(quarantine_dir, exist_ok=True)
    
    print("Loading raw datasets for cleaning...")
    trips_df = spark.read.csv(os.path.join(raw_dir, "trips.csv"), header=True, inferSchema=True)
    tickets_df = spark.read.csv(os.path.join(raw_dir, "tickets.csv"), header=True, inferSchema=True)
    delays_df = spark.read.csv(os.path.join(raw_dir, "delays.csv"), header=True, inferSchema=True)
    pass_counts_df = spark.read.csv(os.path.join(raw_dir, "passenger_counts.csv"), header=True, inferSchema=True)
    
    audit_logs = []
    
    # Helper to quarantine
    def quarantine_records(df, condition, reason, table_name):
        invalid_df = df.filter(condition).withColumn("quarantine_reason", lit(reason))
        count = invalid_df.count()
        if count > 0:
            invalid_df.write.mode("append").parquet(os.path.join(quarantine_dir, f"{table_name}_quarantined.parquet"))
        return df.filter(~condition), count
        
    summary_lines = ["# Cleaning Summary", "\n| Table | Action | Rows Affected | Rule |", "|---|---|---|---|"]

    # 1. Trips: Missing Vehicle ID -> Fill Default 'V_UNKNOWN'
    missing_v_count = trips_df.filter(isnull(col("vehicle_id"))).count()
    trips_df = trips_df.fillna({"vehicle_id": "V_UNKNOWN"})
    summary_lines.append(f"| Trips | Corrected | {missing_v_count} | Null vehicle_id -> V_UNKNOWN |")
    
    # 2. Tickets: Duplicates -> Drop
    initial_tickets = tickets_df.count()
    tickets_df = tickets_df.dropDuplicates(["passenger_id", "trip_id"])
    dropped_tickets = initial_tickets - tickets_df.count()
    summary_lines.append(f"| Tickets | Removed | {dropped_tickets} | Dropped duplicate transactions |")
    
    # 3. Passenger Counts: Negative Counts -> Quarantine
    pass_counts_df, neg_count_qty = quarantine_records(
        pass_counts_df, 
        (col("boarding_count") < 0) | (col("alighting_count") < 0), 
        "Negative passenger count", 
        "passenger_counts"
    )
    summary_lines.append(f"| Passenger Counts | Quarantined | {neg_count_qty} | Negative boarding/alighting |")
    
    # 4. Delays: Invalid negative delays -> Quarantine
    delays_df, invalid_delays_qty = quarantine_records(
        delays_df,
        col("delay_minutes") < -10,
        "Impossible negative delay",
        "delays"
    )
    summary_lines.append(f"| Delays | Quarantined | {invalid_delays_qty} | Delay minutes < -10 |")
    
    # Write Clean Data
    print("Writing clean datasets to Parquet...")
    trips_df.write.mode("overwrite").parquet(os.path.join(clean_dir, "trips.parquet"))
    tickets_df.write.mode("overwrite").parquet(os.path.join(clean_dir, "tickets.parquet"))
    delays_df.write.mode("overwrite").parquet(os.path.join(clean_dir, "delays.parquet"))
    pass_counts_df.write.mode("overwrite").parquet(os.path.join(clean_dir, "passenger_counts.parquet"))
    
    # Others are passed through as clean (routes, stops, vehicles, passengers)
    for tbl in ["routes", "stops", "vehicles", "passengers", "route_stops", "service_calendar", "schedules", "gps_events"]:
        df = spark.read.csv(os.path.join(raw_dir, f"{tbl}.csv"), header=True, inferSchema=True)
        df.write.mode("overwrite").parquet(os.path.join(clean_dir, f"{tbl}.parquet"))
        
    with open("reports/cleaning_summary.md", "w") as f:
        f.write("\n".join(summary_lines))
        
    print("Cleaning complete. Summaries and clean parquets generated.")
    spark.stop()

if __name__ == "__main__":
    run_data_cleaning()
