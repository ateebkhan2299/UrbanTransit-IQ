from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models_db import RouteSummary
from backend.schemas import RecommendationSchema

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

@router.get("", response_model=List[RecommendationSchema])
def get_recommendations(route_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    query = db.query(RouteSummary)
    if route_id:
        query = query.filter(RouteSummary.route_id == route_id)
    routes = query.all()
    recommendations = []
    rec_id = 1

    for r in routes:
        if r.avg_occupancy_pct > 85.0:
            recommendations.append(RecommendationSchema(
                id=str(rec_id),
                title=f"Deploy Additional Capacity on Route {r.route_id}",
                description=f"{r.route_name} operates at high occupancy ({r.avg_occupancy_pct}%). Deploy 2 extra buses during 07:30 - 09:00.",
                priority="HIGH",
                route_id=r.route_id,
                expected_impact="Reduces overcrowding by ~18% and improves passenger comfort."
            ))
            rec_id += 1
        elif r.avg_occupancy_pct < 30.0:
            recommendations.append(RecommendationSchema(
                id=str(rec_id),
                title=f"Optimize Off-Peak Headway for Route {r.route_id}",
                description=f"{r.route_name} is underutilized ({r.avg_occupancy_pct}% avg occupancy). Increase headway interval during off-peak.",
                priority="MEDIUM",
                route_id=r.route_id,
                expected_impact="Reduces operational cost by ~12% without impacting service level."
            ))
            rec_id += 1

        if r.avg_delay_minutes > 15.0:
            recommendations.append(RecommendationSchema(
                id=str(rec_id),
                title=f"Traffic Signal Priority Allocation for Route {r.route_id}",
                description=f"{r.route_name} experiences severe delays ({r.avg_delay_minutes} mins avg). Enable TSP at major intersections.",
                priority="HIGH",
                route_id=r.route_id,
                expected_impact="Cuts signal delay by up to 25%."
            ))
            rec_id += 1

    if not recommendations:
        recommendations.append(RecommendationSchema(
            id="1",
            title="System Operating Within Optimal Parameters",
            description="All monitored routes are operating within normal occupancy and delay limits.",
            priority="LOW",
            route_id=None,
            expected_impact="Maintain baseline schedules."
        ))

    return recommendations
