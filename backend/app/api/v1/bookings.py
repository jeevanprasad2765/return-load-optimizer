import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserRole
from app.models.trip import Trip, TripStatus
from app.models.shipment import Shipment, ShipmentStatus
from app.models.match import Match, MatchStatus
from app.models.booking import Booking, BookingStatus
from app.models.notification import NotificationType
from app.schemas.auth import UserResponse
from app.schemas.truck import TruckResponse
from app.schemas.trip import TripResponse
from app.schemas.booking import BookingCreate, BookingResponse, BookingStatusUpdate
from app.schemas.match import MatchResponse
from app.services.notification_service import create_notification

router = APIRouter()

def format_trip_schema(t: Optional[Trip]) -> Optional[TripResponse]:
    if not t:
        return None
    carrier_data = None
    truck_data = None
    if "carrier" in t.__dict__ and t.__dict__["carrier"] is not None:
        try:
            carrier_data = UserResponse.model_validate(t.carrier)
        except Exception:
            carrier_data = None
    if "truck" in t.__dict__ and t.__dict__["truck"] is not None:
        try:
            truck_data = TruckResponse.model_validate(t.truck)
        except Exception:
            truck_data = None

    return TripResponse(
        id=t.id,
        carrier_id=t.carrier_id,
        truck_id=t.truck_id,
        origin_name=t.origin_name,
        origin_lat=t.origin_lat,
        origin_lon=t.origin_lon,
        dest_name=t.dest_name,
        dest_lat=t.dest_lat,
        dest_lon=t.dest_lon,
        departure_time=t.departure_time,
        available_capacity_kg=t.available_capacity_kg,
        cost_per_km=t.cost_per_km,
        status=t.status,
        created_at=t.created_at,
        carrier=carrier_data,
        truck=truck_data
    )

def format_match_schema(m: Optional[Match]) -> Optional[MatchResponse]:
    if not m:
        return None
    trip_data = format_trip_schema(m.trip) if ("trip" in m.__dict__ and m.__dict__["trip"] is not None) else None
    shipment_data = m.shipment if ("shipment" in m.__dict__ and m.__dict__["shipment"] is not None) else None
    return MatchResponse(
        id=m.id,
        trip_id=m.trip_id,
        shipment_id=m.shipment_id,
        score=m.score,
        breakdown={
            "route_score": m.route_score,
            "capacity_score": m.capacity_score,
            "time_score": m.time_score,
            "vehicle_score": m.vehicle_score
        },
        is_rejected=m.is_rejected,
        rejection_reason=m.rejection_reason,
        detour_km=m.detour_km,
        detour_minutes=m.detour_minutes,
        direct_trip_km=m.direct_trip_km,
        estimated_revenue=m.estimated_revenue,
        estimated_cost_shipper=m.estimated_cost_shipper,
        baseline_full_truck_cost=m.baseline_full_truck_cost,
        cost_savings_amount=m.cost_savings_amount,
        cost_savings_pct=m.cost_savings_pct,
        estimated_co2_saved_kg=m.estimated_co2_saved_kg,
        is_osrm_fallback=m.is_osrm_fallback,
        status=m.status,
        created_at=m.created_at,
        trip=trip_data,
        shipment=shipment_data
    )

