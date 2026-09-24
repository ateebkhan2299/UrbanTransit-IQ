from fastapi import APIRouter, HTTPException
import os
import json

router = APIRouter(prefix="/api/models", tags=["models"])

COMPARISON_REPORT_PATH = "./comparison/model_comparison_report.json"

@router.get("/comparison")
def get_model_comparison():
    if not os.path.exists(COMPARISON_REPORT_PATH):
        raise HTTPException(status_code=404, detail="Model comparison report not found. Run comparison pipeline first.")

    with open(COMPARISON_REPORT_PATH, "r") as f:
        data = json.load(f)
    return data
