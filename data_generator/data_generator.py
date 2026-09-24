import os
import random
import uuid
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Operational directory paths
RAW_DATA_DIR = "./raw_data"
PARQUET_DATA_DIR = "./parquet_data"

# Full Scale Parameters requested by User
NUM_STOPS = 500
NUM_ROUTES = 100
NUM_VEHICLES = 250
NUM_PASSENGERS = 50000
NUM_TRIPS = 50000
NUM_TICKETS = 2000000
DAYS_SPAN = 365

def set_random_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)

def generate_stops(num_stops=NUM_STOPS):
    base_lat, base_lon = 40.7128, -74.0060
    lats = np.round(base_lat + np.random.uniform(-0.25, 0.25, num_stops), 6)
    lons = np.round(base_lon + np.random.uniform(-0.25, 0.25, num_stops), 6)
    zones = [f"ZONE_{random.randint(1, 10)}" for _ in range(num_stops)]
    wheelchair = np.random.choice([0, 1], size=num_stops)

    stops_df = pd.DataFrame({
        "stop_id": [f"STOP_{i+1:04d}" for i in range(num_stops)],
        "stop_name": [f"Station {i+1}" for i in range(num_stops)],
        "latitude": lats,
        "longitude": lons,
        "zone_id": zones,
        "wheelchair_boarding": wheelchair
    })
    return stops_df

def generate_routes(num_routes=NUM_ROUTES):
    route_types = [0, 1, 3] # 0: Tram, 1: Subway, 3: Bus
    routes_df = pd.DataFrame({
        "route_id": [f"ROUTE_{i+1:03d}" for i in range(num_routes)],
        "route_short_name": [f"R{i+1}" for i in range(num_routes)],
        "route_long_name": [f"Line {i+1} - Main Transit Route" for i in range(num_routes)],
        "route_type": np.random.choice(route_types, size=num_routes),
        "agency_id": "TRANSIT_AGENCY_MAIN",
        "fare_zone": [f"FARE_ZONE_{random.randint(1, 5)}" for _ in range(num_routes)]
    })
    return routes_df

def generate_route_stops(routes_df, stops_df):
    route_stops = []
    all_stops = stops_df["stop_id"].values
    for r_id in routes_df["route_id"].values:
        n_stops = random.randint(8, 20)
        selected_stops = np.random.choice(all_stops, size=n_stops, replace=False)
        for seq, s_id in enumerate(selected_stops):
            route_stops.append({
                "route_id": r_id,
                "stop_id": s_id,
                "stop_sequence": seq + 1
            })
    return pd.DataFrame(route_stops)

def generate_vehicles(num_vehicles=NUM_VEHICLES):
    v_types = ["Bus Standard", "Articulated Bus", "Subway Train", "Light Rail Tram"]
    v_type_arr = np.random.choice(v_types, size=num_vehicles)
    cap_map = {"Bus Standard": 50, "Articulated Bus": 85, "Subway Train": 250, "Light Rail Tram": 120}

    vehicles_df = pd.DataFrame({
        "vehicle_id": [f"VEH_{i+1:04d}" for i in range(num_vehicles)],
        "vehicle_type": v_type_arr,
        "total_capacity": [cap_map[vt] for vt in v_type_arr],
        "manufacture_year": np.random.randint(2015, 2026, size=num_vehicles),
        "license_plate": [f"BUS-{random.randint(1000,9999)}" for _ in range(num_vehicles)]
    })
    return vehicles_df

def generate_passengers(num_passengers=NUM_PASSENGERS):
    passengers_df = pd.DataFrame({
        "passenger_id": [f"PAX_{i+1:06d}" for i in range(num_passengers)],
        "card_type": np.random.choice(["Standard", "Student", "Senior", "Monthly_Pass"], size=num_passengers),
        "registered_date": [f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}" for _ in range(num_passengers)]
    })
    return passengers_df

def generate_service_calendar():
    return pd.DataFrame([
        {"service_id": "WEEKDAY", "monday": 1, "tuesday": 1, "wednesday": 1, "thursday": 1, "friday": 1, "saturday": 0, "sunday": 0},
        {"service_id": "SATURDAY", "monday": 0, "tuesday": 0, "wednesday": 0, "thursday": 0, "friday": 0, "saturday": 1, "sunday": 0},
        {"service_id": "SUNDAY", "monday": 0, "tuesday": 0, "wednesday": 0, "thursday": 0, "friday": 0, "saturday": 0, "sunday": 1}
    ])

