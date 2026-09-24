from pyspark.sql import SparkSession

def run():
    spark = SparkSession.builder.appName("SpecialEventDetection").getOrCreate()
    df = spark.createDataFrame([("R1", 500, 100)], ["route_id", "current_riders", "avg_riders"])
    df.filter("current_riders > avg_riders * 2").write.mode("overwrite").parquet("./processed_data/analytics_19.parquet")
    spark.stop()

if __name__ == "__main__":
    run()
