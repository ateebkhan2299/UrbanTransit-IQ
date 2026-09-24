import os
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib

def run_python_forecast():
    data_dir = "parquet_data/ml_features/daily_demand.parquet"
    if not os.path.exists(data_dir):
        print("Data not found.")
        return
        
    df = pd.read_parquet(data_dir)
    print("Running Python Regressor Forecast...")
    
    # Create lag features for chronological prediction
    df = df.sort_values(by=["route_id", "travel_date"])
    df["lag_1"] = df.groupby("route_id")["daily_passengers"].shift(1)
    df["lag_7"] = df.groupby("route_id")["daily_passengers"].shift(7)
    df = df.dropna()
    
    X = df[["lag_1", "lag_7"]]
    y = df["daily_passengers"]
    
    # Chronological Split
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    
    preds = lr.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = mean_squared_error(y_test, preds, squared=False)
    
    os.makedirs("models/forecasting", exist_ok=True)
    joblib.dump(lr, "models/forecasting/python_demand_lr.pkl")
    
    print(f"Python Forecast Complete. MAE: {mae:.2f}, RMSE: {rmse:.2f}")

if __name__ == "__main__":
    run_python_forecast()
