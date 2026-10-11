from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from app.models.trip import TripStatus
from app.schemas.common import UTCDateTime, OptionalUTCDateTime

class TripCreate(BaseModel):
    truck_id: str
    origin_name: str
    origin_lat: float = Field(..., ge=-90, le=90)
    origin_lon: float = Field(..., ge=-180, le=180)
    dest_name: str
    dest_lat: float = Field(..., ge=-90, le=90)
    dest_lon: float = Field(..., ge=-180, le=180)
    departure_time: UTCDateTime
    available_capacity_kg: float = Field(..., gt=0)
    cost_per_km: float = Field(15.0, gt=0)

class TripUpdate(BaseModel):
    departure_time: OptionalUTCDateTime = None
    available_capacity_kg: Optional[float] = Field(None, gt=0)
    cost_per_km: Optional[float] = Field(None, gt=0)
    status: Optional[TripStatus] = None

from app.schemas.auth import UserResponse
from app.schemas.truck import TruckResponse

class TripResponse(BaseModel):
    id: str
    carrier_id: str
    truck_id: str
    origin_name: str
    origin_lat: float
    origin_lon: float
    dest_name: str
    dest_lat: float
    dest_lon: float
    departure_time: UTCDateTime
    available_capacity_kg: float
    cost_per_km: float
    status: TripStatus
    created_at: UTCDateTime
    carrier: Optional[UserResponse] = None
    truck: Optional[TruckResponse] = None

    model_config = ConfigDict(from_attributes=True)