@router.get("", response_model=List[BookingResponse])
async def list_bookings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Auto-sync any accepted matches that do not have booking records
    stmt_acc = select(Match).options(
        selectinload(Match.trip).selectinload(Trip.carrier),
        selectinload(Match.trip).selectinload(Trip.truck),
        selectinload(Match.shipment)
    ).where(Match.status == MatchStatus.ACCEPTED)
    
    if current_user.role == UserRole.CARRIER:
        stmt_acc = stmt_acc.join(Trip, Match.trip_id == Trip.id).where(Trip.carrier_id == current_user.id)
    else:
        stmt_acc = stmt_acc.join(Shipment, Match.shipment_id == Shipment.id).where(Shipment.shipper_id == current_user.id)

    accepted_matches = (await db.execute(stmt_acc)).scalars().all()
    for m in accepted_matches:
        stmt_b_check = select(Booking).where(
            Booking.trip_id == m.trip_id,
            Booking.shipment_id == m.shipment_id
        )
        existing_b = (await db.execute(stmt_b_check)).scalar_one_or_none()
        if not existing_b and m.trip and m.shipment:
            b_new = Booking(
                id=str(uuid.uuid4()),
                match_id=m.id,
                trip_id=m.trip_id,
                shipment_id=m.shipment_id,
                carrier_id=m.trip.carrier_id,
                shipper_id=m.shipment.shipper_id,
                agreed_price=m.estimated_cost_shipper or m.estimated_revenue or 1000.0,
                status=BookingStatus.CONFIRMED
            )
            db.add(b_new)
            m.trip.available_capacity_kg = max(0.0, m.trip.available_capacity_kg - m.shipment.weight_kg)
            m.shipment.status = ShipmentStatus.BOOKED

    await db.commit()

    stmt = select(Booking).options(
        selectinload(Booking.match).selectinload(Match.trip).selectinload(Trip.carrier),
        selectinload(Booking.match).selectinload(Match.trip).selectinload(Trip.truck),
        selectinload(Booking.match).selectinload(Match.shipment),
        selectinload(Booking.trip).selectinload(Trip.carrier),
        selectinload(Booking.trip).selectinload(Trip.truck),
        selectinload(Booking.shipment)
    )

    if current_user.role == UserRole.CARRIER:
        stmt = stmt.where(Booking.carrier_id == current_user.id)
    else:
        stmt = stmt.where(Booking.shipper_id == current_user.id)

    stmt = stmt.order_by(Booking.created_at.desc())
    res = await db.execute(stmt)
    bookings = res.scalars().all()

    formatted = []
    for b in bookings:
        formatted.append(BookingResponse(
            id=b.id,
            match_id=b.match_id,
            trip_id=b.trip_id,
            shipment_id=b.shipment_id,
            carrier_id=b.carrier_id,
            shipper_id=b.shipper_id,
            agreed_price=b.agreed_price,
            status=b.status,
            created_at=b.created_at,
            updated_at=b.updated_at,
            match=format_match_schema(b.match),
            trip=format_trip_schema(b.trip),
            shipment=b.shipment
        ))
    return formatted

