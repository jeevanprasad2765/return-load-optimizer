from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.dashboard import DashboardMetricsResponse, PlatformImpactResponse
from app.services.dashboard_service import calculate_dashboard_metrics, calculate_platform_impact

router = APIRouter()

@router.get("/metrics", response_model=DashboardMetricsResponse)
async def get_dashboard_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns user-scoped ROI and environmental metrics:
    - Scoped strictly to the authenticated user from the JWT.
    - Counts only in_transit and delivered bookings for empty km, revenue, cost saved, CO2.
    - Vehicle utilization computed only from confirmed/in_transit/delivered bookings (0 for new accounts).
    - Map routes and analytics trends scoped to user's activity.
    """
    return await calculate_dashboard_metrics(db, current_user)

@router.get("/platform-impact", response_model=PlatformImpactResponse)
async def get_platform_impact(
    db: AsyncSession = Depends(get_db)
):
    """
    Returns global platform-wide totals across all delivered/in_transit freight bookings.
    Publicly accessible aggregate overview of platform network savings.
    """
    return await calculate_platform_impact(db)
