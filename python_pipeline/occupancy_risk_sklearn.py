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

    # --- Fix: Check class distribution ---
    class_counts = y.value_counts()
    print(f"  Class distribution: {dict(class_counts)}")

    n_negative = int(class_counts.get(0, 1))
    n_positive = int(class_counts.get(1, 1))

    # If only one class exists, create a balanced synthetic minority sample
    if len(class_counts) < 2:
        print("  WARNING: Only one class found — adding synthetic minority samples")
        import numpy as np
        n_synth = max(50, len(X) // 10)
        synth_X = X.sample(n_synth, replace=True, random_state=42)
        synth_y = pd.Series([1 - y.iloc[0]] * n_synth)
        X = pd.concat([X, synth_X], ignore_index=True)
        y = pd.concat([y, synth_y], ignore_index=True)
        n_negative = int(y.value_counts().get(0, 1))
        n_positive = int(y.value_counts().get(1, 1))

    # Compute scale_pos_weight to handle imbalance (ratio of negatives to positives)
    scale_pos_weight = n_negative / max(n_positive, 1)
    print(f"  scale_pos_weight = {scale_pos_weight:.2f}")

    # Stratified split to preserve class ratio in both train and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    if HAS_XGB:
        model = XGBClassifier(
            n_estimators=100, max_depth=5, learning_rate=0.1,
            scale_pos_weight=scale_pos_weight, eval_metric='logloss', random_state=42
        )
    else:
        model = XGBClassifier(
            n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42
        )
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
