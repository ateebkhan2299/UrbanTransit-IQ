import pandas as pd
import numpy as np
import os
from config_gen import RAW_DIR, MIN_TRIP_RECORDS, DAYS_TOTAL

np.random.seed(42)

def generate_trips_schedules():
    print("Generating trips and schedules...")
    routes_df = pd.read_csv(os.path.join(RAW_DIR, 'routes.csv'))
    vehicles_df = pd.read_csv(os.path.join(RAW_DIR, 'vehicles.csv'))
    route_stops_df = pd.read_csv(os.path.join(RAW_DIR, 'route_stops.csv'))
    
    route_ids = routes_df['route_id'].values
    vehicle_ids = vehicles_df['vehicle_id'].values
    
    # Distribute trips over 360 days
    date_range = pd.date_range(start='2025-01-01', periods=DAYS_TOTAL, freq='D')
    
    # Generate 510,000 trips
    num_trips = MIN_TRIP_RECORDS
    trip_ids = [f"T{str(i).zfill(6)}" for i in range(1, num_trips + 1)]
    trip_routes = np.random.choice(route_ids, num_trips)
    trip_vehicles = np.random.choice(vehicle_ids, num_trips)
    
    # Assign random dates and times for scheduled_start
    random_dates = np.random.choice(date_range, num_trips)
    random_hours = np.random.randint(5, 23, num_trips)
    random_mins = np.random.randint(0, 60, num_trips)
    
    # Create start times
    start_times = random_dates + pd.to_timedelta(random_hours, unit='h') + pd.to_timedelta(random_mins, unit='m')
    # Random trip duration 30 to 120 mins
    durations = pd.to_timedelta(np.random.randint(30, 120, num_trips), unit='m')
    end_times = start_times + durations
    
    # Weekday vs Weekend service
    day_of_week = start_times.dayofweek
    services = np.where(day_of_week < 5, 'SVC_WEEKDAY', 'SVC_WEEKEND')
    
    trips_df = pd.DataFrame({
        'trip_id': trip_ids,
        'route_id': trip_routes,
        'vehicle_id': trip_vehicles,
        'service_id': services,
        'scheduled_start': start_times,
        'scheduled_end': end_times
    })
    
    trips_df.to_csv(os.path.join(RAW_DIR, 'trips.csv'), index=False)
    
    # Schedules: We'll create generic schedules per route instead of per trip to keep it realistic
    # Let's create 5 blueprint schedules per route
    schedules = []
    sched_id = 1
    for r in route_ids:
        stops_for_route = route_stops_df[route_stops_df['route_id'] == r].sort_values('stop_sequence')
        for bp in range(5):
            base_hour = 6 + (bp * 3)
            current_time = pd.Timestamp('2025-01-01') + pd.Timedelta(hours=base_hour)
            for _, row in stops_for_route.iterrows():
                arr = current_time
                current_time += pd.Timedelta(minutes=2) # 2 min dwell
                dep = current_time
                current_time += pd.Timedelta(minutes=np.random.randint(3, 8)) # travel to next stop
                
                schedules.append({
                    'schedule_id': f"SCH_{sched_id}",
                    'route_id': r,
                    'stop_id': row['stop_id'],
                    'scheduled_arrival': arr.strftime('%H:%M:%S'),
                    'scheduled_departure': dep.strftime('%H:%M:%S')
                })
            sched_id += 1
            
    pd.DataFrame(schedules).to_csv(os.path.join(RAW_DIR, 'schedules.csv'), index=False)

if __name__ == "__main__":
    generate_trips_schedules()
