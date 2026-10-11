import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.trip import Trip, TripStatus
from app.models.shipment import Shipment, ShipmentStatus
from app.models.match import Match, MatchStatus
from app.models.notification import NotificationType
from app.config import settings
from app.services.notification_service import create_notification

from return_load_matcher import (
    score_match, rank_matches, find_multi_shipment_consolidation,
    TripInfo, ShipmentInfo, Coordinate, MatchConfig
)

def trip_to_engine(trip: Trip) -> TripInfo:
    return TripInfo(
        trip_id=trip.id,
        origin=Coordinate(lat=trip.origin_lat, lon=trip.origin_lon),
        destination=Coordinate(lat=trip.dest_lat, lon=trip.dest_lon),
        departure_time=trip.departure_time,
        available_capacity_kg=trip.available_capacity_kg,
        max_capacity_kg=trip.truck.max_capacity_kg if trip.truck else 10000.0,
        vehicle_type=trip.truck.vehicle_type if trip.truck else "closed",
        cost_per_km=trip.cost_per_km
    )

def shipment_to_engine(shipment: Shipment) -> ShipmentInfo:
    return ShipmentInfo(
        shipment_id=shipment.id,
        pickup=Coordinate(lat=shipment.pickup_lat, lon=shipment.pickup_lon),
        destination=Coordinate(lat=shipment.dest_lat, lon=shipment.dest_lon),
        weight_kg=shipment.weight_kg,
        goods_type=shipment.goods_type,
        required_vehicle_type=shipment.required_vehicle_type,
        pickup_window_start=shipment.pickup_window_start,
        pickup_window_end=shipment.pickup_window_end,
        delivery_deadline=shipment.delivery_deadline
    )

