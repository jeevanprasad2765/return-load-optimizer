import pytest
from datetime import datetime, timedelta, timezone
from return_load_matcher import (
    find_multi_shipment_consolidation, TripInfo, ShipmentInfo, Coordinate
)

@pytest.mark.asyncio
async def test_consolidation():
    now = datetime.now(timezone.utc)
    trip = TripInfo(
        trip_id="trip-c1",
        origin=Coordinate(13.0827, 80.2707),      # Chennai
        destination=Coordinate(11.0168, 76.9558), # Coimbatore
        departure_time=now + timedelta(hours=2),
        available_capacity_kg=5000.0,
        vehicle_type="closed"
    )

    # 3 small shipments that total 4500 kg (< 5000 kg capacity)
    s1 = ShipmentInfo(
        shipment_id="s1",
        pickup=Coordinate(11.6643, 78.1460),
        destination=Coordinate(11.0168, 76.9558),
        weight_kg=2000.0,
        goods_type="textiles"
    )
    s2 = ShipmentInfo(
        shipment_id="s2",
        pickup=Coordinate(11.6643, 78.1460),
        destination=Coordinate(11.0168, 76.9558),
        weight_kg=1500.0,
        goods_type="auto parts"
    )
    s3 = ShipmentInfo(
        shipment_id="s3",
        pickup=Coordinate(11.6643, 78.1460),
        destination=Coordinate(11.0168, 76.9558),
        weight_kg=1000.0,
        goods_type="food items"
    )
    # Exceeds capacity when combined
    s4_large = ShipmentInfo(
        shipment_id="s4",
        pickup=Coordinate(11.6643, 78.1460),
        destination=Coordinate(11.0168, 76.9558),
        weight_kg=4000.0,
        goods_type="heavy steel"
    )

    res = await find_multi_shipment_consolidation(trip, [s1, s2, s3, s4_large])
    assert res.total_weight_kg <= 5000.0
    assert len(res.shipments) >= 2
    assert res.capacity_utilization_pct > 0.0
