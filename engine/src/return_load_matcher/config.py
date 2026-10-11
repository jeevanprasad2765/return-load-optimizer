from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class RateCard:
    rate_per_km: float
    rate_per_kg: float
    base_fee: float = 100.0

DEFAULT_VEHICLE_RATE_CARDS: Dict[str, RateCard] = {
    "closed": RateCard(rate_per_km=15.0, rate_per_kg=0.50, base_fee=200.0),
    "open": RateCard(rate_per_km=14.0, rate_per_kg=0.40, base_fee=150.0),
    "refrigerated": RateCard(rate_per_km=20.0, rate_per_kg=0.85, base_fee=300.0),
    "flatbed": RateCard(rate_per_km=16.0, rate_per_kg=0.45, base_fee=200.0),
    "container": RateCard(rate_per_km=18.0, rate_per_kg=0.60, base_fee=250.0),
}

@dataclass
class MatchConfig:
    # Weights for score calculation (must sum to 1.0)
    route_weight: float = 0.40
    capacity_weight: float = 0.25
    time_weight: float = 0.20
    vehicle_weight: float = 0.15

    # Thresholds for hard rejection
    max_detour_km: float = 60.0         # Max absolute detour allowed in km
    max_detour_ratio: float = 0.35      # Max detour as fraction of direct trip distance (35%)
    
    # Notification score threshold
    notification_score_threshold: float = 70.0

    # Rate Cards per vehicle type
    vehicle_rate_cards: Dict[str, RateCard] = field(default_factory=lambda: DEFAULT_VEHICLE_RATE_CARDS.copy())

    # OSRM router endpoint
    osrm_base_url: str = "https://router.project-osrm.org"
    request_timeout_seconds: float = 5.0

    # Mapbox integration access token
    mapbox_access_token: Optional[str] = None

    # Environmental metric factor: average CO2 emissions per ton-km for heavy diesel truck in kg
    co2_per_ton_km_kg: float = 0.105

    def validate(self) -> None:
        total_weight = self.route_weight + self.capacity_weight + self.time_weight + self.vehicle_weight
        if abs(total_weight - 1.0) > 1e-4:
            raise ValueError(f"MatchConfig weights must sum to 1.0, got {total_weight}")

    def get_rate_card(self, vehicle_type: str) -> RateCard:
        vtype = (vehicle_type or "closed").lower().strip()
        return self.vehicle_rate_cards.get(vtype, self.vehicle_rate_cards.get("closed", RateCard(15.0, 0.50, 200.0)))
