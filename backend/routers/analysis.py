"""
UrbanTransit IQ - Analysis Router
Handles passenger flow, stop performance, and OD matrix endpoints.
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/passenger-flow")
def get_passenger_flow():
    """Passenger flow breakdown by type, time, and weekday."""
    return {
        "passenger_types": [
            {"name": "Regular",  "value": 32500},
            {"name": "Student",  "value": 11200},
            {"name": "Senior",   "value": 4800 },
            {"name": "Monthly",  "value": 8700 },
        ],
        "monthly_registrations": [
            {"month": "Jan", "registrations": 3200},
            {"month": "Feb", "registrations": 2800},
            {"month": "Mar", "registrations": 4100},
            {"month": "Apr", "registrations": 3700},
            {"month": "May", "registrations": 4500},
            {"month": "Jun", "registrations": 5200},
            {"month": "Jul", "registrations": 4900},
            {"month": "Aug", "registrations": 5600},
            {"month": "Sep", "registrations": 4300},
            {"month": "Oct", "registrations": 3900},
            {"month": "Nov", "registrations": 3400},
            {"month": "Dec", "registrations": 2900},
        ],
        "hourly_tickets": [
            {"hour": "06", "tickets": 1200},
            {"hour": "07", "tickets": 3400},
            {"hour": "08", "tickets": 6800},
            {"hour": "09", "tickets": 4200},
            {"hour": "10", "tickets": 2100},
            {"hour": "11", "tickets": 1800},
            {"hour": "12", "tickets": 2400},
            {"hour": "13", "tickets": 2200},
            {"hour": "14", "tickets": 1900},
            {"hour": "15", "tickets": 2600},
            {"hour": "16", "tickets": 3800},
            {"hour": "17", "tickets": 7200},
            {"hour": "18", "tickets": 5400},
            {"hour": "19", "tickets": 3100},
            {"hour": "20", "tickets": 1600},
            {"hour": "21", "tickets": 900 },
        ],
        "weekday_volume": [
            {"day": "Mon", "trips": 4200},
            {"day": "Tue", "trips": 4050},
            {"day": "Wed", "trips": 4300},
            {"day": "Thu", "trips": 4150},
            {"day": "Fri", "trips": 4700},
            {"day": "Sat", "trips": 3100},
            {"day": "Sun", "trips": 2400},
        ],
    }

@router.get("/route-performance")
def get_route_performance():
    """Route scoring, classification, and radar metrics."""
    return {
        "top_routes": [
            {"route": "R12", "score": 91, "on_time": 94, "occupancy": 88, "freq": 85},
            {"route": "R04", "score": 87, "on_time": 89, "occupancy": 72, "freq": 90},
            {"route": "R22", "score": 83, "on_time": 85, "occupancy": 79, "freq": 84},
            {"route": "R08", "score": 80, "on_time": 82, "occupancy": 65, "freq": 88},
            {"route": "R01", "score": 76, "on_time": 77, "occupancy": 58, "freq": 79},
        ],
        "classification": [
            {"name": "High Performing", "count": 28},
            {"name": "Overcrowded",     "count": 14},
            {"name": "Balanced",        "count": 32},
            {"name": "Low Performing",  "count": 18},
            {"name": "Underutilized",   "count": 13},
        ],
        "radar": [
            {"metric": "On-Time %",   "R12": 94, "R04": 89, "R08": 82},
            {"metric": "Occupancy",   "R12": 88, "R04": 72, "R08": 65},
            {"metric": "Frequency",   "R12": 85, "R04": 90, "R08": 88},
            {"metric": "Punctuality", "R12": 90, "R04": 86, "R08": 80},
            {"metric": "Load Factor", "R12": 82, "R04": 74, "R08": 70},
        ],
        "route_table": [
            {"route": "R12", "classification": "High Performing", "score": 91, "delay_avg": 5.2,  "occ": 88 },
            {"route": "R04", "classification": "Overcrowded",     "score": 87, "delay_avg": 9.1,  "occ": 105},
            {"route": "R22", "classification": "Balanced",        "score": 83, "delay_avg": 7.4,  "occ": 72 },
            {"route": "R09", "classification": "Underutilized",   "score": 41, "delay_avg": 3.1,  "occ": 22 },
            {"route": "R17", "classification": "Low Performing",  "score": 38, "delay_avg": 21.5, "occ": 34 },
        ],
    }

@router.get("/stop-performance")
def get_stop_performance():
    """Top bottleneck stops by avg boarding time."""
    return {
        "bottleneck_stops": [
            {"stop_id": "S042", "stop_name": "Central Station",   "avg_dwell": 3.8, "daily_boardings": 8200},
            {"stop_id": "S017", "stop_name": "Market Square",     "avg_dwell": 3.1, "daily_boardings": 6100},
            {"stop_id": "S089", "stop_name": "University Gate",   "avg_dwell": 2.9, "daily_boardings": 5400},
            {"stop_id": "S031", "stop_name": "Airport Terminal",  "avg_dwell": 2.6, "daily_boardings": 4800},
            {"stop_id": "S055", "stop_name": "Hospital Entrance", "avg_dwell": 2.2, "daily_boardings": 3900},
        ]
    }
