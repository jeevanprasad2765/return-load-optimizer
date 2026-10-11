import math
from collections import defaultdict
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.user import User, UserRole
from app.models.match import Match, MatchStatus
from app.models.booking import Booking, BookingStatus
from app.models.trip import Trip
from app.models.shipment import Shipment
from app.schemas.dashboard import (
    KeyMetrics, MonthlyTrendPoint, CityPairVolume, ActiveMatchedRoute,
    DashboardMetricsResponse, PlatformImpactResponse
)

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance between two coordinates in kilometers."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

async def calculate_platform_impact(db: AsyncSession) -> PlatformImpactResponse:
    """Calculates global platform-wide totals across all completed/active bookings."""
    stmt = (
        select(Booking)
        .options(
            selectinload(Booking.match),
            selectinload(Booking.trip).selectinload(Trip.truck),
            selectinload(Booking.shipment),
        )
        .where(Booking.status.in_([BookingStatus.IN_TRANSIT, BookingStatus.DELIVERED]))
    )
    res = await db.execute(stmt)
    bookings = res.scalars().all()

    total_km = 0.0
    total_rev = 0.0
    total_saved = 0.0
    total_co2 = 0.0
    utilization_samples = []

    for b in bookings:
        km = 0.0
        if b.match and b.match.direct_trip_km:
            km = b.match.direct_trip_km
        elif b.trip:
            km = haversine_distance_km(b.trip.origin_lat, b.trip.origin_lon, b.trip.dest_lat, b.trip.dest_lon)

        total_km += km
        total_rev += b.agreed_price

        if b.match and b.match.cost_savings_amount and b.match.cost_savings_amount > 0:
            total_saved += b.match.cost_savings_amount
        else:
            total_saved += b.agreed_price * 0.25

        if b.match and b.match.estimated_co2_saved_kg and b.match.estimated_co2_saved_kg > 0:
            total_co2 += b.match.estimated_co2_saved_kg
        else:
            total_co2 += km * 0.105

        truck_cap = 0.0
        if b.trip:
            if b.trip.truck and b.trip.truck.max_capacity_kg > 0:
                truck_cap = b.trip.truck.max_capacity_kg
            elif b.trip.available_capacity_kg > 0:
                truck_cap = b.trip.available_capacity_kg

        if truck_cap > 0 and b.shipment and b.shipment.weight_kg > 0:
            utilization_samples.append(min(100.0, (b.shipment.weight_kg / truck_cap) * 100.0))

    avg_util = round(sum(utilization_samples) / len(utilization_samples), 1) if utilization_samples else 0.0

    return PlatformImpactResponse(
        empty_km_reduced=round(total_km, 1),
        total_revenue_generated=round(total_rev, 2),
        total_cost_saved_shippers=round(total_saved, 2),
        average_vehicle_utilization_pct=avg_util,
        total_co2_saved_kg=round(total_co2, 1),
        total_completed_trips=len(bookings)
    )

