import os
import yaml
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lag, unix_timestamp
from pyspark.sql.window import Window

def run():
    spark = SparkSession.builder.appName("UrbanTransit_Headway").getOrCreate()
    trip_features = spark.read.parquet("parquet_data/features/trip_features.parquet")
    
    # Calculate headway: difference between this trip's start and previous trip's start on same route+direction
    window_spec = Window.partitionBy("route_id", "direction").orderBy("scheduled_start")
    
    headway = trip_features.withColumn(
        "prev_start", lag("scheduled_start").over(window_spec)
    ).withColumn(
        "headway_minutes", (unix_timestamp("scheduled_start") - unix_timestamp("prev_start")) / 60
    )
    
    headway.select("trip_id", "route_id", "headway_minutes") \
        .write.mode("overwrite").parquet("parquet_data/analytics/headway_analysis.parquet")
    spark.stop()

if __name__ == "__main__":
    run()
