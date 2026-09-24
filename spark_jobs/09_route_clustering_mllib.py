import os
import sys
import json
import importlib
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import backend.config as config

ingest_module = importlib.import_module("spark_jobs.01_ingest")
get_spark_session = ingest_module.get_spark_session

PROCESSED_DATA_DIR = "./processed_data"
MODELS_DIR = "./models"

def train_route_clustering_model(spark):
    print("=== PySpark MLlib Route Clustering Pipeline ===")

    summary_path = os.path.join(PROCESSED_DATA_DIR, "summary_route_performance.parquet")
    df = spark.read.parquet(summary_path)

    feature_cols = ["avg_occupancy_pct", "total_boardings", "overcrowded_events", "avg_delay_minutes", "performance_score"]
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="raw_features")
    assembled_data = assembler.transform(df)

    scaler = StandardScaler(inputCol="raw_features", outputCol="features", withStd=True, withMean=True)
    scaler_model = scaler.fit(assembled_data)
    data = scaler_model.transform(assembled_data)

    kmeans = KMeans(featuresCol="features", k=3, seed=42)
    model = kmeans.fit(data)

    predictions = model.transform(data)
    evaluator = ClusteringEvaluator(featuresCol="features", metricName="silhouette")
    silhouette = evaluator.evaluate(predictions)

    print(f"\n=== MLLIB ROUTE CLUSTERING EVALUATION ===")
    print(f"  K-Means Cluster Count: 3")
    print(f"  Silhouette Score:     {silhouette:.4f}")

    centers = [c.tolist() for c in model.clusterCenters()]
    print("\nCluster Centers:")
    for i, center in enumerate(centers):
        print(f"  Cluster {i}: {center}")

    os.makedirs(MODELS_DIR, exist_ok=True)
    metrics_info = {
        "model_type": "PySpark_MLlib_KMeans",
        "features": feature_cols,
        "k": 3,
        "silhouette": round(silhouette, 4),
        "cluster_centers": centers
    }

    metrics_path = os.path.join(MODELS_DIR, "spark_clustering_model_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics_info, f, indent=2)

    print(f"\n[SAVED] Spark MLlib route clustering model metrics saved to {metrics_path}")
    return model, metrics_info

if __name__ == "__main__":
    spark = get_spark_session(app_name="UrbanTransit_MLlib_Clustering")
    train_route_clustering_model(spark)
    spark.stop()