async def calculate_dashboard_metrics(db: AsyncSession, current_user: User) -> DashboardMetricsResponse:
    """
    Returns user-scoped ROI and environmental metrics:
    - Carrier: only bookings where booking.carrier_id == current_user.id
    - Shipper: only bookings where booking.shipper_id == current_user.id
    - Count only delivered/in_transit bookings for empty km, revenue, cost saved, CO2.
    - Vehicle utilization: computed only from confirmed/in_transit/delivered bookings (0 for new user).
    - Map & charts: only user's active routes and trends.
    """
    # 1. Fetch user's bookings
    stmt_bookings = (
        select(Booking)
        .options(
            selectinload(Booking.match),
            selectinload(Booking.trip).selectinload(Trip.truck),
            selectinload(Booking.shipment),
        )
    )
    if current_user.role == UserRole.CARRIER:
        stmt_bookings = stmt_bookings.where(Booking.carrier_id == current_user.id)
    else:
        stmt_bookings = stmt_bookings.where(Booking.shipper_id == current_user.id)

    res_bookings = await db.execute(stmt_bookings)
    all_user_bookings = res_bookings.scalars().all()

    # 2. Filter bookings:
    # ROI & Environmental metrics count only delivered / in_transit bookings
    eligible_bookings = [
        b for b in all_user_bookings
        if b.status in [BookingStatus.IN_TRANSIT, BookingStatus.DELIVERED]
    ]

    total_empty_km_reduced = 0.0
    total_revenue = 0.0
    total_cost_saved = 0.0
    total_co2_saved = 0.0

    # Trend aggregation structures
    months_dict = defaultdict(lambda: {"empty_km_reduced": 0.0, "revenue": 0.0, "matches_count": 0, "co2_saved": 0.0})
    routes_dict = defaultdict(lambda: {"trips_count": 0, "volume_tons": 0.0})

    for b in eligible_bookings:
        # Distance
        km = 0.0
        if b.match and b.match.direct_trip_km:
            km = b.match.direct_trip_km
        elif b.trip:
            km = haversine_distance_km(b.trip.origin_lat, b.trip.origin_lon, b.trip.dest_lat, b.trip.dest_lon)
        total_empty_km_reduced += km

        # Revenue & Cost Saved
        if current_user.role == UserRole.CARRIER:
            total_revenue += b.agreed_price
            if b.match and b.match.cost_savings_amount and b.match.cost_savings_amount > 0:
                total_cost_saved += b.match.cost_savings_amount
            else:
                total_cost_saved += b.agreed_price * 0.25
        else:
            # For shipper, revenue earned is 0, cost saved is what they saved
            total_revenue += 0.0
            if b.match and b.match.cost_savings_amount and b.match.cost_savings_amount > 0:
                total_cost_saved += b.match.cost_savings_amount
            else:
                total_cost_saved += b.agreed_price * 0.25

        # CO2 Saved
        if b.match and b.match.estimated_co2_saved_kg and b.match.estimated_co2_saved_kg > 0:
            total_co2_saved += b.match.estimated_co2_saved_kg
        else:
            total_co2_saved += km * 0.105

        # Monthly Trends aggregation
        m_label = b.created_at.strftime("%b") if b.created_at else "Active"
        months_dict[m_label]["empty_km_reduced"] += km
        months_dict[m_label]["revenue"] += b.agreed_price if current_user.role == UserRole.CARRIER else (b.match.cost_savings_amount if b.match else b.agreed_price * 0.25)
        months_dict[m_label]["matches_count"] += 1
        months_dict[m_label]["co2_saved"] += b.match.estimated_co2_saved_kg if (b.match and b.match.estimated_co2_saved_kg > 0) else km * 0.105

        # Route Volumes aggregation
        if b.trip:
            r_label = f"{b.trip.origin_name} → {b.trip.dest_name}"
            routes_dict[r_label]["trips_count"] += 1
            if b.shipment:
                routes_dict[r_label]["volume_tons"] += b.shipment.weight_kg / 1000.0

    # 3. Vehicle utilization: computed from confirmed, in_transit, or delivered bookings
    utilization_bookings = [
        b for b in all_user_bookings
        if b.status in [BookingStatus.CONFIRMED, BookingStatus.IN_TRANSIT, BookingStatus.DELIVERED]
    ]
    utilization_samples = []
    for b in utilization_bookings:
        truck_cap = 0.0
        if b.trip:
            if b.trip.truck and b.trip.truck.max_capacity_kg > 0:
                truck_cap = b.trip.truck.max_capacity_kg
            elif b.trip.available_capacity_kg > 0:
                truck_cap = b.trip.available_capacity_kg

        if truck_cap > 0 and b.shipment and b.shipment.weight_kg > 0:
            utilization_samples.append(min(100.0, (b.shipment.weight_kg / truck_cap) * 100.0))

    avg_utilization = round(sum(utilization_samples) / len(utilization_samples), 1) if utilization_samples else 0.0

    # 4. Active matched routes for map: scoped strictly to user
    active_routes: List[ActiveMatchedRoute] = []
    if current_user.role == UserRole.CARRIER:
        stmt_matches = (
            select(Match)
            .join(Trip, Match.trip_id == Trip.id)
            .options(
                selectinload(Match.trip),
                selectinload(Match.shipment)
            )
            .where(
                Trip.carrier_id == current_user.id,
                Match.is_rejected == False,
                Match.status.in_([MatchStatus.PENDING, MatchStatus.ACCEPTED])
            )
        )
    else:
        stmt_matches = (
            select(Match)
            .join(Shipment, Match.shipment_id == Shipment.id)
            .options(
                selectinload(Match.trip),
                selectinload(Match.shipment)
            )
            .where(
                Shipment.shipper_id == current_user.id,
                Match.is_rejected == False,
                Match.status.in_([MatchStatus.PENDING, MatchStatus.ACCEPTED])
            )
        )

    user_matches = (await db.execute(stmt_matches)).scalars().all()
    for m in user_matches:
        if m.trip and m.shipment:
            active_routes.append(
                ActiveMatchedRoute(
                    match_id=m.id,
                    trip_id=m.trip_id,
                    shipment_id=m.shipment_id,
                    origin=m.trip.origin_name,
                    destination=m.trip.dest_name,
                    pickup=m.shipment.pickup_name,
                    dropoff=m.shipment.dest_name,
                    score=m.score,
                    detour_km=m.detour_km,
                    status=m.status.value,
                    origin_coords=[m.trip.origin_lat, m.trip.origin_lon],
                    dest_coords=[m.trip.dest_lat, m.trip.dest_lon],
                    pickup_coords=[m.shipment.pickup_lat, m.shipment.pickup_lon],
                    dropoff_coords=[m.shipment.dest_lat, m.shipment.dest_lon]
                )
            )

    # 5. Build response objects
    metrics = KeyMetrics(
        empty_km_reduced=round(total_empty_km_reduced, 1),
        additional_revenue_generated=round(total_revenue, 2),
        cost_saved_for_shippers=round(total_cost_saved, 2),
        average_vehicle_utilization_pct=avg_utilization,
        estimated_co2_saved_kg=round(total_co2_saved, 1)
    )

    monthly_trends = [
        MonthlyTrendPoint(
            month=m,
            empty_km_reduced=round(vals["empty_km_reduced"], 1),
            revenue=round(vals["revenue"], 1),
            matches_count=vals["matches_count"],
            co2_saved=round(vals["co2_saved"], 1)
        )
        for m, vals in months_dict.items()
    ]

    route_volumes = [
        CityPairVolume(
            route=r,
            trips_count=vals["trips_count"],
            volume_tons=round(vals["volume_tons"], 1)
        )
        for r, vals in routes_dict.items()
    ]

    # Global platform metrics
    platform_impact = await calculate_platform_impact(db)

    return DashboardMetricsResponse(
        metrics=metrics,
        monthly_trends=monthly_trends,
        route_volumes=route_volumes,
        active_matched_routes=active_routes,
        platform_metrics=platform_impact
    )
