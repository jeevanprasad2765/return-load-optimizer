from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class KeyMetrics(BaseModel):
    empty_km_reduced: float            # Total km filled by return trips
    additional_revenue_generated: float # Total ₹ earned by carriers
    cost_saved_for_shippers: float     # Total ₹ saved vs standard freight rates (20% avg discount)
    average_vehicle_utilization_pct: float # Average % of truck load capacity utilized
    estimated_co2_saved_kg: float      # Total kg of CO2 emissions prevented

class MonthlyTrendPoint(BaseModel):
    month: str
    empty_km_reduced: float
    revenue: float
    matches_count: int
    co2_saved: float

class CityPairVolume(BaseModel):
    route: str
    trips_count: int
    volume_tons: float

class ActiveMatchedRoute(BaseModel):
    match_id: str
    trip_id: str
    shipment_id: str
    origin: str
    destination: str
    pickup: str
    dropoff: str
    score: float
    detour_km: float
    status: str
    origin_coords: List[float]    # [lat, lon]
    dest_coords: List[float]
    pickup_coords: List[float]
    dropoff_coords: List[float]

class PlatformImpactResponse(BaseModel):
    empty_km_reduced: float
    total_revenue_generated: float
    total_cost_saved_shippers: float
    average_vehicle_utilization_pct: float
    total_co2_saved_kg: float
    total_completed_trips: int

class DashboardMetricsResponse(BaseModel):
    metrics: KeyMetrics
    monthly_trends: List[MonthlyTrendPoint]
    route_volumes: List[CityPairVolume]
    active_matched_routes: List[ActiveMatchedRoute]
    platform_metrics: Optional[PlatformImpactResponse] = None
