import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when

def run():
    spark = SparkSession.builder.appName("UrbanTransit_ScheduleAdherence").getOrCreate()
    trip_features = spark.read.parquet("parquet_data/features/trip_features.parquet")
    adherence = trip_features.withColumn(
        "adherence_status",
        when(col("total_delay_minutes") < -2, "Early")
        .when(col("total_delay_minutes") > 5, "Late")
        .otherwise("On-Time")
    )
    adherence.select("trip_id", "route_id", "adherence_status") \
        .write.mode("overwrite").parquet("parquet_data/analytics/schedule_adherence.parquet")
    spark.stop()

if __name__ == "__main__":
    run()
