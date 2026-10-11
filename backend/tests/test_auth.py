import pytest

@pytest.mark.asyncio
async def test_register_and_login_carrier(client):
    # Register carrier
    res = await client.post("/api/v1/auth/register", json={
        "email": "carrier_test@example.com",
        "password": "password123",
        "full_name": "Test Carrier",
        "company_name": "Test Carrier Corp",
        "phone": "+91 90000 11111",
        "role": "carrier"
    })
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "carrier"

    # Login carrier
    res_login = await client.post("/api/v1/auth/login", json={
        "email": "carrier_test@example.com",
        "password": "password123"
    })
    assert res_login.status_code == 200
    token_data = res_login.json()
    token = token_data["access_token"]

    # Get Me
    res_me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == 200
    assert res_me.json()["email"] == "carrier_test@example.com"
