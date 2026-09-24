import os
import json
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, hour, sum as spark_sum, count, avg, desc, lit, to_timestamp, avg as spark_avg
import sqlite3

def run_passenger_flow_analysis():
    print("Starting Passenger Flow Analysis...")
    spark = SparkSession.builder \
        .appName("PassengerFlowAnalysis") \
        .config("spark.sql.session.timeZone", "UTC") \
        .getOrCreate()

    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    hdfs_clean = os.path.join(base_path, "hdfs_data", "parquet_clean")
    
    # 1. Load Data
    try:
        trips = spark.read.parquet(os.path.join(hdfs_clean, "Trips"))
        tickets = spark.read.parquet(os.path.join(hdfs_clean, "Tickets"))
        passenger_counts = spark.read.parquet(os.path.join(hdfs_clean, "Passenger_Counts"))
        stops = spark.read.parquet(os.path.join(hdfs_clean, "Stops"))
    except Exception as e:
        print(f"Error loading clean parquet data: {e}")
        return

    # Convert timestamps if necessary
    tickets = tickets.withColumn("timestamp", to_timestamp("timestamp"))
    passenger_counts = passenger_counts.withColumn("timestamp", to_timestamp("timestamp"))

    # 2. Compute Boarding/Alighting per hour
    ba_hourly = passenger_counts.withColumn("time", hour("timestamp")) \
        .groupBy("time") \
        .agg(
            spark_sum("boarding_count").alias("boarding"),
            spark_sum("alighting_count").alias("alighting")
        ).orderBy("time")
    
    boarding_alighting_json = [{"time": f"{row['time']:02d}:00", "boarding": int(row['boarding']), "alighting": int(row['alighting'])} for row in ba_hourly.collect()]

    # 3. OD Matrix (top 200 pairs)
    # Join tickets with trips to get route_id and day_type
    tickets_joined = tickets.join(trips, "trip_id")
    
    od_counts = tickets_joined.groupBy("boarding_stop_id", "alighting_stop_id", "route_id", "day_type") \
        .agg(count("*").alias("count")) \
        .orderBy(desc("count")) \
        .limit(200)

    # Bring in stop names
    od_counts = od_counts.alias("od").join(stops.alias("s1"), col("od.boarding_stop_id") == col("s1.stop_id")) \
        .join(stops.alias("s2"), col("od.alighting_stop_id") == col("s2.stop_id")) \
        .select(
            col("s1.stop_name").alias("origin"),
            col("s2.stop_name").alias("destination"),
            col("od.count"),
            col("od.route_id"),
            col("od.day_type")
        ).orderBy(desc("count"))

    od_matrix_json = [row.asDict() for row in od_counts.collect()]

    # 4. Peak Periods
    hourly_volume = tickets.withColumn("hour", hour("timestamp")) \
        .groupBy("hour") \
        .agg(count("*").alias("volume"))

    avg_hourly = hourly_volume.select(spark_avg("volume")).first()[0]
    peak_threshold = avg_hourly * 1.5

    peak_periods = hourly_volume.withColumn("is_peak", col("volume") > peak_threshold) \
        .orderBy("hour")
    
    peak_periods_json = [{"time": f"{row['hour']:02d}:00", "volume": int(row['volume']), "is_peak": row['is_peak']} for row in peak_periods.collect()]

    total_demand = tickets.count()
    
    # Busiest stop
    busiest = passenger_counts.groupBy("stop_id").agg(spark_sum("boarding_count").alias("t_boarding")) \
        .join(stops, "stop_id") \
        .orderBy(desc("t_boarding")) \
        .select("stop_name").first()
    
    busiest_stop_name = busiest["stop_name"] if busiest else "Unknown"

    # Write JSON report
    report_dir = os.path.join(base_path, "hdfs_data", "reports")
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, "passenger_flow.json")
    
    report_data = {
        "boarding_alighting": boarding_alighting_json,
        "od_matrix": od_matrix_json,
        "peak_periods": peak_periods_json,
        "total_demand": total_demand,
        "busiest_stop": busiest_stop_name
    }
    
    with open(report_path, "w") as f:
        json.dump(report_data, f, indent=2)

    # 5. Load to SQLite (UPSERT)
    db_path = os.path.join(base_path, "backend", "transit.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Clear existing
    cursor.execute("DELETE FROM passenger_flow_summaries")
    
    # Insert new
    cursor.execute("""
        INSERT INTO passenger_flow_summaries 
        (boarding_alighting_json, od_matrix_json, peak_periods_json, total_demand, busiest_stop_name, computed_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        json.dumps(boarding_alighting_json),
        json.dumps(od_matrix_json),
        json.dumps(peak_periods_json),
        total_demand,
        busiest_stop_name,
        datetime.utcnow().isoformat()
    ))
    
    conn.commit()
    conn.close()
    
    print("Passenger Flow Analysis complete. Data saved to HDFS and SQLite.")
    spark.stop()

if __name__ == "__main__":
    run_passenger_flow_analysis()
