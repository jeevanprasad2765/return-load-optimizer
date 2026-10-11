from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from app.schemas.common import UTCDateTime
from app.models.user import UserRole

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str
    company_name: str
    phone: Optional[str] = None
    role: UserRole

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    company_name: str
    phone: Optional[str] = None
    role: UserRole
    created_at: UTCDateTime

    model_config = ConfigDict(from_attributes=True)

Token.model_rebuild()
