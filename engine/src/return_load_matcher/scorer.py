import httpx
from typing import List, Optional
from return_load_matcher.models import (
    TripInfo, ShipmentInfo, MatchResult, ScoreBreakdown
)
from return_load_matcher.config import MatchConfig
from return_load_matcher.route import evaluate_route_compatibility
from return_load_matcher.capacity import evaluate_capacity_fit
from return_load_matcher.time import evaluate_time_compatibility
from return_load_matcher.vehicle import evaluate_vehicle_compatibility

async def score_match(
    trip: TripInfo,
    shipment: ShipmentInfo,
    config: Optional[MatchConfig] = None,
    client: Optional[httpx.AsyncClient] = None
) -> MatchResult:
    """
    Computes a weighted match score from 0-100 for a trip/shipment pair.
    Applies hard rejection filters first:
    - Weight > Capacity
    - Excessive detour
    - Vehicle type incompatibility
    - Time window/deadline conflict
    """
    if config is None:
        config = MatchConfig()
    config.validate()

    # 1. Capacity Fit Evaluation
    cap_score, cap_rejected, cap_reason = evaluate_capacity_fit(trip, shipment)
    if cap_rejected:
        return MatchResult(
            score=0.0,
            breakdown=ScoreBreakdown(capacity_score=0.0),
            is_rejected=True,
            rejection_reason=cap_reason,
            trip_id=trip.trip_id,
            shipment_id=shipment.shipment_id
        )

    # 2. Vehicle Compatibility Evaluation
    veh_score, veh_rejected, veh_reason = evaluate_vehicle_compatibility(trip, shipment)
    if veh_rejected:
        return MatchResult(
            score=0.0,
            breakdown=ScoreBreakdown(capacity_score=cap_score, vehicle_score=0.0),
            is_rejected=True,
            rejection_reason=veh_reason,
            trip_id=trip.trip_id,
            shipment_id=shipment.shipment_id
        )

    # 3. Route Compatibility Evaluation (OSRM Real Road Detour)
    (route_score, detour_km, detour_min, direct_km,
     route_rejected, route_reason, route_geom, is_fallback) = await evaluate_route_compatibility(
        trip, shipment, config, client=client
    )

    if route_rejected:
        return MatchResult(
            score=0.0,
            breakdown=ScoreBreakdown(
                route_score=0.0,
                capacity_score=cap_score,
                vehicle_score=veh_score
            ),
            is_rejected=True,
            rejection_reason=route_reason,
            detour_km=detour_km,
            detour_minutes=detour_min,
            direct_trip_km=direct_km,
            trip_id=trip.trip_id,
            shipment_id=shipment.shipment_id,
            matched_route_geometry=route_geom,
            is_osrm_fallback=is_fallback
        )

    # 4. Time Compatibility Evaluation
    time_score, time_rejected, time_reason = evaluate_time_compatibility(
        trip, shipment, estimated_drive_minutes=detour_min
    )

    if time_rejected:
        return MatchResult(
            score=0.0,
            breakdown=ScoreBreakdown(
                route_score=route_score,
                capacity_score=cap_score,
                vehicle_score=veh_score,
                time_score=0.0
            ),
            is_rejected=True,
            rejection_reason=time_reason,
            detour_km=detour_km,
            detour_minutes=detour_min,
            direct_trip_km=direct_km,
            trip_id=trip.trip_id,
            shipment_id=shipment.shipment_id,
            matched_route_geometry=route_geom,
            is_osrm_fallback=is_fallback
        )

    # 5. Weighted Score Calculation
    total_score = (
        (config.route_weight * route_score) +
        (config.capacity_weight * cap_score) +
        (config.time_weight * time_score) +
        (config.vehicle_weight * veh_score)
    )

    # Rate / Price & Cost Savings Calculations
    rate_card = config.get_rate_card(trip.vehicle_type)
    
    # Billable route distance for this shipment (direct route + detour portion)
    billable_km = direct_km + detour_km

    # Estimated revenue for carrier (earnings)
    estimated_revenue = round(billable_km * trip.cost_per_km, 2)

    # Estimated price for shipper based on rate card (per km + per kg)
    estimated_cost_shipper = round(
        (billable_km * rate_card.rate_per_km) + (shipment.weight_kg * rate_card.rate_per_kg) + rate_card.base_fee,
        2
    )

    # Baseline cost if shipper booked a full dedicated truck for the route
    baseline_full_truck_cost = round(
        (direct_km * rate_card.rate_per_km * 1.30) + (trip.max_capacity_kg * rate_card.rate_per_kg) + rate_card.base_fee,
        2
    )

    # Savings calculation
    cost_savings_amount = max(0.0, round(baseline_full_truck_cost - estimated_cost_shipper, 2))
    cost_savings_pct = round((cost_savings_amount / max(1.0, baseline_full_truck_cost)) * 100.0, 1)

    # Environmental impact metrics
    weight_tons = shipment.weight_kg / 1000.0
    co2_saved_kg = round(weight_tons * direct_km * config.co2_per_ton_km_kg, 2)

    breakdown = ScoreBreakdown(
        route_score=route_score,
        capacity_score=cap_score,
        time_score=time_score,
        vehicle_score=veh_score
    )

    return MatchResult(
        score=round(total_score, 2),
        breakdown=breakdown,
        is_rejected=False,
        rejection_reason=None,
        detour_km=detour_km,
        detour_minutes=detour_min,
        direct_trip_km=direct_km,
        estimated_revenue=estimated_revenue,
        estimated_cost_shipper=estimated_cost_shipper,
        baseline_full_truck_cost=baseline_full_truck_cost,
        cost_savings_amount=cost_savings_amount,
        cost_savings_pct=cost_savings_pct,
        estimated_co2_saved_kg=co2_saved_kg,
        matched_route_geometry=route_geom,
        trip_id=trip.trip_id,
        shipment_id=shipment.shipment_id,
        is_osrm_fallback=is_fallback
    )

async def rank_matches(
    trip: TripInfo,
    shipments: List[ShipmentInfo],
    config: Optional[MatchConfig] = None,
    client: Optional[httpx.AsyncClient] = None
) -> List[MatchResult]:
    """
    Ranks multiple shipments for a given trip from best to worst score.
    Filter out rejected matches or put them at the end.
    """
    results: List[MatchResult] = []
    
    close_client = False
    if client is None:
        client = httpx.AsyncClient(timeout=config.request_timeout_seconds if config else 5.0)
        close_client = True

    try:
        for shipment in shipments:
            res = await score_match(trip, shipment, config=config, client=client)
            results.append(res)
    finally:
        if close_client:
            await client.aclose()

    # Sort non-rejected first by score descending, then rejected
    results.sort(key=lambda r: (-1 if r.is_rejected else 1, r.score), reverse=True)
    return results
