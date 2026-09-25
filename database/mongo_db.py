"""
=============================================================================
UrbanTransit IQ — MongoDB Connection & Helper Module
=============================================================================
Purpose : Provide a reusable MongoDB client for FastAPI backend endpoints.
          All API endpoints use this module to query MongoDB collections.
=============================================================================
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# ─── Connection Settings ──────────────────────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME   = os.getenv("MONGO_DB",  "urbantransit_iq")

# Singleton client — reused across all FastAPI requests
_mongo_client: MongoClient | None = None


def get_mongo_client() -> MongoClient:
    """Return the singleton MongoClient, creating it on first call."""
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return _mongo_client


def get_db():
    """Return the urbantransit_iq database object."""
    client = get_mongo_client()
    return client[DB_NAME]


def get_collection(collection_name: str):
    """
    Return a specific MongoDB collection by name.
    Usage:
        passengers_col = get_collection("passengers")
        doc = passengers_col.find_one({"passenger_id": "P00001"})
    """
    db = get_db()
    return db[collection_name]


# ─── Collection Name Constants ────────────────────────────────────────────────
COL_PASSENGERS       = "passengers"
COL_ROUTES           = "routes"
COL_STOPS            = "stops"
COL_VEHICLES         = "vehicles"
COL_ROUTE_STOPS      = "route_stops"
COL_SCHEDULES        = "schedules"
COL_SERVICE_CALENDAR = "service_calendar"
COL_TRIPS            = "trips"
COL_DELAYS           = "delays"
COL_TICKETS          = "tickets"
COL_PASSENGER_COUNTS = "passenger_counts"
COL_GPS_EVENTS       = "gps_events"
