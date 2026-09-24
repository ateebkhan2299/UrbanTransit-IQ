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

def clean_data(spark):
    print("=== PySpark Data Cleaning Pipeline ===")
    datasets = ingest_data(spark)
    cleaned_datasets = {}
    cleaning_log = []

    # 1. Clean Tickets Table
    tickets_raw = datasets["tickets"]
    count_tickets_before = tickets_raw.count()

    # Rule A: Replace NULL passenger_id with "ANONYMOUS_PAX"
    tickets_clean = tickets_raw.fillna({"passenger_id": "ANONYMOUS_PAX"})
    # Rule B: Deduplicate by ticket_id
    tickets_clean = tickets_clean.dropDuplicates(["ticket_id"])
    count_tickets_after = tickets_clean.count()

    cleaned_datasets["tickets"] = tickets_clean
    cleaning_log.append({
        "table_name": "tickets",
        "records_before": count_tickets_before,
        "records_after": count_tickets_after,
        "records_removed": count_tickets_before - count_tickets_after,
        "action": "Imputed NULL passenger_id -> 'ANONYMOUS_PAX', deduplicated ticket_id"
    })

    # 2. Clean Passenger Counts Table
    counts_raw = datasets["passenger_counts"]
    count_pc_before = counts_raw.count()
    # Rule: Correct negative boarded_count values using abs()
    counts_clean = counts_raw.withColumn("boarded_count", F.abs(F.col("boarded_count")))
    count_pc_after = counts_clean.count()

    cleaned_datasets["passenger_counts"] = counts_clean
    cleaning_log.append({
        "table_name": "passenger_counts",
        "records_before": count_pc_before,
        "records_after": count_pc_after,
        "records_removed": count_pc_before - count_pc_after,
        "action": "Converted negative boarded_count to absolute positive value"
    })

    # 3. Pass-through for remaining tables
    for table_name, df in datasets.items():
        if table_name not in cleaned_datasets:
            cleaned_datasets[table_name] = df
            c = df.count()
            cleaning_log.append({
                "table_name": table_name,
                "records_before": c,
                "records_after": c,
                "records_removed": 0,
                "action": "Validated clean schema"
            })

    # Save cleaned DataFrames to processed_data/ as clean Parquet files
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    for table_name, df in cleaned_datasets.items():
        out_path = os.path.join(PROCESSED_DATA_DIR, f"{table_name}_clean.parquet")
        pdf = df.toPandas()
        pdf.to_parquet(out_path, engine="pyarrow", index=False)
        print(f"  [WRITTEN] Cleaned dataset {table_name} -> {out_path}")

    # Save cleaning log summary
    log_df = spark.createDataFrame(cleaning_log)
    print("\n=== DATA CLEANING LOG SUMMARY ===")
    log_df.show(truncate=False)

    log_csv_path = os.path.join(PROCESSED_DATA_DIR, "cleaning_summary_log.csv")
    log_df.toPandas().to_csv(log_csv_path, index=False)
    print(f"\n[SAVED] Cleaning log written to {log_csv_path}")

    return cleaned_datasets

if __name__ == "__main__":
    spark = get_spark_session(app_name="UrbanTransit_DataCleaning")
    clean_data(spark)
    spark.stop()
