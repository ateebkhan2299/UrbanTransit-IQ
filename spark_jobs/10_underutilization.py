import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count, when, round

def run_underutilization():
    spark = SparkSession.builder \
        .appName("UrbanTransit_Underutilization") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()
        
    features_dir = "parquet_data/features"
    trip_features = spark.read.parquet(os.path.join(features_dir, "trip_features.parquet"))
    
    print("Evaluating underutilized services...")
    
    # Underutilization cannot be judged on occupancy alone (social/feeder routes tricky case).
    # We require low occupancy AND low total passenger volume to mark it as underutilized.
    
    route_stats = trip_features.groupBy("route_id").agg(
        count("trip_id").alias("trip_count"),
        avg("vehicle_occupancy_pct").alias("avg_occupancy"),
        avg("total_boardings").alias("avg_boardings_per_trip")
    )
    
    # A route is underutilized if it averages < 20% occupancy AND < 10 boardings per trip
    underutilized = route_stats.withColumn(
        "is_underutilized",
        when((col("avg_occupancy") < 20) & (col("avg_boardings_per_trip") < 10), True).otherwise(False)
    )
    
    out_dir = "parquet_data/analytics"
    os.makedirs(out_dir, exist_ok=True)
    
    underutilized.write.mode("overwrite").parquet(os.path.join(out_dir, "underutilized_routes.parquet"))
        
    print("Underutilization evaluation complete.")
    spark.stop()

if __name__ == "__main__":
    run_underutilization()
