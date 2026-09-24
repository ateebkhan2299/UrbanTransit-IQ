import os
import sys

# Ensure backend.config sets JAVA_HOME before PySpark imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import backend.config

from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType, StructField, StringType, LongType, DoubleType
)

PARQUET_DATA_DIR = "./parquet_data"

def get_spark_session(app_name="UrbanTransit_Ingestion"):
    spark = SparkSession.builder \
        .appName(app_name) \
        .master("local[*]") \
        .config("spark.sql.parquet.enableVectorizedReader", "false") \
        .config("spark.hadoop.fs.file.impl", "org.apache.hadoop.fs.RawLocalFileSystem") \
        .config("spark.hadoop.io.native.lib.available", "false") \
        .getOrCreate()

    # Disable Hadoop NativeIO Windows DLL check
    try:
        spark.sparkContext._jsc.hadoopConfiguration().set("io.native.lib.available", "false")
    except Exception:
        pass

    return spark

# Explicit Schema Definitions matching Parquet data types
SCHEMAS = {
    "stops": StructType([
        StructField("stop_id", StringType(), True),
        StructField("stop_name", StringType(), True),
        StructField("latitude", DoubleType(), True),
        StructField("longitude", DoubleType(), True),
        StructField("zone_id", StringType(), True),
        StructField("wheelchair_boarding", LongType(), True)
    ]),
    "routes": StructType([
        StructField("route_id", StringType(), True),
        StructField("route_short_name", StringType(), True),
        StructField("route_long_name", StringType(), True),
        StructField("route_type", LongType(), True),
        StructField("agency_id", StringType(), True),
        StructField("fare_zone", StringType(), True)
    ]),
    "route_stops": StructType([
        StructField("route_id", StringType(), True),
        StructField("stop_id", StringType(), True),
        StructField("stop_sequence", LongType(), True),
        StructField("distance_from_start_km", DoubleType(), True)
    ]),
    "vehicles": StructType([
        StructField("vehicle_id", StringType(), True),
        StructField("vehicle_type", StringType(), True),
        StructField("capacity_seated", LongType(), True),
        StructField("capacity_standing", LongType(), True),
        StructField("total_capacity", LongType(), True),
        StructField("manufacture_year", LongType(), True)
    ]),
    "passengers": StructType([
        StructField("passenger_id", StringType(), True),
        StructField("card_type", StringType(), True),
        StructField("registration_date", StringType(), True)
    ]),
    "service_calendar": StructType([
        StructField("service_id", StringType(), True),
        StructField("monday", LongType(), True),
        StructField("tuesday", LongType(), True),
        StructField("wednesday", LongType(), True),
        StructField("thursday", LongType(), True),
        StructField("friday", LongType(), True),
        StructField("saturday", LongType(), True),
        StructField("sunday", LongType(), True),
        StructField("start_date", StringType(), True),
        StructField("end_date", StringType(), True)
    ]),
    "trips": StructType([
        StructField("trip_id", StringType(), True),
        StructField("route_id", StringType(), True),
        StructField("service_id", StringType(), True),
        StructField("vehicle_id", StringType(), True),
        StructField("direction_id", LongType(), True),
        StructField("start_time", StringType(), True),
        StructField("end_time", StringType(), True)
    ]),
    "schedules": StructType([
        StructField("schedule_id", StringType(), True),
        StructField("trip_id", StringType(), True),
        StructField("stop_id", StringType(), True),
        StructField("stop_sequence", LongType(), True),
        StructField("scheduled_arrival", StringType(), True),
        StructField("scheduled_departure", StringType(), True)
    ]),
    "tickets": StructType([
        StructField("ticket_id", StringType(), True),
        StructField("passenger_id", StringType(), True),
        StructField("trip_id", StringType(), True),
        StructField("origin_stop_id", StringType(), True),
        StructField("destination_stop_id", StringType(), True),
        StructField("fare_amount", DoubleType(), True),
        StructField("purchase_timestamp", StringType(), True),
        StructField("validation_timestamp", StringType(), True)
    ]),
    "passenger_counts": StructType([
        StructField("count_id", StringType(), True),
        StructField("trip_id", StringType(), True),
        StructField("stop_id", StringType(), True),
        StructField("stop_sequence", LongType(), True),
        StructField("timestamp", StringType(), True),
        StructField("boarded_count", LongType(), True),
        StructField("alighted_count", LongType(), True),
        StructField("current_occupancy", LongType(), True)
    ]),
    "delays": StructType([
        StructField("delay_id", StringType(), True),
        StructField("trip_id", StringType(), True),
        StructField("stop_id", StringType(), True),
        StructField("scheduled_time", StringType(), True),
        StructField("actual_time", StringType(), True),
        StructField("delay_minutes", LongType(), True),
        StructField("delay_cause", StringType(), True)
    ]),
    "gps_events": StructType([
        StructField("event_id", StringType(), True),
        StructField("vehicle_id", StringType(), True),
        StructField("trip_id", StringType(), True),
        StructField("timestamp", StringType(), True),
        StructField("latitude", DoubleType(), True),
        StructField("longitude", DoubleType(), True),
        StructField("speed_kmh", DoubleType(), True),
        StructField("heading", LongType(), True)
    ])
}

def ingest_data(spark, data_dir=PARQUET_DATA_DIR):
    print("=== PySpark Data Ingestion Pipeline ===")
    dataframes = {}
    for table_name, schema in SCHEMAS.items():
        file_path = os.path.join(data_dir, f"{table_name}.parquet")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Parquet file not found: {file_path}")

        df = spark.read.schema(schema).parquet(file_path)
        count = df.count()
        dataframes[table_name] = df

        print(f"\n--- Ingested Dataset: {table_name.upper()} (Row Count: {count}) ---")
        df.printSchema()

    print("\n[SUCCESS] Ingested all 12 PySpark DataFrames successfully.")
    return dataframes

if __name__ == "__main__":
    spark = get_spark_session()
    ingest_data(spark)
    spark.stop()
