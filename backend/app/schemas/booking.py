from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from app.models.booking import BookingStatus
from app.schemas.match import MatchResponse
from app.schemas.trip import TripResponse
from app.schemas.shipment import ShipmentResponse
from app.schemas.common import UTCDateTime

class BookingCreate(BaseModel):
    match_id: Optional[str] = None
    trip_id: Optional[str] = None
    shipment_id: Optional[str] = None
    agreed_price: Optional[float] = None

class BookingStatusUpdate(BaseModel):
    status: BookingStatus
    agreed_price: Optional[float] = None

class BookingResponse(BaseModel):
    id: str
    match_id: Optional[str] = None
    trip_id: str
    shipment_id: str
    carrier_id: str
    shipper_id: str
    agreed_price: float
    status: BookingStatus
    created_at: UTCDateTime
    updated_at: UTCDateTime
    match: Optional[MatchResponse] = None
    trip: Optional[TripResponse] = None
    shipment: Optional[ShipmentResponse] = None

    model_config = ConfigDict(from_attributes=True)
