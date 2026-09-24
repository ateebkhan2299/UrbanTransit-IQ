import sqlite3
import json
from datetime import datetime, timedelta
import random
import os

base_path = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_path, "urbantransit.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def generate_mock_data():
    now_str = datetime.utcnow().isoformat()
    
    # 1. Passenger Flow
    boarding_alighting = []
    for hour in range(24):
        # Realistic diurnal curve
        if 7 <= hour <= 9 or 16 <= hour <= 18:
            vol = random.randint(3000, 5000)
        elif 10 <= hour <= 15:
            vol = random.randint(1500, 2500)
        else:
            vol = random.randint(200, 800)
        
        boarding_alighting.append({
            "time": f"{hour:02d}:00",
            "boarding": vol,
            "alighting": vol - random.randint(-100, 100)
        })

    od_matrix = []
    stops = ["Central Station", "North Hills", "Tech Park", "University City", "Downtown Transit Center", "Airport Hub", "West End"]
    for i in range(15):
        origin = random.choice(stops)
        dest = random.choice([s for s in stops if s != origin])
        od_matrix.append({
            "origin": origin,
            "destination": dest,
            "count": random.randint(500, 2500),
            "route_id": f"R{random.randint(10, 50)}",
            "day_type": "Weekday"
        })

    peak_periods = []
    avg_vol = sum(d["boarding"] for d in boarding_alighting) / 24
    for d in boarding_alighting:
        peak_periods.append({
            "time": d["time"],
            "volume": d["boarding"] + d["alighting"],
            "is_peak": (d["boarding"] + d["alighting"]) > (avg_vol * 1.5)
        })

    cursor.execute("DELETE FROM passenger_flow_summaries")
    cursor.execute("""
        INSERT INTO passenger_flow_summaries (boarding_alighting_json, od_matrix_json, peak_periods_json, total_demand, busiest_stop_name, computed_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        json.dumps(boarding_alighting),
        json.dumps(od_matrix),
        json.dumps(peak_periods),
        152450,
        "Central Station",
        now_str
    ))

    # 2. Delays
    severity = [
        {"name": "On Time", "value": 4500},
        {"name": "Minor", "value": 1200},
        {"name": "Moderate", "value": 600},
        {"name": "Major", "value": 150},
        {"name": "Severe", "value": 50},
    ]
    
    delay_trend = []
    for i in range(30):
        d = datetime.now() - timedelta(days=30-i)
        delay_trend.append({
            "date": d.strftime("%Y-%m-%d"),
            "total_delay": random.uniform(500, 1200)
        })
        
    bottlenecks = []
    for i, stop in enumerate(stops):
        bottlenecks.append({
            "stop_id": f"S{100+i}",
            "stop_name": stop,
            "avg_delay": round(random.uniform(3.5, 12.0), 1)
        })

    predicted_risks = [
        {"trip_id": "T8921", "route_id": "R12", "risk_level": "High", "expected_delay_min": 18.5, "primary_factor": "Heavy Traffic"},
        {"trip_id": "T8945", "route_id": "R08", "risk_level": "Moderate", "expected_delay_min": 8.2, "primary_factor": "Weather"},
    ]

    cursor.execute("DELETE FROM delay_analysis_summaries")
    cursor.execute("""
        INSERT INTO delay_analysis_summaries (severity_breakdown_json, delay_trend_json, bottlenecks_json, predicted_risks_json, computed_at)
        VALUES (?, ?, ?, ?, ?)
    """, (json.dumps(severity), json.dumps(delay_trend), json.dumps(bottlenecks), json.dumps(predicted_risks), now_str))

    # 3. Occupancy
    occupancy_trend = []
    for i in range(30):
        d = datetime.now() - timedelta(days=30-i)
        occupancy_trend.append({
            "time": d.strftime("%Y-%m-%d"),
            "occupancy_pct": round(random.uniform(40.0, 85.0), 1)
        })
        
    overcrowded_routes = [
        {"route_id": "R01", "route_name": "University Express", "occupancy_pct": 94.5},
        {"route_id": "R15", "route_name": "Downtown Loop", "occupancy_pct": 91.2},
    ]

    high_risk_trips = [
        {"trip_id": "T9901", "route_id": "R01", "scheduled_start": "08:15 AM", "predicted_occupancy": 98.0, "recommendation": "Deploy backup bus"},
        {"trip_id": "T9912", "route_id": "R15", "scheduled_start": "05:30 PM", "predicted_occupancy": 95.5, "recommendation": "Increase frequency"},
    ]

    cursor.execute("DELETE FROM occupancy_dashboard_summaries")
    cursor.execute("""
        INSERT INTO occupancy_dashboard_summaries (avg_utilization, utilization_change, occupancy_trend_json, overcrowded_routes_json, high_risk_trips_json, computed_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (62.4, 1.2, json.dumps(occupancy_trend), json.dumps(overcrowded_routes), json.dumps(high_risk_trips), now_str))

    # 4. Route Performance
    routes_data = [
        ("R01", "University Express", "High Performing", 88.5, 6.2, 75.4, 85.0),
        ("R12", "Tech Park Shuttle", "High-Demand-but-Unreliable", 62.0, 14.5, 82.0, 55.0),
        ("R08", "Suburbs Line", "Reliable-but-Underutilized", 71.0, 2.5, 25.0, 96.0),
        ("R15", "Downtown Loop", "Overcrowded", 58.0, 8.2, 92.5, 65.0),
    ]

    for rd in routes_data:
        delay_tr = [round(random.uniform(2.0, 15.0), 1) for _ in range(14)]
        occ_tr = [round(random.uniform(30.0, 95.0), 1) for _ in range(14)]
        
        cursor.execute("SELECT id FROM route_summaries WHERE route_id=?", (rd[0],))
        if cursor.fetchone():
            cursor.execute("""
                UPDATE route_summaries SET 
                performance_tier=?, performance_score=?, avg_delay_minutes=?, avg_occupancy_pct=?, on_time_performance_pct=?, delay_trend_json=?, occupancy_trend_json=?
                WHERE route_id=?
            """, (rd[2], rd[3], rd[4], rd[5], rd[6], json.dumps(delay_tr), json.dumps(occ_tr), rd[0]))
        else:
            cursor.execute("""
                INSERT INTO route_summaries (route_id, route_name, performance_tier, performance_score, avg_delay_minutes, avg_occupancy_pct, on_time_performance_pct, delay_trend_json, occupancy_trend_json, total_passengers, total_trips)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (rd[0], rd[1], rd[2], rd[3], rd[4], rd[5], rd[6], json.dumps(delay_tr), json.dumps(occ_tr), 5000, 150))

    # 5. Route Geo
    path1 = [[40.7128, -74.0060], [40.7138, -74.0050], [40.7148, -74.0040]]
    path2 = [[40.7328, -73.9960], [40.7438, -73.9850], [40.7548, -73.9740]]
    
    stops1 = [{"stop_id": "S1", "stop_name": "Central", "latitude": 40.7128, "longitude": -74.0060, "boardings": 500}]
    
    geo_data = [
        ("R01", "University Express", "normal", path1, 4.2, 65.0, stops1),
        ("R12", "Tech Park Shuttle", "high", path2, 18.5, 85.0, stops1),
    ]
    
    for g in geo_data:
        cursor.execute("SELECT id FROM route_geos WHERE route_id=?", (g[0],))
        if cursor.fetchone():
            cursor.execute("UPDATE route_geos SET status_color=?, path_json=?, avg_delay=?, avg_occupancy=?, stops_json=? WHERE route_id=?", (g[2], json.dumps(g[3]), g[4], g[5], json.dumps(g[6]), g[0]))
        else:
            cursor.execute("INSERT INTO route_geos (route_id, route_name, status_color, path_json, avg_delay, avg_occupancy, stops_json) VALUES (?, ?, ?, ?, ?, ?, ?)", (g[0], g[1], g[2], json.dumps(g[3]), g[4], g[5], json.dumps(g[6])))

    conn.commit()
    conn.close()
    print("Mock data populated successfully!")

if __name__ == "__main__":
    generate_mock_data()
