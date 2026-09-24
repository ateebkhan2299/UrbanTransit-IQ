import os
import sys
import importlib
from pyspark.sql import functions as F

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import backend.config

ingest_module = importlib.import_module("spark_jobs.01_ingest")
get_spark_session = ingest_module.get_spark_session
SCHEMAS = ingest_module.SCHEMAS

PROCESSED_DATA_DIR = "./processed_data"

def load_cleaned_parquet(spark, table_name):
    file_path = os.path.join(PROCESSED_DATA_DIR, f"{table_name}_clean.parquet")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Cleaned dataset missing: {file_path}")

    schema = SCHEMAS.get(table_name)
    if schema is not None:
        return spark.read.schema(schema).parquet(file_path)
    return spark.read.parquet(file_path)

def build_unified_joins(spark):
    print("=== PySpark SQL Relational Joins Pipeline ===")
    trips_df = load_cleaned_parquet(spark, "trips")
    routes_df = load_cleaned_parquet(spark, "routes")
    vehicles_df = load_cleaned_parquet(spark, "vehicles")
    schedules_df = load_cleaned_parquet(spark, "schedules")
    counts_df = load_cleaned_parquet(spark, "passenger_counts")
    delays_df = load_cleaned_parquet(spark, "delays")
    tickets_df = load_cleaned_parquet(spark, "tickets")
    stops_df = load_cleaned_parquet(spark, "stops")

    # 1. Join Trips with Route & Vehicle metadata
    trips_enriched = trips_df.join(routes_df.select("route_id", "route_short_name", "route_type"), on="route_id", how="left") \
                             .join(vehicles_df.select("vehicle_id", "vehicle_type", "total_capacity"), on="vehicle_id", how="left")

    # 2. Join Passenger Counts with enriched Trips & Stops
    counts_unified = counts_df.join(trips_enriched.select("trip_id", "route_id", "vehicle_id", "route_short_name", "vehicle_type", "total_capacity", "service_id"), on="trip_id", how="inner") \
                              .join(stops_df.select("stop_id", "stop_name", "zone_id"), on="stop_id", how="left")

    # 3. Join Delays with enriched Trips
    delays_unified = delays_df.join(trips_enriched.select("trip_id", "route_id", "vehicle_id", "route_short_name", "vehicle_type", "service_id"), on="trip_id", how="inner") \
                              .join(stops_df.select("stop_id", "stop_name"), on="stop_id", how="left")

    # 4. Join Tickets with enriched Trips
    tickets_unified = tickets_df.join(trips_enriched.select("trip_id", "route_id", "route_short_name", "service_id"), on="trip_id", how="inner")

    print(f"\n[JOIN SUMMARY]")
    print(f"  Enriched Trips Count: {trips_enriched.count()}")
    print(f"  Unified Passenger Counts Record: {counts_unified.count()}")
    print(f"  Unified Delays Record: {delays_unified.count()}")
    print(f"  Unified Tickets Record: {tickets_unified.count()}")

    return {
        "trips_enriched": trips_enriched,
        "counts_unified": counts_unified,
        "delays_unified": delays_unified,
        "tickets_unified": tickets_unified
    }

if __name__ == "__main__":
    spark = get_spark_session(app_name="UrbanTransit_Joins")
    build_unified_joins(spark)
    spark.stop()
