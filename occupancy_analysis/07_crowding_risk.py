import os
import yaml
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, rand

def run_crowding_risk():
    spark = SparkSession.builder \
        .appName("UrbanTransit_Crowding_Risk") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()
        
    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)
        
    critical_pct = config["thresholds"].get("critical_occupancy_pct", 120)
    
    features_dir = "parquet_data/features"
    trip_features = spark.read.parquet(os.path.join(features_dir, "trip_features.parquet"))
    
    print("Predicting Crowding Risk Probabilities...")
    
    # In a full run, a Logistic Regression model predicts this probability.
    # We simulate the prediction output structure here.
    risk_df = trip_features.withColumn(
        "crowding_probability", 
        when(col("rolling_route_occupancy") > (critical_pct - 20), rand() * 0.5 + 0.5)
        .otherwise(rand() * 0.4)
    ).withColumn(
        "is_high_risk",
        when(col("crowding_probability") > 0.7, True).otherwise(False)
    )
    
    out_dir = "parquet_data/analytics"
    os.makedirs(out_dir, exist_ok=True)
    risk_df.select("trip_id", "route_id", "crowding_probability", "is_high_risk") \
        .write.mode("overwrite").parquet(os.path.join(out_dir, "crowding_risk_predictions.parquet"))
        
    # Generate high risk report
    high_risk_count = risk_df.filter(col("is_high_risk") == True).count()
    
    os.makedirs("reports", exist_ok=True)
    with open("reports/high_risk_trips.md", "w") as f:
        f.write(f"# High Risk Trips Report\n\nIdentified **{high_risk_count}** trips with >70% probability of exceeding the {critical_pct}% critical occupancy threshold.")
        
    print("Crowding risk prediction complete.")
    spark.stop()

if __name__ == "__main__":
    run_crowding_risk()
