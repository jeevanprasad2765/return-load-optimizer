import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import init_db, async_session_factory
from app.models.user import User, UserRole
from app.models.truck import Truck
from app.models.trip import Trip, TripStatus
from app.models.shipment import Shipment, ShipmentStatus
from app.models.booking import Booking, BookingStatus
from app.models.notification import Notification, NotificationType
from app.services.auth_service import get_password_hash
from app.services.matching_service import compute_and_save_matches_for_trip

async def seed_data():
    print("Initializing database tables...")
    await init_db()

    async with async_session_factory() as db:
        # Check if already seeded
        stmt = select(User).where(User.email == "carrier@kovaitransports.com")
        existing_user = (await db.execute(stmt)).scalar_one_or_none()
        if existing_user:
            print("Database already seeded. Skipping initial seed.")
            return

        print("Seeding Tamil Nadu demo data with multi-shipment consolidation & booking lifecycles...")

        # 1. Create Carrier Users
        carrier1 = User(
            id="c1111111-1111-1111-1111-111111111111",
            email="carrier@kovaitransports.com",
            password_hash=get_password_hash("password123"),
            full_name="Rajesh Kumar",
            company_name="Kovai Express Logistics",
            phone="+91 98765 43210",
            role=UserRole.CARRIER
        )
        carrier2 = User(
            id="c2222222-2222-2222-2222-222222222222",
            email="carrier@chennaifreight.com",
            password_hash=get_password_hash("password123"),
            full_name="Anand V",
            company_name="Chennai Freight Lines",
            phone="+91 98400 12345",
            role=UserRole.CARRIER
        )

        # 2. Create Shipper Users
        shipper1 = User(
            id="s1111111-1111-1111-1111-111111111111",
            email="shipper@salemsteels.com",
            password_hash=get_password_hash("password123"),
            full_name="Suresh Nathan",
            company_name="Salem Steel Industries",
            phone="+91 94432 99887",
            role=UserRole.SHIPPER
        )
        shipper2 = User(
            id="s2222222-2222-2222-2222-222222222222",
            email="shipper@tiruppurtextiles.com",
            password_hash=get_password_hash("password123"),
            full_name="Priya Dharshini",
            company_name="Tiruppur Garment Exports",
            phone="+91 97900 55443",
            role=UserRole.SHIPPER
        )

        db.add_all([carrier1, carrier2, shipper1, shipper2])
        await db.commit()

        # 3. Create Trucks
        truck1 = Truck(
            id="t1111111-1111-1111-1111-111111111111",
            carrier_id=carrier1.id,
            registration_number="TN-37-AB-1234",
            vehicle_type="closed",
            max_capacity_kg=10000.0,
            model_name="Tata Prima 2830.K"
        )
        truck2 = Truck(
            id="t2222222-2222-2222-2222-222222222222",
            carrier_id=carrier1.id,
            registration_number="TN-38-CD-5678",
            vehicle_type="open",
            max_capacity_kg=12000.0,
            model_name="Ashok Leyland 1615"
        )
        truck3 = Truck(
            id="t3333333-3333-3333-3333-333333333333",
            carrier_id=carrier2.id,
            registration_number="TN-01-EF-9012",
            vehicle_type="refrigerated",
            max_capacity_kg=6000.0,
            model_name="BharatBenz 1217R"
        )

        db.add_all([truck1, truck2, truck3])
        await db.commit()

        # 4. Create Empty Return Trips
        now = datetime.now(timezone.utc)

        # Trip 1: Chennai -> Coimbatore (10,000 kg capacity)
        trip1 = Trip(
            id="trip-chennai-coimbatore",
            carrier_id=carrier1.id,
            truck_id=truck1.id,
            origin_name="Chennai",
            origin_lat=13.0827,
            origin_lon=80.2707,
            dest_name="Coimbatore",
            dest_lat=11.0168,
            dest_lon=76.9558,
            departure_time=now + timedelta(hours=4),
            available_capacity_kg=9500.0,
            cost_per_km=16.0,
            status=TripStatus.POSTED
        )

        # Trip 2: Madurai -> Salem
        trip2 = Trip(
            id="trip-madurai-salem",
            carrier_id=carrier1.id,
            truck_id=truck2.id,
            origin_name="Madurai",
            origin_lat=9.9252,
            origin_lon=78.1198,
            dest_name="Salem",
            dest_lat=11.6643,
            dest_lon=78.1460,
            departure_time=now + timedelta(hours=6),
            available_capacity_kg=11000.0,
            cost_per_km=18.0,
            status=TripStatus.POSTED
        )

        # Trip 3: Trichy -> Chennai
        trip3 = Trip(
            id="trip-trichy-chennai",
            carrier_id=carrier2.id,
            truck_id=truck3.id,
            origin_name="Trichy",
            origin_lat=10.7905,
            origin_lon=78.7047,
            dest_name="Chennai",
            dest_lat=13.0827,
            dest_lon=80.2707,
            departure_time=now + timedelta(hours=8),
            available_capacity_kg=5500.0,
            cost_per_km=20.0,
            status=TripStatus.POSTED
        )

        db.add_all([trip1, trip2, trip3])
        await db.commit()

        # 5. Create Shipments (Multiple small shipments for consolidation showcase)
        shipment1 = Shipment(
            id="shipment-salem-coimbatore",
            shipper_id=shipper1.id,
            pickup_name="Salem",
            pickup_lat=11.6643,
            pickup_lon=78.1460,
            dest_name="Coimbatore",
            dest_lat=11.0168,
            dest_lon=76.9558,
            weight_kg=3000.0,
            goods_type="Steel Sheets & Fasteners",
            required_vehicle_type="closed",
            pickup_window_start=now,
            pickup_window_end=now + timedelta(hours=8),
            delivery_deadline=now + timedelta(hours=20),
            status=ShipmentStatus.POSTED
        )

        shipment2 = Shipment(
            id="shipment-tiruppur-coimbatore",
            shipper_id=shipper2.id,
            pickup_name="Tiruppur",
            pickup_lat=11.1085,
            pickup_lon=77.3411,
            dest_name="Coimbatore",
            dest_lat=11.0168,
            dest_lon=76.9558,
            weight_kg=2500.0,
            goods_type="Cotton Yarn & Finished Garments",
            required_vehicle_type="closed",
            pickup_window_start=now + timedelta(hours=1),
            pickup_window_end=now + timedelta(hours=9),
            delivery_deadline=now + timedelta(hours=22),
            status=ShipmentStatus.POSTED
        )

        shipment3 = Shipment(
            id="shipment-chennai-salem",
            shipper_id=shipper1.id,
            pickup_name="Chennai",
            pickup_lat=13.0827,
            pickup_lon=80.2707,
            dest_name="Salem",
            dest_lat=11.6643,
            dest_lon=78.1460,
            weight_kg=2000.0,
            goods_type="Electrical Switchgear",
            required_vehicle_type="closed",
            pickup_window_start=now,
            pickup_window_end=now + timedelta(hours=6),
            delivery_deadline=now + timedelta(hours=18),
            status=ShipmentStatus.POSTED
        )

        shipment4 = Shipment(
            id="shipment-madurai-salem",
            shipper_id=shipper1.id,
            pickup_name="Madurai",
            pickup_lat=9.9252,
            pickup_lon=78.1198,
            dest_name="Salem",
            dest_lat=11.6643,
            dest_lon=78.1460,
            weight_kg=6500.0,
            goods_type="Machinery Parts",
            required_vehicle_type="open",
            pickup_window_start=now,
            pickup_window_end=now + timedelta(hours=12),
            delivery_deadline=now + timedelta(hours=36),
            status=ShipmentStatus.POSTED
        )

        db.add_all([shipment1, shipment2, shipment3, shipment4])
        await db.commit()

        # 6. Compute initial matches
        print("Computing matches for seeded trips...")
        matches1 = await compute_and_save_matches_for_trip(db, trip1.id)
        matches2 = await compute_and_save_matches_for_trip(db, trip2.id)

        # 7. Create Pre-seeded Bookings in various lifecycle states
        if matches1:
            match_to_book = matches1[0]
            booking1 = Booking(
                id="booking-confirmed-1",
                match_id=match_to_book.id,
                trip_id=trip1.id,
                shipment_id=shipment1.id,
                carrier_id=carrier1.id,
                shipper_id=shipper1.id,
                agreed_price=match_to_book.estimated_cost_shipper or 8500.0,
                status=BookingStatus.DELIVERED
            )
            db.add(booking1)

        if matches2:
            match_to_book2 = matches2[0]
            booking2 = Booking(
                id="booking-pending-2",
                match_id=match_to_book2.id,
                trip_id=trip2.id,
                shipment_id=shipment4.id,
                carrier_id=carrier1.id,
                shipper_id=shipper1.id,
                agreed_price=match_to_book2.estimated_cost_shipper or 14500.0,
                status=BookingStatus.IN_TRANSIT
            )
            db.add(booking2)

        # 8. Create Pre-seeded Notifications
        notif1 = Notification(
            id=str(uuid.uuid4()),
            user_id=carrier1.id,
            type=NotificationType.BOOKING_REQUEST,
            message="New booking request from Salem Steel Industries for Chennai -> Coimbatore trip. Agreed Price: ₹8,500",
            related_entity_id=matches1[0].id if matches1 else "trip-chennai-coimbatore",
            is_read=False
        )
        notif2 = Notification(
            id=str(uuid.uuid4()),
            user_id=shipper1.id,
            type=NotificationType.NEW_MATCH,
            message="High match score (92/100) found for your Salem -> Coimbatore shipment! You save ₹2,400 (22%).",
            related_entity_id=matches1[0].id if matches1 else "shipment-salem-coimbatore",
            is_read=False
        )

        db.add_all([notif1, notif2])
        await db.commit()

        print("Successfully seeded Tamil Nadu demo data with multi-shipment consolidation & booking lifecycles!")

if __name__ == "__main__":
    asyncio.run(seed_data())
