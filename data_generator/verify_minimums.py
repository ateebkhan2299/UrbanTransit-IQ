import pandas as pd
import os

CHECKS = {
    "tickets.csv": 2_000_000,
    "passenger_counts.csv": 500_000,
    "routes.csv": 100,
    "stops.csv": 500,
    "vehicles.csv": 250,
    "passengers.csv": 50_000,
    "delays.csv": 250_000,
}

def verify_minimums():
    all_pass = True
    print(f"{'TABLE':25s} {'REQUIRED':>10s}  {'ACTUAL':>10s}  STATUS")
    print("-" * 60)
    for filename, minimum in CHECKS.items():
        filepath = os.path.join("raw_data", filename)
        if not os.path.exists(filepath):
            print(f"{filename:25s} required>={minimum:>10,}  actual=MISSING  [FAIL]")
            all_pass = False
            continue
            
        count = sum(1 for _ in open(filepath, errors='ignore')) - 1
        status = "PASS" if count >= minimum else "FAIL"
        if status == "FAIL":
            all_pass = False
        print(f"{filename:25s} required>={minimum:>10,}  actual={count:>10,}  [{status}]")

    print("\nOVERALL:", "ALL MINIMUMS MET ✅" if all_pass else "MINIMUMS NOT MET ❌ — DO NOT PROCEED TO PHASE 2")

if __name__ == "__main__":
    verify_minimums()
