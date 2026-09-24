import os
import json
from datetime import datetime
import pandas as pd
import sqlite3

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
hdfs_clean = os.path.join(base_path, "hdfs_data", "parquet_clean")
db_path = os.path.join(base_path, "backend", "transit.db")

# Load data
trips = pd.read_parquet(os.path.join(hdfs_clean, "Trips"))
tickets = pd.read_parquet(os.path.join(hdfs_clean, "Tickets"))
passenger_counts = pd.read_parquet(os.path.join(hdfs_clean, "Passenger_Counts"))
stops = pd.read_parquet(os.path.join(hdfs_clean, "Stops"))
delays = pd.read_parquet(os.path.join(hdfs_clean, "Delays"))
routes = pd.read_parquet(os.path.join(hdfs_clean, "Routes"))
route_stops = pd.read_parquet(os.path.join(hdfs_clean, "Route_Stops"))

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Passenger Flow
pc = passenger_counts.copy()
pc['timestamp'] = pd.to_datetime(pc['timestamp'])
pc['time'] = pc['timestamp'].dt.hour
ba = pc.groupby('time')[['boarding_count', 'alighting_count']].sum().reset_index()
boarding_alighting_json = [{"time": f"{int(row['time']):02d}:00", "boarding": int(row['boarding_count']), "alighting": int(row['alighting_count'])} for _, row in ba.iterrows()]

tickets_trips = tickets.merge(trips, on='trip_id')
od = tickets_trips.groupby(['boarding_stop_id', 'alighting_stop_id', 'route_id', 'day_type']).size().reset_index(name='count')
od = od.sort_values('count', ascending=False).head(200)
od = od.merge(stops[['stop_id', 'stop_name']], left_on='boarding_stop_id', right_on='stop_id').rename(columns={'stop_name': 'origin'})
od = od.merge(stops[['stop_id', 'stop_name']], left_on='alighting_stop_id', right_on='stop_id').rename(columns={'stop_name': 'destination'})
od_matrix_json = [{"origin": row['origin'], "destination": row['destination'], "count": int(row['count']), "route_id": row['route_id'], "day_type": row['day_type']} for _, row in od.iterrows()]

tickets['timestamp'] = pd.to_datetime(tickets['timestamp'])
tickets['hour'] = tickets['timestamp'].dt.hour
hv = tickets.groupby('hour').size().reset_index(name='volume')
avg_h = hv['volume'].mean()
hv['is_peak'] = hv['volume'] > (avg_h * 1.5)
peak_periods_json = [{"time": f"{int(row['hour']):02d}:00", "volume": int(row['volume']), "is_peak": bool(row['is_peak'])} for _, row in hv.iterrows()]

total_demand = len(tickets)
busiest = pc.groupby('stop_id')['boarding_count'].sum().reset_index().merge(stops, on='stop_id').sort_values('boarding_count', ascending=False)
busiest_stop_name = busiest.iloc[0]['stop_name'] if not busiest.empty else "Unknown"

cursor.execute("DELETE FROM passenger_flow_summaries")
cursor.execute("INSERT INTO passenger_flow_summaries (boarding_alighting_json, od_matrix_json, peak_periods_json, total_demand, busiest_stop_name, computed_at) VALUES (?, ?, ?, ?, ?, ?)",
               (json.dumps(boarding_alighting_json), json.dumps(od_matrix_json), json.dumps(peak_periods_json), total_demand, busiest_stop_name, datetime.utcnow().isoformat()))

# 2. Delays
delays['severity'] = pd.cut(delays['delay_minutes'], bins=[-1, 2, 5, 15, 30, 9999], labels=["On Time", "Minor", "Moderate", "Major", "Severe"])
sev = delays['severity'].value_counts().reset_index()
sev.columns = ['name', 'value']
severity_breakdown_json = [{"name": row['name'], "value": int(row['value'])} for _, row in sev.iterrows()]

delays['date'] = pd.to_datetime(delays['timestamp']).dt.date
dt = delays.groupby('date')['delay_minutes'].mean().reset_index()
delay_trend_json = [{"date": str(row['date']), "total_delay": float(row['delay_minutes'])} for _, row in dt.tail(30).iterrows()]

dtrips = delays[delays['delay_minutes'] > 5].merge(trips, on='trip_id')
tstops = dtrips.merge(route_stops, on='route_id')
bc = tstops.groupby('stop_id').agg(freq=('stop_id', 'count'), avg_delay=('delay_minutes', 'mean')).reset_index()
bc = bc.sort_values('freq', ascending=False).head(10).merge(stops, on='stop_id')
bottlenecks_json = [{"stop_id": row['stop_id'], "stop_name": row['stop_name'], "avg_delay": float(row['avg_delay'])} for _, row in bc.iterrows()]

cursor.execute("DELETE FROM delay_analysis_summaries")
cursor.execute("INSERT INTO delay_analysis_summaries (severity_breakdown_json, delay_trend_json, bottlenecks_json, predicted_risks_json, computed_at) VALUES (?, ?, ?, ?, ?)",
               (json.dumps(severity_breakdown_json), json.dumps(delay_trend_json), json.dumps(bottlenecks_json), json.dumps([]), datetime.utcnow().isoformat()))

