from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when

def run():
    spark = SparkSession.builder.appName("ScheduleAdherence").getOrCreate()
    df = spark.read.parquet("./processed_data/features_delays.parquet") if os.path.exists("./processed_data/features_delays.parquet") else spark.createDataFrame([(1, 2.0), (1, 10.0)], ["route_id", "delay_minutes"])
    if "delay_minutes" in df.columns:
        res = df.withColumn("adherence", when(col("delay_minutes") <= 3, "On-Time").otherwise("Late"))
        res.groupBy("route_id", "adherence").count().write.mode("overwrite").parquet("./processed_data/analytics_15.parquet")
    spark.stop()

if __name__ == "__main__":
    run()
