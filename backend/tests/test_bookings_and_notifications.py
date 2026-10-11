import pytest

@pytest.mark.asyncio
async def test_booking_confirmation_lifecycle_and_notifications(client):
    # 1. Register Carrier
    reg_c = await client.post("/api/v1/auth/register", json={
        "email": "carrier_booking@example.com",
        "password": "password123",
        "full_name": "Carrier Test",
        "company_name": "Carrier Test Logistics",
        "role": "carrier"
    })
    token_c = reg_c.json()["access_token"]
    headers_c = {"Authorization": f"Bearer {token_c}"}

    # 2. Register Shipper
    reg_s = await client.post("/api/v1/auth/register", json={
        "email": "shipper_booking@example.com",
        "password": "password123",
        "full_name": "Shipper Test",
        "company_name": "Shipper Test Corp",
        "role": "shipper"
    })
    token_s = reg_s.json()["access_token"]
    headers_s = {"Authorization": f"Bearer {token_s}"}

    # 3. Carrier adds Truck and posts Trip
    truck_res = await client.post("/api/v1/trucks", headers=headers_c, json={
        "registration_number": "TN-99-AA-1111",
        "vehicle_type": "closed",
        "max_capacity_kg": 5000.0
    })
    truck_id = truck_res.json()["id"]

    trip_res = await client.post("/api/v1/trips", headers=headers_c, json={
        "truck_id": truck_id,
        "origin_name": "Chennai",
        "origin_lat": 13.0827,
        "origin_lon": 80.2707,
        "dest_name": "Coimbatore",
        "dest_lat": 11.0168,
        "dest_lon": 76.9558,
        "departure_time": "2026-10-10T10:00:00Z",
        "available_capacity_kg": 5000.0,
        "cost_per_km": 15.0
    })
    trip_id = trip_res.json()["id"]

    # 4. Shipper posts Shipment
    shp_res = await client.post("/api/v1/shipments", headers=headers_s, json={
        "pickup_name": "Salem",
        "pickup_lat": 11.6643,
        "pickup_lon": 78.1460,
        "dest_name": "Coimbatore",
        "dest_lat": 11.0168,
        "dest_lon": 76.9558,
        "weight_kg": 2000.0,
        "goods_type": "Hardware Parts",
        "required_vehicle_type": "closed"
    })
    shipment_id = shp_res.json()["id"]

    # 5. Shipper requests Booking
    booking_req = await client.post("/api/v1/bookings", headers=headers_s, json={
        "trip_id": trip_id,
        "shipment_id": shipment_id,
        "agreed_price": 7500.0
    })
    assert booking_req.status_code == 201
    booking_data = booking_req.json()
    booking_id = booking_data["id"]
    assert booking_data["status"] == "pending"

    # 6. Carrier checks Notifications for Booking Request
    notif_res = await client.get("/api/v1/notifications", headers=headers_c)
    assert notif_res.status_code == 200
    notifs = notif_res.json()
    assert len(notifs) >= 1
    assert notifs[0]["type"] == "booking_request"

    # 7. Carrier Confirms Booking (pending -> confirmed)
    patch_res = await client.patch(f"/api/v1/bookings/{booking_id}/status", headers=headers_c, json={
        "status": "confirmed",
        "agreed_price": 7500.0
    })
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "confirmed"

    # 8. Carrier updates transit: confirmed -> in_transit -> delivered
    transit_res = await client.patch(f"/api/v1/bookings/{booking_id}/status", headers=headers_c, json={
        "status": "in_transit"
    })
    assert transit_res.json()["status"] == "in_transit"

    delivered_res = await client.patch(f"/api/v1/bookings/{booking_id}/status", headers=headers_c, json={
        "status": "delivered"
    })
    assert delivered_res.json()["status"] == "delivered"
