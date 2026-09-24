import argparse
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, TimestampType
import sys

def main(raw_dir, out_dir):
    spark = SparkSession.builder \
        .appName("UrbanTransitIQ_Ingestion") \
        .getOrCreate()
    
    # 1. Explicit Schemas
    trips_schema = StructType([
        StructField("trip_id", StringType(), True),
        StructField("route_id", StringType(), True),
        StructField("vehicle_id", StringType(), True),
        StructField("service_date", StringType(), True),
        StructField("scheduled_start", StringType(), True),
        StructField("status", StringType(), True)
    ])

    tickets_schema = StructType([
        StructField("ticket_id", StringType(), True),
        StructField("passenger_id", StringType(), True),
        StructField("trip_id", StringType(), True),
        StructField("boarding_stop_id", StringType(), True),
        StructField("alighting_stop_id", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("fare", FloatType(), True)
    ])

    delays_schema = StructType([
        StructField("delay_id", StringType(), True),
        StructField("trip_id", StringType(), True),
        StructField("stop_id", StringType(), True),
        StructField("service_date", StringType(), True),
        StructField("delay_minutes", IntegerType(), True),
        StructField("cause", StringType(), True)
    ])

    pc_schema = StructType([
        StructField("count_id", StringType(), True),
        StructField("trip_id", StringType(), True),
        StructField("stop_id", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("boarding_count", IntegerType(), True),
        StructField("alighting_count", IntegerType(), True)
    ])

    # Ingest Trips
    print("Ingesting Trips...")
    trips_df = spark.read.csv(f"{raw_dir}/Trips.csv", schema=trips_schema, header=True, mode="PERMISSIVE")
    trips_count = trips_df.count()
    print(f"Trips loaded: {trips_count}")
    trips_df.write.partitionBy("service_date").parquet(f"{out_dir}/parquet/trips", mode="overwrite")
    trips_df.write.partitionBy("service_date").json(f"{out_dir}/json/trips", mode="overwrite")

    # Ingest Tickets
    print("Ingesting Tickets...")
    tickets_df = spark.read.csv(f"{raw_dir}/Tickets.csv", schema=tickets_schema, header=True, mode="PERMISSIVE")
    print(f"Tickets loaded: {tickets_df.count()}")
    tickets_df.write.parquet(f"{out_dir}/parquet/tickets", mode="overwrite")
    tickets_df.write.json(f"{out_dir}/json/tickets", mode="overwrite")

    # Ingest Delays
    print("Ingesting Delays...")
    delays_df = spark.read.csv(f"{raw_dir}/Delays.csv", schema=delays_schema, header=True, mode="PERMISSIVE")
    print(f"Delays loaded: {delays_df.count()}")
    delays_df.write.partitionBy("service_date").parquet(f"{out_dir}/parquet/delays", mode="overwrite")
    delays_df.write.partitionBy("service_date").json(f"{out_dir}/json/delays", mode="overwrite")

    # Ingest Passenger_Counts
    print("Ingesting Passenger Counts...")
    pc_df = spark.read.csv(f"{raw_dir}/Passenger_Counts.csv", schema=pc_schema, header=True, mode="PERMISSIVE")
    print(f"Passenger Counts loaded: {pc_df.count()}")
    pc_df.write.parquet(f"{out_dir}/parquet/passenger_counts", mode="overwrite")
    pc_df.write.json(f"{out_dir}/json/passenger_counts", mode="overwrite")

    # Schema Inference Example: Vehicles
    print("Ingesting Vehicles (with schema inference)...")
    vehicles_df = spark.read.csv(f"{raw_dir}/Vehicles.csv", inferSchema=True, header=True)
    vehicles_df.printSchema()
    print(f"Vehicles loaded: {vehicles_df.count()}")
    vehicles_df.write.parquet(f"{out_dir}/parquet/vehicles", mode="overwrite")
    vehicles_df.write.json(f"{out_dir}/json/vehicles", mode="overwrite")

    # Also ingest Routes & Stops so they are available
    routes_df = spark.read.csv(f"{raw_dir}/Routes.csv", inferSchema=True, header=True)
    routes_df.write.parquet(f"{out_dir}/parquet/routes", mode="overwrite")
    
    stops_df = spark.read.csv(f"{raw_dir}/Stops.csv", inferSchema=True, header=True)
    stops_df.write.parquet(f"{out_dir}/parquet/stops", mode="overwrite")

    print("Ingestion complete.")
    spark.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=str, default="raw_data", help="Path to raw CSVs")
    parser.add_argument("--out", type=str, default="parquet_data/raw", help="Output path for Parquet/JSON")
    args = parser.parse_args()
    main(args.raw, args.out)
