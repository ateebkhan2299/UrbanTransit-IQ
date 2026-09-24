import os
from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.functions import avg, col, lag

def run_spark_forecast():
    spark = SparkSession.builder \
        .appName("UrbanTransit_Demand_Forecast_Spark") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()
        
    data_dir = "parquet_data/ml_features/daily_demand.parquet"
    if not os.path.exists(data_dir):
        print("Dataset not found.")
        return
        
    df = spark.read.parquet(data_dir)
    print("Running Spark Baseline Forecast (7-day rolling)...")
    
    # 7-day rolling average (Baseline)
    # Ensure chronological validity (only use past data)
    window_spec = Window.partitionBy("route_id").orderBy("travel_date").rowsBetween(-7, -1)
    
    forecast_df = df.withColumn("forecast_passengers", avg("daily_passengers").over(window_spec))
    
    out_dir = "parquet_data/analytics"
    forecast_df.write.mode("overwrite").parquet(os.path.join(out_dir, "spark_demand_forecast.parquet"))
    
    print("Spark Forecast baseline complete.")
    spark.stop()

if __name__ == "__main__":
    run_spark_forecast()
