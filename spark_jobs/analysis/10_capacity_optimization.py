import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def run():
    spark = SparkSession.builder.appName("UrbanTransit_CapacityOpt").getOrCreate()
    gap = spark.read.parquet("parquet_data/analytics/demand_supply_gap.parquet")
    
    opt = gap.filter(col("gap_status") != "Balanced")
    opt.write.mode("overwrite").parquet("parquet_data/analytics/capacity_optimization.parquet")
    spark.stop()

if __name__ == "__main__":
    run()
