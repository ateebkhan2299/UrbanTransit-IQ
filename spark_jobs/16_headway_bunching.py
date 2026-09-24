from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.functions import lag, col

def run():
    spark = SparkSession.builder.appName("HeadwayBunching").getOrCreate()
    df = spark.createDataFrame([("R1", 1, 100), ("R1", 1, 105), ("R1", 1, 150)], ["route_id", "stop_id", "timestamp"])
    w = Window.partitionBy("route_id", "stop_id").orderBy("timestamp")
    df = df.withColumn("headway", col("timestamp") - lag("timestamp").over(w))
    df.write.mode("overwrite").parquet("./processed_data/analytics_16.parquet")
    spark.stop()

if __name__ == "__main__":
    run()
