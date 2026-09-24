import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def run():
    spark = SparkSession.builder.appName("UrbanTransit_AnomalyDetection").getOrCreate()
    trip_features = spark.read.parquet("parquet_data/features/trip_features.parquet")
    
    # Statistical anomalies: Delay > 120 mins or Occupancy > 250%
    anomalies = trip_features.filter((col("total_delay_minutes") > 120) | (col("vehicle_occupancy_pct") > 250))
    anomalies.write.mode("overwrite").parquet("parquet_data/analytics/anomalies_detected.parquet")
    
    os.makedirs("reports", exist_ok=True)
    with open("reports/anomalies_detected.md", "w") as f:
        f.write(f"# Anomaly Detection Report\n\nDetected {anomalies.count()} severe statistical anomalies in operations.")
        
    spark.stop()

if __name__ == "__main__":
    run()
