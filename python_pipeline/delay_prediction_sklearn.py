import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from python_pipeline.feature_engineering import build_python_features

MODELS_DIR = "./models"

def train_python_delay_model():
    print("=== Python DS Pipeline: Delay Prediction (Scikit-Learn) ===")

    feats = build_python_features()
    delays_df = feats["delays_features"]

    feature_cols = ["hour_of_day", "day_of_week", "is_peak_hour"]
    X = delays_df[feature_cols]
    y = delays_df["delay_minutes"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = HistGradientBoostingRegressor(max_iter=100, max_depth=5, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    mae = float(mean_absolute_error(y_test, y_pred))
    r2 = float(r2_score(y_test, y_pred))

    print(f"\n=== PYTHON SKLEARN DELAY MODEL EVALUATION ===")
    print(f"  RMSE: {rmse:.4f}")
    print(f"  MAE:  {mae:.4f}")
    print(f"  R2:   {r2:.4f}")

    os.makedirs(MODELS_DIR, exist_ok=True)
    model_path = os.path.join(MODELS_DIR, "python_delay_model.pkl")
    joblib.dump(model, model_path)

    metrics_info = {
        "model_type": "Scikit_Learn_HistGradientBoostingRegressor",
        "features": feature_cols,
        "rmse": round(rmse, 4),
        "mae": round(mae, 4),
        "r2": round(r2, 4)
    }

    metrics_path = os.path.join(MODELS_DIR, "python_delay_model_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics_info, f, indent=2)

    print(f"\n[SAVED] Python delay model saved to {model_path} and {metrics_path}")
    return model, metrics_info

if __name__ == "__main__":
    train_python_delay_model()
