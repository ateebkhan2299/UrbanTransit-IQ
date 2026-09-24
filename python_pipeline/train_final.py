import os
import json
import pandas as pd
from datetime import datetime
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib

def run_python_final():
    data_dir = "parquet_data/ml_features/delay_prediction_dataset.parquet"
    if not os.path.exists(data_dir):
        print("Data not found.")
        return
        
    print("Training Independent Python ML Pipeline...")
    df = pd.read_parquet(data_dir)
    
    features = ["time_of_day", "day_of_week", "historical_occupancy", "passenger_load", "scheduled_travel_time_min"]
    X = df[features].fillna(0)
    y = df["label"]
    
    # Chronological Split
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    # Evaluate 3 models independently
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    lr_rmse = mean_squared_error(y_test, lr.predict(X_test), squared=False)
    
    dt = DecisionTreeRegressor()
    dt.fit(X_train, y_train)
    dt_rmse = mean_squared_error(y_test, dt.predict(X_test), squared=False)
    
    rf = RandomForestRegressor(n_estimators=15)
    rf.fit(X_train, y_train)
    rf_preds = rf.predict(X_test)
    rf_rmse = mean_squared_error(y_test, rf_preds, squared=False)
    
    # Save Model
    out_dir = "models/python_pipeline"
    os.makedirs(out_dir, exist_ok=True)
    joblib.dump(rf, os.path.join(out_dir, "delay_model_v1.pkl"))
    
    # Generate Report
    os.makedirs("reports", exist_ok=True)
    with open("reports/python_model_report.md", "w") as f:
        f.write("# Python Sklearn Final Delay Model\n\n")
        f.write("Algorithm Selected: Random Forest Regressor\n")
        f.write("Evaluated: Linear Regression, Decision Tree, Random Forest\n")
        f.write(f"Final RMSE: {rf_rmse:.2f}\n")
        
    # Register Model
    registry_path = "models/model_registry.json"
    registry = []
    if os.path.exists(registry_path):
        with open(registry_path, "r") as f:
            registry = json.load(f)
            
    registry.append({
        "model_name": "delay_prediction",
        "pipeline": "python",
        "version": len([m for m in registry if m["pipeline"] == "python"]) + 1,
        "trained_date": datetime.now().isoformat(),
        "metrics": {"rmse": rf_rmse},
        "file_path": "models/python_pipeline/delay_model_v1.pkl"
    })
    
    with open(registry_path, "w") as f:
        json.dump(registry, f, indent=4)
        
    print("Python Final training and registration complete.")

if __name__ == "__main__":
    run_python_final()
