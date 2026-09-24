import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg

def run():
    spark = SparkSession.builder.appName("UrbanTransit_ServiceFrequency").getOrCreate()
    trip_features = spark.read.parquet("parquet_data/features/trip_features.parquet")
    
    freq = trip_features.groupBy("route_id").agg(
        count("trip_id").alias("total_trips"),
        avg("vehicle_occupancy_pct").alias("avg_occupancy")
    )
    freq.write.mode("overwrite").parquet("parquet_data/analytics/service_frequency.parquet")
    spark.stop()

if __name__ == "__main__":
    run()
