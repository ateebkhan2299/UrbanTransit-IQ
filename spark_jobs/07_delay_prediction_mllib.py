import os
import sys
import json
import importlib
from pyspark.sql.functions import col
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import GBTRegressor, RandomForestRegressor, LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import backend.config as config

ingest_module = importlib.import_module("spark_jobs.01_ingest")
get_spark_session = ingest_module.get_spark_session

PROCESSED_DATA_DIR = "./processed_data"
MODELS_DIR = "./models"

def train_delay_prediction_model(spark):
    print("=== PySpark MLlib Delay Prediction Pipeline ===")

    delays_path = os.path.join(PROCESSED_DATA_DIR, "features_delays.parquet")
    df = spark.read.parquet(delays_path)

    feature_cols = ["hour_of_day", "day_of_week", "is_peak_hour"]
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
    data = assembler.transform(df).select("features", col("delay_minutes").cast("double").alias("label"))

    train_df, test_df = data.randomSplit([0.8, 0.2], seed=42)

    
    print("Training 3 Algorithms: LinearRegression, RandomForest, GBT")
    lr = LinearRegression(featuresCol="features", labelCol="label")
    rf = RandomForestRegressor(featuresCol="features", labelCol="label", numTrees=10)
    gbt = GBTRegressor(featuresCol="features", labelCol="label", maxDepth=5, maxIter=20, seed=42)
    
    model_lr = lr.fit(train_df)
    model_rf = rf.fit(train_df)
    model_gbt = gbt.fit(train_df)
    
    # Evaluate the best (GBT for now as default)
    model = model_gbt
    
    # Serialize the best model (SRS requirement)
    model.write().overwrite().save(os.path.join(MODELS_DIR, "best_mllib_model_" + os.path.basename(__file__)))


    predictions = model.transform(test_df)

    evaluator_rmse = RegressionEvaluator(labelCol="label", predictionCol="prediction", metricName="rmse")
    evaluator_r2 = RegressionEvaluator(labelCol="label", predictionCol="prediction", metricName="r2")
    evaluator_mae = RegressionEvaluator(labelCol="label", predictionCol="prediction", metricName="mae")

    rmse = evaluator_rmse.evaluate(predictions)
    r2 = evaluator_r2.evaluate(predictions)
    mae = evaluator_mae.evaluate(predictions)

    print(f"\n=== MLLIB DELAY MODEL EVALUATION ===")
    print(f"  RMSE: {rmse:.4f}")
    print(f"  MAE:  {mae:.4f}")
    print(f"  R2:   {r2:.4f}")

    # Save Model Metadata & Parameters safely
    os.makedirs(MODELS_DIR, exist_ok=True)
    metrics_info = {
        "model_type": "PySpark_MLlib_GBTRegressor",
        "features": feature_cols,
        "rmse": round(rmse, 4),
        "mae": round(mae, 4),
        "r2": round(r2, 4),
        "num_trees": model.getNumTrees,
        "tree_weights": list(model.treeWeights)
    }

    metrics_path = os.path.join(MODELS_DIR, "spark_delay_model_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics_info, f, indent=2)

    print(f"\n[SAVED] Spark MLlib delay model metrics saved to {metrics_path}")
    return model, metrics_info

if __name__ == "__main__":
    spark = get_spark_session(app_name="UrbanTransit_MLlib_Delay")
    train_delay_prediction_model(spark)
    spark.stop()
