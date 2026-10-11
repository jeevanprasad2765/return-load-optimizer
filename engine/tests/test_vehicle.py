import pytest
from return_load_matcher import evaluate_vehicle_compatibility, TripInfo, ShipmentInfo, Coordinate
from datetime import datetime, timezone

def make_trip(v_type: str):
    return TripInfo(
        origin=Coordinate(13.0827, 80.2707),
        destination=Coordinate(11.0168, 76.9558),
        departure_time=datetime.now(timezone.utc),
        available_capacity_kg=5000.0,
        vehicle_type=v_type
    )

def make_shipment(req_v_type: str):
    return ShipmentInfo(
        pickup=Coordinate(11.6643, 78.1460),
        destination=Coordinate(11.0168, 76.9558),
        weight_kg=1000.0,
        goods_type="cargo",
        required_vehicle_type=req_v_type
    )

def test_exact_vehicle_match():
    trip = make_trip("closed")
    shipment = make_shipment("closed")
    score, rejected, reason = evaluate_vehicle_compatibility(trip, shipment)
    assert not rejected
    assert score == 100.0

def test_compatible_vehicle_match():
    trip = make_trip("container")
    shipment = make_shipment("closed")
    score, rejected, reason = evaluate_vehicle_compatibility(trip, shipment)
    assert not rejected
    assert score > 80.0

def test_incompatible_vehicle_rejection():
    trip = make_trip("open")
    shipment = make_shipment("refrigerated")
    score, rejected, reason = evaluate_vehicle_compatibility(trip, shipment)
    assert rejected
    assert "Incompatible vehicle type" in reason
    assert score == 0.0

def test_unspecified_required_vehicle():
    trip = make_trip("flatbed")
    shipment = make_shipment(None)
    score, rejected, reason = evaluate_vehicle_compatibility(trip, shipment)
    assert not rejected
    assert score == 100.0
