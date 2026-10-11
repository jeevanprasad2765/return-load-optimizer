# Empty Return Load Optimizer 🚚♻️

> **Open-Source Freight Optimization Platform** that fills trucks' empty return trips with compatible freight shipments, turning deadhead kilometers into extra revenue for carriers, lower shipping costs for businesses, and reduced CO₂ emissions.

---

## 🌟 Enhanced Feature Set

1. **Multi-Shipment Consolidation**: Combines 2 to 3 compatible smaller shipments onto a single return truck trip using bin-packing optimization.
2. **Stateful Booking Confirmation Flow**: Complete booking lifecycle (`pending → confirmed → in_transit → delivered → cancelled`) with real-time status updates and capacity locking.
3. **Real Road-Based Scoring via OSRM**: Calculates detour distances using actual road routing (`https://router.project-osrm.org`) with in-memory caching and graceful straight-line fallback.
4. **Rate & Price Estimation**: Vehicle-type rate cards (base rate/km + rate/kg) showing **Estimated Cost**, **Estimated Earnings**, and **Shipper Savings ("You save ₹X / Y%")**.
5. **In-App Notifications**: Real-time navbar bell icon with unread badge count for high-scoring matches ($\ge 70$), booking requests, and status changes.

---

## 🏗️ Architecture & Monorepo Structure

```
/empty-return-load-optimizer
├── /engine       # Standalone, reusable Python package `return-load-matcher` (pip-installable, unit-tested)
├── /backend      # FastAPI app (Async SQLAlchemy, PyJWT, REST API v1, Tamil Nadu seed script)
├── /frontend     # React.js app (Vite, TailwindCSS v4, Leaflet OpenStreetMap, Recharts)
├── /docs         # Architecture diagrams, matching algorithm math, API specs, CONTRIBUTING, LICENSE
└── docker-compose.yml
```

---

## 🚀 Quick Start with Docker Compose

Run the entire system (PostgreSQL + FastAPI Backend + React Frontend + Seed Data) in a single command:

```bash
docker-compose up -d
```

* **Frontend Dashboard**: `http://localhost:3000`
* **FastAPI Backend API**: `http://localhost:8000`
* **Interactive OpenAPI Docs**: `http://localhost:8000/api/v1/docs`

---

## 🔐 Pre-seeded Tamil Nadu Demo Accounts

The database comes pre-seeded with realistic freight data across Tamil Nadu logistics hubs (**Coimbatore, Chennai, Madurai, Salem, Trichy, Tiruppur**):

| Role | Email | Password | Pre-configured Data |
| :--- | :--- | :--- | :--- |
| **Carrier** | `carrier@kovaitransports.com` | `password123` | Kovai Express fleet, Return trip **Chennai → Coimbatore**, pre-seeded bookings |
| **Shipper** | `shipper@salemsteels.com` | `password123` | Salem Steel shipments, active matches & booking requests |

---

## 📦 Using the `return-load-matcher` Engine Package in Other Systems

```bash
pip install ./engine
```

```python
from return_load_matcher import score_match, TripInfo, ShipmentInfo, Coordinate

trip = TripInfo(
    origin=Coordinate(lat=13.0827, lon=80.2707),      # Chennai
    destination=Coordinate(lat=11.0168, lon=76.9558), # Coimbatore
    departure_time=datetime.now(timezone.utc),
    available_capacity_kg=10000.0,
    vehicle_type="closed"
)

shipment = ShipmentInfo(
    pickup=Coordinate(lat=11.6643, lon=78.1460),      # Salem
    destination=Coordinate(lat=11.0168, lon=76.9558), # Coimbatore
    weight_kg=3000.0,
    goods_type="Steel Sheets"
)

result = await score_match(trip, shipment)
print(f"Match Score: {result.score}/100 | Price: ₹{result.estimated_cost_shipper} | Savings: ₹{result.cost_savings_amount} ({result.cost_savings_pct}%)")
```

---

## 📚 Documentation Links

* [System Architecture & Data Flow](file:///c:/Users/JEEVA/Desktop/Ost/docs/ARCHITECTURE.md)
* [Detailed Matching Algorithm Math](file:///c:/Users/JEEVA/Desktop/Ost/docs/MATCHING_ALGORITHM.md)
* [REST API Reference](file:///c:/Users/JEEVA/Desktop/Ost/docs/API.md)
* [Contributing Guide](file:///c:/Users/JEEVA/Desktop/Ost/docs/CONTRIBUTING.md)
* [MIT License](file:///c:/Users/JEEVA/Desktop/Ost/docs/LICENSE)
