import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.trip import Trip, TripStatus
from app.models.shipment import Shipment, ShipmentStatus
from app.models.match import Match, MatchStatus
from app.models.booking import Booking, BookingStatus
from app.schemas.match import MatchResponse
from app.services.matching_service import compute_and_save_matches_for_trip

router = APIRouter()

@router.post("/find", response_model=List[MatchResponse])
async def trigger_matching_run(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Triggers matching algorithm across all active trips."""
    stmt = select(Trip).where(Trip.status == TripStatus.POSTED)
    trips = (await db.execute(stmt)).scalars().all()

    all_matches = []
    for trip in trips:
        matches = await compute_and_save_matches_for_trip(db, trip.id)
        all_matches.extend(matches)

    # Re-query formatted matches
    stmt_full = select(Match).options(
        selectinload(Match.trip),
        selectinload(Match.shipment)
    ).order_by(Match.score.desc())
    
    full_matches = (await db.execute(stmt_full)).scalars().all()
    
    return [
        MatchResponse(
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
            estimated_co2_saved_kg=m.estimated_co2_saved_kg,
            status=m.status,
            created_at=m.created_at,
            trip=m.trip,
            shipment=m.shipment
        )
        for m in full_matches
    ]

@router.put("/{match_id}/accept", response_model=MatchResponse)
async def accept_match(
    match_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Match).options(
        selectinload(Match.trip),
        selectinload(Match.shipment)
    ).where(Match.id == match_id)
    match_obj = (await db.execute(stmt)).scalar_one_or_none()

    if not match_obj:
        raise HTTPException(status_code=404, detail="Match not found")

    if match_obj.is_rejected:
        raise HTTPException(status_code=400, detail="Cannot accept a rejected match")

    match_obj.status = MatchStatus.ACCEPTED

    # Automatically create / lock a Booking record
    stmt_b = select(Booking).where(
        Booking.trip_id == match_obj.trip_id,
        Booking.shipment_id == match_obj.shipment_id
    )
    existing_b = (await db.execute(stmt_b)).scalar_one_or_none()

    if not existing_b:
        booking = Booking(
            id=str(uuid.uuid4()),
            match_id=match_obj.id,
            trip_id=match_obj.trip_id,
            shipment_id=match_obj.shipment_id,
            carrier_id=match_obj.trip.carrier_id,
            shipper_id=match_obj.shipment.shipper_id,
            agreed_price=match_obj.estimated_cost_shipper or match_obj.estimated_revenue or 1000.0,
            status=BookingStatus.CONFIRMED
        )
        db.add(booking)

        # Deduct trip capacity & update shipment status
        if match_obj.trip and match_obj.shipment:
            match_obj.trip.available_capacity_kg = max(0.0, match_obj.trip.available_capacity_kg - match_obj.shipment.weight_kg)
            match_obj.shipment.status = ShipmentStatus.BOOKED

    await db.commit()
    await db.refresh(match_obj)

    return MatchResponse(
        id=match_obj.id,
        trip_id=match_obj.trip_id,
        shipment_id=match_obj.shipment_id,
        score=match_obj.score,
        breakdown={
            "route_score": match_obj.route_score,
            "capacity_score": match_obj.capacity_score,
            "time_score": match_obj.time_score,
            "vehicle_score": match_obj.vehicle_score
        },
        is_rejected=match_obj.is_rejected,
        rejection_reason=match_obj.rejection_reason,
        detour_km=match_obj.detour_km,
        detour_minutes=match_obj.detour_minutes,
        direct_trip_km=match_obj.direct_trip_km,
        estimated_revenue=match_obj.estimated_revenue,
        estimated_co2_saved_kg=match_obj.estimated_co2_saved_kg,
        status=match_obj.status,
        created_at=match_obj.created_at,
        trip=match_obj.trip,
        shipment=match_obj.shipment
    )

@router.put("/{match_id}/reject", response_model=MatchResponse)
async def reject_match(
    match_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Match).options(
        selectinload(Match.trip),
        selectinload(Match.shipment)
    ).where(Match.id == match_id)
    match_obj = (await db.execute(stmt)).scalar_one_or_none()

    if not match_obj:
        raise HTTPException(status_code=404, detail="Match not found")

    match_obj.status = MatchStatus.REJECTED
    await db.commit()
    await db.refresh(match_obj)

    return MatchResponse(
        id=match_obj.id,
        trip_id=match_obj.trip_id,
        shipment_id=match_obj.shipment_id,
        score=match_obj.score,
        breakdown={
            "route_score": match_obj.route_score,
            "capacity_score": match_obj.capacity_score,
            "time_score": match_obj.time_score,
            "vehicle_score": match_obj.vehicle_score
        },
        is_rejected=match_obj.is_rejected,
        rejection_reason=match_obj.rejection_reason,
        detour_km=match_obj.detour_km,
        detour_minutes=match_obj.detour_minutes,
        direct_trip_km=match_obj.direct_trip_km,
        estimated_revenue=match_obj.estimated_revenue,
        estimated_co2_saved_kg=match_obj.estimated_co2_saved_kg,
        status=match_obj.status,
        created_at=match_obj.created_at,
        trip=match_obj.trip,
        shipment=match_obj.shipment
    )
