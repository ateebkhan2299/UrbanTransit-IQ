from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from backend.database import get_db
from backend.models_db import RouteSummary, WhatIfScenario
from backend.schemas import (
    WhatIfSimulateContractRequest,
    WhatIfSimulateContractResponse,
    WhatIfSimulateMetrics
)

router = APIRouter(prefix="/api/whatif", tags=["whatif"])

@router.post("/simulate", response_model=WhatIfSimulateContractResponse)
def simulate_whatif_scenario(req: WhatIfSimulateContractRequest, db: Session = Depends(get_db)):
    route = db.query(RouteSummary).filter(RouteSummary.route_id == req.route_id).first()

    base_occ = route.avg_occupancy_pct if route else 65.0
    base_delay = route.avg_delay_minutes if route else 12.0

    # Baseline metrics
    before = WhatIfSimulateMetrics(
        occupancy_pct=round(base_occ, 1),
        avg_wait_min=round(base_delay * 0.8, 1),
        overcrowd_risk_pct=round(min(100.0, base_occ * 1.1), 1)
    )

    # Heuristic model based on change_type
    change_type = req.change_type.lower()
    val = req.change_value

    if change_type in ["frequency", "headway"]:
        # Increase frequency reduces wait min and occupancy
        factor = 1.0 + (val / 100.0) if val > 0 else 1.0
        after_occ = max(10.0, base_occ / max(0.5, factor))
        after_wait = max(2.0, before.avg_wait_min / max(0.5, factor))
    elif change_type in ["capacity", "fleet"]:
        factor = 1.0 + (val / 100.0) if val > 0 else 1.0
        after_occ = max(10.0, base_occ / max(0.5, factor))
        after_wait = before.avg_wait_min
    elif change_type == "add_trip":
        after_occ = max(10.0, base_occ * 0.85)
        after_wait = max(2.0, before.avg_wait_min * 0.8)
    elif change_type == "remove_trip":
        after_occ = min(100.0, base_occ * 1.2)
        after_wait = before.avg_wait_min * 1.25
    else:
        after_occ = base_occ
        after_wait = before.avg_wait_min

    after_risk = min(100.0, after_occ * 1.1)

    after = WhatIfSimulateMetrics(
        occupancy_pct=round(after_occ, 1),
        avg_wait_min=round(after_wait, 1),
        overcrowd_risk_pct=round(after_risk, 1)
    )

    scenario_record = WhatIfScenario(
        scenario_name=f"Sim_{req.route_id}_{req.change_type}_{req.change_value}",
        inputs_json=req.model_dump(),
        results_json={
            "before": before.model_dump(),
            "after": after.model_dump(),
            "is_estimate": True
        }
    )
    db.add(scenario_record)
    db.commit()

    return WhatIfSimulateContractResponse(
        before=before,
        after=after,
        is_estimate=True
    )
