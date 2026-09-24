import argparse
import json
import sqlite3
import os
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, countDistinct, avg, count, sum as spark_sum, when, round as spark_round

ON_TIME_THRESHOLD_MINUTES = 2

def main(clean_base, db_path):
    spark = SparkSession.builder \
        .appName("UrbanTransitIQ_DashboardComputation") \
        .getOrCreate()
    
    print("Loading cleaned Parquet data...")
    tickets_df = spark.read.parquet(f"{clean_base}/parquet/tickets")
    trips_df = spark.read.parquet(f"{clean_base}/parquet/trips")
    delays_df = spark.read.parquet(f"{clean_base}/parquet/delays")
    pc_df = spark.read.parquet(f"{clean_base}/parquet/passenger_counts")
    routes_df = spark.read.parquet("parquet_data/raw/parquet/routes") # from raw
    vehicles_df = spark.read.parquet(f"{clean_base}/parquet/vehicles")

    # 1. Delay-Cause Breakdown
    print("Computing Delay Causes...")
    delay_summary = delays_df.filter(col("delay_minutes").isNotNull()) \
        .groupBy("cause") \
        .agg(
            count("delay_id").alias("incident_count"),
            spark_sum("delay_minutes").alias("total_delay_minutes"),
            avg("delay_minutes").alias("avg_delay_minutes")
        ).toPandas()

    total_incidents = delay_summary["incident_count"].sum()
    if total_incidents > 0:
        delay_summary["percentage_share"] = (delay_summary["incident_count"] / total_incidents) * 100
    else:
        delay_summary["percentage_share"] = 0.0

    # 2. Route Summary Computation
    print("Computing Route Summaries...")
    # Join Trips + Tickets + Routes to get passenger counts and trip counts
    # A passenger is a unique ticket_id
    tickets_trips = tickets_df.join(trips_df, "trip_id", "inner")
    
    route_passengers = tickets_trips.groupBy("route_id") \
        .agg(
            countDistinct("ticket_id").alias("total_passengers"),
            countDistinct("trip_id").alias("total_trips")
        )

    # Delay computation per route
    route_delays = delays_df.join(trips_df, "trip_id", "inner") \
        .groupBy("route_id") \
        .agg(
            avg("delay_minutes").alias("avg_delay_minutes"),
            (spark_sum(when(col("delay_minutes") <= ON_TIME_THRESHOLD_MINUTES, 1).otherwise(0)) / count("trip_id") * 100).alias("on_time_performance_pct")
        )

    # Occupancy computation (Mocking the percentage for now based on boardings / capacity)
    pc_joined = pc_df.join(trips_df, "trip_id", "inner").join(vehicles_df, "vehicle_id", "inner")
    route_occupancy = pc_joined.groupBy("route_id") \
        .agg(
            (avg(col("boarding_count") / col("capacity")) * 100).alias("avg_occupancy_pct")
        )

    # Combine everything
    final_routes = routes_df \
        .join(route_passengers, "route_id", "left") \
        .join(route_delays, "route_id", "left") \
        .join(route_occupancy, "route_id", "left") \
        .fillna({
            "total_passengers": 0, "total_trips": 0, 
            "avg_delay_minutes": 0.0, "on_time_performance_pct": 100.0,
            "avg_occupancy_pct": 0.0
        }).toPandas()

    # Write JSON outputs
    timestamp = datetime.utcnow().isoformat()
    output_dir = "processed_data/dashboards"
    os.makedirs(output_dir, exist_ok=True)

    with open(f"{output_dir}/delay_causes.json", "w") as f:
        json.dump({
            "computed_at": timestamp,
            "source": "real_pipeline",
            "data": delay_summary.to_dict(orient="records")
        }, f)

    with open(f"{output_dir}/route_summaries.json", "w") as f:
        json.dump({
            "computed_at": timestamp,
            "source": "real_pipeline",
            "data": final_routes.to_dict(orient="records")
        }, f)

    # 3. Load into SQLite Database (backend/models_db.py schema)
    print("Loading into SQLite database...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Clear old seeded data
    cursor.execute("DELETE FROM route_summaries")
    cursor.execute("DELETE FROM delay_summaries")
    cursor.execute("DELETE FROM pipeline_sync_log")

    # Insert RouteSummary
    for _, row in final_routes.iterrows():
        cursor.execute("""
            INSERT INTO route_summaries (
                route_id, route_name, transport_mode, total_trips, total_passengers,
                avg_occupancy_pct, avg_delay_minutes, on_time_performance_pct,
                performance_score, performance_tier
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["route_id"], row["route_name"], row["transport_mode"], 
            int(row["total_trips"]), int(row["total_passengers"]), 
            float(row["avg_occupancy_pct"]), float(row["avg_delay_minutes"]), 
            float(row["on_time_performance_pct"]), 
            85.0, "Tier A" # Default scores for now
        ))

    # Insert DelayCauseSummary
    for _, row in delay_summary.iterrows():
        cursor.execute("""
            INSERT INTO delay_summaries (
                cause, incident_count, total_delay_minutes, avg_delay_minutes, percentage_share
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            row["cause"], int(row["incident_count"]), float(row["total_delay_minutes"]),
            float(row["avg_delay_minutes"]), float(row["percentage_share"])
        ))

    # Record sync log
    cursor.execute("""
        INSERT INTO pipeline_sync_log (last_updated, status) VALUES (?, ?)
    """, (timestamp, "ok"))

    conn.commit()
    conn.close()

    print("Dashboard computation complete and loaded into SQLite!")
    spark.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", type=str, default="processed_data/clean")
    parser.add_argument("--db", type=str, default="backend/transit.db")
    args = parser.parse_args()
    main(args.clean, args.db)
