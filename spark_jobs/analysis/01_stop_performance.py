import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, sum as _sum

def run():
    spark = SparkSession.builder.appName("UrbanTransit_StopPerf").getOrCreate()
    trip_features = spark.read.parquet("parquet_data/features/trip_features.parquet")
    # In a full flow we would join with stops/route_stops. Here we simulate using trip data.
    perf = trip_features.groupBy("stop_id").agg(
        _sum("total_boardings").alias("total_boardings"),
        avg("total_delay_minutes").alias("avg_delay")
    )
    os.makedirs("parquet_data/analytics", exist_ok=True)
    perf.write.mode("overwrite").parquet("parquet_data/analytics/stop_performance.parquet")
    spark.stop()

if __name__ == "__main__":
    run()
