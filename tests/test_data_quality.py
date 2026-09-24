import os
import importlib
import pytest
import pandas as pd

PROCESSED_DATA_DIR = "./processed_data"

@pytest.fixture(scope="module")
def spark_session():
    ingest = importlib.import_module("spark_jobs.01_ingest")
    spark = ingest.get_spark_session("PyTest_SparkSession")
    yield spark
    spark.stop()

def test_data_quality_report_generated(spark_session):
    dq = importlib.import_module("spark_jobs.02_data_quality")
    dq.run_data_quality_audit(spark_session)

    csv_path = os.path.join(PROCESSED_DATA_DIR, "data_quality_report.csv")
    assert os.path.exists(csv_path), "Data quality report CSV missing"
    df = pd.read_csv(csv_path)
    assert len(df) > 0, "Data quality report is empty"

def test_data_cleaning_rules(spark_session):
    cleaning = importlib.import_module("spark_jobs.03_cleaning")
    cleaned_map = cleaning.clean_data(spark_session)

    # Check tickets clean rules
    tickets_clean = cleaned_map["tickets"]
    null_pax_count = tickets_clean.filter(tickets_clean.passenger_id.isNull()).count()
    assert null_pax_count == 0, "Cleaned tickets dataset still contains NULL passenger_id"

    # Check passenger_counts clean rules
    counts_clean = cleaned_map["passenger_counts"]
    neg_boardings = counts_clean.filter(counts_clean.boarded_count < 0).count()
    assert neg_boardings == 0, "Cleaned passenger_counts dataset still contains negative boarded_count"
