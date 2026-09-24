import os
import yaml
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when

def run_severity_classification():
    spark = SparkSession.builder \
        .appName("UrbanTransit_Delay_Severity") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()
        
    # Load config dynamically
    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)
        
    minor = config["thresholds"].get("delay_minor_min", 5)
    moderate = config["thresholds"].get("delay_moderate_min", 15)
    major = config["thresholds"].get("delay_major_min", 30)
    severe = config["thresholds"].get("delay_severe_min", 60)
    
    features_dir = "parquet_data/features"
    trip_features = spark.read.parquet(os.path.join(features_dir, "trip_features.parquet"))
    
    print("Classifying Delay Severity...")
    
    classified = trip_features.withColumn(
        "delay_severity",
        when(col("total_delay_minutes") >= severe, "Severe Delay")
        .when(col("total_delay_minutes") >= major, "Major Delay")
        .when(col("total_delay_minutes") >= moderate, "Moderate Delay")
        .when(col("total_delay_minutes") >= minor, "Minor Delay")
        .otherwise("On Time")
    )
    
    out_dir = "parquet_data/analytics"
    classified.select("trip_id", "route_id", "total_delay_minutes", "delay_severity") \
        .write.mode("overwrite").parquet(os.path.join(out_dir, "delay_severity.parquet"))
        
    print("Delay Severity classification complete.")
    spark.stop()

if __name__ == "__main__":
    run_severity_classification()
