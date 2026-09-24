import os
import sys
import json
import time
import pandas as pd
import numpy as np

# PySpark imports
from pyspark.sql import SparkSession
from pyspark.ml.regression import GBTRegressionModel, RandomForestRegressionModel
from pyspark.ml.classification import RandomForestClassificationModel
import joblib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.config import get_spark_session
from python_pipeline.feature_engineering import build_python_features

MODELS_DIR = "./models"
COMPARISON_DIR = "./comparison"

def run_dual_pipeline_comparison():
    print("=== Phase 8: Dual-Pipeline Comparison Engine ===")
    os.makedirs(COMPARISON_DIR, exist_ok=True)

    # 1. Load Pre-computed Metrics
    spark_delay_metrics = load_json_file(os.path.join(MODELS_DIR, "spark_delay_model_metrics.json"))
    python_delay_metrics = load_json_file(os.path.join(MODELS_DIR, "python_delay_model_metrics.json"))

    spark_forecast_metrics = load_json_file(os.path.join(MODELS_DIR, "spark_forecast_model_metrics.json"))
    python_forecast_metrics = load_json_file(os.path.join(MODELS_DIR, "python_forecast_model_metrics.json"))

    spark_clustering_metrics = load_json_file(os.path.join(MODELS_DIR, "spark_clustering_model_metrics.json"))
    python_clustering_metrics = load_json_file(os.path.join(MODELS_DIR, "python_clustering_model_metrics.json"))

    spark_occupancy_metrics = load_json_file(os.path.join(MODELS_DIR, "spark_occupancy_risk_model_metrics.json"))
    python_occupancy_metrics = load_json_file(os.path.join(MODELS_DIR, "python_occupancy_risk_model_metrics.json"))

    # 2. Side-by-side execution comparison on held-out sample
    feats = build_python_features()
    sample_df = feats["delays_features"].head(5)

    sample_cases = []
    for idx, row in sample_df.iterrows():
        sample_cases.append({
            "route_id": str(row.get("route_id", "R1")),
            "scheduled_delay_minutes": float(row.get("delay_minutes", 10.0)),
            "hour_of_day": int(row.get("hour_of_day", 8)),
            "day_of_week": int(row.get("day_of_week", 2)),
            "temperature_c": float(row.get("temperature_c", 20.0)),
            "is_peak_hour": int(row.get("is_peak_hour", 1))
        })

    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "models": {
            "delay_prediction": {
                "spark_mllib": spark_delay_metrics,
                "python_sklearn": python_delay_metrics,
                "winner": "python_sklearn" if (python_delay_metrics.get("r2", -1) > spark_delay_metrics.get("r2", -1)) else "spark_mllib"
            },
            "demand_forecast": {
                "spark_mllib": spark_forecast_metrics,
                "python_sklearn": python_forecast_metrics,
                "winner": "python_sklearn" if (python_forecast_metrics.get("r2", -1) > spark_forecast_metrics.get("r2", -1)) else "spark_mllib"
            },
            "route_clustering": {
                "spark_mllib": spark_clustering_metrics,
                "python_sklearn": python_clustering_metrics
            },
            "occupancy_risk": {
                "spark_mllib": spark_occupancy_metrics,
                "python_sklearn": python_occupancy_metrics,
                "winner": "python_sklearn" if (python_occupancy_metrics.get("f1", -1) > spark_occupancy_metrics.get("f1", -1)) else "spark_mllib"
            }
        },
        "sample_test_cases": sample_cases
    }

    report_path = os.path.join(COMPARISON_DIR, "model_comparison_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n[SUCCESS] Dual-Pipeline Comparison Report written to {report_path}")
    print("\n--- Summary Comparison Table ---")
    print(f"Task                   | Spark MLlib Metric               | Python Sklearn Metric            | Winner")
    print(f"-----------------------+----------------------------------+----------------------------------+-------------")
    print(f"Delay Prediction (R2)  | R2={spark_delay_metrics.get('r2', 'N/A'):.4f}                    | R2={python_delay_metrics.get('r2', 'N/A'):.4f}                   | {report['models']['delay_prediction']['winner']}")
    print(f"Demand Forecast (R2)   | R2={spark_forecast_metrics.get('r2', 'N/A'):.4f}                    | R2={python_forecast_metrics.get('r2', 'N/A'):.4f}                   | {report['models']['demand_forecast']['winner']}")
    print(f"Occupancy Risk (F1)    | F1={spark_occupancy_metrics.get('f1', 'N/A'):.4f}                    | F1={python_occupancy_metrics.get('f1', 'N/A'):.4f}                   | {report['models']['occupancy_risk']['winner']}")

    return report

def load_json_file(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {}

if __name__ == "__main__":
    run_dual_pipeline_comparison()
