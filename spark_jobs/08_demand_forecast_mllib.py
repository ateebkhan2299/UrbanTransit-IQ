import os
import sys
import json
import importlib
from pyspark.sql import functions as F
from pyspark.sql.functions import col
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml.evaluation import RegressionEvaluator

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import backend.config as config

ingest_module = importlib.import_module("spark_jobs.01_ingest")
get_spark_session = ingest_module.get_spark_session

PROCESSED_DATA_DIR = "./processed_data"
MODELS_DIR = "./models"

def train_demand_forecast_model(spark):
    print("=== PySpark MLlib Demand Forecast Pipeline ===")

    occ_path = os.path.join(PROCESSED_DATA_DIR, "features_occupancy.parquet")
    df = spark.read.parquet(occ_path)

    # Aggregate passenger demand sum per route, day, hour
    demand_df = df.groupBy("hour_of_day", "day_of_week", "is_peak_hour").agg(
        F.sum("boarded_count").alias("label")
    )

    feature_cols = ["hour_of_day", "day_of_week", "is_peak_hour"]
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
    data = assembler.transform(demand_df).select("features", col("label").cast("double"))

    train_df, test_df = data.randomSplit([0.8, 0.2], seed=42)

    rf = RandomForestRegressor(featuresCol="features", labelCol="label", numTrees=30, seed=42)
    model = rf.fit(train_df)

    predictions = model.transform(test_df)

    evaluator_rmse = RegressionEvaluator(labelCol="label", predictionCol="prediction", metricName="rmse")
    evaluator_r2 = RegressionEvaluator(labelCol="label", predictionCol="prediction", metricName="r2")
    evaluator_mae = RegressionEvaluator(labelCol="label", predictionCol="prediction", metricName="mae")

    rmse = evaluator_rmse.evaluate(predictions)
    r2 = evaluator_r2.evaluate(predictions)
    mae = evaluator_mae.evaluate(predictions)

    print(f"\n=== MLLIB DEMAND FORECAST EVALUATION ===")
    print(f"  RMSE: {rmse:.4f}")
    print(f"  MAE:  {mae:.4f}")
    print(f"  R2:   {r2:.4f}")

    os.makedirs(MODELS_DIR, exist_ok=True)
    metrics_info = {
        "model_type": "PySpark_MLlib_RandomForestRegressor",
        "features": feature_cols,
        "rmse": round(rmse, 4),
        "mae": round(mae, 4),
        "r2": round(r2, 4),
        "num_trees": model.getNumTrees
    }

    metrics_path = os.path.join(MODELS_DIR, "spark_forecast_model_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics_info, f, indent=2)

    print(f"\n[SAVED] Spark MLlib demand forecast model metrics saved to {metrics_path}")
    return model, metrics_info

if __name__ == "__main__":
    spark = get_spark_session(app_name="UrbanTransit_MLlib_Forecast")
    train_demand_forecast_model(spark)
    spark.stop()
