from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, UTCDateTime
import enum

class UserRole(str, enum.Enum):
    CARRIER = "carrier"
    SHIPPER = "shipper"

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    company_name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=True)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    trucks: Mapped[list["Truck"]] = relationship("Truck", back_populates="carrier", cascade="all, delete-orphan")
    trips: Mapped[list["Trip"]] = relationship("Trip", back_populates="carrier", cascade="all, delete-orphan")
    shipments: Mapped[list["Shipment"]] = relationship("Shipment", back_populates="shipper", cascade="all, delete-orphan")
