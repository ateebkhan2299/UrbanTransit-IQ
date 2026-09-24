import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def run():
    spark = SparkSession.builder.appName("UrbanTransit_SpecialEvent").getOrCreate()
    # Simple placeholder: Detect trips where occupancy > 200% as 'Special Events'
    trip_features = spark.read.parquet("parquet_data/features/trip_features.parquet")
    events = trip_features.filter(col("vehicle_occupancy_pct") > 200)
    events.write.mode("overwrite").parquet("parquet_data/analytics/special_events.parquet")
    spark.stop()

if __name__ == "__main__":
    run()
