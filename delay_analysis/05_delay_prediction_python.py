import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib

def run_python_prediction():
    # Phase 7: Independent Python Pipeline
    data_dir = "parquet_data/ml_features/delay_prediction_dataset.parquet"
    if not os.path.exists(data_dir):
        print("Data not found. Run 03_delay_prediction_features.py first.")
        return
        
    print("Loading data for Scikit-Learn...")
    df = pd.read_parquet(data_dir)
    
    features = ["time_of_day", "day_of_week", "historical_occupancy", "passenger_load", "scheduled_travel_time_min"]
    X = df[features].fillna(0)
    y = df["label"]
    
    # Chronological Split (simulated chronologically by taking first 80% of rows since they are ordered by time)
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    metrics = []
    print("Training Python Models...")
    
    # 1. Linear Regression
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    lr_rmse = mean_squared_error(y_test, lr.predict(X_test), squared=False)
    metrics.append(f"| Python Linear Regression | {lr_rmse:.2f} |")
    
    # 2. Decision Tree
    dt = DecisionTreeRegressor()
    dt.fit(X_train, y_train)
    dt_rmse = mean_squared_error(y_test, dt.predict(X_test), squared=False)
    metrics.append(f"| Python Decision Tree | {dt_rmse:.2f} |")
    
    # 3. Random Forest
    rf = RandomForestRegressor(n_estimators=10)
    rf.fit(X_train, y_train)
    rf_rmse = mean_squared_error(y_test, rf.predict(X_test), squared=False)
    metrics.append(f"| Python Random Forest | {rf_rmse:.2f} |")
    
    # Save Model
    os.makedirs("models/delay_python", exist_ok=True)
    joblib.dump(rf, "models/delay_python/best_rf_model.pkl")
    
    with open("reports/delay_model_metrics.md", "a") as f:
        f.write("\n".join(metrics) + "\n")
        
    print("Python ML training complete. Metrics saved.")

if __name__ == "__main__":
    run_python_prediction()
