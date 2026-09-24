from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models_db import Route, Stop, Vehicle, Trip, SparkJobStatus
from backend.schemas_admin import (
    RouteCreate, RouteOut,
    StopCreate, StopOut,
    VehicleCreate, VehicleOut,
    TripCreate, TripOut,
    SparkJobStatusOut
)
from backend.routers.auth import require_roles, log_audit, get_current_user

router = APIRouter(prefix="/api/admin", tags=["admin-management"])

# --- ROUTES CRUD ---
@router.get("/routes", response_model=List[RouteOut])
def get_routes(db: Session = Depends(get_db), current_user = Depends(require_roles(["Admin", "Operator", "Analyst"]))):
    return db.query(Route).all()

@router.post("/routes", response_model=RouteOut, status_code=status.HTTP_201_CREATED)
def create_route(route: RouteCreate, db: Session = Depends(get_db), current_user = Depends(require_roles(["Admin", "Operator"]))):
    existing = db.query(Route).filter(Route.route_id == route.route_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Route with this ID already exists")
    new_route = Route(**route.model_dump())
    db.add(new_route)
    db.commit()
    db.refresh(new_route)
    log_audit(db, current_user.username, current_user.role, "CREATE_ROUTE", "/api/admin/routes", f"Created route {route.route_id}")
    return new_route

@router.put("/routes/{route_id}", response_model=RouteOut)
def update_route(route_id: str, route: RouteCreate, db: Session = Depends(get_db), current_user = Depends(require_roles(["Admin", "Operator"]))):
    existing = db.query(Route).filter(Route.route_id == route_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Route not found")
    for key, value in route.model_dump().items():
        setattr(existing, key, value)
    db.commit()
    db.refresh(existing)
    return existing

@router.delete("/routes/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_route(route_id: str, db: Session = Depends(get_db), current_user = Depends(require_roles(["Admin", "Operator"]))):
    existing = db.query(Route).filter(Route.route_id == route_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Route not found")
    db.delete(existing)
    db.commit()
    return None


# --- STOPS CRUD ---
@router.get("/stops", response_model=List[StopOut])
def get_stops(db: Session = Depends(get_db), current_user = Depends(require_roles(["Admin", "Operator", "Analyst"]))):
    return db.query(Stop).all()

@router.post("/stops", response_model=StopOut, status_code=status.HTTP_201_CREATED)
def create_stop(stop: StopCreate, db: Session = Depends(get_db), current_user = Depends(require_roles(["Admin", "Operator"]))):
    existing = db.query(Stop).filter(Stop.stop_id == stop.stop_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Stop with this ID already exists")
    new_stop = Stop(**stop.model_dump())
    db.add(new_stop)
    db.commit()
    db.refresh(new_stop)
    log_audit(db, current_user.username, current_user.role, "CREATE_STOP", "/api/admin/stops", f"Created stop {stop.stop_id}")
    return new_stop

@router.put("/stops/{stop_id}", response_model=StopOut)
def update_stop(stop_id: str, stop: StopCreate, db: Session = Depends(get_db), current_user = Depends(require_roles(["Admin", "Operator"]))):
    existing = db.query(Stop).filter(Stop.stop_id == stop_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Stop not found")
    for key, value in stop.model_dump().items():
        setattr(existing, key, value)
    db.commit()
    db.refresh(existing)
    return existing

@router.delete("/stops/{stop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stop(stop_id: str, db: Session = Depends(get_db), current_user = Depends(require_roles(["Admin", "Operator"]))):
    existing = db.query(Stop).filter(Stop.stop_id == stop_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Stop not found")
    db.delete(existing)
    db.commit()
    return None

# --- VEHICLES CRUD ---
@router.get("/vehicles", response_model=List[VehicleOut])
def get_vehicles(db: Session = Depends(get_db), current_user = Depends(require_roles(["Admin", "Operator", "Analyst"]))):
    return db.query(Vehicle).all()

@router.post("/vehicles", response_model=VehicleOut, status_code=status.HTTP_201_CREATED)
def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db), current_user = Depends(require_roles(["Admin", "Operator"]))):
    existing = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle.vehicle_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Vehicle with this ID already exists")
    new_vehicle = Vehicle(**vehicle.model_dump())
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)
    log_audit(db, current_user.username, current_user.role, "CREATE_VEHICLE", "/api/admin/vehicles", f"Created vehicle {vehicle.vehicle_id}")
    return new_vehicle

@router.put("/vehicles/{vehicle_id}", response_model=VehicleOut)
def update_vehicle(vehicle_id: str, vehicle: VehicleCreate, db: Session = Depends(get_db), current_user = Depends(require_roles(["Admin", "Operator"]))):
    existing = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    for key, value in vehicle.model_dump().items():
        setattr(existing, key, value)
    db.commit()
    db.refresh(existing)
    return existing

@router.delete("/vehicles/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(vehicle_id: str, db: Session = Depends(get_db), current_user = Depends(require_roles(["Admin", "Operator"]))):
    existing = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    db.delete(existing)
    db.commit()
    return None

# --- TRIPS CRUD ---
@router.get("/trips", response_model=List[TripOut])
def get_trips(db: Session = Depends(get_db), current_user = Depends(require_roles(["Admin", "Operator", "Analyst"]))):
    return db.query(Trip).all()

@router.post("/trips", response_model=TripOut, status_code=status.HTTP_201_CREATED)
def create_trip(trip: TripCreate, db: Session = Depends(get_db), current_user = Depends(require_roles(["Admin", "Operator"]))):
    existing = db.query(Trip).filter(Trip.trip_id == trip.trip_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Trip with this ID already exists")
    new_trip = Trip(**trip.model_dump())
    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)
    log_audit(db, current_user.username, current_user.role, "CREATE_TRIP", "/api/admin/trips", f"Created trip {trip.trip_id}")
    return new_trip

@router.put("/trips/{trip_id}", response_model=TripOut)
def update_trip(trip_id: str, trip: TripCreate, db: Session = Depends(get_db), current_user = Depends(require_roles(["Admin", "Operator"]))):
    existing = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Trip not found")
    for key, value in trip.model_dump().items():
        setattr(existing, key, value)
    db.commit()
    db.refresh(existing)
    return existing

@router.delete("/trips/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(trip_id: str, db: Session = Depends(get_db), current_user = Depends(require_roles(["Admin", "Operator"]))):
    existing = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Trip not found")
    db.delete(existing)
    db.commit()
    return None

# --- SPARK JOBS STATUS ---
@router.get("/spark-jobs", response_model=List[SparkJobStatusOut])
def get_spark_jobs(db: Session = Depends(get_db), current_user = Depends(require_roles(["Admin", "Evaluator"]))):
    return db.query(SparkJobStatus).order_by(SparkJobStatus.start_time.desc()).all()
