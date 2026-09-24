import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg

def run():
    spark = SparkSession.builder.appName("UrbanTransit_TravelTime").getOrCreate()
    trip_features = spark.read.parquet("parquet_data/features/trip_features.parquet")
    tt = trip_features.groupBy("route_id").agg(avg("scheduled_travel_time_min").alias("avg_scheduled_tt"))
    tt.write.mode("overwrite").parquet("parquet_data/analytics/travel_time_analysis.parquet")
    spark.stop()

if __name__ == "__main__":
    run()
