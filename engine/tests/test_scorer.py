import pytest
from datetime import datetime, timedelta, timezone
from return_load_matcher import (
    score_match, rank_matches, TripInfo, ShipmentInfo, Coordinate, MatchConfig
)
from return_load_matcher.route import clear_route_cache

@pytest.mark.asyncio
async def test_score_match_high_score(httpx_mock):
    clear_route_cache()
    # Mock direct and detour OSRM calls
    httpx_mock.add_response(
        json={
            "code": "Ok",
            "routes": [{
                "distance": 480000.0,  # 480 km
                "duration": 32400.0,   # 9 hours
                "geometry": {"type": "LineString", "coordinates": [[80.27, 13.08], [78.14, 11.66], [76.95, 11.01]]}
            }]
        },
        is_reusable=True
    )

    now = datetime.now(timezone.utc)
    trip = TripInfo(
        trip_id="trip-1",
        origin=Coordinate(13.0827, 80.2707),      # Chennai
        destination=Coordinate(11.0168, 76.9558), # Coimbatore
        departure_time=now + timedelta(hours=2),
        available_capacity_kg=5000.0,
        vehicle_type="closed",
        cost_per_km=15.0
    )

    shipment = ShipmentInfo(
        shipment_id="shipment-1",
        pickup=Coordinate(11.6643, 78.1460),      # Salem (along route)
        destination=Coordinate(11.0168, 76.9558), # Coimbatore
        weight_kg=3500.0,
        goods_type="electronics",
        required_vehicle_type="closed",
        pickup_window_start=now,
        pickup_window_end=now + timedelta(hours=6),
        delivery_deadline=now + timedelta(hours=18)
    )

    result = await score_match(trip, shipment)
    assert not result.is_rejected
    assert result.score > 70.0
    assert result.breakdown.capacity_score > 70.0
    assert result.breakdown.vehicle_score == 100.0
    assert result.estimated_revenue > 0
    assert result.estimated_cost_shipper > 0
    assert result.cost_savings_amount >= 0
    assert result.estimated_co2_saved_kg > 0

@pytest.mark.asyncio
async def test_rank_matches():
    clear_route_cache()
    now = datetime.now(timezone.utc)
    trip = TripInfo(
        trip_id="trip-tn",
        origin=Coordinate(13.0827, 80.2707),
        destination=Coordinate(11.0168, 76.9558),
        departure_time=now + timedelta(hours=2),
        available_capacity_kg=4000.0,
        vehicle_type="closed"
    )

    s1 = ShipmentInfo(
        shipment_id="s1",
        pickup=Coordinate(11.6643, 78.1460), # Salem
        destination=Coordinate(11.0168, 76.9558),
        weight_kg=3000.0,
        goods_type="goods",
        required_vehicle_type="closed"
    )

    s2_overweight = ShipmentInfo(
        shipment_id="s2",
        pickup=Coordinate(11.6643, 78.1460),
        destination=Coordinate(11.0168, 76.9558),
        weight_kg=8000.0, # overweight
        goods_type="machinery"
    )

    results = await rank_matches(trip, [s1, s2_overweight])
    assert len(results) == 2
    assert results[0].shipment_id == "s1"
    assert not results[0].is_rejected
    assert results[1].shipment_id == "s2"
    assert results[1].is_rejected
