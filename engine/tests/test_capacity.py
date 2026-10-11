import pytest
from return_load_matcher import evaluate_capacity_fit, TripInfo, ShipmentInfo, Coordinate
from datetime import datetime, timezone

def make_trip(capacity_kg: float):
    return TripInfo(
        origin=Coordinate(13.0827, 80.2707),
        destination=Coordinate(11.0168, 76.9558),
        departure_time=datetime.now(timezone.utc),
        available_capacity_kg=capacity_kg,
        vehicle_type="closed"
    )

def make_shipment(weight_kg: float):
    return ShipmentInfo(
        pickup=Coordinate(11.6643, 78.1460),
        destination=Coordinate(11.0168, 76.9558),
        weight_kg=weight_kg,
        goods_type="textiles"
    )

def test_valid_capacity_fit():
    trip = make_trip(5000.0)
    shipment = make_shipment(3000.0)
    score, rejected, reason = evaluate_capacity_fit(trip, shipment)
    assert not rejected
    assert reason is None
    assert 50.0 <= score <= 100.0

def test_overweight_capacity_rejection():
    trip = make_trip(3000.0)
    shipment = make_shipment(5000.0)
    score, rejected, reason = evaluate_capacity_fit(trip, shipment)
    assert rejected
    assert "exceeds available trip capacity" in reason
    assert score == 0.0

def test_zero_weight_rejection():
    trip = make_trip(5000.0)
    shipment = make_shipment(0.0)
    score, rejected, reason = evaluate_capacity_fit(trip, shipment)
    assert rejected
    assert "greater than zero" in reason
