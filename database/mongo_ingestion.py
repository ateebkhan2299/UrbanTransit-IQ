"""
=============================================================================
UrbanTransit IQ — MongoDB Data Ingestion Script
=============================================================================
Purpose  : Read ALL cleaned CSVs from processed_data/ and ingest them
           into MongoDB collections at mongodb://localhost:27017/
Database : urbantransit_iq
Author   : AI-assisted (flagged in AI_USAGE.md)
=============================================================================

Collections Created:
  1.  passengers        — 50K+ passenger records
  2.  routes            — 100+ route definitions
  3.  stops             — 500+ bus stops
  4.  vehicles          — 250+ vehicles
  5.  route_stops       — route ↔ stop mapping
  6.  schedules         — planned schedules
  7.  service_calendar  — operating calendar
  8.  trips             — 500K+ trip records
  9.  delays            — 250K+ delay records
  10. tickets           — 2M+ ticketing records
  11. passenger_counts  — occupancy counts per stop
  12. gps_events        — GPS tracking events

Indexes Created per collection for fast API queries.
=============================================================================
"""

import os
import sys
import math
import time
import pandas as pd
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import BulkWriteError, ConnectionFailure

# ─── Configuration ────────────────────────────────────────────────────────────
MONGO_URI      = "mongodb://localhost:27017/"
DB_NAME        = "urbantransit_iq"
PROCESSED_DIR  = "./processed_data/"   # Cleaned CSVs location
CHUNK_SIZE     = 5_000                 # Records per batch insert (memory safe)

# Maps: CSV filename → MongoDB collection name
CSV_TO_COLLECTION = {
    "passengers_clean.csv"       : "passengers",
    "routes_clean.csv"           : "routes",
    "stops_clean.csv"            : "stops",
    "vehicles_clean.csv"         : "vehicles",
    "route_stops_clean.csv"      : "route_stops",
    "schedules_clean.csv"        : "schedules",
    "service_calendar_clean.csv" : "service_calendar",
    "trips_clean.csv"            : "trips",
    "delays_clean.csv"           : "delays",
    "tickets_clean.csv"          : "tickets",
    "passenger_counts_clean.csv" : "passenger_counts",
    "gps_events_clean.csv"       : "gps_events",
}

# Indexes per collection: list of (field, direction) tuples
COLLECTION_INDEXES = {
    "passengers"      : [("passenger_id", ASCENDING)],
    "routes"          : [("route_id", ASCENDING)],
    "stops"           : [("stop_id", ASCENDING)],
    "vehicles"        : [("vehicle_id", ASCENDING)],
    "route_stops"     : [("route_id", ASCENDING), ("stop_id", ASCENDING)],
    "schedules"       : [("route_id", ASCENDING)],
    "service_calendar": [],
    "trips"           : [("trip_id", ASCENDING), ("route_id", ASCENDING)],
    "delays"          : [("delay_id", ASCENDING), ("trip_id", ASCENDING)],
    "tickets"         : [("ticket_id", ASCENDING), ("passenger_id", ASCENDING)],
    "passenger_counts": [("trip_id", ASCENDING), ("stop_id", ASCENDING)],
    "gps_events"      : [("vehicle_id", ASCENDING), ("timestamp", DESCENDING)],
}


def connect_to_mongodb(uri: str) -> MongoClient:
    """
    Establish connection to MongoDB and verify it is reachable.
    Raises SystemExit if MongoDB is not running.
    """
    print(f"\n{'='*65}")
    print("  UrbanTransit IQ — MongoDB Data Ingestion")
    print(f"{'='*65}")
    print(f"  Connecting to: {uri}")

    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Ping the server to confirm connection
        client.admin.command("ping")
        print("  ✅ MongoDB connection successful!\n")
        return client
    except ConnectionFailure as connection_err:
        print(f"\n  ❌ ERROR: Cannot connect to MongoDB at {uri}")
        print(f"     Reason: {connection_err}")
        print("     Make sure MongoDB is running: net start MongoDB")
        sys.exit(1)


def clean_record(record: dict) -> dict:
    """
    Convert NaN / Infinity / NaT values to None so MongoDB can accept them.
    Converts pandas Timestamp objects to Python datetime.
    """
    clean = {}
    for key, value in record.items():
        # Handle float NaN / Infinity
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            clean[key] = None
        # Handle pandas Timestamp
        elif hasattr(value, 'to_pydatetime'):
            try:
                clean[key] = value.to_pydatetime()
            except Exception:
                clean[key] = str(value)
        # Handle pandas NA
        elif pd.isna(value) if not isinstance(value, (list, dict)) else False:
            clean[key] = None
        else:
            clean[key] = value
    return clean


