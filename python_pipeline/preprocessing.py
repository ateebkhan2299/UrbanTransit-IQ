import os
import pandas as pd
import numpy as np

RAW_DATA_DIR = "./raw_data"
PARQUET_DATA_DIR = "./parquet_data"

def load_and_preprocess_pandas():
    print("=== Python DS Pipeline: Preprocessing & Cleaning ===")

    tickets_df = pd.read_parquet(os.path.join(PARQUET_DATA_DIR, "tickets.parquet"))
    counts_df = pd.read_parquet(os.path.join(PARQUET_DATA_DIR, "passenger_counts.parquet"))
    trips_df = pd.read_parquet(os.path.join(PARQUET_DATA_DIR, "trips.parquet"))
    routes_df = pd.read_parquet(os.path.join(PARQUET_DATA_DIR, "routes.parquet"))
    vehicles_df = pd.read_parquet(os.path.join(PARQUET_DATA_DIR, "vehicles.parquet"))
    delays_df = pd.read_parquet(os.path.join(PARQUET_DATA_DIR, "delays.parquet"))
    stops_df = pd.read_parquet(os.path.join(PARQUET_DATA_DIR, "stops.parquet"))

    # 1. Clean Tickets: Impute missing passenger_id & drop duplicate ticket_id
    tickets_clean = tickets_df.copy()
    tickets_clean["passenger_id"] = tickets_clean["passenger_id"].fillna("ANONYMOUS_PAX")
    tickets_clean = tickets_clean.drop_duplicates(subset=["ticket_id"])

    # 2. Clean Passenger Counts: Correct negative boarded_count values
    counts_clean = counts_df.copy()
    counts_clean["boarded_count"] = counts_clean["boarded_count"].abs()

    print(f"  Tickets Cleaned: {len(tickets_clean)} rows")
    print(f"  Passenger Counts Cleaned: {len(counts_clean)} rows")

    return {
        "tickets": tickets_clean,
        "passenger_counts": counts_clean,
        "trips": trips_df,
        "routes": routes_df,
        "vehicles": vehicles_df,
        "delays": delays_df,
        "stops": stops_df
    }

if __name__ == "__main__":
    load_and_preprocess_pandas()
