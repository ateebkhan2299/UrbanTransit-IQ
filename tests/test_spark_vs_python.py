import os
import sys
import json
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from comparison.dual_pipeline_comparison import run_dual_pipeline_comparison

def test_spark_vs_python_comparison_report():
    report = run_dual_pipeline_comparison()

    assert "models" in report
    models = report["models"]

    # Verify Delay Prediction metrics present
    assert "spark_mllib" in models["delay_prediction"]
    assert "python_sklearn" in models["delay_prediction"]

    # Verify Demand Forecast metrics present
    assert "spark_mllib" in models["demand_forecast"]
    assert "python_sklearn" in models["demand_forecast"]

    # Verify Occupancy Risk metrics present
    assert "spark_mllib" in models["occupancy_risk"]
    assert "python_sklearn" in models["occupancy_risk"]

    # Check that model metrics contain numerical values
    py_forecast_r2 = models["demand_forecast"]["python_sklearn"].get("r2")
    assert py_forecast_r2 is not None
    assert isinstance(py_forecast_r2, float)

    # Check report file output exists
    assert os.path.exists("./comparison/model_comparison_report.json")
