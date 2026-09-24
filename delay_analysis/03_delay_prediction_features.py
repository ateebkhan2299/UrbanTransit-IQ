import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, dayofweek, hour

def extract_prediction_features():
    spark = SparkSession.builder \
        .appName("UrbanTransit_Delay_Features") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()
        
    features_dir = "parquet_data/features"
    out_dir = "parquet_data/ml_features"
    os.makedirs(out_dir, exist_ok=True)
    
    trip_features = spark.read.parquet(os.path.join(features_dir, "trip_features.parquet"))
    
    print("Extracting ML features for Delay Prediction...")
    
    # Base features for prediction
    ml_data = trip_features.select(
        col("route_id"),
        col("direction"),
        hour(col("scheduled_start")).alias("time_of_day"),
        dayofweek(col("scheduled_start")).alias("day_of_week"),
        col("rolling_route_occupancy").alias("historical_occupancy"),
        col("total_boardings").alias("passenger_load"),
        col("scheduled_travel_time_min"),
        col("total_delay_minutes").alias("label") # Target variable
    ).dropna()
    
    ml_data.write.mode("overwrite").parquet(os.path.join(out_dir, "delay_prediction_dataset.parquet"))
    
    print("ML features extracted.")
    spark.stop()

if __name__ == "__main__":
    extract_prediction_features()
