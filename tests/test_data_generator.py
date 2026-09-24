import os
import pytest
import pandas as pd
from data_generator.data_generator import run_data_generation, RAW_DATA_DIR, PARQUET_DATA_DIR

TABLE_NAMES = [
    "stops", "routes", "route_stops", "vehicles", "passengers",
    "service_calendar", "trips", "schedules", "passenger_counts",
    "delays", "gps_events", "tickets"
]

@pytest.fixture(scope="module", autouse=True)
def generate_test_data():
    """Ensure data is generated before tests run."""
    run_data_generation()

def test_raw_csv_files_exist():
    for table in TABLE_NAMES:
        csv_path = os.path.join(RAW_DATA_DIR, f"{table}.csv")
        assert os.path.exists(csv_path), f"Missing CSV file: {csv_path}"

def test_parquet_files_exist():
    for table in TABLE_NAMES:
        parquet_path = os.path.join(PARQUET_DATA_DIR, f"{table}.parquet")
        assert os.path.exists(parquet_path), f"Missing Parquet file: {parquet_path}"

def test_reference_json_files_exist():
    for table in ["stops", "routes"]:
        json_path = os.path.join(RAW_DATA_DIR, f"{table}.json")
        assert os.path.exists(json_path), f"Missing JSON reference file: {json_path}"

def test_tickets_injected_anomalies():
    tickets_df = pd.read_csv(os.path.join(RAW_DATA_DIR, "tickets.csv"))
    # Check non-empty
    assert len(tickets_df) > 0, "Tickets table is empty"
    # Check injected NaN passenger IDs
    missing_pax = tickets_df["passenger_id"].isna().sum()
    assert missing_pax > 0, "Expected missing passenger_id anomalies in tickets table"
    # Check injected duplicate ticket_id
    dupe_tickets = tickets_df["ticket_id"].duplicated().sum()
    assert dupe_tickets > 0, "Expected duplicate ticket_id anomalies in tickets table"

def test_passenger_counts_negative_boarding_injected():
    counts_df = pd.read_csv(os.path.join(RAW_DATA_DIR, "passenger_counts.csv"))
    assert len(counts_df) > 0, "Passenger counts table is empty"
    neg_boarded = (counts_df["boarded_count"] < 0).sum()
    assert neg_boarded > 0, "Expected negative boarded_count anomalies in passenger_counts table"