async def compute_and_save_matches_for_trip(
    db: AsyncSession,
    trip_id: str
) -> List[Match]:
    # Fetch trip with truck and carrier
    stmt = select(Trip).options(selectinload(Trip.truck)).where(Trip.id == trip_id)
    res = await db.execute(stmt)
    trip = res.scalar_one_or_none()
    if not trip:
        raise ValueError(f"Trip {trip_id} not found")

    # Fetch all posted shipments
    stmt_shipments = select(Shipment).options(selectinload(Shipment.shipper)).where(Shipment.status == ShipmentStatus.POSTED)
    res_shipments = await db.execute(stmt_shipments)
    shipments = res_shipments.scalars().all()

    if not shipments:
        return []

    engine_trip = trip_to_engine(trip)
    engine_shipments = [shipment_to_engine(s) for s in shipments]
    config = MatchConfig(osrm_base_url=settings.OSRM_BASE_URL)

    engine_results = await rank_matches(engine_trip, engine_shipments, config=config)

    saved_matches = []
    shipment_dict = {s.id: s for s in shipments}

    for res in engine_results:
        stmt_existing = select(Match).where(
            Match.trip_id == trip.id,
            Match.shipment_id == res.shipment_id
        )
        existing_match = (await db.execute(stmt_existing)).scalar_one_or_none()
        is_new_high_match = False

        if existing_match:
            match_obj = existing_match
            # Trigger notification if score jumped to >= 70
            if existing_match.score < 70.0 and res.score >= 70.0 and not res.is_rejected:
                is_new_high_match = True
            
            match_obj.score = res.score
            match_obj.route_score = res.breakdown.route_score
            match_obj.capacity_score = res.breakdown.capacity_score
            match_obj.time_score = res.breakdown.time_score
            match_obj.vehicle_score = res.breakdown.vehicle_score
            match_obj.is_rejected = res.is_rejected
            match_obj.rejection_reason = res.rejection_reason
            match_obj.detour_km = res.detour_km
            match_obj.detour_minutes = res.detour_minutes
            match_obj.direct_trip_km = res.direct_trip_km
            match_obj.estimated_revenue = res.estimated_revenue
            match_obj.estimated_cost_shipper = res.estimated_cost_shipper
            match_obj.baseline_full_truck_cost = res.baseline_full_truck_cost
            match_obj.cost_savings_amount = res.cost_savings_amount
            match_obj.cost_savings_pct = res.cost_savings_pct
            match_obj.estimated_co2_saved_kg = res.estimated_co2_saved_kg
            match_obj.is_osrm_fallback = res.is_osrm_fallback
        else:
            match_obj = Match(
                id=str(uuid.uuid4()),
                trip_id=trip.id,
                shipment_id=res.shipment_id,
                score=res.score,
                route_score=res.breakdown.route_score,
                capacity_score=res.breakdown.capacity_score,
                time_score=res.breakdown.time_score,
                vehicle_score=res.breakdown.vehicle_score,
                is_rejected=res.is_rejected,
                rejection_reason=res.rejection_reason,
                detour_km=res.detour_km,
                detour_minutes=res.detour_minutes,
                direct_trip_km=res.direct_trip_km,
                estimated_revenue=res.estimated_revenue,
                estimated_cost_shipper=res.estimated_cost_shipper,
                baseline_full_truck_cost=res.baseline_full_truck_cost,
                cost_savings_amount=res.cost_savings_amount,
                cost_savings_pct=res.cost_savings_pct,
                estimated_co2_saved_kg=res.estimated_co2_saved_kg,
                is_osrm_fallback=res.is_osrm_fallback,
                status=MatchStatus.PENDING
            )
            db.add(match_obj)
            if res.score >= 70.0 and not res.is_rejected:
                is_new_high_match = True

        saved_matches.append(match_obj)

        # Fire notification for high-scoring match
        if is_new_high_match:
            shp = shipment_dict.get(res.shipment_id)
            if shp:
                # Notify Shipper
                await create_notification(
                    db,
                    user_id=shp.shipper_id,
                    notification_type=NotificationType.NEW_MATCH,
                    message=f"High match score ({res.score}/100) found for your shipment ({shp.pickup_name} -> {shp.dest_name}) on truck trip {trip.origin_name} -> {trip.dest_name}. Estimated savings: ₹{res.cost_savings_amount} ({res.cost_savings_pct}%)",
                    related_entity_id=match_obj.id
                )
                # Notify Carrier
                await create_notification(
                    db,
                    user_id=trip.carrier_id,
                    notification_type=NotificationType.NEW_MATCH,
                    message=f"New high-scoring shipment match ({res.score}/100) found for your return trip {trip.origin_name} -> {trip.dest_name} ({shp.weight_kg} kg). Estimated earnings: ₹{res.estimated_revenue}",
                    related_entity_id=match_obj.id
                )

    await db.commit()
    return saved_matches

