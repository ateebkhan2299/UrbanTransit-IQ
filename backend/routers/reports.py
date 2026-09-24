from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from backend.database import get_db
import csv
import io

from backend.models_db import RouteSummary, PassengerFlowSummary
from backend.routers.auth import require_roles

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.get("/export")
def export_csv(type: str = "routes", format: str = "csv", db: Session = Depends(get_db), current_user = Depends(require_roles(["Admin", "Operator", "Analyst", "Evaluator"]))):
    output = io.StringIO()
    writer = csv.writer(output)
    
    if type == "route_performance" or type == "routes":
        data = db.query(RouteSummary).all()
        if not data:
            return Response(content="No data available", media_type="text/csv")
        # Write headers
        writer.writerow(["ID", "Route ID", "Route Name", "Avg Occupancy", "Avg Delay Mins", "Crowding Risk", "Last Updated"])
        for row in data:
            writer.writerow([row.id, row.route_id, row.route_name, row.avg_occupancy, row.avg_delay_minutes, row.crowding_risk_level, row.updated_at])
            
    elif type == "passenger_demand" or type == "flow":
        data = db.query(PassengerFlowSummary).all()
        if not data:
            return Response(content="No data available", media_type="text/csv")
        writer.writerow(["ID", "Total Boardings", "Total Alightings", "Peak Hour Ridership", "Top Route ID", "Last Updated"])
        for row in data:
            writer.writerow([row.id, row.total_boardings, row.total_alightings, row.peak_hour_ridership, row.top_route_id, row.updated_at])
            
    else:
        # Fallback empty csv for other types not yet mapped in DB
        writer.writerow(["Data not available for this report type yet."])
    
    csv_content = output.getvalue()
    output.close()
    
    return Response(
        content=csv_content,
        media_type="text/csv" if format == "csv" else "application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=urbantransit_{type}_export.{format}"
        }
    )
