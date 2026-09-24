import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, sum as _sum

def run_delay_analysis():
    spark = SparkSession.builder \
        .appName("UrbanTransit_Delay_Analysis") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()
        
    features_dir = "parquet_data/features"
    out_dir = "parquet_data/analytics"
    os.makedirs(out_dir, exist_ok=True)
    
    trip_features = spark.read.parquet(os.path.join(features_dir, "trip_features.parquet"))
    
    print("Running Descriptive Delay Analysis...")
    
    # 1. By Route
    route_delays = trip_features.groupBy("route_id") \
        .agg(avg("total_delay_minutes").alias("avg_route_delay"), 
             _sum("total_delay_minutes").alias("total_route_delay"))
    route_delays.write.mode("overwrite").parquet(os.path.join(out_dir, "delay_summary_route.parquet"))
    
    # 2. By Vehicle
    vehicle_delays = trip_features.groupBy("vehicle_id") \
        .agg(avg("total_delay_minutes").alias("avg_vehicle_delay"))
    vehicle_delays.write.mode("overwrite").parquet(os.path.join(out_dir, "delay_summary_vehicle.parquet"))
    
    # Note: Direction and Time of day aggregations can be built similarly.
    
    print("Descriptive Delay Analysis complete.")
    spark.stop()

if __name__ == "__main__":
    run_delay_analysis()
