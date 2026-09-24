import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, avg, max as _max, when, lag, unix_timestamp, round
from pyspark.sql.window import Window

def run_feature_engineering():
    spark = SparkSession.builder \
        .appName("UrbanTransit_Feature_Eng") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()
        
    clean_dir = "processed_data/clean"
    features_dir = "parquet_data/features"
    os.makedirs(features_dir, exist_ok=True)
    
    print("Loading clean datasets...")
    # Load required tables for trip_master
    trips_df = spark.read.parquet(os.path.join(clean_dir, "trips.parquet"))
    vehicles_df = spark.read.parquet(os.path.join(clean_dir, "vehicles.parquet"))
    pass_counts_df = spark.read.parquet(os.path.join(clean_dir, "passenger_counts.parquet"))
    delays_df = spark.read.parquet(os.path.join(clean_dir, "delays.parquet"))
    
    # 4.1 Integration logic directly applied to create trip_master equivalents
    # Join Trips + Vehicles for capacity
    trips_v = trips_df.join(vehicles_df, "vehicle_id", "left")
    
    # Aggregate delays per trip
    trip_delays = delays_df.groupBy("trip_id").agg(_sum("delay_minutes").alias("total_delay_minutes"))
    
    # Aggregate passengers per trip
    trip_pass = pass_counts_df.groupBy("trip_id").agg(
        _sum("boarding_count").alias("total_boardings"),
        _max("occupancy").alias("max_occupancy")
    )
    
    # 4.2 Feature Engineering
    print("Computing features...")
    # Base Join
    trip_features = trips_v.join(trip_delays, "trip_id", "left") \
                           .join(trip_pass, "trip_id", "left")
                           
    # Passenger/occupancy features
    trip_features = trip_features.withColumn("vehicle_occupancy_pct", round((col("max_occupancy") / col("capacity")) * 100, 2))
    trip_features = trip_features.withColumn("overcrowded_flag", when(col("vehicle_occupancy_pct") > 100, 1).otherwise(0))
    
    # Time features (Travel time in minutes)
    trip_features = trip_features.withColumn(
        "scheduled_travel_time_min", 
        round((unix_timestamp(col("end_time")) - unix_timestamp(col("start_time"))) / 60, 2)
    )
    
    # Fill null delays with 0
    trip_features = trip_features.fillna({"total_delay_minutes": 0})
    
    # Reliability
    trip_features = trip_features.withColumn(
        "is_delayed", 
        when(col("total_delay_minutes") > 5, 1).otherwise(0)
    )
    
    # Rolling Features (Route load factor / Historical average)
    window_spec = Window.partitionBy("route_id").orderBy("start_time").rowsBetween(-7, 0)
    trip_features = trip_features.withColumn("rolling_route_occupancy", avg("vehicle_occupancy_pct").over(window_spec))
    
    # Save Output
    print("Saving feature table...")
    trip_features.write.mode("overwrite").parquet(os.path.join(features_dir, "trip_features.parquet"))
    print(f"Features saved to {features_dir}/trip_features.parquet")
    
    spark.stop()

if __name__ == "__main__":
    run_feature_engineering()
