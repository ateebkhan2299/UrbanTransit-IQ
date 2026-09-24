import os
import sys
import json
import importlib
from pyspark.sql.functions import col
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import backend.config as config

ingest_module = importlib.import_module("spark_jobs.01_ingest")
get_spark_session = ingest_module.get_spark_session

PROCESSED_DATA_DIR = "./processed_data"
MODELS_DIR = "./models"

def train_occupancy_risk_model(spark):
    print("=== PySpark MLlib Occupancy Risk Classification Pipeline ===")

    occ_path = os.path.join(PROCESSED_DATA_DIR, "features_occupancy.parquet")
    df = spark.read.parquet(occ_path)

    feature_cols = ["hour_of_day", "day_of_week", "is_peak_hour", "total_capacity", "headway_minutes"]
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
    data = assembler.transform(df).select("features", col("is_overcrowded").cast("double").alias("label"))

    train_df, test_df = data.randomSplit([0.8, 0.2], seed=42)

    rf = RandomForestClassifier(featuresCol="features", labelCol="label", numTrees=40, maxDepth=6, seed=42)
    model = rf.fit(train_df)

    predictions = model.transform(test_df)

    evaluator_acc = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")
    evaluator_f1 = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="f1")
    evaluator_prec = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="weightedPrecision")
    evaluator_rec = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="weightedRecall")

    accuracy = evaluator_acc.evaluate(predictions)
    f1 = evaluator_f1.evaluate(predictions)
    precision = evaluator_prec.evaluate(predictions)
    recall = evaluator_rec.evaluate(predictions)

    print(f"\n=== MLLIB OCCUPANCY RISK EVALUATION ===")
    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1-Score:  {f1:.4f}")

    os.makedirs(MODELS_DIR, exist_ok=True)
    metrics_info = {
        "model_type": "PySpark_MLlib_RandomForestClassifier",
        "features": feature_cols,
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "num_trees": model.getNumTrees
    }

    metrics_path = os.path.join(MODELS_DIR, "spark_occupancy_risk_model_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics_info, f, indent=2)

    print(f"\n[SAVED] Spark MLlib occupancy risk model metrics saved to {metrics_path}")
    return model, metrics_info

if __name__ == "__main__":
    spark = get_spark_session(app_name="UrbanTransit_MLlib_OccupancyRisk")
    train_occupancy_risk_model(spark)
    spark.stop()
