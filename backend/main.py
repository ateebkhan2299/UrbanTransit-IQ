import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.database import engine, Base
from backend.init_db import populate_database
from backend.routers import (
    dashboard,
    notifications,
    routes,
    delays,
    map as map_router,
    occupancy,
    forecast,
    recommendations,
    whatif,
    comparison,
    auth,
    health,
    admin_management,
    reports
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="UrbanTransit IQ API",
    description="Big Data + Data Science Public Transit Analytics API",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for React Frontend (Vite default port 5173, 5174, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers with /api prefix
app.include_router(dashboard.router)
app.include_router(notifications.router)
app.include_router(routes.router)
app.include_router(delays.router)
app.include_router(map_router.router)
app.include_router(occupancy.router)
app.include_router(forecast.router)
app.include_router(recommendations.router)
app.include_router(whatif.router)
app.include_router(comparison.router)
app.include_router(auth.router)
app.include_router(auth.admin_router)
app.include_router(health.router)
app.include_router(admin_management.router)
app.include_router(reports.router)

@app.get("/")
def root():
    return {
        "message": "Welcome to UrbanTransit IQ API",
        "docs": "/docs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
