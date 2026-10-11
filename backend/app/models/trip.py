from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, UTCDateTime
import enum

class TripStatus(str, enum.Enum):
    POSTED = "posted"
    MATCHED = "matched"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    carrier_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    truck_id: Mapped[str] = mapped_column(String, ForeignKey("trucks.id"), nullable=False)
    
    origin_name: Mapped[str] = mapped_column(String, nullable=False)
    origin_lat: Mapped[float] = mapped_column(Float, nullable=False)
    origin_lon: Mapped[float] = mapped_column(Float, nullable=False)

    dest_name: Mapped[str] = mapped_column(String, nullable=False)
    dest_lat: Mapped[float] = mapped_column(Float, nullable=False)
    dest_lon: Mapped[float] = mapped_column(Float, nullable=False)

    departure_time: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)
    available_capacity_kg: Mapped[float] = mapped_column(Float, nullable=False)
    cost_per_km: Mapped[float] = mapped_column(Float, default=15.0)
    status: Mapped[TripStatus] = mapped_column(SQLEnum(TripStatus), default=TripStatus.POSTED)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    carrier: Mapped["User"] = relationship("User", back_populates="trips")
    truck: Mapped["Truck"] = relationship("Truck", back_populates="trips")
    matches: Mapped[list["Match"]] = relationship("Match", back_populates="trip", cascade="all, delete-orphan")
