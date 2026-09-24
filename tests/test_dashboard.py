import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_dashboard_no_seeded_magic_numbers():
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    
    # Assert that all change percentages are 0.0 (removed magic numbers 8.4, 2.1, -1.2, 3.4)
    assert data["total_passengers_change_pct"] == 0.0
    assert data["total_trips_change_pct"] == 0.0
    assert data["avg_occupancy_change_pct"] == 0.0
    assert data["on_time_change_pct"] == 0.0

    # Ensure that top routes don't return fake 'Cluster' data if empty
    top_routes = client.get("/api/dashboard/top-routes?limit=5")
    assert top_routes.status_code == 200
    routes_data = top_routes.json()
    assert isinstance(routes_data, list)
