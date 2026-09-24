import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, when, round

def run_performance_scoring():
    spark = SparkSession.builder \
        .appName("UrbanTransit_Performance_Score") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()
        
    features_dir = "parquet_data/features"
    analytics_dir = "parquet_data/analytics"
    
    trip_features = spark.read.parquet(os.path.join(features_dir, "trip_features.parquet"))
    
    print("Calculating composite route performance scores...")
    
    # Aggregate route metrics
    route_metrics = trip_features.groupBy("route_id").agg(
        avg("vehicle_occupancy_pct").alias("avg_occupancy"),
        avg("total_boardings").alias("avg_demand"),
        avg("total_delay_minutes").alias("avg_delay")
    )
    
    # Calculate score out of 100
    # Base 100 - Delay penalty - Extreme occupancy penalty
    # Note: 60-80% occupancy is ideal. >100% or <20% gets penalized.
    scored = route_metrics.withColumn(
        "occupancy_penalty",
        when(col("avg_occupancy") > 100, (col("avg_occupancy") - 100) * 0.5)
        .when(col("avg_occupancy") < 20, (20 - col("avg_occupancy")) * 0.5)
        .otherwise(0)
    ).withColumn(
        "delay_penalty",
        when(col("avg_delay") > 0, col("avg_delay") * 2).otherwise(0)
    )
    
    scored = scored.withColumn(
        "performance_score", 
        round(100 - col("occupancy_penalty") - col("delay_penalty"), 2)
    )
    
    # Bound score between 0 and 100
    scored = scored.withColumn(
        "performance_score",
        when(col("performance_score") < 0, 0)
        .when(col("performance_score") > 100, 100)
        .otherwise(col("performance_score"))
    )
    
    # Route Classification
    classified = scored.withColumn(
        "route_classification",
        when((col("performance_score") >= 80) & (col("avg_delay") <= 5), "High Performing")
        .when((col("avg_demand") > 50) & (col("avg_delay") > 15), "High Demand, but Unreliable")
        .when((col("avg_occupancy") < 30) & (col("performance_score") >= 75), "Reliable, but Underutilized")
        .when(col("avg_occupancy") > 100, "Overcrowded")
        .otherwise("Low Performing")
    )
    
    classified.write.mode("overwrite").parquet(os.path.join(analytics_dir, "route_scores.parquet"))
        
    print("Route performance scoring & classification complete.")
    spark.stop()

if __name__ == "__main__":
    run_performance_scoring()
