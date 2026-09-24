import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, count, when, round

def run_persistent_overcrowding():
    # Phase 6: Route-level Persistent Overcrowding
    spark = SparkSession.builder \
        .appName("UrbanTransit_Persistent_Overcrowding") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()
        
    features_dir = "parquet_data/features"
    trip_features = spark.read.parquet(os.path.join(features_dir, "trip_features.parquet"))
    
    print("Evaluating persistent route-level overcrowding...")
    
    # A single overloaded trip does NOT classify a route as overcrowded.
    # We require >= 20% of trips on the route+direction to be overcrowded to call it 'Persistent'
    
    route_direction_stats = trip_features.groupBy("route_id", "direction") \
        .agg(
            count("trip_id").alias("total_trips"),
            _sum("overcrowded_flag").alias("overcrowded_trips")
        )
        
    persistent = route_direction_stats.withColumn(
        "overcrowded_pct", 
        round((col("overcrowded_trips") / col("total_trips")) * 100, 2)
    ).withColumn(
        "is_persistently_overcrowded",
        when((col("overcrowded_pct") >= 20) & (col("total_trips") >= 10), True).otherwise(False)
    )
    
    out_dir = "parquet_data/analytics"
    os.makedirs(out_dir, exist_ok=True)
    
    persistent.write.mode("overwrite").parquet(os.path.join(out_dir, "persistent_overcrowding.parquet"))
        
    print("Persistent overcrowding evaluation complete.")
    spark.stop()

if __name__ == "__main__":
    run_persistent_overcrowding()
