import httpx
import uuid
import itertools
from typing import List, Optional
from return_load_matcher.models import (
    TripInfo, ShipmentInfo, MatchResult, ConsolidationResult, ConsolidationGroupResult
)
from return_load_matcher.config import MatchConfig
from return_load_matcher.scorer import rank_matches, score_match

async def find_multi_shipment_consolidation(
    trip: TripInfo,
    shipments: List[ShipmentInfo],
    config: Optional[MatchConfig] = None,
    client: Optional[httpx.AsyncClient] = None
) -> ConsolidationResult:
    """
    Evaluates combinations of 2 to 3 compatible shipments for a single truck trip.
    Scores each group based on combined weight utilization, individual match scores, and detour compatibility.
    """
    if config is None:
        config = MatchConfig()

    ranked = await rank_matches(trip, shipments, config=config, client=client)
    accepted_matches = [m for m in ranked if not m.is_rejected]

    if not accepted_matches:
        return ConsolidationResult(
            trip_id=trip.trip_id,
            shipments=[],
            matches=[],
            total_weight_kg=0.0,
            total_capacity_kg=trip.available_capacity_kg,
            capacity_utilization_pct=0.0,
            combined_score=0.0,
            groups=[]
        )

    # Create map from shipment_id to ShipmentInfo & MatchResult
    match_map = {m.shipment_id: m for m in accepted_matches if m.shipment_id}
    shipment_map = {s.shipment_id: s for s in shipments if s.shipment_id and s.shipment_id in match_map}

    candidate_shipments = list(shipment_map.values())
    groups: List[ConsolidationGroupResult] = []

    # Evaluate single, pair, and 3-shipment combinations
    for r in range(2, min(4, len(candidate_shipments) + 1)):
        for combo in itertools.combinations(candidate_shipments, r):
            total_weight = sum(s.weight_kg for s in combo)
            if total_weight > trip.available_capacity_kg:
                continue

            combo_matches = [match_map[s.shipment_id] for s in combo]
            if any(m.is_rejected for m in combo_matches):
                continue

            # Calculate metrics
            utilization_pct = round((total_weight / max(1.0, trip.available_capacity_kg)) * 100.0, 1)
            
            # Combine individual scores with a bonus for higher capacity fill %
            avg_individual_score = sum(m.score for m in combo_matches) / len(combo_matches)
            utilization_bonus = (utilization_pct / 100.0) * 10.0
            combined_score = round(min(100.0, avg_individual_score + utilization_bonus), 2)

            total_revenue = round(sum(m.estimated_revenue for m in combo_matches), 2)
            total_co2_saved = round(sum(m.estimated_co2_saved_kg for m in combo_matches), 2)
            is_fallback = any(m.is_osrm_fallback for m in combo_matches)

            groups.append(ConsolidationGroupResult(
                group_id=str(uuid.uuid4()),
                shipment_ids=[s.shipment_id for s in combo],
                shipments=list(combo),
                matches=combo_matches,
                total_weight_kg=total_weight,
                total_capacity_kg=trip.available_capacity_kg,
                capacity_utilization_pct=utilization_pct,
                combined_score=combined_score,
                total_estimated_revenue=total_revenue,
                total_co2_saved_kg=total_co2_saved,
                is_osrm_fallback=is_fallback
            ))

    # Sort groups by combined score descending
    groups.sort(key=lambda g: g.combined_score, reverse=True)

    # Top single greedy bin-packed selection for backward compatibility
    packed_shipments: List[ShipmentInfo] = []
    packed_matches: List[MatchResult] = []
    rem_cap = trip.available_capacity_kg
    acc_weight = 0.0

    for m in accepted_matches:
        s = shipment_map.get(m.shipment_id)
        if s and s.weight_kg <= rem_cap:
            packed_shipments.append(s)
            packed_matches.append(m)
            rem_cap -= s.weight_kg
            acc_weight += s.weight_kg

    util_pct = round((acc_weight / trip.available_capacity_kg) * 100.0, 1) if trip.available_capacity_kg > 0 else 0.0
    comb_score = round(sum(m.score for m in packed_matches) / len(packed_matches), 2) if packed_matches else 0.0

    return ConsolidationResult(
        trip_id=trip.trip_id,
        shipments=packed_shipments,
        matches=packed_matches,
        total_weight_kg=acc_weight,
        total_capacity_kg=trip.available_capacity_kg,
        capacity_utilization_pct=util_pct,
        combined_score=comb_score,
        groups=groups
    )
