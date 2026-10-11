from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from app.schemas.common import UTCDateTime
import re

class TruckCreate(BaseModel):
    registration_number: str = Field(..., min_length=3, max_length=20)
    vehicle_type: str  # open, closed, refrigerated, flatbed, container
    max_capacity_kg: float = Field(..., gt=0)
    model_name: Optional[str] = None

    @field_validator('registration_number')
    @classmethod
    def validate_registration_number(cls, v: str) -> str:
        clean_v = v.strip().upper()
        if not re.search(r'\d{4}$', clean_v):
            raise ValueError("Registration number must end with 4 digits (e.g. TN-37-R-4085)")
        return clean_v

class TruckUpdate(BaseModel):
    vehicle_type: Optional[str] = None
    max_capacity_kg: Optional[float] = Field(None, gt=0)
    model_name: Optional[str] = None

class TruckResponse(BaseModel):
    id: str
    carrier_id: str
    registration_number: str
    vehicle_type: str
    max_capacity_kg: float
    model_name: Optional[str] = None
    created_at: UTCDateTime

    model_config = ConfigDict(from_attributes=True)