def ingest_csv_to_collection(
    db,
    csv_filename: str,
    collection_name: str,
    chunk_size: int = CHUNK_SIZE
) -> dict:
    """
    Read a cleaned CSV file in chunks and insert all records into a
    MongoDB collection. Returns a summary dict with counts and timing.
    """
    csv_path = os.path.join(PROCESSED_DIR, csv_filename)

    # Check file exists
    if not os.path.exists(csv_path):
        print(f"  ⚠️  SKIPPED: {csv_filename} not found in {PROCESSED_DIR}")
        return {"collection": collection_name, "status": "skipped",
                "inserted": 0, "errors": 0}

    file_size_mb = os.path.getsize(csv_path) / (1024 * 1024)
    print(f"\n  📂 Ingesting: {csv_filename}  ({file_size_mb:.1f} MB)")
    print(f"     → Collection: {DB_NAME}.{collection_name}")

    collection    = db[collection_name]
    total_inserted = 0
    total_errors   = 0
    chunk_num      = 0
    start_time     = time.time()

    # Drop existing collection data before fresh ingestion
    collection.drop()
    print(f"     → Dropped existing collection (fresh load)")

    # Read CSV in chunks for memory efficiency
    reader = pd.read_csv(csv_path, chunksize=chunk_size, low_memory=False)

    for chunk_df in reader:
        chunk_num += 1

        # Convert each row to a clean dict
        records = [clean_record(row) for row in chunk_df.to_dict(orient='records')]

        try:
            result = collection.insert_many(records, ordered=False)
            total_inserted += len(result.inserted_ids)
        except BulkWriteError as bwe:
            # Some records failed — count successes and failures
            inserted_in_batch = bwe.details.get('nInserted', 0)
            errors_in_batch   = len(bwe.details.get('writeErrors', []))
            total_inserted   += inserted_in_batch
            total_errors     += errors_in_batch

        # Progress indicator every 10 chunks
        if chunk_num % 10 == 0:
            elapsed = time.time() - start_time
            print(f"     → Chunk {chunk_num:>4} | Inserted so far: {total_inserted:>10,} | "
                  f"Elapsed: {elapsed:.1f}s")

    elapsed_total = time.time() - start_time
    rate = total_inserted / elapsed_total if elapsed_total > 0 else 0

    print(f"     ✅ Done! Inserted: {total_inserted:,} records | "
          f"Errors: {total_errors} | Time: {elapsed_total:.1f}s | "
          f"Rate: {rate:,.0f} rec/s")

    return {
        "collection" : collection_name,
        "status"     : "success",
        "inserted"   : total_inserted,
        "errors"     : total_errors,
        "time_sec"   : round(elapsed_total, 2),
    }


def create_indexes(db, indexes_map: dict) -> None:
    """
    Create MongoDB indexes on each collection for fast query performance.
    """
    print(f"\n{'─'*65}")
    print("  Creating Indexes for fast API queries...")
    print(f"{'─'*65}")

    for collection_name, index_fields in indexes_map.items():
        if not index_fields:
            continue
        collection = db[collection_name]
        for field, direction in index_fields:
            try:
                collection.create_index([(field, direction)])
                print(f"  ✅ Index created: {collection_name}.{field}")
            except Exception as idx_err:
                print(f"  ⚠️  Index failed on {collection_name}.{field}: {idx_err}")


def print_ingestion_summary(results: list, total_time: float) -> None:
    """
    Print a formatted summary table of all ingestion results.
    """
    print(f"\n{'='*65}")
    print("  INGESTION SUMMARY REPORT")
    print(f"{'='*65}")
    print(f"  {'Collection':<25} {'Status':<10} {'Records':>12} {'Errors':>8}")
    print(f"  {'-'*25} {'-'*10} {'-'*12} {'-'*8}")

    total_records = 0
    total_errors  = 0

    for r in results:
        status_icon = "✅" if r["status"] == "success" else "⚠️ "
        print(f"  {r['collection']:<25} {status_icon} {r['status']:<8} "
              f"{r['inserted']:>12,} {r['errors']:>8}")
        total_records += r["inserted"]
        total_errors  += r["errors"]

    print(f"  {'─'*65}")
    print(f"  {'TOTAL':<25} {'':10} {total_records:>12,} {total_errors:>8}")
    print(f"\n  Total ingestion time : {total_time:.1f} seconds")
    print(f"  Database             : {DB_NAME}")
    print(f"  Host                 : {MONGO_URI}")
    print(f"{'='*65}\n")


def main():
    """Main entry point — connects, ingests all CSVs, creates indexes."""

    # 1. Connect to MongoDB
    client = connect_to_mongodb(MONGO_URI)
    db     = client[DB_NAME]

    # 2. Ingest each CSV → MongoDB collection
    ingestion_results = []
    overall_start     = time.time()

    for csv_file, collection_name in CSV_TO_COLLECTION.items():
        result = ingest_csv_to_collection(
            db=db,
            csv_filename=csv_file,
            collection_name=collection_name,
            chunk_size=CHUNK_SIZE
        )
        ingestion_results.append(result)

    overall_elapsed = time.time() - overall_start

    # 3. Create indexes
    create_indexes(db, COLLECTION_INDEXES)

    # 4. Print summary
    print_ingestion_summary(ingestion_results, overall_elapsed)

    # 5. Verify by counting documents in each collection
    print("  Document counts in MongoDB (verification):")
    for col_name in CSV_TO_COLLECTION.values():
        count = db[col_name].count_documents({})
        print(f"  {col_name:<25} → {count:>12,} documents")

    print(f"\n  ✅ MongoDB ingestion complete! Open MongoDB Compass at:")
    print(f"     {MONGO_URI}")
    print(f"     Database: {DB_NAME}\n")

    client.close()


if __name__ == "__main__":
    main()
