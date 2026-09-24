import pandas as pd
import numpy as np
import os
from config_gen import RAW_DIR, MIN_DELAYS, CHUNK_SIZE

np.random.seed(42)

def generate_delays_gps():
    print("Generating delays and GPS events...")
    
    trips_df = pd.read_csv(os.path.join(RAW_DIR, 'trips.csv'), usecols=['trip_id', 'vehicle_id', 'scheduled_start'])
    stops_df = pd.read_csv(os.path.join(RAW_DIR, 'stops.csv'), usecols=['stop_id', 'latitude', 'longitude'])
    
    trip_ids = trips_df['trip_id'].values
    stop_ids = stops_df['stop_id'].values
    
    total_delays = MIN_DELAYS
    reasons = ['Traffic', 'Weather', 'Mechanical', 'Passenger Incident', 'Signal Failure']
    
    print(f"Generating {total_delays:,} delays...")
    first_chunk = True
    for start in range(0, total_delays, CHUNK_SIZE):
        n = min(CHUNK_SIZE, total_delays - start)
        d_ids = [f"D{str(i).zfill(7)}" for i in range(start + 1, start + n + 1)]
        d_trips = np.random.choice(trip_ids, n)
        d_stops = np.random.choice(stop_ids, n)
        
        sched_times = pd.to_datetime('2025-01-01') + pd.to_timedelta(np.random.randint(0, 360*24*60, n), unit='m')
        delay_mins = np.random.exponential(scale=10, size=n).astype(int)
        actual_times = sched_times + pd.to_timedelta(delay_mins, unit='m')
        d_reasons = np.random.choice(reasons, n, p=[0.5, 0.15, 0.15, 0.1, 0.1])
        
        chunk_df = pd.DataFrame({
            'delay_id': d_ids,
            'trip_id': d_trips,
            'stop_id': d_stops,
            'scheduled_time': sched_times,
            'actual_time': actual_times,
            'delay_minutes': delay_mins,
            'reason': d_reasons
        })
        
        chunk_df.to_csv(os.path.join(RAW_DIR, 'delays.csv'), mode='a', header=first_chunk, index=False)
        first_chunk = False
        print(f"  Written {start + n:,} / {total_delays:,} delays")
        
    print("Generating GPS events (sampled)...")
    # For speed, we will generate 1,000,000 GPS events
    total_gps = 1_000_000
    first_chunk = True
    for start in range(0, total_gps, CHUNK_SIZE):
        n = min(CHUNK_SIZE, total_gps - start)
        g_ids = [f"G{str(i).zfill(7)}" for i in range(start + 1, start + n + 1)]
        # Sample trips and vehicles properly
        sampled = trips_df.sample(n, replace=True)
        g_trips = sampled['trip_id'].values
        g_vehicles = sampled['vehicle_id'].values
        
        g_times = pd.to_datetime(sampled['scheduled_start']) + pd.to_timedelta(np.random.randint(0, 60, n), unit='m')
        g_lats = np.round(np.random.uniform(40.5, 40.9, n), 6)
        g_lons = np.round(np.random.uniform(-74.3, -73.7, n), 6)
        
        chunk_df = pd.DataFrame({
            'event_id': g_ids,
            'vehicle_id': g_vehicles,
            'trip_id': g_trips,
            'timestamp': g_times,
            'latitude': g_lats,
            'longitude': g_lons
        })
        
        chunk_df.to_csv(os.path.join(RAW_DIR, 'gps_events.csv'), mode='a', header=first_chunk, index=False)
        first_chunk = False

if __name__ == "__main__":
    generate_delays_gps()
