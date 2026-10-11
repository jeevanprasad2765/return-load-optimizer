# return-load-matcher

Standalone, pip-installable Python library for scoring and matching empty return truck trips with pending freight shipments.

## Features
- Multi-factor scoring (Route compatibility, Capacity fit, Time compatibility, Vehicle type match)
- OSRM route detour calculation
- Hard-rejection validation
- Multi-shipment consolidation algorithm

## Installation
```bash
pip install return-load-matcher
```

## Quick Start
```python
from datetime import datetime, timezone
from return_load_matcher import score_match, TripInfo, ShipmentInfo, Coordinate

trip = TripInfo(
    origin=Coordinate(lat=13.0827, lon=80.2707), # Chennai
    destination=Coordinate(lat=11.0168, lon=76.9558), # Coimbatore
    departure_time=datetime(2026, 10, 1, 8, 0, tzinfo=timezone.utc),
    available_capacity_kg=5000.0,
    vehicle_type="closed",
    cost_per_km=15.0
)

shipment = ShipmentInfo(
    pickup=Coordinate(lat=11.6643, lon=78.1460), # Salem (on Chennai -> Coimbatore route)
    destination=Coordinate(lat=11.0168, lon=76.9558), # Coimbatore
    weight_kg=3000.0,
    goods_type="electronics",
    required_vehicle_type="closed",
    pickup_window_start=datetime(2026, 10, 1, 6, 0, tzinfo=timezone.utc),
    pickup_window_end=datetime(2026, 10, 1, 14, 0, tzinfo=timezone.utc),
    delivery_deadline=datetime(2026, 10, 1, 20, 0, tzinfo=timezone.utc)
)

result = await score_match(trip, shipment)
print(f"Match Score: {result.score}/100, Rejected: {result.is_rejected}")
```
