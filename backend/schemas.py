from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Auth & User Schemas
class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    full_name: str
    is_active: bool

class AuditLogSchema(BaseModel):
    id: int
    username: str
    role: str
    action: str
    endpoint: str
    details: Optional[str] = None
    timestamp: Any

# Health Status Schema
class HealthStatusResponse(BaseModel):
    status: str
    database: str
    uptime_seconds: float
    memory_usage_mb: float
    timestamp: str

# Section 7 Contract Schemas
class SyncStatusResponse(BaseModel):
    last_updated: str
    status: str

class NotificationResponse(BaseModel):
    id: int
    severity: str
    message: str
    route_id: Optional[str] = None
    route_name: Optional[str] = None
    created_at: str
    is_read: bool

class RouteListItem(BaseModel):
    route_id: str
    route_name: str

class DashboardSummaryContractResponse(BaseModel):
    total_passengers: int
    total_passengers_change_pct: float
    total_trips: int
    total_trips_change_pct: float
    avg_occupancy_pct: float
    avg_occupancy_change_pct: float
    on_time_pct: float
    on_time_change_pct: float

class TopRouteItem(BaseModel):
    route_id: str
    route_name: str
    total_passengers: int
    occupancy_pct: float

class DelayCauseItem(BaseModel):
    cause: str
    incident_count: int
    percentage_share: float

class PathPoint(BaseModel):
    lat: float
    lon: float
    stop_name: str

class RouteGeoItem(BaseModel):
    route_id: str
    route_name: str
    status_color: str
    path: List[PathPoint]

class StopHotspotItem(BaseModel):
    stop_id: str
    stop_name: str
    latitude: float
    longitude: float
    delay_events: int

class RouteDetailResponse(BaseModel):
    route_id: str
    route_name: str
    avg_delay_minutes: float
    occupancy_pct: float
    on_time_pct: float
    performance_category: str

class WhatIfSimulateContractRequest(BaseModel):
    route_id: str
    change_type: str
    change_value: float

class WhatIfSimulateMetrics(BaseModel):
    occupancy_pct: float
    avg_wait_min: float
    overcrowd_risk_pct: float

class WhatIfSimulateContractResponse(BaseModel):
    before: WhatIfSimulateMetrics
    after: WhatIfSimulateMetrics
    is_estimate: bool = True

class RouteSummarySchema(BaseModel):
    route_id: str
    route_name: str
    transport_mode: str
    total_trips: int
    total_passengers: int
    avg_occupancy_pct: float
    avg_delay_minutes: float
    on_time_performance_pct: float
    performance_score: float
    performance_tier: str
    cluster_id: Optional[int] = 0
    cluster_label: Optional[str] = ""

class DelaySummarySchema(BaseModel):
    cause: str
    incident_count: int
    total_delay_minutes: float
    avg_delay_minutes: float
    max_delay_minutes: float
    percentage_share: Optional[float] = 0.0

class OccupancySummarySchema(BaseModel):
    route_id: str
    route_name: str
    hour_of_day: int
    avg_passengers: float
    avg_capacity: float
    avg_occupancy_pct: float
    overcrowded_trips_count: int
    underutilized_trips_count: int

class ForecastResultSchema(BaseModel):
    route_id: str
    forecast_date: str
    predicted_passenger_demand: float
    confidence_lower: float
    confidence_upper: float

class RecommendationSchema(BaseModel):
    id: str
    title: str
    description: str
    priority: str
    route_id: Optional[str] = None
    expected_impact: str
