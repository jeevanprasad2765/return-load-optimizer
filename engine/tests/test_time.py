import pytest
from datetime import datetime, timedelta, timezone
from return_load_matcher import evaluate_time_compatibility, TripInfo, ShipmentInfo, Coordinate

def test_valid_time_window():
    now = datetime.now(timezone.utc)
    trip = TripInfo(
        origin=Coordinate(13.0827, 80.2707),
        destination=Coordinate(11.0168, 76.9558),
        departure_time=now + timedelta(hours=2),
        available_capacity_kg=5000.0,
        vehicle_type="closed"
    )
    shipment = ShipmentInfo(
        pickup=Coordinate(11.6643, 78.1460),
        destination=Coordinate(11.0168, 76.9558),
        weight_kg=1000.0,
        goods_type="parts",
        pickup_window_start=now,
        pickup_window_end=now + timedelta(hours=4),
        delivery_deadline=now + timedelta(hours=12)
    )
    score, rejected, reason = evaluate_time_compatibility(trip, shipment, estimated_drive_minutes=300)
    assert not rejected
    assert score > 70.0

def test_deadline_exceeded_rejection():
    now = datetime.now(timezone.utc)
    trip = TripInfo(
        origin=Coordinate(13.0827, 80.2707),
        destination=Coordinate(11.0168, 76.9558),
        departure_time=now,
        available_capacity_kg=5000.0,
        vehicle_type="closed"
    )
    shipment = ShipmentInfo(
        pickup=Coordinate(11.6643, 78.1460),
        destination=Coordinate(11.0168, 76.9558),
        weight_kg=1000.0,
        goods_type="perishable",
        delivery_deadline=now + timedelta(hours=2)
    )
    # 5 hours drive time exceeds 2 hour deadline
    score, rejected, reason = evaluate_time_compatibility(trip, shipment, estimated_drive_minutes=300)
    assert rejected
    assert "past delivery deadline" in reason