def generate_trips(routes_df, vehicles_df, num_trips=NUM_TRIPS, days_span=DAYS_SPAN):
    route_ids = routes_df["route_id"].values
    vehicle_ids = vehicles_df["vehicle_id"].values
    base_date = datetime(2026, 1, 1)

    r_choices = np.random.choice(route_ids, size=num_trips)
    v_choices = np.random.choice(vehicle_ids, size=num_trips)
    day_offsets = np.random.randint(0, days_span, size=num_trips)
    hour_offsets = np.random.randint(5, 23, size=num_trips)
    min_offsets = np.random.randint(0, 60, size=num_trips)

    start_times = [
        (base_date + timedelta(days=int(d), hours=int(h), minutes=int(m))).strftime("%Y-%m-%d %H:%M:%S")
        for d, h, m in zip(day_offsets, hour_offsets, min_offsets)
    ]
    service_choices = np.random.choice(["WEEKDAY", "SATURDAY", "SUNDAY"], size=num_trips)

    trips_df = pd.DataFrame({
        "trip_id": [f"TRIP_{i+1:06d}" for i in range(num_trips)],
        "route_id": r_choices,
        "service_id": service_choices,
        "vehicle_id": v_choices,
        "start_time": start_times,
        "direction_id": np.random.choice([0, 1], size=num_trips)
    })
    return trips_df

def generate_schedules_and_events(trips_df, route_stops_df, vehicles_df, max_stops_sampled=50000):
    print("  Sampling stops and simulating schedules/delays/counts...")
    # Sample subset of trips for high density schedules
    sample_trips = trips_df.head(max_stops_sampled)
    route_stops_dict = route_stops_df.groupby("route_id")["stop_id"].apply(list).to_dict()
    veh_cap_dict = vehicles_df.set_index("vehicle_id")["total_capacity"].to_dict()

    schedules, counts, delays, gps_events = [], [], [], []
    delay_causes = ["Traffic Congestion", "Weather Conditions", "Signal Priority Fault", "Mechanical Issue", "Passenger Hold"]

    delay_id = 1
    event_id = 1
    count_id = 1

    for idx, row in sample_trips.iterrows():
        t_id = row["trip_id"]
        r_id = row["route_id"]
        v_id = row["vehicle_id"]
        start_dt = datetime.strptime(row["start_time"], "%Y-%m-%d %H:%M:%S")

        r_stops = route_stops_dict.get(r_id, ["STOP_0001", "STOP_0002"])
        cap = veh_cap_dict.get(v_id, 80)
        curr_occupancy = 0
        curr_time = start_dt

        for seq, s_id in enumerate(r_stops):
            sched_arr = curr_time
            sched_dep = curr_time + timedelta(seconds=45)

            schedules.append({
                "trip_id": t_id,
                "stop_id": s_id,
                "stop_sequence": seq + 1,
                "scheduled_arrival": sched_arr.strftime("%Y-%m-%d %H:%M:%S"),
                "scheduled_departure": sched_dep.strftime("%Y-%m-%d %H:%M:%S")
            })

            boarded = random.randint(0, 15)
            alighted = random.randint(0, min(curr_occupancy, 12)) if curr_occupancy > 0 else 0
            if random.random() < 0.01:
                boarded = -2  # Anomaly injection

            curr_occupancy = max(0, curr_occupancy + boarded - alighted)

            counts.append({
                "count_id": f"CNT_{count_id:08d}",
                "trip_id": t_id,
                "stop_id": s_id,
                "timestamp": sched_arr.strftime("%Y-%m-%d %H:%M:%S"),
                "boarded_count": boarded,
                "alighted_count": alighted,
                "current_occupancy": curr_occupancy
            })
            count_id += 1

            if random.random() < 0.25:
                delay_min = random.randint(2, 45)
                actual_arr = sched_arr + timedelta(minutes=delay_min)
                delays.append({
                    "delay_id": f"DEL_{delay_id:08d}",
                    "trip_id": t_id,
                    "stop_id": s_id,
                    "scheduled_time": sched_arr.strftime("%Y-%m-%d %H:%M:%S"),
                    "actual_time": actual_arr.strftime("%Y-%m-%d %H:%M:%S"),
                    "delay_minutes": delay_min,
                    "delay_cause": random.choice(delay_causes)
                })
                delay_id += 1

            gps_events.append({
                "event_id": f"GPS_{event_id:08d}",
                "vehicle_id": v_id,
                "trip_id": t_id,
                "timestamp": sched_arr.strftime("%Y-%m-%d %H:%M:%S"),
                "latitude": round(40.7128 + random.uniform(-0.1, 0.1), 6),
                "longitude": round(-74.0060 + random.uniform(-0.1, 0.1), 6),
                "speed_kmh": round(random.uniform(10.0, 55.0), 1),
                "heading": random.randint(0, 359)
            })
            event_id += 1

            curr_time += timedelta(minutes=random.randint(3, 8))

    return pd.DataFrame(schedules), pd.DataFrame(counts), pd.DataFrame(delays), pd.DataFrame(gps_events)

