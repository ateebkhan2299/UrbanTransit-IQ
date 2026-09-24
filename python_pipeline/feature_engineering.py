import os
import sys
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import backend.config as config
from python_pipeline.preprocessing import load_and_preprocess_pandas

def build_python_features():
    print("=== Python DS Pipeline: Feature Engineering ===")
    cleaned = load_and_preprocess_pandas()

    counts_df = cleaned["passenger_counts"]
    trips_df = cleaned["trips"]
    vehicles_df = cleaned["vehicles"]
    delays_df = cleaned["delays"]

    # 1. Enriched Passenger Counts with Vehicle Capacity
    trips_veh = trips_df.merge(vehicles_df[["vehicle_id", "total_capacity"]], on="vehicle_id", how="left")
    counts_feat = counts_df.merge(trips_veh[["trip_id", "route_id", "total_capacity"]], on="trip_id", how="left")

    counts_feat["timestamp_dt"] = pd.to_datetime(counts_feat["timestamp"])
    counts_feat["hour_of_day"] = counts_feat["timestamp_dt"].dt.hour
    counts_feat["day_of_week"] = counts_feat["timestamp_dt"].dt.dayofweek
    counts_feat["is_peak_hour"] = counts_feat["hour_of_day"].isin([7, 8, 9, 17, 18, 19]).astype(int)

    counts_feat["occupancy_pct"] = (counts_feat["current_occupancy"] / counts_feat["total_capacity"] * 100.0).round(2)
    counts_feat["is_overcrowded"] = (counts_feat["occupancy_pct"] >= config.OVERCROWDING_THRESHOLD_PCT).astype(int)
    counts_feat["is_underutilized"] = (counts_feat["occupancy_pct"] <= config.UNDERUTILIZED_THRESHOLD_PCT).astype(int)

    # 2. Delays Feature Processing
    delays_feat = delays_df.copy()
    delays_feat["scheduled_dt"] = pd.to_datetime(delays_feat["scheduled_time"])
    delays_feat["hour_of_day"] = delays_feat["scheduled_dt"].dt.hour
    delays_feat["day_of_week"] = delays_feat["scheduled_dt"].dt.dayofweek
    delays_feat["is_peak_hour"] = delays_feat["hour_of_day"].isin([7, 8, 9, 17, 18, 19]).astype(int)

    def categorize_delay(m):
        if m == 0: return "NONE"
        elif m < config.DELAY_MODERATE_MIN: return "MINOR"
        elif m < config.DELAY_MAJOR_MIN: return "MODERATE"
        elif m < config.DELAY_SEVERE_MIN: return "MAJOR"
        else: return "SEVERE"

    delays_feat["delay_severity"] = delays_feat["delay_minutes"].apply(categorize_delay)

    print(f"  Pandas Occupancy Features: {counts_feat.shape}")
    print(f"  Pandas Delays Features: {delays_feat.shape}")

    return {
        "occupancy_features": counts_feat,
        "delays_features": delays_feat
    }

if __name__ == "__main__":
    build_python_features()
