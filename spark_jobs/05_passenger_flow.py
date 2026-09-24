import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, desc

def run_passenger_flow():
    spark = SparkSession.builder \
        .appName("UrbanTransit_PassengerFlow") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()
        
    features_dir = "parquet_data/features"
    analytics_dir = "processed_data/analytics"
    os.makedirs(analytics_dir, exist_ok=True)
    
    trip_features = spark.read.parquet(os.path.join(features_dir, "trip_features.parquet"))
    
    # Simple EDA Logic for Flow
    print("Calculating Highest Demand Routes...")
    top_routes = trip_features.groupBy("route_id") \
        .sum("total_boardings").alias("total_passengers") \
        .orderBy(desc("sum(total_boardings)")).limit(10)
    
    top_routes.write.mode("overwrite").csv(os.path.join(analytics_dir, "top_10_routes.csv"), header=True)
    
    # Save a flag to indicate EDA/Flow computation is complete
    print("Passenger flow basic calculations complete.")
    spark.stop()

if __name__ == "__main__":
    run_passenger_flow()
