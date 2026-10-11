import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.database import get_db
from app.api.deps import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.shipment import Shipment, ShipmentStatus
from app.models.match import Match
from app.models.trip import Trip
from app.models.booking import Booking
from app.schemas.shipment import ShipmentCreate, ShipmentResponse, ShipmentUpdate
from app.schemas.match import MatchResponse
from app.services.matching_service import compute_and_save_matches_for_shipment

router = APIRouter()

@router.get("", response_model=List[ShipmentResponse])
async def list_shipments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Shipment)
    if current_user.role == UserRole.SHIPPER:
        stmt = stmt.where(Shipment.shipper_id == current_user.id)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("", response_model=ShipmentResponse, status_code=status.HTTP_201_CREATED)
async def create_shipment(
    shipment_in: ShipmentCreate,
    current_user: User = Depends(require_role(UserRole.SHIPPER)),
    db: AsyncSession = Depends(get_db)
):
    shipment = Shipment(
        id=str(uuid.uuid4()),
        shipper_id=current_user.id,
        pickup_name=shipment_in.pickup_name,
        pickup_lat=shipment_in.pickup_lat,
        pickup_lon=shipment_in.pickup_lon,
        dest_name=shipment_in.dest_name,
        dest_lat=shipment_in.dest_lat,
        dest_lon=shipment_in.dest_lon,
        weight_kg=shipment_in.weight_kg,
        goods_type=shipment_in.goods_type,
        required_vehicle_type=shipment_in.required_vehicle_type,
        pickup_window_start=shipment_in.pickup_window_start,
        pickup_window_end=shipment_in.pickup_window_end,
        delivery_deadline=shipment_in.delivery_deadline,
        status=ShipmentStatus.POSTED
    )
    db.add(shipment)
    await db.commit()
    await db.refresh(shipment)

    # Compute matches for newly created shipment
    try:
        await compute_and_save_matches_for_shipment(db, shipment.id)
    except Exception as e:
        print(f"Error computing matches on shipment create: {e}")

    return shipment

@router.get("/{shipment_id}/matches", response_model=List[MatchResponse])
async def get_shipment_matches(
    shipment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        await compute_and_save_matches_for_shipment(db, shipment_id)
    except Exception as e:
        print(f"Error computing matches in get_shipment_matches: {e}")

    stmt = (
        select(Match)
        .options(
            selectinload(Match.trip).selectinload(Trip.carrier),
            selectinload(Match.trip).selectinload(Trip.truck),
            selectinload(Match.shipment)
        )
        .where(Match.shipment_id == shipment_id)
        .order_by(Match.is_rejected.asc(), Match.score.desc())
    )

    res = await db.execute(stmt)
    matches = res.scalars().all()

    # Query active bookings for this shipment to populate booking_status
    stmt_b = select(Booking).where(Booking.shipment_id == shipment_id)
    existing_bookings = (await db.execute(stmt_b)).scalars().all()
    booking_map = {b.trip_id: b.status.value for b in existing_bookings}

    # Deduplicate matches by trip_id so each trip card is distinct
    seen_trips = set()
    formatted = []
    for m in matches:
        if m.trip_id in seen_trips:
            continue
        seen_trips.add(m.trip_id)

        formatted.append(MatchResponse(
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
            trip=m.trip,
            shipment=m.shipment,
            booking_status=booking_map.get(m.trip_id)
        ))
    return formatted

@router.delete("/{shipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shipment(
    shipment_id: str,
    current_user: User = Depends(require_role(UserRole.SHIPPER)),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Shipment).where(Shipment.id == shipment_id, Shipment.shipper_id == current_user.id)
    shipment = (await db.execute(stmt)).scalar_one_or_none()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    await db.delete(shipment)
    await db.commit()

