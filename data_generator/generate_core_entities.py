import pandas as pd
import numpy as np
from faker import Faker
import os
from config_gen import RAW_DIR, NUM_ROUTES, NUM_STOPS, NUM_VEHICLES

fake = Faker()
Faker.seed(42)
np.random.seed(42)

def generate_core_entities():
    print("Generating core entities...")
    
    # 1. Routes
    route_ids = [f"R{str(i).zfill(3)}" for i in range(1, NUM_ROUTES + 1)]
    directions = np.random.choice(['Northbound', 'Southbound', 'Eastbound', 'Westbound'], NUM_ROUTES)
    distances = np.round(np.random.uniform(5.0, 35.0, NUM_ROUTES), 2)
    statuses = np.random.choice(['Active', 'Inactive', 'Maintenance'], NUM_ROUTES, p=[0.9, 0.05, 0.05])
    
    routes_df = pd.DataFrame({
        'route_id': route_ids,
        'route_name': [fake.street_name() + " Line" for _ in range(NUM_ROUTES)],
        'direction': directions,
        'distance_km': distances,
        'status': statuses
    })
    routes_df.to_csv(os.path.join(RAW_DIR, 'routes.csv'), index=False)
    
    # 2. Stops
    stop_ids = [f"S{str(i).zfill(3)}" for i in range(1, NUM_STOPS + 1)]
    lats = np.round(np.random.uniform(40.5, 40.9, NUM_STOPS), 6)
    lons = np.round(np.random.uniform(-74.3, -73.7, NUM_STOPS), 6)
    
    stops_df = pd.DataFrame({
        'stop_id': stop_ids,
        'stop_name': [fake.street_name() + " Station" for _ in range(NUM_STOPS)],
        'latitude': lats,
        'longitude': lons
    })
    stops_df.to_csv(os.path.join(RAW_DIR, 'stops.csv'), index=False)
    
    # 3. Route Stops
    route_stops = []
    for r in route_ids:
        num_route_stops = np.random.randint(10, 30)
        selected_stops = np.random.choice(stop_ids, num_route_stops, replace=False)
        for seq, s in enumerate(selected_stops, 1):
            route_stops.append({'route_id': r, 'stop_id': s, 'stop_sequence': seq})
            
    route_stops_df = pd.DataFrame(route_stops)
    route_stops_df.to_csv(os.path.join(RAW_DIR, 'route_stops.csv'), index=False)
    
    # 4. Vehicles
    vehicle_ids = [f"V{str(i).zfill(3)}" for i in range(1, NUM_VEHICLES + 1)]
    v_types = np.random.choice(['Bus', 'Tram', 'Subway'], NUM_VEHICLES, p=[0.7, 0.2, 0.1])
    capacities = np.where(v_types == 'Bus', np.random.randint(40, 60, NUM_VEHICLES), 
                  np.where(v_types == 'Tram', np.random.randint(80, 120, NUM_VEHICLES), 
                           np.random.randint(300, 500, NUM_VEHICLES)))
    v_statuses = np.random.choice(['Active', 'Maintenance', 'Retired'], NUM_VEHICLES, p=[0.85, 0.10, 0.05])
    
    vehicles_df = pd.DataFrame({
        'vehicle_id': vehicle_ids,
        'type': v_types,
        'capacity': capacities,
        'status': v_statuses
    })
    vehicles_df.to_csv(os.path.join(RAW_DIR, 'vehicles.csv'), index=False)
    
    # 5. Service Calendar
    calendar_data = [
        {'service_id': 'SVC_WEEKDAY', 'day_of_week': 'Mon-Fri', 'start_date': '2025-01-01', 'end_date': '2025-12-31', 'holiday_flag': 0},
        {'service_id': 'SVC_WEEKEND', 'day_of_week': 'Sat-Sun', 'start_date': '2025-01-01', 'end_date': '2025-12-31', 'holiday_flag': 0},
        {'service_id': 'SVC_HOLIDAY', 'day_of_week': 'Any', 'start_date': '2025-01-01', 'end_date': '2025-12-31', 'holiday_flag': 1},
    ]
    pd.DataFrame(calendar_data).to_csv(os.path.join(RAW_DIR, 'service_calendar.csv'), index=False)

if __name__ == "__main__":
    generate_core_entities()
