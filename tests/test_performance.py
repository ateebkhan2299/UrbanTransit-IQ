import pytest
import requests
import time

def test_sla_performance():
    # SLA: Dashboard API must respond in under 2 seconds
    start = time.time()
    response = requests.get("http://127.0.0.1:8000/api/health")
    duration = time.time() - start
    
    assert response.status_code == 200
    assert duration < 2.0, f"SLA Violation: API took {duration}s"
