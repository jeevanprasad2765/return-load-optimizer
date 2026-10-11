import enum
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, UTCDateTime

class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    match_id: Mapped[str] = mapped_column(String, ForeignKey("matches.id"), nullable=True)
    trip_id: Mapped[str] = mapped_column(String, ForeignKey("trips.id"), nullable=False)
    shipment_id: Mapped[str] = mapped_column(String, ForeignKey("shipments.id"), nullable=False)
    carrier_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    shipper_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)

    agreed_price: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[BookingStatus] = mapped_column(SQLEnum(BookingStatus), default=BookingStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    match: Mapped["Match"] = relationship("Match", back_populates="booking", uselist=False)
    trip: Mapped["Trip"] = relationship("Trip")
    shipment: Mapped["Shipment"] = relationship("Shipment")
    carrier: Mapped["User"] = relationship("User", foreign_keys=[carrier_id])
    shipper: Mapped["User"] = relationship("User", foreign_keys=[shipper_id])
