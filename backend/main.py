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
        
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
