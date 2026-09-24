import os
import json
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, avg, stddev, sum as spark_sum, count, when, lit, 
    to_date, countDistinct, max as spark_max, round as spark_round, 
    collect_list, struct, coalesce, array_sort
)
import sqlite3

def run_route_performance_scoring():
    print("Starting Route Performance Scoring...")
    spark = SparkSession.builder \
        .appName("RoutePerformanceScoring") \
        .getOrCreate()

    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    hdfs_clean = os.path.join(base_path, "hdfs_data", "parquet_clean")
    db_path = os.path.join(base_path, "backend", "transit.db")
    
    # 1. Load Data
    try:
        trips = spark.read.parquet(os.path.join(hdfs_clean, "Trips"))
        delays = spark.read.parquet(os.path.join(hdfs_clean, "Delays"))
        passenger_counts = spark.read.parquet(os.path.join(hdfs_clean, "Passenger_Counts"))
        routes = spark.read.parquet(os.path.join(hdfs_clean, "Routes"))
    except Exception as e:
        print(f"Error loading clean parquet data: {e}")
        return

    # Ensure dates and metrics
    if "occupancy_pct" not in trips.columns:
        trips = trips.withColumn("occupancy_pct", (col("passenger_load") / col("capacity")) * 100)
    
    trips = trips.withColumn("date", to_date("scheduled_start"))
    
    # Left join trips with delays (if trip not in delays, delay_minutes = 0)
    trip_delays = trips.join(delays.select("trip_id", "delay_minutes"), "trip_id", "left_outer") \
        .withColumn("delay_minutes", coalesce(col("delay_minutes"), lit(0.0)))

    # Compute base metrics per trip
    trip_metrics = trip_delays.withColumn("is_on_time", when(col("delay_minutes") <= 2.0, 1.0).otherwise(0.0)) \
        .withColumn("is_overcrowded", when(col("occupancy_pct") > 90.0, 1).otherwise(0))

    # Aggregations per route
    route_stats = trip_metrics.groupBy("route_id").agg(
        count("trip_id").alias("total_trips"),
        avg("occupancy_pct").alias("avg_occ"),
        avg("delay_minutes").alias("mean_delay"),
        stddev("delay_minutes").alias("std_delay"),
        (spark_sum("is_on_time") / count("trip_id")).alias("punctuality_norm"),
        countDistinct(when(col("is_overcrowded") == 1, col("date"))).alias("overcrowded_days"),
        (spark_sum("is_overcrowded") / count("trip_id")).alias("raw_occupancy_penalty")
    )

    # Fill nulls for std_delay (when route has 1 trip)
    route_stats = route_stats.fillna(0.0, subset=["std_delay"])

    # Total boardings per route (via trips -> passenger_counts)
    # Actually, passenger_counts has trip_id. Let's aggregate boardings per trip
    trip_boardings = passenger_counts.groupBy("trip_id").agg(spark_sum("boarding_count").alias("trip_boardings"))
    route_boardings = trips.select("trip_id", "route_id").join(trip_boardings, "trip_id", "left_outer") \
        .groupBy("route_id").agg(spark_sum("trip_boardings").alias("total_boardings"))

    route_stats = route_stats.join(route_boardings, "route_id", "left_outer").fillna(0, subset=["total_boardings"])

    # Get max boardings across all routes to normalize demand
    max_boardings_row = route_stats.select(spark_max("total_boardings").alias("max_b")).first()
    max_boardings = max_boardings_row["max_b"] if max_boardings_row and max_boardings_row["max_b"] > 0 else 1

    # Get median trips for underutilization penalty
    # Approximate median via sorting
    all_trips = sorted([row["total_trips"] for row in route_stats.select("total_trips").collect()])
    median_trips = all_trips[len(all_trips)//2] if all_trips else 0

    # Calculate final components
    scored_routes = route_stats.withColumn(
        "demand_norm", col("total_boardings") / lit(max_boardings)
    ).withColumn(
        "reliability_norm", 
        when(col("mean_delay") > 0, 
            when(1 - (col("std_delay") / col("mean_delay")) < 0, 0.0)
            .otherwise(1 - (col("std_delay") / col("mean_delay")))
        ).otherwise(1.0) # If mean delay is 0, perfectly reliable
    ).withColumn(
        "occupancy_penalty", 
        when(col("overcrowded_days") >= 3, col("raw_occupancy_penalty")).otherwise(0.0)
    ).withColumn(
        "underutil_penalty", 
        when((col("avg_occ") < 30) & (col("total_trips") > lit(median_trips)), 1.0).otherwise(0.0)
    )

    # Composite Score (0-100)
    scored_routes = scored_routes.withColumn(
        "raw_score", 
        (lit(100.0) * (
            lit(0.30) * col("demand_norm") +
            lit(0.30) * col("punctuality_norm") +
            lit(0.20) * col("reliability_norm") +
            lit(0.20) * (lit(1.0) - col("occupancy_penalty"))
        )) - (lit(15.0) * col("underutil_penalty"))
    )
    scored_routes = scored_routes.withColumn(
        "composite_score",
        when(col("raw_score") < 0, 0.0).otherwise(spark_round(col("raw_score"), 1))
    )

    # Categories
    scored_routes = scored_routes.withColumn(
        "category",
        when((col("composite_score") >= 75) & (col("occupancy_penalty") < 0.1), "High Performing")
        .when(col("occupancy_penalty") >= 0.3, "Overcrowded")
        .when((col("demand_norm") >= 0.6) & (col("punctuality_norm") < 0.5), "High-Demand-but-Unreliable")
        .when((col("punctuality_norm") >= 0.8) & (col("demand_norm") < 0.3), "Reliable-but-Underutilized")
        .when(col("composite_score") < 40, "Low Performing")
        .otherwise("Moderate")
    )

    # Sparklines: delay_trend and occupancy_trend (last 14 days per route)
    # We first group by route_id and date
    daily_stats = trip_delays.groupBy("route_id", "date").agg(
        avg("delay_minutes").alias("daily_delay"),
        avg("occupancy_pct").alias("daily_occ")
    )
    
    # Order by date within collect_list by struct string cast (cheap hack for Spark < 3) or just use sort_array
    daily_stats_struct = daily_stats.withColumn(
        "stat_struct", 
        struct(col("date").cast("string").alias("d"), spark_round(col("daily_delay"), 1).alias("dl"), spark_round(col("daily_occ"), 1).alias("oc"))
    )
    
    route_sparklines = daily_stats_struct.groupBy("route_id").agg(
        array_sort(collect_list("stat_struct")).alias("sorted_stats")
    )
    
    # Join everything
    final_output = routes.select("route_id", "route_name").join(scored_routes, "route_id") \
        .join(route_sparklines, "route_id", "left_outer")
        
    result_data = final_output.collect()

    # Load to SQLite RouteSummary
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for row in result_data:
        r_id = row["route_id"]
        
        stats = row["sorted_stats"] or []
        # Keep only last 14 days
        stats = stats[-14:]
        
        delay_trend = [s["dl"] for s in stats]
        occ_trend = [s["oc"] for s in stats]
        
        cursor.execute("SELECT id FROM route_summaries WHERE route_id = ?", (r_id,))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute("""
                UPDATE route_summaries SET 
                    performance_score = ?, performance_tier = ?, 
                    delay_trend_json = ?, occupancy_trend_json = ?
                WHERE route_id = ?
            """, (
                row["composite_score"], row["category"],
                json.dumps(delay_trend), json.dumps(occ_trend),
                r_id
            ))
        else:
            # If not exists, insert a placeholder with the computed values
            cursor.execute("""
                INSERT INTO route_summaries (
                    route_id, route_name, total_passengers, total_trips, 
                    avg_occupancy_pct, avg_delay_minutes, on_time_performance_pct, 
                    performance_score, performance_tier, delay_trend_json, occupancy_trend_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                r_id, row["route_name"], row["total_boardings"], row["total_trips"],
                row["avg_occ"], row["mean_delay"], row["punctuality_norm"] * 100,
                row["composite_score"], row["category"], json.dumps(delay_trend), json.dumps(occ_trend)
            ))
            
    conn.commit()
    conn.close()

    print("Route Performance Scoring complete.")
    spark.stop()

if __name__ == "__main__":
    run_route_performance_scoring()
