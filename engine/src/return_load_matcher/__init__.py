"""
return-load-matcher
-------------------
Standalone, reusable Python engine for matching and scoring empty return truck trips with compatible freight shipments.
"""

from return_load_matcher.models import (
    Coordinate,
    TripInfo,
    ShipmentInfo,
    ScoreBreakdown,
    MatchResult,
    ConsolidationResult,
)
from return_load_matcher.config import MatchConfig
from return_load_matcher.scorer import score_match, rank_matches
from return_load_matcher.consolidation import find_multi_shipment_consolidation
from return_load_matcher.capacity import evaluate_capacity_fit
from return_load_matcher.vehicle import evaluate_vehicle_compatibility
from return_load_matcher.time import evaluate_time_compatibility
from return_load_matcher.route import evaluate_route_compatibility, haversine_distance_km

__version__ = "0.1.0"

__all__ = [
    "Coordinate",
    "TripInfo",
    "ShipmentInfo",
    "ScoreBreakdown",
    "MatchResult",
    "ConsolidationResult",
    "MatchConfig",
    "score_match",
    "rank_matches",
    "find_multi_shipment_consolidation",
    "evaluate_capacity_fit",
    "evaluate_vehicle_compatibility",
    "evaluate_time_compatibility",
    "evaluate_route_compatibility",
    "haversine_distance_km",
]
