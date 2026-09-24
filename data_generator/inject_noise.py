import pandas as pd
import numpy as np
import json
import os
from config_gen import RAW_DIR

np.random.seed(42)

def inject_noise():
    print("Injecting noise into datasets for Phase 3 cleaning...")
    manifest = []
    
    # 1. Nulls in Trips
    trips_df = pd.read_csv(os.path.join(RAW_DIR, 'trips.csv'))
    n_nulls = int(len(trips_df) * 0.01)
    null_indices = np.random.choice(trips_df.index, n_nulls, replace=False)
    trips_df.loc[null_indices, 'vehicle_id'] = np.nan
    trips_df.to_csv(os.path.join(RAW_DIR, 'trips.csv'), index=False)
    manifest.append({"type": "missing_values", "table": "trips", "column": "vehicle_id", "count": n_nulls})
    
    # 2. Duplicates in Tickets (read first chunk to save memory)
    # Tickets is huge, we'll append a small chunk of duplicates to the end
    tickets_chunk = pd.read_csv(os.path.join(RAW_DIR, 'tickets.csv'), nrows=10000)
    dupes = tickets_chunk.sample(5000)
    dupes.to_csv(os.path.join(RAW_DIR, 'tickets.csv'), mode='a', header=False, index=False)
    manifest.append({"type": "duplicates", "table": "tickets", "count": 5000})
    
    # 3. Invalid Timestamps in Delays
    delays_df = pd.read_csv(os.path.join(RAW_DIR, 'delays.csv'))
    n_invalid = int(len(delays_df) * 0.003)
    invalid_idx = np.random.choice(delays_df.index, n_invalid, replace=False)
    # Set negative delays
    delays_df.loc[invalid_idx, 'delay_minutes'] = -50
    delays_df.to_csv(os.path.join(RAW_DIR, 'delays.csv'), index=False)
    manifest.append({"type": "invalid_timestamps", "table": "delays", "column": "delay_minutes", "count": n_invalid})
    
    # 4. Vehicle Bunching Events
    # We log this as synthetic injection
    manifest.append({"type": "vehicle_bunching", "table": "gps_events", "count": "synthetic implicit via random gen"})
    manifest.append({"type": "overcrowding", "table": "passenger_counts", "count": "synthetic implicit via >100% capacity"})

    with open(os.path.join(RAW_DIR, 'injection_manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=4)
        
    print(f"Injected {len(manifest)} noise patterns. Manifest saved.")

if __name__ == "__main__":
    inject_noise()
