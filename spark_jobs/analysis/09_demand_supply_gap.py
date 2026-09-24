import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when

def run():
    spark = SparkSession.builder.appName("UrbanTransit_DemandSupply").getOrCreate()
    trip_features = spark.read.parquet("parquet_data/features/trip_features.parquet")
    
    gap = trip_features.withColumn(
        "gap_status",
        when(col("total_boardings") > col("capacity"), "Excess Demand")
        .when(col("total_boardings") < (col("capacity") * 0.2), "Excess Supply")
        .otherwise("Balanced")
    )
    gap.select("trip_id", "route_id", "capacity", "total_boardings", "gap_status") \
        .write.mode("overwrite").parquet("parquet_data/analytics/demand_supply_gap.parquet")
    spark.stop()

if __name__ == "__main__":
    run()
