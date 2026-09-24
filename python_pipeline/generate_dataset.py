import os
import argparse
import random
import uuid
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Fixed rates of data-quality issues as per SRS
DUPLICATE_TICKETS_RATE = 0.02
MISSING_IDS_RATE = 0.015
INVALID_DELAYS_RATE = 0.005
NEGATIVE_PASSENGERS_RATE = 0.01
CANCELLED_TRIPS_RATE = 0.02

def generate_data(scale="small", output_dir="raw_data"):
    os.makedirs(output_dir, exist_ok=True)
    print(f"Generating data with {scale} scale in {output_dir}")

    if scale == "full":
        N_PASSENGERS = 50_000
        N_TICKETS = 2_000_000
        N_ROUTES = 100
        N_STOPS = 500
        N_TRIPS = 500_000
        N_VEHICLES = 250
        N_DELAYS = 250_000
        N_DAYS = 365
    else:
        # Small scale for testing
        N_PASSENGERS = 1_000
        N_TICKETS = 5_000
        N_ROUTES = 20
        N_STOPS = 100
        N_TRIPS = 2_000
        N_VEHICLES = 50
        N_DELAYS = 1_000
        N_DAYS = 7

    start_date = datetime(2025, 1, 1)

    # 1. Routes
    routes_data = []
    for i in range(1, N_ROUTES + 1):
        routes_data.append({
            "route_id": f"R{i:03d}",
            "route_name": f"Route {i}",
            "transport_mode": random.choice(["Bus", "Tram"])
        })
    pd.DataFrame(routes_data).to_csv(f"{output_dir}/Routes.csv", index=False)
    print("Routes.csv generated.")

    # 2. Stops
    stops_data = []
    for i in range(1, N_STOPS + 1):
        stops_data.append({
            "stop_id": f"S{i:04d}",
            "stop_name": f"Stop {i}",
            "latitude": 40.7128 + random.uniform(-0.1, 0.1),
            "longitude": -74.0060 + random.uniform(-0.1, 0.1),
            "zone": f"Zone {random.randint(1, 10)}"
        })
    pd.DataFrame(stops_data).to_csv(f"{output_dir}/Stops.csv", index=False)
    print("Stops.csv generated.")

    # 3. Route_Stops
    route_stops_data = []
    for r in routes_data:
        num_stops = random.randint(10, 30)
        route_stops = random.sample(stops_data, num_stops)
        for seq, s in enumerate(route_stops, 1):
            route_stops_data.append({
                "route_id": r["route_id"],
                "stop_id": s["stop_id"],
                "stop_sequence": seq
            })
    pd.DataFrame(route_stops_data).to_csv(f"{output_dir}/Route_Stops.csv", index=False)
    print("Route_Stops.csv generated.")

    # 4. Vehicles
    vehicles_data = []
    for i in range(1, N_VEHICLES + 1):
        vehicles_data.append({
            "vehicle_id": f"V{i:04d}",
            "transport_mode": random.choice(["Bus", "Tram"]),
            "capacity": random.choice([40, 60, 80, 120])
        })
    pd.DataFrame(vehicles_data).to_csv(f"{output_dir}/Vehicles.csv", index=False)
    print("Vehicles.csv generated.")

    # 5. Service_Calendar
    calendar_data = []
    for i in range(N_DAYS):
        d = start_date + timedelta(days=i)
        calendar_data.append({
            "service_date": d.strftime("%Y-%m-%d"),
            "day_type": "Weekend" if d.weekday() >= 5 else "Weekday"
        })
    pd.DataFrame(calendar_data).to_csv(f"{output_dir}/Service_Calendar.csv", index=False)
    print("Service_Calendar.csv generated.")

    # 6. Schedules (simplified per route)
    schedules_data = []
    for r in routes_data:
        schedules_data.append({
            "route_id": r["route_id"],
            "start_time": "06:00:00",
            "end_time": "22:00:00",
            "headway_mins": random.choice([10, 15, 20])
        })
    pd.DataFrame(schedules_data).to_csv(f"{output_dir}/Schedules.csv", index=False)
    print("Schedules.csv generated.")

    # 7. Trips (Chunked)
    print("Generating Trips...")
    trip_ids = []
    trips_file = f"{output_dir}/Trips.csv"
    with open(trips_file, "w") as f:
        f.write("trip_id,route_id,vehicle_id,service_date,scheduled_start,status\n")
    
    trip_records = []
    chunk_size = 50_000
    for i in range(1, N_TRIPS + 1):
        t_id = f"T{i:07d}"
        trip_ids.append(t_id)
        route = random.choice(routes_data)
        vehicle = random.choice(vehicles_data)
        service_date = random.choice(calendar_data)["service_date"]
        
        # Inject ~2% cancelled trips
        status = "Cancelled" if random.random() < CANCELLED_TRIPS_RATE else "Completed"
        
        trip_records.append(f"{t_id},{route['route_id']},{vehicle['vehicle_id']},{service_date},08:00:00,{status}")
        
        if len(trip_records) >= chunk_size:
            with open(trips_file, "a") as f:
                f.write("\n".join(trip_records) + "\n")
            trip_records = []
    if trip_records:
        with open(trips_file, "a") as f:
            f.write("\n".join(trip_records) + "\n")
    print("Trips.csv generated.")

    # 8. Passengers
    passengers_data = []
    passenger_ids = []
    for i in range(1, N_PASSENGERS + 1):
        p_id = f"P{i:06d}"
        passenger_ids.append(p_id)
        passengers_data.append({
            "passenger_id": p_id,
            "card_type": random.choice(["Standard", "Student", "Senior", "Monthly"])
        })
    pd.DataFrame(passengers_data).to_csv(f"{output_dir}/Passengers.csv", index=False)
    print("Passengers.csv generated.")

    # 9. Tickets (Chunked with duplicates and missing IDs)
    print("Generating Tickets...")
    tickets_file = f"{output_dir}/Tickets.csv"
    with open(tickets_file, "w") as f:
        f.write("ticket_id,passenger_id,trip_id,boarding_stop_id,alighting_stop_id,timestamp,fare\n")
    
    ticket_records = []
    for i in range(1, N_TICKETS + 1):
        tk_id = f"TK{i:08d}"
        p_id = random.choice(passenger_ids)
        t_id = random.choice(trip_ids)
        b_stop = random.choice(stops_data)["stop_id"]
        a_stop = random.choice(stops_data)["stop_id"]
        fare = round(random.uniform(1.5, 5.0), 2)
        
        # Missing IDs ~1.5%
        if random.random() < MISSING_IDS_RATE:
            p_id = ""
            
        record = f"{tk_id},{p_id},{t_id},{b_stop},{a_stop},2025-01-01 08:15:00,{fare}"
        ticket_records.append(record)
        
        # Duplicates ~2%
        if random.random() < DUPLICATE_TICKETS_RATE:
            ticket_records.append(record)
            
        if len(ticket_records) >= chunk_size:
            with open(tickets_file, "a") as f:
                f.write("\n".join(ticket_records) + "\n")
            ticket_records = []
    if ticket_records:
        with open(tickets_file, "a") as f:
            f.write("\n".join(ticket_records) + "\n")
    print("Tickets.csv generated.")

    # 10. Passenger_Counts (Chunked)
    print("Generating Passenger_Counts...")
    pc_file = f"{output_dir}/Passenger_Counts.csv"
    with open(pc_file, "w") as f:
        f.write("count_id,trip_id,stop_id,timestamp,boarding_count,alighting_count\n")
    
    pc_records = []
    for i in range(1, N_TRIPS + 1): # Roughly one count per trip for demo
        t_id = random.choice(trip_ids)
        s_id = random.choice(stops_data)["stop_id"]
        b_count = random.randint(0, 50)
        a_count = random.randint(0, 30)
        
        # ~1% impossible/negative passenger counts or exceeding capacity
        if random.random() < NEGATIVE_PASSENGERS_RATE:
            b_count = -5  # Negative
        elif random.random() < 0.01:
            b_count = 500 # Exceeds bus capacity
            
        pc_records.append(f"PC{i:07d},{t_id},{s_id},2025-01-01 08:10:00,{b_count},{a_count}")
        
        if len(pc_records) >= chunk_size:
            with open(pc_file, "a") as f:
                f.write("\n".join(pc_records) + "\n")
            pc_records = []
    if pc_records:
        with open(pc_file, "a") as f:
            f.write("\n".join(pc_records) + "\n")
    print("Passenger_Counts.csv generated.")

    # 11. Delays (Chunked)
    print("Generating Delays...")
    delays_file = f"{output_dir}/Delays.csv"
    with open(delays_file, "w") as f:
        f.write("delay_id,trip_id,stop_id,service_date,delay_minutes,cause\n")
    
    delay_records = []
    causes = ["Traffic", "Weather", "Mechanical", "Passenger", "Signal"]
    for i in range(1, N_DELAYS + 1):
        t_id = random.choice(trip_ids)
        s_id = random.choice(stops_data)["stop_id"]
        date = random.choice(calendar_data)["service_date"]
        d_min = random.randint(1, 45)
        cause = random.choice(causes)
        
        # ~0.5% invalid/negative delays
        if random.random() < INVALID_DELAYS_RATE:
            d_min = -10
            
        delay_records.append(f"D{i:07d},{t_id},{s_id},{date},{d_min},{cause}")
        
        if len(delay_records) >= chunk_size:
            with open(delays_file, "a") as f:
                f.write("\n".join(delay_records) + "\n")
            delay_records = []
    if delay_records:
        with open(delays_file, "a") as f:
            f.write("\n".join(delay_records) + "\n")
    print("Delays.csv generated.")

    # 12. GPS_Events
    print("Generating GPS_Events...")
    gps_data = []
    for i in range(1, min(N_TRIPS, 5000) + 1): # Just a sample
        gps_data.append({
            "event_id": f"G{i:07d}",
            "vehicle_id": random.choice(vehicles_data)["vehicle_id"],
            "timestamp": "2025-01-01 08:15:00",
            "latitude": 40.7128 + random.uniform(-0.1, 0.1),
            "longitude": -74.0060 + random.uniform(-0.1, 0.1),
            "speed_kmh": random.randint(0, 60)
        })
    pd.DataFrame(gps_data).to_csv(f"{output_dir}/GPS_Events.csv", index=False)
    print("GPS_Events.csv generated.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scale", type=str, default="small", choices=["small", "full"])
    parser.add_argument("--out", type=str, default="raw_data")
    args = parser.parse_args()
    generate_data(args.scale, args.out)
