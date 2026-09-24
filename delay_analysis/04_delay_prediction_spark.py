import os
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression, DecisionTreeRegressor, RandomForestRegressor
from pyspark.ml.evaluation import RegressionEvaluator

def run_spark_prediction():
    spark = SparkSession.builder \
        .appName("UrbanTransit_Delay_SparkML") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()
        
    data_dir = "parquet_data/ml_features/delay_prediction_dataset.parquet"
    if not os.path.exists(data_dir):
        print("Data not found. Run 03_delay_prediction_features.py first.")
        return
        
    df = spark.read.parquet(data_dir)
    
    # Vectorize features
    feature_cols = ["time_of_day", "day_of_week", "historical_occupancy", "passenger_load", "scheduled_travel_time_min"]
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
    ml_df = assembler.transform(df)
    
    # Chronological Split (simulated via rough split for sandbox, but in production use date filters)
    train_data, test_data = ml_df.randomSplit([0.8, 0.2], seed=42) 
    
    evaluator = RegressionEvaluator(labelCol="label", predictionCol="prediction", metricName="rmse")
    
    metrics = []
    
    print("Training Spark Models...")
    
    # Model 1: Linear Regression
    lr = LinearRegression(featuresCol="features", labelCol="label")
    lr_model = lr.fit(train_data)
    lr_preds = lr_model.transform(test_data)
    lr_rmse = evaluator.evaluate(lr_preds)
    metrics.append(f"| Spark Linear Regression | {lr_rmse:.2f} |")
    
    # Model 2: Decision Tree
    dt = DecisionTreeRegressor(featuresCol="features", labelCol="label")
    dt_model = dt.fit(train_data)
    dt_preds = dt_model.transform(test_data)
    dt_rmse = evaluator.evaluate(dt_preds)
    metrics.append(f"| Spark Decision Tree | {dt_rmse:.2f} |")
    
    # Model 3: Random Forest
    rf = RandomForestRegressor(featuresCol="features", labelCol="label", numTrees=10)
    rf_model = rf.fit(train_data)
    rf_preds = rf_model.transform(test_data)
    rf_rmse = evaluator.evaluate(rf_preds)
    metrics.append(f"| Spark Random Forest | {rf_rmse:.2f} |")
    
    # Save models
    os.makedirs("models/delay_spark", exist_ok=True)
    rf_model.write().overwrite().save("models/delay_spark/best_rf_model")
    
    # Append to metrics doc
    os.makedirs("reports", exist_ok=True)
    with open("reports/delay_model_metrics.md", "a") as f:
        f.write("\n".join(metrics) + "\n")
        
    print("Spark ML training complete. Metrics saved.")
    spark.stop()

if __name__ == "__main__":
    run_spark_prediction()
