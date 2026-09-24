import os
import sys
import importlib
from pyspark.sql import functions as F

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import backend.config

ingest_module = importlib.import_module("spark_jobs.01_ingest")
get_spark_session = ingest_module.get_spark_session
ingest_data = ingest_module.ingest_data

PROCESSED_DATA_DIR = "./processed_data"

def run_data_quality_audit(spark):
    print("=== PySpark Data Quality Audit Pipeline ===")
    datasets = ingest_data(spark)
    report_rows = []

    # 1. Audit Tickets Table (Check missing passenger_id, duplicate ticket_id)
    tickets_df = datasets["tickets"]
    total_tickets = tickets_df.count()
    null_pax = tickets_df.filter(F.col("passenger_id").isNull()).count()
    dupe_tickets = tickets_df.groupBy("ticket_id").count().filter(F.col("count") > 1).count()

    report_rows.append({
        "table_name": "tickets",
        "total_records": total_tickets,
        "null_passenger_ids": null_pax,
        "duplicate_ticket_ids": dupe_tickets,
        "negative_boardings": 0,
        "invalid_timestamps": 0
    })

    # 2. Audit Passenger Counts Table (Check negative boarded_count)
    counts_df = datasets["passenger_counts"]
    total_counts = counts_df.count()
    neg_boardings = counts_df.filter(F.col("boarded_count") < 0).count()

    report_rows.append({
        "table_name": "passenger_counts",
        "total_records": total_counts,
        "null_passenger_ids": 0,
        "duplicate_ticket_ids": 0,
        "negative_boardings": neg_boardings,
        "invalid_timestamps": 0
    })

    # 3. Audit all other datasets
    for table_name, df in datasets.items():
        if table_name in ["tickets", "passenger_counts"]:
            continue
        report_rows.append({
            "table_name": table_name,
            "total_records": df.count(),
            "null_passenger_ids": 0,
            "duplicate_ticket_ids": 0,
            "negative_boardings": 0,
            "invalid_timestamps": 0
        })

    report_df = spark.createDataFrame(report_rows)
    print("\n=== DATA QUALITY REPORT SUMMARY ===")
    report_df.show(truncate=False)

    # Save Quality Report
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    out_path = os.path.join(PROCESSED_DATA_DIR, "data_quality_report.csv")
    report_df.toPandas().to_csv(out_path, index=False)
    print(f"\n[SAVED] Data Quality Report written to {out_path}")

    return report_df

if __name__ == "__main__":
    spark = get_spark_session(app_name="UrbanTransit_DataQuality")
    run_data_quality_audit(spark)
    spark.stop()
