import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.database import get_db
from app.api.deps import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.trip import Trip, TripStatus
from app.models.truck import Truck
from app.models.match import Match
from app.models.booking import Booking
from app.schemas.trip import TripCreate, TripResponse, TripUpdate
from app.schemas.match import MatchResponse, MultiShipmentConsolidationResponse
from app.services.matching_service import compute_and_save_matches_for_trip, get_multi_shipment_consolidation_for_trip

router = APIRouter()

@router.get("", response_model=List[TripResponse])
async def list_trips(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Trip).options(
        selectinload(Trip.carrier),
        selectinload(Trip.truck)
    )
    if current_user.role == UserRole.CARRIER:
        stmt = stmt.where(Trip.carrier_id == current_user.id)
    stmt = stmt.order_by(Trip.created_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
async def create_trip(
    trip_in: TripCreate,
    current_user: User = Depends(require_role(UserRole.CARRIER)),
    db: AsyncSession = Depends(get_db)
):
    # Verify truck ownership
    stmt = select(Truck).where(Truck.id == trip_in.truck_id, Truck.carrier_id == current_user.id)
    truck = (await db.execute(stmt)).scalar_one_or_none()
    if not truck:
        raise HTTPException(status_code=400, detail="Truck not found or does not belong to you")

    trip = Trip(
        id=str(uuid.uuid4()),
        carrier_id=current_user.id,
        truck_id=trip_in.truck_id,
        origin_name=trip_in.origin_name,
        origin_lat=trip_in.origin_lat,
        origin_lon=trip_in.origin_lon,
        dest_name=trip_in.dest_name,
        dest_lat=trip_in.dest_lat,
        dest_lon=trip_in.dest_lon,
        departure_time=trip_in.departure_time,
        available_capacity_kg=trip_in.available_capacity_kg,
        cost_per_km=trip_in.cost_per_km,
        status=TripStatus.POSTED
    )
    db.add(trip)
    await db.commit()
    await db.refresh(trip)

    # Automatically compute matches for newly created trip in background
    try:
        await compute_and_save_matches_for_trip(db, trip.id)
    except Exception:
        pass

    stmt_loaded = select(Trip).options(
        selectinload(Trip.carrier),
        selectinload(Trip.truck)
    ).where(Trip.id == trip.id)
    return (await db.execute(stmt_loaded)).scalar_one()

@router.get("/{trip_id}/matches", response_model=List[MatchResponse])
async def get_trip_matches(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Re-compute to ensure latest scores
    await compute_and_save_matches_for_trip(db, trip_id)

    stmt = select(Match).options(
        selectinload(Match.trip).selectinload(Trip.carrier),
        selectinload(Match.trip).selectinload(Trip.truck),
        selectinload(Match.shipment)
    ).where(Match.trip_id == trip_id).order_by(Match.is_rejected.asc(), Match.score.desc())

    res = await db.execute(stmt)
    matches = res.scalars().all()

    # Format response with nested breakdown
    formatted = []
    for m in matches:
        m_dict = {
            "id": m.id,
            "trip_id": m.trip_id,
            "shipment_id": m.shipment_id,
            "score": m.score,
            "breakdown": {
                "route_score": m.route_score,
                "capacity_score": m.capacity_score,
                "time_score": m.time_score,
                "vehicle_score": m.vehicle_score
            },
            "is_rejected": m.is_rejected,
            "rejection_reason": m.rejection_reason,
            "detour_km": m.detour_km,
            "detour_minutes": m.detour_minutes,
            "direct_trip_km": m.direct_trip_km,
            "estimated_revenue": m.estimated_revenue,
            "estimated_co2_saved_kg": m.estimated_co2_saved_kg,
            "status": m.status,
            "created_at": m.created_at,
            "trip": m.trip,
            "shipment": m.shipment
        }
        formatted.append(MatchResponse(**m_dict))
    return formatted

@router.get("/{trip_id}/consolidation", response_model=MultiShipmentConsolidationResponse)
async def get_trip_consolidation(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await get_multi_shipment_consolidation_for_trip(db, trip_id)
    
    # Fetch matched DB records
    stmt = (
        select(Match)
        .options(
            selectinload(Match.trip).selectinload(Trip.carrier),
            selectinload(Match.trip).selectinload(Trip.truck),
            selectinload(Match.shipment)
        )
        .where(Match.trip_id == trip_id)
        .order_by(Match.score.desc())
    )
    db_matches = (await db.execute(stmt)).scalars().all()
    db_match_map = {m.shipment_id: m for m in db_matches}

    # Query active bookings for this trip
    stmt_b = select(Booking).where(Booking.trip_id == trip_id)
    existing_bookings = (await db.execute(stmt_b)).scalars().all()
    booking_map = {b.shipment_id: b.status.value for b in existing_bookings}

    formatted_matches = []
    seen_shipments = set()
    for engine_match in res.matches:
        if engine_match.shipment_id in seen_shipments:
            continue
        seen_shipments.add(engine_match.shipment_id)

        db_m = db_match_map.get(engine_match.shipment_id)
        if db_m:
            formatted_matches.append(MatchResponse(
                id=db_m.id,
                trip_id=db_m.trip_id,
                shipment_id=db_m.shipment_id,
                score=db_m.score,
                breakdown={
                    "route_score": db_m.route_score,
                    "capacity_score": db_m.capacity_score,
                    "time_score": db_m.time_score,
                    "vehicle_score": db_m.vehicle_score
                },
                is_rejected=db_m.is_rejected,
                rejection_reason=db_m.rejection_reason,
                detour_km=db_m.detour_km,
                detour_minutes=db_m.detour_minutes,
                direct_trip_km=db_m.direct_trip_km,
                estimated_revenue=db_m.estimated_revenue,
                estimated_cost_shipper=db_m.estimated_cost_shipper,
                baseline_full_truck_cost=db_m.baseline_full_truck_cost,
                cost_savings_amount=db_m.cost_savings_amount,
                cost_savings_pct=db_m.cost_savings_pct,
                estimated_co2_saved_kg=db_m.estimated_co2_saved_kg,
                is_osrm_fallback=db_m.is_osrm_fallback,
                status=db_m.status,
                created_at=db_m.created_at,
                trip=db_m.trip,
                shipment=db_m.shipment,
                booking_status=booking_map.get(db_m.shipment_id)
            ))

    return MultiShipmentConsolidationResponse(
        trip_id=trip_id,
        matches=formatted_matches,
        total_weight_kg=res.total_weight_kg,
        total_capacity_kg=res.total_capacity_kg,
        capacity_utilization_pct=res.capacity_utilization_pct,
        combined_score=res.combined_score
    )

@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip(
    trip_id: str,
    current_user: User = Depends(require_role(UserRole.CARRIER)),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Trip).where(Trip.id == trip_id, Trip.carrier_id == current_user.id)
    trip = (await db.execute(stmt)).scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    await db.delete(trip)
    await db.commit()