# 3. Occupancy
if 'occupancy_pct' not in trips.columns:
    trips['occupancy_pct'] = (trips['passenger_load'] / trips['capacity']) * 100
avg_utilization = float(trips['occupancy_pct'].mean())
trips['date'] = pd.to_datetime(trips['scheduled_start']).dt.date
ot = trips.groupby('date')['occupancy_pct'].mean().reset_index()
occupancy_trend_json = [{"time": str(row['date']), "occupancy_pct": float(row['occupancy_pct'])} for _, row in ot.tail(30).iterrows()]
roc = trips.groupby('route_id')['occupancy_pct'].mean().reset_index().merge(routes, on='route_id').sort_values('occupancy_pct', ascending=False).head(20)
overcrowded_routes_json = [{"route_id": row['route_id'], "route_name": row['route_name'], "occupancy_pct": float(row['occupancy_pct'])} for _, row in roc.iterrows()]

cursor.execute("DELETE FROM occupancy_dashboard_summaries")
cursor.execute("INSERT INTO occupancy_dashboard_summaries (avg_utilization, utilization_change, occupancy_trend_json, overcrowded_routes_json, high_risk_trips_json, computed_at) VALUES (?, ?, ?, ?, ?, ?)",
               (avg_utilization, 0.0, json.dumps(occupancy_trend_json), json.dumps(overcrowded_routes_json), json.dumps([]), datetime.utcnow().isoformat()))

# 4. Route Geo
cursor.execute("SELECT route_id, avg_delay_minutes FROM route_summaries")
r_delays = dict(cursor.fetchall())
for _, r in routes.iterrows():
    rid = r['route_id']
    rname = r['route_name']
    path = []
    sstops = []
    
    st = route_stops[route_stops['route_id'] == rid].merge(stops, on='stop_id').sort_values('stop_sequence')
    for _, s in st.iterrows():
        b_count = passenger_counts[passenger_counts['stop_id'] == s['stop_id']]['boarding_count'].sum()
        sstops.append({"stop_id": s['stop_id'], "stop_name": s['stop_name'], "latitude": s['latitude'], "longitude": s['longitude'], "boardings": float(b_count)})
        path.append([s['latitude'], s['longitude']])
        
    avg_d = r_delays.get(rid, 0.0)
    avg_o = float(trips[trips['route_id'] == rid]['occupancy_pct'].mean())
    status = 'high' if avg_d > 15 else 'moderate' if avg_d > 5 else 'normal'
    
    cursor.execute("SELECT id FROM route_geos WHERE route_id=?", (rid,))
    if cursor.fetchone():
        cursor.execute("UPDATE route_geos SET route_name=?, status_color=?, path_json=?, avg_delay=?, avg_occupancy=?, stops_json=? WHERE route_id=?",
                       (rname, status, json.dumps(path), avg_d, avg_o, json.dumps(sstops), rid))
    else:
        cursor.execute("INSERT INTO route_geos (route_id, route_name, status_color, path_json, avg_delay, avg_occupancy, stops_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (rid, rname, status, json.dumps(path), avg_d, avg_o, json.dumps(sstops)))

# 5. Route Performance Phase B
for _, r in routes.iterrows():
    rid = r['route_id']
    rtrips = trips[trips['route_id'] == rid]
    if rtrips.empty: continue
    
    avg_occ = rtrips['occupancy_pct'].mean()
    rdelays = delays.merge(rtrips, on='trip_id', how='right')
    rdelays['delay_minutes'] = rdelays['delay_minutes'].fillna(0)
    mean_delay = rdelays['delay_minutes'].mean()
    
    punc = (rdelays['delay_minutes'] <= 2).mean() * 100
    score = 80.0
    cat = "High Performing"
    
    delay_trend = [float(x) for x in rdelays['delay_minutes'].tail(14)]
    occ_trend = [float(x) for x in rtrips['occupancy_pct'].tail(14)]
    
    cursor.execute("SELECT id FROM route_summaries WHERE route_id=?", (rid,))
    if cursor.fetchone():
        cursor.execute("UPDATE route_summaries SET performance_score=?, performance_tier=?, delay_trend_json=?, occupancy_trend_json=? WHERE route_id=?",
                       (score, cat, json.dumps(delay_trend), json.dumps(occ_trend), rid))
    else:
        cursor.execute("INSERT INTO route_summaries (route_id, route_name, total_passengers, total_trips, avg_occupancy_pct, avg_delay_minutes, on_time_performance_pct, performance_score, performance_tier, delay_trend_json, occupancy_trend_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (rid, r['route_name'], 1000, len(rtrips), avg_occ, mean_delay, punc, score, cat, json.dumps(delay_trend), json.dumps(occ_trend)))
                       
conn.commit()
conn.close()
print("Pandas test population complete!")
