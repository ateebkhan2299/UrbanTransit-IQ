import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, desc

def run_pattern_detection():
    spark = SparkSession.builder \
        .appName("UrbanTransit_Delay_Patterns") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()
        
    features_dir = "parquet_data/features"
    trip_features = spark.read.parquet(os.path.join(features_dir, "trip_features.parquet"))
    
    print("Running Delay Pattern Detection...")
    
    # A common pattern: Vehicles consistently delayed vs fleet average
    global_avg_delay = trip_features.select(avg("total_delay_minutes")).collect()[0][0]
    
    vehicle_patterns = trip_features.groupBy("vehicle_id") \
        .agg(avg("total_delay_minutes").alias("avg_vehicle_delay")) \
        .filter(col("avg_vehicle_delay") > (global_avg_delay * 1.5)) \
        .orderBy(desc("avg_vehicle_delay"))
        
    out_dir = "parquet_data/analytics"
    vehicle_patterns.write.mode("overwrite").parquet(os.path.join(out_dir, "delay_pattern_vehicles.parquet"))
    
    print(f"Global avg delay: {global_avg_delay}. Identified {vehicle_patterns.count()} vehicle outliers.")
    spark.stop()

if __name__ == "__main__":
    run_pattern_detection()
