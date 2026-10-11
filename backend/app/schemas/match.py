from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from app.schemas.common import UTCDateTime
from app.models.match import MatchStatus
from app.schemas.trip import TripResponse
from app.schemas.shipment import ShipmentResponse

class ScoreBreakdownSchema(BaseModel):
    route_score: float
    capacity_score: float
    time_score: float
    vehicle_score: float

class MatchResponse(BaseModel):
    id: str
    trip_id: str
    shipment_id: str
    score: float
    breakdown: ScoreBreakdownSchema
    is_rejected: bool
    rejection_reason: Optional[str] = None
    detour_km: float
    detour_minutes: float
    direct_trip_km: float
    estimated_revenue: float
    estimated_cost_shipper: float = 0.0
    baseline_full_truck_cost: float = 0.0
    cost_savings_amount: float = 0.0
    cost_savings_pct: float = 0.0
    estimated_co2_saved_kg: float
    is_osrm_fallback: bool = False
    status: MatchStatus
    created_at: UTCDateTime
    trip: Optional[TripResponse] = None
    shipment: Optional[ShipmentResponse] = None
    booking_status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ConsolidationGroupResponse(BaseModel):
    group_id: str
    shipment_ids: List[str]
    shipments: List[ShipmentResponse]
    matches: List[MatchResponse]
    total_weight_kg: float
    total_capacity_kg: float
    capacity_utilization_pct: float
    combined_score: float
    total_estimated_revenue: float
    total_co2_saved_kg: float
    is_osrm_fallback: bool = False

class MultiShipmentConsolidationResponse(BaseModel):
    trip_id: str
    matches: List[MatchResponse]
    total_weight_kg: float
    total_capacity_kg: float
    capacity_utilization_pct: float
    combined_score: float
    groups: List[ConsolidationGroupResponse] = []
