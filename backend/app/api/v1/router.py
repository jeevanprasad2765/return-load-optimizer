from fastapi import APIRouter
from app.api.v1 import auth, trucks, trips, shipments, matches, bookings, dashboard, notifications

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(trucks.router, prefix="/trucks", tags=["Trucks"])
api_router.include_router(trips.router, prefix="/trips", tags=["Trips"])
api_router.include_router(shipments.router, prefix="/shipments", tags=["Shipments"])
api_router.include_router(matches.router, prefix="/matches", tags=["Matches"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
