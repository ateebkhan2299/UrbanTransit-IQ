from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, variance, stddev

def run():
    spark = SparkSession.builder.appName("TravelTimeAnalysis").getOrCreate()
    df = spark.read.parquet("./processed_data/features_trips.parquet") if os.path.exists("./processed_data/features_trips.parquet") else spark.createDataFrame([(1, 10), (1, 15), (2, 20)], ["route_id", "duration"])
    if "duration" in df.columns:
        res = df.groupBy("route_id").agg(avg("duration").alias("avg_time"), stddev("duration").alias("std_time"))
        res.write.mode("overwrite").parquet("./processed_data/analytics_14.parquet")
    spark.stop()

if __name__ == "__main__":
    run()
