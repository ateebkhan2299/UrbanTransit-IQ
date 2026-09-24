import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def run():
    spark = SparkSession.builder.appName("UrbanTransit_Bottleneck").getOrCreate()
    perf = spark.read.parquet("parquet_data/analytics/stop_performance.parquet")
    bottlenecks = perf.filter((col("avg_delay") > 5) & (col("total_boardings") > 100))
    bottlenecks.write.mode("overwrite").parquet("parquet_data/analytics/bottleneck_stops.parquet")
    spark.stop()

if __name__ == "__main__":
    run()
