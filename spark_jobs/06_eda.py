import os
import sys
import importlib
from pyspark.sql import functions as F

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import backend.config

ingest_module = importlib.import_module("spark_jobs.01_ingest")
get_spark_session = ingest_module.get_spark_session

PROCESSED_DATA_DIR = "./processed_data"

def run_exploratory_data_analysis(spark):
    print("=== PySpark Exploratory Data Analysis (EDA) Pipeline ===")

    occ_path = os.path.join(PROCESSED_DATA_DIR, "features_occupancy.parquet")
    del_path = os.path.join(PROCESSED_DATA_DIR, "features_delays.parquet")
    tck_path = os.path.join(PROCESSED_DATA_DIR, "features_tickets.parquet")

    counts_df = spark.read.parquet(occ_path)
    delays_df = spark.read.parquet(del_path)
    tickets_df = spark.read.parquet(tck_path)

    # 1. Route Performance Summary & Efficiency Scoring
    route_occ = counts_df.groupBy("route_id", "route_short_name").agg(
        F.round(F.avg("occupancy_pct"), 2).alias("avg_occupancy_pct"),
        F.sum("boarded_count").alias("total_boardings"),
        F.sum("is_overcrowded").alias("overcrowded_events")
    )

    route_del = delays_df.groupBy("route_id").agg(
        F.round(F.avg("delay_minutes"), 2).alias("avg_delay_minutes"),
        F.count("delay_id").alias("total_delays")
    )

    route_summary = route_occ.join(route_del, on="route_id", how="left").fillna(0)

    # Route Efficiency Score Formula
    route_summary = route_summary.withColumn(
        "performance_score",
        F.round(
            (F.col("avg_occupancy_pct") * 0.4) +
            (F.greatest(F.lit(0.0), 100.0 - F.col("avg_delay_minutes")) * 0.4) +
            (F.least(F.lit(100.0), F.col("total_boardings") / 50.0) * 0.2), 2
        )
    )

    # 2. Delay Cause Breakdown
    delay_cause_summary = delays_df.groupBy("delay_cause", "delay_severity").agg(
        F.count("delay_id").alias("delay_count"),
        F.round(F.avg("delay_minutes"), 2).alias("avg_duration_min")
    )

    # 3. Hourly Passenger Demand Flow
    hourly_demand = counts_df.groupBy("hour_of_day", "is_peak_hour").agg(
        F.sum("boarded_count").alias("total_boardings"),
        F.round(F.avg("occupancy_pct"), 2).alias("avg_occupancy_pct")
    ).sort("hour_of_day")

    print("\n=== TOP 5 ROUTE PERFORMANCE SCORES ===")
    route_summary.sort(F.col("performance_score").desc()).show(5, truncate=False)

    print("\n=== DELAY CAUSE SUMMARY ===")
    delay_cause_summary.show(10, truncate=False)

    # Export EDA Summaries for Serving DB / FastAPI Layer
    route_summary.toPandas().to_parquet(os.path.join(PROCESSED_DATA_DIR, "summary_route_performance.parquet"), index=False)
    delay_cause_summary.toPandas().to_parquet(os.path.join(PROCESSED_DATA_DIR, "summary_delay_causes.parquet"), index=False)
    hourly_demand.toPandas().to_parquet(os.path.join(PROCESSED_DATA_DIR, "summary_hourly_demand.parquet"), index=False)

    print(f"\n[SAVED] EDA summary datasets written to {PROCESSED_DATA_DIR}")

    return {
        "route_summary": route_summary,
        "delay_cause_summary": delay_cause_summary,
        "hourly_demand": hourly_demand
    }

if __name__ == "__main__":
    spark = get_spark_session(app_name="UrbanTransit_EDA")
    run_exploratory_data_analysis(spark)
    spark.stop()
