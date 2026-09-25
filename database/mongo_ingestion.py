"""
UrbanTransit IQ -- Complete MongoDB Data Ingestion
Saves ALL project data to MongoDB: Transport tables, Features, Reports, Model Metrics
"""
import os, sys, json, math, time
import pandas as pd
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import BulkWriteError, ConnectionFailure

MONGO_URI     = "mongodb://localhost:27017/"
DB_NAME       = "urbantransit_iq"
PROCESSED_DIR = "./processed_data/"
REPORTS_DIR   = "./reports/"
MODELS_DIR    = "./models/"
CHUNK_SIZE    = 5000

PARQUET_COLLECTIONS = {
    "passengers_clean.parquet"          : "passengers",
    "routes_clean.parquet"              : "routes",
    "stops_clean.parquet"               : "stops",
    "vehicles_clean.parquet"            : "vehicles",
    "route_stops_clean.parquet"         : "route_stops",
    "schedules_clean.parquet"           : "schedules",
    "service_calendar_clean.parquet"    : "service_calendar",
    "trips_clean.parquet"               : "trips",
    "delays_clean.parquet"              : "delays",
    "tickets_clean.parquet"             : "tickets",
    "passenger_counts_clean.parquet"    : "passenger_counts",
    "gps_events_clean.parquet"          : "gps_events",
    "features_delays.parquet"           : "features_delays",
    "features_occupancy.parquet"        : "features_occupancy",
    "features_tickets.parquet"          : "features_tickets",
    "summary_route_performance.parquet" : "summary_route_performance",
    "summary_hourly_demand.parquet"     : "summary_hourly_demand",
    "summary_delay_causes.parquet"      : "summary_delay_causes",
}

INDEXES = {
    "passengers"              : [("passenger_id", ASCENDING)],
    "routes"                  : [("route_id", ASCENDING)],
    "stops"                   : [("stop_id", ASCENDING)],
    "vehicles"                : [("vehicle_id", ASCENDING)],
    "route_stops"             : [("route_id", ASCENDING)],
    "trips"                   : [("trip_id", ASCENDING), ("route_id", ASCENDING)],
    "delays"                  : [("trip_id", ASCENDING)],
    "tickets"                 : [("ticket_id", ASCENDING), ("passenger_id", ASCENDING)],
    "passenger_counts"        : [("trip_id", ASCENDING)],
    "gps_events"              : [("vehicle_id", ASCENDING)],
    "recommendations"         : [("priority", DESCENDING)],
    "dual_pipeline_comparison": [("trip_id", ASCENDING)],
}

def connect(uri):
    print("="*60)
    print("  UrbanTransit IQ - MongoDB Complete Ingestion")
    print("="*60)
    print(f"  URI: {uri}  |  DB: {DB_NAME}")
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        print("  [OK] MongoDB connected!\n")
        return client
    except ConnectionFailure as e:
        print(f"  [ERROR] Cannot connect: {e}")
        sys.exit(1)

def clean_row(record):
    """Convert NaN/Inf/NaT/Timestamp to MongoDB-safe Python types."""
    import pandas as pd
    out = {}
    for k, v in record.items():
        # Handle pandas NaT explicitly (must come before isna check)
        if type(v).__name__ == 'NaTType':
            out[k] = None
        # Handle float NaN / Infinity
        elif isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            out[k] = None
        # Handle pandas Timestamp -> Python datetime
        elif hasattr(v, 'to_pydatetime'):
            try:
                dt = v.to_pydatetime()
                # Remove timezone info if present (MongoDB stores UTC)
                if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
                    dt = dt.replace(tzinfo=None)
                out[k] = dt
            except Exception:
                out[k] = None
        # Handle numpy integer types
        elif hasattr(v, 'item'):
            try:    out[k] = v.item()
            except: out[k] = None
        # Handle Python datetime.date -> datetime.datetime
        elif isinstance(v, __import__('datetime').date) and not isinstance(v, __import__('datetime').datetime):
            out[k] = __import__('datetime').datetime.combine(v, __import__('datetime').datetime.min.time())
        # Handle generic pandas NA / None / datetime
        else:
            try:
                out[k] = None if pd.isna(v) else v
            except Exception:
                out[k] = v
    return out


def ingest_parquet(db, filename, col_name):
    path = os.path.join(PROCESSED_DIR, filename)
    if not os.path.exists(path):
        print(f"  [SKIP] Not found: {filename}")
        return {"collection": col_name, "inserted": 0, "status": "skipped"}

    size_mb = os.path.getsize(path) / 1_048_576
    print(f"\n  [FILE] {filename}  ({size_mb:.1f} MB)  ->  {col_name}")
    col = db[col_name]
    col.drop()

    df    = pd.read_parquet(path)
    total = len(df)
    ins   = 0
    t0    = time.time()

    for i in range(0, total, CHUNK_SIZE):
        chunk   = df.iloc[i:i+CHUNK_SIZE]
        records = [clean_row(r) for r in chunk.to_dict(orient='records')]
        try:
            col.insert_many(records, ordered=False)
            ins += len(records)
        except BulkWriteError as bwe:
            ins += bwe.details.get('nInserted', 0)
        if ins % 50000 < CHUNK_SIZE and ins > 0:
            print(f"     -> {ins:>10,} / {total:,}  inserted ...")

    elapsed = time.time() - t0
    rate    = ins / elapsed if elapsed > 0 else 0
    print(f"     [OK] {ins:,} records | {elapsed:.1f}s | {rate:,.0f} rec/s")
    return {"collection": col_name, "inserted": ins, "status": "success"}

