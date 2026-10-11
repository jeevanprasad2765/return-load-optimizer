from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, UTCDateTime
import enum

class ShipmentStatus(str, enum.Enum):
    POSTED = "posted"
    BOOKING_REQUESTED = "booking_requested"
    MATCHED = "matched"
    BOOKED = "booked"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    shipper_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)

    pickup_name: Mapped[str] = mapped_column(String, nullable=False)
    pickup_lat: Mapped[float] = mapped_column(Float, nullable=False)
    pickup_lon: Mapped[float] = mapped_column(Float, nullable=False)

    dest_name: Mapped[str] = mapped_column(String, nullable=False)
    dest_lat: Mapped[float] = mapped_column(Float, nullable=False)
    dest_lon: Mapped[float] = mapped_column(Float, nullable=False)

    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    goods_type: Mapped[str] = mapped_column(String, nullable=False)
    required_vehicle_type: Mapped[str] = mapped_column(String, nullable=True)

    pickup_window_start: Mapped[datetime] = mapped_column(UTCDateTime, nullable=True)
    pickup_window_end: Mapped[datetime] = mapped_column(UTCDateTime, nullable=True)
    delivery_deadline: Mapped[datetime] = mapped_column(UTCDateTime, nullable=True)

    status: Mapped[ShipmentStatus] = mapped_column(SQLEnum(ShipmentStatus), default=ShipmentStatus.POSTED)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    shipper: Mapped["User"] = relationship("User", back_populates="shipments")
    matches: Mapped[list["Match"]] = relationship("Match", back_populates="shipment", cascade="all, delete-orphan")