async def compute_and_save_matches_for_shipment(
    db: AsyncSession,
    shipment_id: str
) -> List[Match]:
    # Fetch shipment
    stmt = select(Shipment).options(selectinload(Shipment.shipper)).where(Shipment.id == shipment_id)
    res = await db.execute(stmt)
    shipment = res.scalar_one_or_none()
    if not shipment:
        raise ValueError(f"Shipment {shipment_id} not found")

    # Fetch all posted trips
    stmt_trips = select(Trip).options(
        selectinload(Trip.truck),
        selectinload(Trip.carrier)
    ).where(Trip.status == TripStatus.POSTED)
    trips = (await db.execute(stmt_trips)).scalars().all()

    if not trips:
        return []

    engine_shipment = shipment_to_engine(shipment)
    config = MatchConfig(osrm_base_url=settings.OSRM_BASE_URL)

    saved_matches = []
    for trip in trips:
        engine_trip = trip_to_engine(trip)
        res = await score_match(engine_trip, engine_shipment, config=config)

        stmt_existing = select(Match).where(
            Match.trip_id == trip.id,
            Match.shipment_id == shipment.id
        )
        existing_match = (await db.execute(stmt_existing)).scalar_one_or_none()
        is_new_high_match = False

        if existing_match:
            match_obj = existing_match
            if existing_match.score < 70.0 and res.score >= 70.0 and not res.is_rejected:
                is_new_high_match = True
            
            match_obj.score = res.score
            match_obj.route_score = res.breakdown.route_score
            match_obj.capacity_score = res.breakdown.capacity_score
            match_obj.time_score = res.breakdown.time_score
            match_obj.vehicle_score = res.breakdown.vehicle_score
            match_obj.is_rejected = res.is_rejected
            match_obj.rejection_reason = res.rejection_reason
            match_obj.detour_km = res.detour_km
            match_obj.detour_minutes = res.detour_minutes
            match_obj.direct_trip_km = res.direct_trip_km
            match_obj.estimated_revenue = res.estimated_revenue
            match_obj.estimated_cost_shipper = res.estimated_cost_shipper
            match_obj.baseline_full_truck_cost = res.baseline_full_truck_cost
            match_obj.cost_savings_amount = res.cost_savings_amount
            match_obj.cost_savings_pct = res.cost_savings_pct
            match_obj.estimated_co2_saved_kg = res.estimated_co2_saved_kg
            match_obj.is_osrm_fallback = res.is_osrm_fallback
        else:
            match_obj = Match(
                id=str(uuid.uuid4()),
                trip_id=trip.id,
                shipment_id=shipment.id,
                score=res.score,
                route_score=res.breakdown.route_score,
                capacity_score=res.breakdown.capacity_score,
                time_score=res.breakdown.time_score,
                vehicle_score=res.breakdown.vehicle_score,
                is_rejected=res.is_rejected,
                rejection_reason=res.rejection_reason,
                detour_km=res.detour_km,
                detour_minutes=res.detour_minutes,
                direct_trip_km=res.direct_trip_km,
                estimated_revenue=res.estimated_revenue,
                estimated_cost_shipper=res.estimated_cost_shipper,
                baseline_full_truck_cost=res.baseline_full_truck_cost,
                cost_savings_amount=res.cost_savings_amount,
                cost_savings_pct=res.cost_savings_pct,
                estimated_co2_saved_kg=res.estimated_co2_saved_kg,
                is_osrm_fallback=res.is_osrm_fallback,
                status=MatchStatus.PENDING
            )
            db.add(match_obj)
            if res.score >= 70.0 and not res.is_rejected:
                is_new_high_match = True

        saved_matches.append(match_obj)

        if is_new_high_match:
            # Notify Shipper
            await create_notification(
                db,
                user_id=shipment.shipper_id,
                notification_type=NotificationType.NEW_MATCH,
                message=f"High match score ({res.score}/100) found for your shipment ({shipment.pickup_name} -> {shipment.dest_name}) on truck trip {trip.origin_name} -> {trip.dest_name}. Estimated savings: ₹{res.cost_savings_amount} ({res.cost_savings_pct}%)",
                related_entity_id=match_obj.id
            )
            # Notify Carrier
            await create_notification(
                db,
                user_id=trip.carrier_id,
                notification_type=NotificationType.NEW_MATCH,
                message=f"New high-scoring shipment match ({res.score}/100) found for your return trip {trip.origin_name} -> {trip.dest_name} ({shipment.weight_kg} kg). Estimated earnings: ₹{res.estimated_revenue}",
                related_entity_id=match_obj.id
            )

    await db.commit()
    return saved_matches

async def get_multi_shipment_consolidation_for_trip(
    db: AsyncSession,
    trip_id: str
):
    stmt = select(Trip).options(selectinload(Trip.truck)).where(Trip.id == trip_id)
    res = await db.execute(stmt)
    trip = res.scalar_one_or_none()
    if not trip:
        raise ValueError(f"Trip {trip_id} not found")

    stmt_shipments = select(Shipment).where(Shipment.status == ShipmentStatus.POSTED)
    shipments = (await db.execute(stmt_shipments)).scalars().all()

    engine_trip = trip_to_engine(trip)
    engine_shipments = [shipment_to_engine(s) for s in shipments]
    config = MatchConfig(osrm_base_url=settings.OSRM_BASE_URL)

    return await find_multi_shipment_consolidation(engine_trip, engine_shipments, config=config)
