import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import hour, col, desc

def run_peak_periods():
    spark = SparkSession.builder \
        .appName("UrbanTransit_Peak_Periods") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()
        
    features_dir = "parquet_data/features"
    trip_features = spark.read.parquet(os.path.join(features_dir, "trip_features.parquet"))
    
    print("Statistically analyzing peak periods from demand curves...")
    
    # Extract hour from start_time
    # Note: start_time might be string if not cast, assuming timestamp.
    hourly_demand = trip_features.withColumn("hour", hour("scheduled_start")) \
        .groupBy("route_id", "hour") \
        .sum("total_boardings").alias("hourly_passengers") \
        .orderBy(desc("sum(total_boardings)"))
        
    analytics_dir = "processed_data/analytics"
    hourly_demand.write.mode("overwrite").csv(os.path.join(analytics_dir, "route_peak_hours.csv"), header=True)
    
    print("Peak periods analysis complete.")
    spark.stop()

if __name__ == "__main__":
    run_peak_periods()
