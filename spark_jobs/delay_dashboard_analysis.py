import os
import json
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, count, avg, to_date, desc
import sqlite3

def run_delay_dashboard_analysis():
    print("Starting Delay Dashboard Analysis...")
    spark = SparkSession.builder \
        .appName("DelayDashboardAnalysis") \
        .getOrCreate()

    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    hdfs_clean = os.path.join(base_path, "hdfs_data", "parquet_clean")
    
    # 1. Load Data
    try:
        delays = spark.read.parquet(os.path.join(hdfs_clean, "Delays"))
        trips = spark.read.parquet(os.path.join(hdfs_clean, "Trips"))
        route_stops = spark.read.parquet(os.path.join(hdfs_clean, "Route_Stops"))
        stops = spark.read.parquet(os.path.join(hdfs_clean, "Stops"))
    except Exception as e:
        print(f"Error loading clean parquet data: {e}")
        return

    # 2. Severity Breakdown
    # Using thresholds: On Time: 0-2, Minor: 2-5, Moderate: 5-15, Major: 15-30, Severe: 30+
    severity_df = delays.withColumn(
        "severity",
        when(col("delay_minutes") <= 2, "On Time")
        .when((col("delay_minutes") > 2) & (col("delay_minutes") <= 5), "Minor")
        .when((col("delay_minutes") > 5) & (col("delay_minutes") <= 15), "Moderate")
        .when((col("delay_minutes") > 15) & (col("delay_minutes") <= 30), "Major")
        .otherwise("Severe")
    )
    
    severity_counts = severity_df.groupBy("severity").agg(count("*").alias("value")).collect()
    severity_breakdown_json = [{"name": row["severity"], "value": row["value"]} for row in severity_counts]

    # Ensure all buckets exist
    buckets = ["On Time", "Minor", "Moderate", "Major", "Severe"]
    existing = {b["name"] for b in severity_breakdown_json}
    for b in buckets:
        if b not in existing:
            severity_breakdown_json.append({"name": b, "value": 0})
    # Sort logically
    severity_breakdown_json.sort(key=lambda x: buckets.index(x["name"]))

    # 3. Delay Trend (avg delay per day over last 30 days)
    trend_df = delays.withColumn("date", to_date("timestamp")) \
        .groupBy("date") \
        .agg(avg("delay_minutes").alias("total_delay")) \
        .orderBy("date")
    
    # If too many days, limit to last 30
    trend_rows = trend_df.tail(30)
    delay_trend_json = [{"date": str(row["date"]), "total_delay": round(row["total_delay"], 2)} for row in trend_rows]

    # 4. Bottlenecks (top 10 stops by frequency of association with delayed trips - join via Route_Stops)
    # Join delays with trips to get route_id
    delayed_trips = delays.filter(col("delay_minutes") > 5).join(trips, "trip_id")
    
    # Join with route_stops to get all stops for these delayed trips
    trip_stops = delayed_trips.join(route_stops, "route_id")
    
    # Count frequency of each stop being on a delayed route/trip
    bottleneck_counts = trip_stops.groupBy("stop_id") \
        .agg(count("*").alias("freq"), avg("delay_minutes").alias("avg_delay")) \
        .orderBy(desc("freq")) \
        .limit(10)
    
    # Join with stops to get names
    bottlenecks = bottleneck_counts.join(stops, "stop_id") \
        .select("stop_id", "stop_name", "avg_delay") \
        .orderBy(desc("avg_delay"))
    
    bottlenecks_json = [{"stop_id": row["stop_id"], "stop_name": row["stop_name"], "avg_delay": round(row["avg_delay"], 2)} for row in bottlenecks.collect()]

    # 5. Load to SQLite (UPSERT)
    db_path = os.path.join(base_path, "backend", "transit.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM delay_analysis_summaries")
    
    cursor.execute("""
        INSERT INTO delay_analysis_summaries 
        (severity_breakdown_json, delay_trend_json, bottlenecks_json, predicted_risks_json, computed_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        json.dumps(severity_breakdown_json),
        json.dumps(delay_trend_json),
        json.dumps(bottlenecks_json),
        json.dumps([]), # Empty array for Phase C
        datetime.utcnow().isoformat()
    ))
    
    conn.commit()
    conn.close()
    
    print("Delay Dashboard Analysis complete. Data saved to SQLite.")
    spark.stop()

if __name__ == "__main__":
    run_delay_dashboard_analysis()
