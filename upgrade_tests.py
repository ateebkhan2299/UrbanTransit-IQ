import os

tests_dir = r"c:\Users\USER\Desktop\techwiz\tests"
real_tests = {
    "test_performance.py": """import pytest
import requests
import time

def test_sla_performance():
    # SLA: Dashboard API must respond in under 2 seconds
    start = time.time()
    response = requests.get("http://127.0.0.1:8000/api/health")
    duration = time.time() - start
    
    assert response.status_code == 200
    assert duration < 2.0, f"SLA Violation: API took {duration}s"
""",
    "test_security_boundary.py": """import pytest
import requests

def test_security_boundary():
    # Test that without token, admin routes return 401
    response = requests.get("http://127.0.0.1:8000/api/admin/routes")
    assert response.status_code == 401, "Security Boundary Violated: Unauthenticated access allowed"
"""
}

for name, content in real_tests.items():
    with open(os.path.join(tests_dir, name), "w", encoding="utf-8") as f:
        f.write(content)

print("Real SLA tests generated.")
