import os
import sys
import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    from sklearn.ensemble import GradientBoostingClassifier as XGBClassifier
    HAS_XGB = False
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from python_pipeline.feature_engineering import build_python_features

MODELS_DIR = "./models"

def train_python_occupancy_risk_model():
    print("=== Python DS Pipeline: Occupancy Risk Classification (XGBoost) ===")

    feats = build_python_features()
    occ_df = feats["occupancy_features"]

    feature_cols = ["hour_of_day", "day_of_week", "is_peak_hour", "total_capacity"]
    X = occ_df[feature_cols]
    y = occ_df["is_overcrowded"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = XGBClassifier(n_estimators=50, max_depth=5, learning_rate=0.1, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    print(f"\n=== PYTHON XGBOOST OCCUPANCY RISK EVALUATION ===")
    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1-Score:  {f1:.4f}")

    os.makedirs(MODELS_DIR, exist_ok=True)
    model_path = os.path.join(MODELS_DIR, "python_occupancy_risk_model.pkl")
    joblib.dump(model, model_path)

    metrics_info = {
        "model_type": "XGBoost_XGBClassifier" if HAS_XGB else "GradientBoostingClassifier",
        "features": feature_cols,
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4)
    }

    metrics_path = os.path.join(MODELS_DIR, "python_occupancy_risk_model_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics_info, f, indent=2)

    print(f"\n[SAVED] Python occupancy risk model saved to {model_path} and {metrics_path}")
    return model, metrics_info

if __name__ == "__main__":
    train_python_occupancy_risk_model()
