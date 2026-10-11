from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from app.models.shipment import ShipmentStatus
from app.schemas.common import UTCDateTime, OptionalUTCDateTime

class ShipmentCreate(BaseModel):
    pickup_name: str
    pickup_lat: float = Field(..., ge=-90, le=90)
    pickup_lon: float = Field(..., ge=-180, le=180)
    dest_name: str
    dest_lat: float = Field(..., ge=-90, le=90)
    dest_lon: float = Field(..., ge=-180, le=180)
    weight_kg: float = Field(..., gt=0)
    goods_type: str
    required_vehicle_type: Optional[str] = None
    pickup_window_start: OptionalUTCDateTime = None
    pickup_window_end: OptionalUTCDateTime = None
    delivery_deadline: OptionalUTCDateTime = None

class ShipmentUpdate(BaseModel):
    weight_kg: Optional[float] = Field(None, gt=0)
    goods_type: Optional[str] = None
    required_vehicle_type: Optional[str] = None
    pickup_window_start: OptionalUTCDateTime = None
    pickup_window_end: OptionalUTCDateTime = None
    delivery_deadline: OptionalUTCDateTime = None
    status: Optional[ShipmentStatus] = None

class ShipmentResponse(BaseModel):
    id: str
    shipper_id: str
    pickup_name: str
    pickup_lat: float
    pickup_lon: float
    dest_name: str
    dest_lat: float
    dest_lon: float
    weight_kg: float
    goods_type: str
    required_vehicle_type: Optional[str] = None
    pickup_window_start: OptionalUTCDateTime = None
    pickup_window_end: OptionalUTCDateTime = None
    delivery_deadline: OptionalUTCDateTime = None
    status: ShipmentStatus
    created_at: UTCDateTime

    model_config = ConfigDict(from_attributes=True)
