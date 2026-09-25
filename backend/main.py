from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db import get_db, engine
from database import models
from sqlalchemy.orm import Session

app = FastAPI(title="UrbanTransit IQ API", version="1.0")

# CORS Configuration for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"], # Vite default is 5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    # Mocking JWT response for demo
    user = db.query(models.User).filter(models.User.username == req.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Normally verify hash here. Since it's a stub, we just return a fake token.
    return {
        "token": f"fake-jwt-token-for-{user.username}",
        "role": user.role,
        "username": user.username
    }

@app.get("/analytics/overview")
def get_overview():
    return {
        "total_passengers": 2150000,
        "active_routes": 105,
        "on_time_pct": 82.4,
        "avg_occupancy_pct": 65.2,
        "open_recommendations": {"low": 5, "medium": 8, "high": 3, "critical": 2},
        "active_anomalies_count": 12,
        "persistently_overcrowded_count": 4
    }

@app.get("/recommendations")
def get_recommendations():
    import json
    try:
        with open("../reports/recommendations.json", "r") as f:
            return json.load(f)
    except:
        return []

@app.get("/config")
def get_config():
    import yaml
    try:
        with open("../config/config.yaml", "r") as f:
            return yaml.safe_load(f)
    except:
        return {}

@app.get("/analytics/delays")
def get_delays():
    return {
        "bar_data": [
            {"route": "R12", "delay_min": 15},
            {"route": "R04", "delay_min": 22},
            {"route": "R08", "delay_min": 8},
            {"route": "R22", "delay_min": 12},
            {"route": "R01", "delay_min": 5},
        ],
        "predictions": [
            {"trip_id": "TR-8812", "spark": "12 min", "python": "14 min", "match": True},
            {"trip_id": "TR-4192", "spark": "25 min", "python": "On Time", "match": False},
            {"trip_id": "TR-1102", "spark": "On Time", "python": "On Time", "match": True},
        ]
    }

@app.get("/analytics/occupancy")
def get_occupancy():
    return {
        "trend": [
            {"time": "06:00", "occ": 30},
            {"time": "08:00", "occ": 95},
            {"time": "10:00", "occ": 60},
            {"time": "12:00", "occ": 55},
            {"time": "15:00", "occ": 70},
            {"time": "17:30", "occ": 105},
            {"time": "20:00", "occ": 40},
        ],
        "high_risk": [
            {"route": "R12 - 08:00 AM", "value": "95%"},
            {"route": "R12 - 05:30 PM", "value": "105% (Overcrowded)"}
        ],
        "underutilized": [
            {"route": "R09 - All Day", "value": "22% Avg"}
        ]
    }

        
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
