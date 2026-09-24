from pyspark.sql import SparkSession

def run():
    spark = SparkSession.builder.appName("ServiceFrequency").getOrCreate()
    df = spark.createDataFrame([("R1", 8), ("R1", 9)], ["route_id", "hour_of_day"])
    df.groupBy("route_id", "hour_of_day").count().write.mode("overwrite").parquet("./processed_data/analytics_17.parquet")
    spark.stop()

if __name__ == "__main__":
    run()