def generate_tickets_vectorized(trips_df, route_stops_df, passengers_df, num_tickets=NUM_TICKETS):
    print(f"  Generating {num_tickets:,} tickets in vectorized batch mode...")
    pax_ids = passengers_df["passenger_id"].values
    trip_ids = trips_df["trip_id"].values

    # Vectorized random choices
    t_id_choices = np.random.choice(trip_ids, size=num_tickets)
    p_id_choices = np.random.choice(pax_ids, size=num_tickets)

    # 5% NaN anomaly
    p_id_choices = p_id_choices.astype(object)
    missing_mask = np.random.random(num_tickets) < 0.05
    p_id_choices[missing_mask] = None

    fares = np.round(np.random.uniform(2.25, 6.50, size=num_tickets), 2)

    all_stops = route_stops_df["stop_id"].values
    orig_stops = np.random.choice(all_stops, size=num_tickets)
    dest_stops = np.random.choice(all_stops, size=num_tickets)

    base_time = datetime(2026, 1, 1)
    time_offsets = np.random.randint(0, 365 * 86400, size=num_tickets)

    purchase_times = [
        (base_time + timedelta(seconds=int(ts))).strftime("%Y-%m-%d %H:%M:%S")
        for ts in time_offsets
    ]
    val_times = [
        (base_time + timedelta(seconds=int(ts) + random.randint(120, 600))).strftime("%Y-%m-%d %H:%M:%S")
        for ts in time_offsets
    ]

    tickets_df = pd.DataFrame({
        "ticket_id": [f"TCK_{i+1:08d}" for i in range(num_tickets)],
        "passenger_id": p_id_choices,
        "trip_id": t_id_choices,
        "origin_stop_id": orig_stops,
        "destination_stop_id": dest_stops,
        "fare_amount": fares,
        "purchase_timestamp": purchase_times,
        "validation_timestamp": val_times
    })

    # 2% Duplicates
    num_dupes = int(num_tickets * 0.02)
    if num_dupes > 0:
        dupes = tickets_df.iloc[:num_dupes].copy()
        tickets_df = pd.concat([tickets_df, dupes], ignore_index=True)

    return tickets_df

def save_all_datasets(datasets_map):
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(PARQUET_DATA_DIR, exist_ok=True)

    for name, df in datasets_map.items():
        csv_path = os.path.join(RAW_DATA_DIR, f"{name}.csv")
        df.to_csv(csv_path, index=False)

        if name in ["stops", "routes"]:
            json_path = os.path.join(RAW_DATA_DIR, f"{name}.json")
            df.to_json(json_path, orient="records", indent=2)

        parquet_path = os.path.join(PARQUET_DATA_DIR, f"{name}.parquet")
        df.to_parquet(parquet_path, engine="pyarrow", index=False)
        print(f"  [SAVED] {name}: {len(df):,} rows -> CSV & Parquet")

def run_data_generation():
    print(f"=== UrbanTransit IQ Full-Scale Data Generator ===")
    print(f"  Target Volume: {NUM_TICKETS:,} Tickets, {NUM_PASSENGERS:,} Passengers, {NUM_STOPS} Stops, {NUM_ROUTES} Routes, {NUM_VEHICLES} Vehicles, {DAYS_SPAN} Days")
    start_time = time.time()
    set_random_seed(42)

    print("\n1. Generating reference & entity tables...")
    stops_df = generate_stops()
    routes_df = generate_routes()
    route_stops_df = generate_route_stops(routes_df, stops_df)
    vehicles_df = generate_vehicles()
    passengers_df = generate_passengers()
    calendar_df = generate_service_calendar()

    print("2. Generating operational trips & schedules...")
    trips_df = generate_trips(routes_df, vehicles_df)
    schedules_df, counts_df, delays_df, gps_df = generate_schedules_and_events(trips_df, route_stops_df, vehicles_df)

    print("3. Generating vectorized ticket sales & validations...")
    tickets_df = generate_tickets_vectorized(trips_df, route_stops_df, passengers_df)

    datasets = {
        "stops": stops_df,
        "routes": routes_df,
        "route_stops": route_stops_df,
        "vehicles": vehicles_df,
        "passengers": passengers_df,
        "service_calendar": calendar_df,
        "trips": trips_df,
        "schedules": schedules_df,
        "passenger_counts": counts_df,
        "delays": delays_df,
        "gps_events": gps_df,
        "tickets": tickets_df
    }

    print("\n4. Saving all 12 tables to raw_data/ and parquet_data/...")
    save_all_datasets(datasets)
    elapsed = time.time() - start_time
    print(f"\n[SUCCESS] Full Scale data generation complete in {elapsed:.2f} seconds!")

if __name__ == "__main__":
    run_data_generation()
