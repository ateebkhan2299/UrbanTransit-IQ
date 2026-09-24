from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models_db import DelaySummary, RouteSummary
from backend.schemas import DelayCauseItem, DelaySummarySchema, RouteSummarySchema

router = APIRouter(prefix="/api/delays", tags=["delays"])

@router.get("/by-cause", response_model=List[DelayCauseItem])
def get_delays_by_cause(route_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    delays = db.query(DelaySummary).all()
    res = [
        DelayCauseItem(
            cause=d.cause,
            incident_count=d.incident_count,
            percentage_share=d.percentage_share
        )
        for d in delays
    ]
    return res

@router.get("/summary", response_model=List[DelaySummarySchema])
def get_delay_summary(db: Session = Depends(get_db)):
    delays = db.query(DelaySummary).all()
    return delays

@router.get("/routes", response_model=List[RouteSummarySchema])
def get_delayed_routes(db: Session = Depends(get_db)):
    routes = db.query(RouteSummary).order_by(RouteSummary.avg_delay_minutes.desc()).all()
    return routes
