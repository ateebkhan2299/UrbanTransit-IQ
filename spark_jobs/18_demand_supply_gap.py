from pyspark.sql import SparkSession

def run():
    spark = SparkSession.builder.appName("DemandSupplyGap").getOrCreate()
    df = spark.createDataFrame([("R1", 100, 50)], ["route_id", "demand", "supply"])
    df.selectExpr("route_id", "demand - supply as gap").write.mode("overwrite").parquet("./processed_data/analytics_18.parquet")
    spark.stop()

if __name__ == "__main__":
    run()
