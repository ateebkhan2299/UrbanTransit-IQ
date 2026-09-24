import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, stddev

def run():
    spark = SparkSession.builder.appName("UrbanTransit_RouteReliability").getOrCreate()
    trip_features = spark.read.parquet("parquet_data/features/trip_features.parquet")
    rel = trip_features.groupBy("route_id").agg(stddev("total_delay_minutes").alias("delay_variation"))
    rel.write.mode("overwrite").parquet("parquet_data/analytics/route_reliability.parquet")
    spark.stop()

if __name__ == "__main__":
    run()
