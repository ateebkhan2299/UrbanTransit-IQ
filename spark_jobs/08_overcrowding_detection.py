import os
import yaml
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when

def run_overcrowding_detection():
    # Phase 6: Single-trip Overcrowding Detection
    spark = SparkSession.builder \
        .appName("UrbanTransit_Overcrowding_Single") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()
        
    # Load Config for Thresholds
    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    thresh_overcrowded = config["thresholds"].get("overcrowding_occupancy_pct", 100)
    thresh_critical = config["thresholds"].get("critical_occupancy_pct", 120)
    
    # Load trip features from Phase 4
    features_dir = "parquet_data/features"
    trip_features = spark.read.parquet(os.path.join(features_dir, "trip_features.parquet"))
    
    print("Classifying trip-level crowding...")
    
    # Categorize occupancy
    crowded_trips = trip_features.withColumn(
        "crowding_category",
        when(col("vehicle_occupancy_pct") >= thresh_critical, "Critical")
        .when(col("vehicle_occupancy_pct") >= thresh_overcrowded, "Overcrowded")
        .when(col("vehicle_occupancy_pct") >= 75, "High")
        .when(col("vehicle_occupancy_pct") >= 30, "Moderate")
        .otherwise("Low")
    )
    
    out_dir = "parquet_data/analytics"
    os.makedirs(out_dir, exist_ok=True)
    
    crowded_trips.select("trip_id", "route_id", "vehicle_occupancy_pct", "crowding_category") \
        .write.mode("overwrite").parquet(os.path.join(out_dir, "single_trip_crowding.parquet"))
        
    print("Overcrowding detection complete.")
    spark.stop()

if __name__ == "__main__":
    run_overcrowding_detection()
