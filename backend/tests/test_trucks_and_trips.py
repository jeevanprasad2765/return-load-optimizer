import pytest

@pytest.mark.asyncio
async def test_carrier_truck_and_trip_lifecycle(client):
    # 1. Register Carrier
    reg = await client.post("/api/v1/auth/register", json={
        "email": "carrier_lifecycle@example.com",
        "password": "password123",
        "full_name": "Kovai Logistics",
        "company_name": "Kovai Logistics",
        "role": "carrier"
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Add Truck
    truck_res = await client.post("/api/v1/trucks", headers=headers, json={
        "registration_number": "TN-37-ZZ-9999",
        "vehicle_type": "closed",
        "max_capacity_kg": 6000.0,
        "model_name": "Tata Prima"
    })
    assert truck_res.status_code == 201
    truck_id = truck_res.json()["id"]

    # 3. Post Trip
    trip_res = await client.post("/api/v1/trips", headers=headers, json={
        "truck_id": truck_id,
        "origin_name": "Chennai",
        "origin_lat": 13.0827,
        "origin_lon": 80.2707,
        "dest_name": "Coimbatore",
        "dest_lat": 11.0168,
        "dest_lon": 76.9558,
        "departure_time": "2026-10-01T10:00:00Z",
        "available_capacity_kg": 5000.0,
        "cost_per_km": 15.0
    })
    assert trip_res.status_code == 201
    assert trip_res.json()["origin_name"] == "Chennai"
