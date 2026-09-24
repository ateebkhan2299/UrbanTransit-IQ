import os
import sys
import importlib
from pyspark.sql import functions as F
from pyspark.sql.window import Window

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import backend.config as config

ingest_module = importlib.import_module("spark_jobs.01_ingest")
joins_module = importlib.import_module("spark_jobs.04_joins")
get_spark_session = ingest_module.get_spark_session
build_unified_joins = joins_module.build_unified_joins

PROCESSED_DATA_DIR = "./processed_data"

def run_feature_engineering(spark):
    print("=== PySpark Feature Engineering Pipeline ===")
    unified = build_unified_joins(spark)

    counts_df = unified["counts_unified"]
    delays_df = unified["delays_unified"]
    tickets_df = unified["tickets_unified"]

    # 1. Occupancy & Passenger Flow Features
    counts_features = counts_df.withColumn(
        "timestamp_dt", F.to_timestamp(F.col("timestamp"))
    ).withColumn(
        "hour_of_day", F.hour(F.col("timestamp_dt"))
    ).withColumn(
        "day_of_week", F.dayofweek(F.col("timestamp_dt"))
    ).withColumn(
        "is_peak_hour", F.when((F.col("hour_of_day").between(7, 9)) | (F.col("hour_of_day").between(17, 19)), 1).otherwise(0)
    ).withColumn(
        "occupancy_pct", F.round((F.col("current_occupancy") / F.col("total_capacity")) * 100.0, 2)
    ).withColumn(
        "is_overcrowded", F.when(F.col("occupancy_pct") >= config.OVERCROWDING_THRESHOLD_PCT, 1).otherwise(0)
    ).withColumn(
        "is_underutilized", F.when(F.col("occupancy_pct") <= config.UNDERUTILIZED_THRESHOLD_PCT, 1).otherwise(0)
    )

    # Compute Headway (minutes between consecutive arrivals at same stop & route)
    window_spec = Window.partitionBy("route_id", "stop_id").orderBy("timestamp_dt")
    counts_features = counts_features.withColumn(
        "prev_arrival", F.lag("timestamp_dt", 1).over(window_spec)
    ).withColumn(
        "headway_minutes", F.round((F.col("timestamp_dt").cast("long") - F.col("prev_arrival").cast("long")) / 60.0, 2)
    ).fillna({"headway_minutes": 0.0})

    # 2. Delay Severity Features
    delays_features = delays_df.withColumn(
        "scheduled_dt", F.to_timestamp(F.col("scheduled_time"))
    ).withColumn(
        "hour_of_day", F.hour(F.col("scheduled_dt"))
    ).withColumn(
        "day_of_week", F.dayofweek(F.col("scheduled_dt"))
    ).withColumn(
        "is_peak_hour", F.when((F.col("hour_of_day").between(7, 9)) | (F.col("hour_of_day").between(17, 19)), 1).otherwise(0)
    ).withColumn(
        "delay_severity",
        F.when(F.col("delay_minutes") == 0, "NONE")
         .when(F.col("delay_minutes") < config.DELAY_MODERATE_MIN, "MINOR")
         .when(F.col("delay_minutes") < config.DELAY_MAJOR_MIN, "MODERATE")
         .when(F.col("delay_minutes") < config.DELAY_SEVERE_MIN, "MAJOR")
         .otherwise("SEVERE")
    )

    # 3. Tickets Demand Features
    tickets_features = tickets_df.withColumn(
        "validation_dt", F.to_timestamp(F.col("validation_timestamp"))
    ).withColumn(
        "purchase_dt", F.to_timestamp(F.col("purchase_timestamp"))
    ).withColumn(
        "lead_time_minutes", F.round((F.col("validation_dt").cast("long") - F.col("purchase_dt").cast("long")) / 60.0, 2)
    ).withColumn(
        "hour_of_day", F.hour(F.col("validation_dt"))
    ).withColumn(
        "day_of_week", F.dayofweek(F.col("validation_dt"))
    ).withColumn(
        "date", F.to_date(F.col("validation_dt"))
    )

    # Export engineered feature datasets to Parquet
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

    counts_features.toPandas().to_parquet(os.path.join(PROCESSED_DATA_DIR, "features_occupancy.parquet"), index=False)
    delays_features.toPandas().to_parquet(os.path.join(PROCESSED_DATA_DIR, "features_delays.parquet"), index=False)
    tickets_features.toPandas().to_parquet(os.path.join(PROCESSED_DATA_DIR, "features_tickets.parquet"), index=False)

    print("\n=== FEATURE ENGINEERING SUMMARY ===")
    print(f"  Occupancy Features shape: ({counts_features.count()}, {len(counts_features.columns)})")
    print(f"  Delays Features shape: ({delays_features.count()}, {len(delays_features.columns)})")
    print(f"  Tickets Features shape: ({tickets_features.count()}, {len(tickets_features.columns)})")
    print(f"\n[SAVED] Engineered datasets saved to {PROCESSED_DATA_DIR}")

    return {
        "occupancy_features": counts_features,
        "delays_features": delays_features,
        "tickets_features": tickets_features
    }

if __name__ == "__main__":
    spark = get_spark_session(app_name="UrbanTransit_FeatureEngineering")
    run_feature_engineering(spark)
    spark.stop()
