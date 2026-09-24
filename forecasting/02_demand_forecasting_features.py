import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, sum as _sum

def build_demand_features():
    spark = SparkSession.builder \
        .appName("UrbanTransit_Demand_Features") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()
        
    features_dir = "parquet_data/features"
    trip_features = spark.read.parquet(os.path.join(features_dir, "trip_features.parquet"))
    
    print("Building Demand Forecasting dataset...")
    
    # Aggregate daily demand per route
    daily_demand = trip_features.withColumn("travel_date", to_date(col("scheduled_start"))) \
        .groupBy("route_id", "travel_date") \
        .agg(_sum("total_boardings").alias("daily_passengers")) \
        .orderBy("travel_date")
        
    out_dir = "parquet_data/ml_features"
    os.makedirs(out_dir, exist_ok=True)
    
    daily_demand.write.mode("overwrite").parquet(os.path.join(out_dir, "daily_demand.parquet"))
    
    print("Demand features built.")
    spark.stop()

if __name__ == "__main__":
    build_demand_features()
