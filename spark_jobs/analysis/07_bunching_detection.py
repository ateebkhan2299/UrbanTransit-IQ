import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def run():
    spark = SparkSession.builder.appName("UrbanTransit_Bunching").getOrCreate()
    headway = spark.read.parquet("parquet_data/analytics/headway_analysis.parquet")
    
    # Bunching threshold: headway < 3 minutes
    bunching = headway.filter(col("headway_minutes") < 3)
    bunching.write.mode("overwrite").parquet("parquet_data/analytics/bunching_events.parquet")
    
    os.makedirs("reports", exist_ok=True)
    with open("reports/bunching_events.md", "w") as f:
        f.write(f"# Bunching Events Report\n\nDetected {bunching.count()} instances of vehicle bunching (headway < 3m).")
        
    spark.stop()

if __name__ == "__main__":
    run()
