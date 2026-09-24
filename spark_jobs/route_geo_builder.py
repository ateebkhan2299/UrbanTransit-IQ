import os
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, collect_list, struct, avg, sum as spark_sum
import sqlite3

def run_route_geo_builder():
    print("Starting Route Geo Builder...")
    spark = SparkSession.builder \
        .appName("RouteGeoBuilder") \
        .getOrCreate()

    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    hdfs_clean = os.path.join(base_path, "hdfs_data", "parquet_clean")
    db_path = os.path.join(base_path, "backend", "transit.db")
    
    # 1. Load Data
    try:
        routes = spark.read.parquet(os.path.join(hdfs_clean, "Routes"))
        route_stops = spark.read.parquet(os.path.join(hdfs_clean, "Route_Stops"))
        stops = spark.read.parquet(os.path.join(hdfs_clean, "Stops"))
        passenger_counts = spark.read.parquet(os.path.join(hdfs_clean, "Passenger_Counts"))
        trips = spark.read.parquet(os.path.join(hdfs_clean, "Trips"))
    except Exception as e:
        print(f"Error loading clean parquet data: {e}")
        return

    # 2. Build stops_json (ONLY route's own stops, with lat/lng and boardings)
    # Get boardings per stop
    stop_boardings = passenger_counts.groupBy("stop_id").agg(spark_sum("boarding_count").alias("total_boardings"))
    stops_enriched = stops.join(stop_boardings, "stop_id", "left_outer").fillna(0, subset=["total_boardings"])

    # Join with route_stops
    rs_joined = route_stops.join(stops_enriched, "stop_id")
    
    route_stops_grouped = rs_joined.orderBy("route_id", "stop_sequence").groupBy("route_id").agg(
        collect_list(struct(
            col("stop_id"),
            col("stop_name"),
            col("latitude"),
            col("longitude"),
            col("total_boardings").alias("boardings")
        )).alias("stops_list"),
        collect_list(struct(
            col("latitude").alias("lat"),
            col("longitude").alias("lng")
        )).alias("path_list")
    )

    # 3. Get avg_occupancy from Trips
    # Assuming Trips has occupancy_pct, or we calculate it. 
    # If not in Trips, we just use a mock aggregate or check Trips schema. Let's calculate avg occupancy per route.
    if "occupancy_pct" in trips.columns:
        route_occupancy = trips.groupBy("route_id").agg(avg("occupancy_pct").alias("avg_occupancy"))
    else:
        # Fallback if occupancy_pct isn't there, though it should be generated in generate_dataset
        route_occupancy = trips.withColumn("occupancy_pct", (col("passenger_load") / col("capacity")) * 100) \
            .groupBy("route_id").agg(avg("occupancy_pct").alias("avg_occupancy"))

    # Join everything with routes
    routes_enriched = routes.join(route_stops_grouped, "route_id", "left_outer") \
        .join(route_occupancy, "route_id", "left_outer")
    
    result_data = [row.asDict(recursive=True) for row in routes_enriched.collect()]

    # 4. Fetch avg_delay from SQLite (RouteSummary)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT route_id, avg_delay_minutes FROM route_summaries")
    delay_dict = {row['route_id']: row['avg_delay_minutes'] for row in cursor.fetchall()}

    # Assign status color based on some simple logic, since this is Phase A
    def get_status(delay):
        if delay is None: return 'normal'
        if delay > 15: return 'high'
        if delay > 5: return 'moderate'
        return 'normal'

    final_routes = []
    for r in result_data:
        r_id = r['route_id']
        avg_del = delay_dict.get(r_id, 0.0)
        
        path_json = [[p['lat'], p['lng']] for p in r.get('path_list', [])] if r.get('path_list') else []
        stops_json = r.get('stops_list', [])
        
        final_routes.append({
            "route_id": r_id,
            "route_name": r.get('route_name', r_id),
            "status_color": get_status(avg_del),
            "path_json": path_json,
            "avg_delay": avg_del,
            "avg_occupancy": r.get('avg_occupancy') or 0.0,
            "stops_json": stops_json
        })

    # Save JSON to HDFS
    report_dir = os.path.join(base_path, "hdfs_data", "reports")
    os.makedirs(report_dir, exist_ok=True)
    with open(os.path.join(report_dir, "route_geo.json"), "w") as f:
        json.dump(final_routes, f, indent=2)

    # 5. UPSERT to SQLite
    for r in final_routes:
        cursor.execute("SELECT id FROM route_geos WHERE route_id = ?", (r["route_id"],))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE route_geos SET 
                    route_name = ?, status_color = ?, path_json = ?, avg_delay = ?, avg_occupancy = ?, stops_json = ?
                WHERE route_id = ?
            """, (
                r["route_name"], r["status_color"], json.dumps(r["path_json"]), r["avg_delay"], r["avg_occupancy"], json.dumps(r["stops_json"]), r["route_id"]
            ))
        else:
            cursor.execute("""
                INSERT INTO route_geos (route_id, route_name, status_color, path_json, avg_delay, avg_occupancy, stops_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                r["route_id"], r["route_name"], r["status_color"], json.dumps(r["path_json"]), r["avg_delay"], r["avg_occupancy"], json.dumps(r["stops_json"])
            ))

    conn.commit()
    conn.close()
    
    print("Route Geo Builder complete. Data saved to HDFS and SQLite.")
    spark.stop()

if __name__ == "__main__":
    run_route_geo_builder()