@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking_request(
    booking_in: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Shipper or Carrier requests booking on a match."""
    match_obj = None
    if booking_in.match_id:
        stmt_m = select(Match).options(
            selectinload(Match.trip).selectinload(Trip.carrier),
            selectinload(Match.trip).selectinload(Trip.truck),
            selectinload(Match.shipment)
        ).where(Match.id == booking_in.match_id)
        match_obj = (await db.execute(stmt_m)).scalar_one_or_none()

    if match_obj:
        trip_id = match_obj.trip_id
        shipment_id = match_obj.shipment_id
        default_price = match_obj.estimated_cost_shipper or match_obj.estimated_revenue
    else:
        trip_id = booking_in.trip_id
        shipment_id = booking_in.shipment_id
        default_price = booking_in.agreed_price or 1000.0

    # Fetch Trip & Shipment
    stmt_trip = select(Trip).options(
        selectinload(Trip.carrier),
        selectinload(Trip.truck)
    ).where(Trip.id == trip_id)
    trip = (await db.execute(stmt_trip)).scalar_one_or_none()
    stmt_shp = select(Shipment).where(Shipment.id == shipment_id)
    shipment = (await db.execute(stmt_shp)).scalar_one_or_none()

    if not trip or not shipment:
        raise HTTPException(status_code=404, detail="Trip or Shipment not found")

    # Check existing active booking
    stmt_b = select(Booking).where(
        Booking.trip_id == trip.id,
        Booking.shipment_id == shipment.id,
        Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED, BookingStatus.IN_TRANSIT])
    )
    existing_b = (await db.execute(stmt_b)).scalar_one_or_none()
    if existing_b:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A booking request for this trip and shipment already exists with status '{existing_b.status.value}'"
        )

    agreed_price = booking_in.agreed_price or default_price

    booking = Booking(
        id=str(uuid.uuid4()),
        match_id=match_obj.id if match_obj else None,
        trip_id=trip.id,
        shipment_id=shipment.id,
        carrier_id=trip.carrier_id,
        shipper_id=shipment.shipper_id,
        agreed_price=agreed_price,
        status=BookingStatus.PENDING
    )
    db.add(booking)
    shipment.status = ShipmentStatus.BOOKING_REQUESTED
    await db.commit()
    await db.refresh(booking)

    # Fire Notification to Carrier for Booking Request
    sender_name = current_user.company_name or current_user.full_name or "Shipper"
    await create_notification(
        db,
        user_id=trip.carrier_id,
        notification_type=NotificationType.BOOKING_REQUEST,
        message=f"New booking request from {sender_name} for your trip {trip.origin_name} -> {trip.dest_name} ({shipment.goods_type}, {shipment.weight_kg} kg). Agreed Price: ₹{agreed_price:,.2f}",
        related_entity_id=booking.id
    )

    return BookingResponse(
        id=booking.id,
        match_id=booking.match_id,
        trip_id=booking.trip_id,
        shipment_id=booking.shipment_id,
        carrier_id=booking.carrier_id,
        shipper_id=booking.shipper_id,
        agreed_price=booking.agreed_price,
        status=booking.status,
        created_at=booking.created_at,
        updated_at=booking.updated_at,
        match=format_match_schema(match_obj),
        trip=format_trip_schema(trip),
        shipment=shipment
    )

@router.patch("/{booking_id}/status", response_model=BookingResponse)
@router.put("/{booking_id}/status", response_model=BookingResponse)
async def update_booking_status(
    booking_id: str,
    status_in: BookingStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Updates booking status (pending -> confirmed -> in_transit -> delivered / cancelled)."""
    stmt = select(Booking).options(
        selectinload(Booking.match).selectinload(Match.trip).selectinload(Trip.carrier),
        selectinload(Booking.match).selectinload(Match.trip).selectinload(Trip.truck),
        selectinload(Booking.match).selectinload(Match.shipment),
        selectinload(Booking.trip).selectinload(Trip.carrier),
        selectinload(Booking.trip).selectinload(Trip.truck),
        selectinload(Booking.shipment)
    ).where(Booking.id == booking_id)
    booking = (await db.execute(stmt)).scalar_one_or_none()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    old_status = booking.status
    new_status = status_in.status

    if status_in.agreed_price is not None:
        booking.agreed_price = status_in.agreed_price

    booking.status = new_status
    trip = booking.trip
    shipment = booking.shipment

    # Capacity and status updates
    if new_status == BookingStatus.CONFIRMED and old_status != BookingStatus.CONFIRMED:
        # Lock capacity on trip
        if trip and shipment:
            trip.available_capacity_kg = max(0.0, trip.available_capacity_kg - shipment.weight_kg)
            shipment.status = ShipmentStatus.BOOKED
            if booking.match:
                booking.match.status = MatchStatus.ACCEPTED

    elif new_status == BookingStatus.CANCELLED:
        # Release capacity back to trip if was confirmed
        if trip and shipment and old_status == BookingStatus.CONFIRMED:
            trip.available_capacity_kg += shipment.weight_kg
        if shipment and shipment.status in [ShipmentStatus.BOOKED, ShipmentStatus.BOOKING_REQUESTED]:
            shipment.status = ShipmentStatus.POSTED
        if booking.match:
            booking.match.status = MatchStatus.REJECTED

    elif new_status == BookingStatus.DELIVERED:
        if shipment:
            shipment.status = ShipmentStatus.DELIVERED

    await db.commit()
    await db.refresh(booking)

    # Notify counterpart of status change
    notify_target_user = booking.shipper_id if current_user.id == booking.carrier_id else booking.carrier_id
    await create_notification(
        db,
        user_id=notify_target_user,
        notification_type=NotificationType.BOOKING_STATUS_CHANGE,
        message=f"Booking status updated to '{new_status.value.upper()}' for trip {trip.origin_name} -> {trip.dest_name}. Price: ₹{booking.agreed_price}",
        related_entity_id=booking.id
    )

    return BookingResponse(
        id=booking.id,
        match_id=booking.match_id,
        trip_id=booking.trip_id,
        shipment_id=booking.shipment_id,
        carrier_id=booking.carrier_id,
        shipper_id=booking.shipper_id,
        agreed_price=booking.agreed_price,
        status=booking.status,
        created_at=booking.created_at,
        updated_at=booking.updated_at,
        match=format_match_schema(booking.match),
        trip=format_trip_schema(trip),
        shipment=shipment
    )

@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Booking).where(Booking.id == booking_id)
    booking = (await db.execute(stmt)).scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.carrier_id != current_user.id and booking.shipper_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this booking")

    await db.delete(booking)
    await db.commit()

