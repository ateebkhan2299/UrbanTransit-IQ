import pandas as pd
import numpy as np
import os
from config_gen import RAW_DIR, NUM_PASSENGERS, MIN_TICKETS, CHUNK_SIZE

np.random.seed(42)

def generate_passengers_tickets():
    print("Generating passengers and tickets...")
    
    # 1. Passengers
    pass_ids = [f"P{str(i).zfill(6)}" for i in range(1, NUM_PASSENGERS + 1)]
    types = np.random.choice(['Adult', 'Student', 'Senior', 'Child'], NUM_PASSENGERS, p=[0.6, 0.2, 0.15, 0.05])
    dates = pd.date_range('2024-01-01', periods=DAYS_TOTAL if 'DAYS_TOTAL' in globals() else 360).values
    reg_dates = np.random.choice(dates, NUM_PASSENGERS)
    
    # Just dummy names for speed
    names = [f"Passenger_{i}" for i in range(1, NUM_PASSENGERS + 1)]
    
    pass_df = pd.DataFrame({
        'passenger_id': pass_ids,
        'name': names,
        'registration_date': reg_dates,
        'passenger_type': types
    })
    pass_df.to_csv(os.path.join(RAW_DIR, 'passengers.csv'), index=False)
    
    # 2. Tickets (Chunked because 2,100,000 is large)
    trips_df = pd.read_csv(os.path.join(RAW_DIR, 'trips.csv'), usecols=['trip_id', 'scheduled_start'])
    trip_ids = trips_df['trip_id'].values
    
    total_tickets = MIN_TICKETS
    ticket_types = ['Single', 'Daily Pass', 'Weekly Pass', 'Monthly Pass']
    ticket_prices = [2.50, 7.00, 25.00, 80.00]
    
    print(f"Generating {total_tickets:,} tickets in chunks of {CHUNK_SIZE:,}...")
    
    first_chunk = True
    for start in range(0, total_tickets, CHUNK_SIZE):
        n = min(CHUNK_SIZE, total_tickets - start)
        t_ids = [f"TK{str(i).zfill(7)}" for i in range(start + 1, start + n + 1)]
        t_pass = np.random.choice(pass_ids, n)
        t_trips = np.random.choice(trip_ids, n)
        
        t_type_choices = np.random.choice(len(ticket_types), n, p=[0.7, 0.15, 0.1, 0.05])
        t_types = [ticket_types[i] for i in t_type_choices]
        t_fares = [ticket_prices[i] for i in t_type_choices]
        
        # Purchase time slightly before trip start
        # To avoid merging 2 million rows, we'll just fake random dates for speed
        p_times = pd.to_datetime('2025-01-01') + pd.to_timedelta(np.random.randint(0, 360*24*60, n), unit='m')
        
        chunk_df = pd.DataFrame({
            'ticket_id': t_ids,
            'passenger_id': t_pass,
            'trip_id': t_trips,
            'fare': t_fares,
            'purchase_time': p_times,
            'ticket_type': t_types
        })
        
        chunk_df.to_csv(os.path.join(RAW_DIR, 'tickets.csv'), mode='a', header=first_chunk, index=False)
        first_chunk = False
        print(f"  Written {start + n:,} / {total_tickets:,} tickets")

if __name__ == "__main__":
    generate_passengers_tickets()
