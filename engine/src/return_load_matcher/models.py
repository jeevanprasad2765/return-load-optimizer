from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class Coordinate:
    lat: float
    lon: float

    def to_osrm(self) -> str:
        """OSRM expects longitude,latitude"""
        return f"{self.lon},{self.lat}"

@dataclass
class TripInfo:
    origin: Coordinate
    destination: Coordinate
    departure_time: datetime
    available_capacity_kg: float
    vehicle_type: str  # e.g., "open", "closed", "refrigerated", "flatbed", "container"
    cost_per_km: float = 15.0
    max_capacity_kg: float = 10000.0
    trip_id: Optional[str] = None
    route_geometry: Optional[List[Coordinate]] = None

@dataclass
class ShipmentInfo:
    pickup: Coordinate
    destination: Coordinate
    weight_kg: float
    goods_type: str
    required_vehicle_type: Optional[str] = None
    pickup_window_start: Optional[datetime] = None
    pickup_window_end: Optional[datetime] = None
    delivery_deadline: Optional[datetime] = None
    shipment_id: Optional[str] = None

@dataclass
class ScoreBreakdown:
    route_score: float = 0.0
    capacity_score: float = 0.0
    time_score: float = 0.0
    vehicle_score: float = 0.0

@dataclass
class MatchResult:
    score: float
    breakdown: ScoreBreakdown
    is_rejected: bool
    rejection_reason: Optional[str] = None
    detour_km: float = 0.0
    detour_minutes: float = 0.0
    direct_trip_km: float = 0.0
    estimated_revenue: float = 0.0           # For carrier (earnings)
    estimated_cost_shipper: float = 0.0      # For shipper (price)
    baseline_full_truck_cost: float = 0.0   # Baseline standalone cost
    cost_savings_amount: float = 0.0         # ₹ Saved
    cost_savings_pct: float = 0.0            # % Saved
    estimated_co2_saved_kg: float = 0.0
    matched_route_geometry: Optional[List[Coordinate]] = None
    trip_id: Optional[str] = None
    shipment_id: Optional[str] = None
    is_osrm_fallback: bool = False           # True if straight-line fallback was used

@dataclass
class ConsolidationGroupResult:
    group_id: str
    shipment_ids: List[str]
    shipments: List[ShipmentInfo]
    matches: List[MatchResult]
    total_weight_kg: float
    total_capacity_kg: float
    capacity_utilization_pct: float
    combined_score: float
    total_estimated_revenue: float
    total_co2_saved_kg: float
    is_osrm_fallback: bool = False

@dataclass
class ConsolidationResult:
    trip_id: Optional[str]
    shipments: List[ShipmentInfo]
    matches: List[MatchResult]
    total_weight_kg: float
    total_capacity_kg: float
    capacity_utilization_pct: float
    combined_score: float
    groups: List[ConsolidationGroupResult] = field(default_factory=list)
