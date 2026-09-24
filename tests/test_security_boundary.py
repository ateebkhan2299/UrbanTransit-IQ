import pytest
import requests

def test_security_boundary():
    # Test that without token, admin routes return 401
    response = requests.get("http://127.0.0.1:8000/api/admin/routes")
    assert response.status_code == 401, "Security Boundary Violated: Unauthenticated access allowed"