def ingest_json(db, filepath, col_name):
    if not os.path.exists(filepath):
        print(f"  [SKIP] Not found: {filepath}")
        return {"collection": col_name, "inserted": 0, "status": "skipped"}

    print(f"\n  [JSON] {os.path.basename(filepath)}  ->  {col_name}")
    col = db[col_name]
    col.drop()

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        records = [clean_row(r) if isinstance(r, dict) else {"value": r} for r in data]
        col.insert_many(records, ordered=False)
        count = len(records)
    else:
        col.insert_one(data if isinstance(data, dict) else {"value": data})
        count = 1

    print(f"     [OK] {count} document(s) inserted")
    return {"collection": col_name, "inserted": count, "status": "success"}

def ingest_csv_report(db, filepath, col_name):
    if not os.path.exists(filepath):
        print(f"  [SKIP] Not found: {filepath}")
        return {"collection": col_name, "inserted": 0, "status": "skipped"}

    size_kb = os.path.getsize(filepath) // 1024
    print(f"\n  [CSV] {os.path.basename(filepath)}  ({size_kb}KB)  ->  {col_name}")
    col = db[col_name]
    col.drop()
    df      = pd.read_csv(filepath, low_memory=False)
    records = [clean_row(r) for r in df.to_dict(orient='records')]
    col.insert_many(records, ordered=False)
    print(f"     [OK] {len(records)} records inserted")
    return {"collection": col_name, "inserted": len(records), "status": "success"}

def ingest_model_metrics(db):
    print(f"\n  [MODEL] All model metrics  ->  model_metrics")
    col = db["model_metrics"]
    col.drop()
    files = [
        ("spark_delay_model_metrics.json",         "spark",  "delay"),
        ("spark_forecast_model_metrics.json",       "spark",  "forecast"),
        ("spark_occupancy_risk_model_metrics.json", "spark",  "occupancy"),
        ("spark_clustering_model_metrics.json",     "spark",  "clustering"),
        ("python_delay_model_metrics.json",         "python", "delay"),
        ("python_forecast_model_metrics.json",      "python", "forecast"),
        ("python_occupancy_risk_model_metrics.json","python", "occupancy"),
        ("python_clustering_model_metrics.json",    "python", "clustering"),
    ]
    ins = 0
    for fname, pipeline, task in files:
        fpath = os.path.join(MODELS_DIR, fname)
        if not os.path.exists(fpath):
            print(f"     [SKIP] {fname}")
            continue
        with open(fpath, "r") as f:
            m = json.load(f)
        col.insert_one({"pipeline": pipeline, "task": task, **m})
        ins += 1
        print(f"     [OK] {pipeline}.{task}")
    return {"collection": "model_metrics", "inserted": ins, "status": "success"}

def create_indexes(db, indexes):
    print("\nCreating Indexes...")
    for col_name, fields in indexes.items():
        for field, direction in fields:
            try:
                db[col_name].create_index([(field, direction)])
                print(f"  [INDEX] {col_name}.{field}")
            except Exception as e:
                print(f"  [WARN]  {col_name}.{field} -> {e}")

def summary(results, elapsed, db):
    print("\n" + "="*60)
    print("  FINAL SUMMARY")
    print("="*60)
    total = 0
    for r in results:
        status = "[OK]  " if r["status"]=="success" else "[SKIP]"
        print(f"  {status} {r['collection']:<30} {r['inserted']:>10,}")
        total += r["inserted"]
    print("  " + "-"*55)
    print(f"  {'TOTAL':<37} {total:>10,}")
    print(f"\n  Time: {elapsed:.1f}s  |  DB: {DB_NAME}")
    print("\n  Live Document Counts:")
    for col in sorted(db.list_collection_names()):
        cnt = db[col].count_documents({})
        print(f"    {col:<35} {cnt:>12,}")
    print(f"\n  [DONE] Open MongoDB Compass: {MONGO_URI}")
    print("="*60 + "\n")

def main():
    client  = connect(MONGO_URI)
    db      = client[DB_NAME]
    results = []
    t0      = time.time()

    # Step 1: Transport + Feature Parquet data
    print("\n" + "-"*60)
    print("  STEP 1: Transport & Feature Data (Parquet -> MongoDB)")
    print("-"*60)
    for pfile, col in PARQUET_COLLECTIONS.items():
        results.append(ingest_parquet(db, pfile, col))

    # Step 2: Reports
    print("\n" + "-"*60)
    print("  STEP 2: Reports & Recommendations")
    print("-"*60)
    results.append(ingest_json(db, os.path.join(REPORTS_DIR,"recommendations.json"), "recommendations"))
    results.append(ingest_csv_report(db, os.path.join(REPORTS_DIR,"dual_pipeline_comparison.csv"), "dual_pipeline_comparison"))
    results.append(ingest_csv_report(db, os.path.join(PROCESSED_DIR,"data_quality_report.csv"), "data_quality_report"))
    results.append(ingest_csv_report(db, os.path.join(PROCESSED_DIR,"cleaning_summary_log.csv"), "cleaning_log"))

    # Step 3: Model Metrics
    print("\n" + "-"*60)
    print("  STEP 3: ML Model Metrics")
    print("-"*60)
    results.append(ingest_model_metrics(db))

    # Step 4: Indexes
    create_indexes(db, INDEXES)

    # Final summary
    summary(results, time.time()-t0, db)
    client.close()

if __name__ == "__main__":
    main()
