import enum
from datetime import datetime, timezone
from sqlalchemy import String, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, UTCDateTime

class MatchStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class Match(Base):
    __tablename__ = "matches"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    trip_id: Mapped[str] = mapped_column(String, ForeignKey("trips.id"), nullable=False)
    shipment_id: Mapped[str] = mapped_column(String, ForeignKey("shipments.id"), nullable=False)

    score: Mapped[float] = mapped_column(Float, nullable=False)
    route_score: Mapped[float] = mapped_column(Float, default=0.0)
    capacity_score: Mapped[float] = mapped_column(Float, default=0.0)
    time_score: Mapped[float] = mapped_column(Float, default=0.0)
    vehicle_score: Mapped[float] = mapped_column(Float, default=0.0)

    is_rejected: Mapped[bool] = mapped_column(Boolean, default=False)
    rejection_reason: Mapped[str] = mapped_column(Text, nullable=True)

    detour_km: Mapped[float] = mapped_column(Float, default=0.0)
    detour_minutes: Mapped[float] = mapped_column(Float, default=0.0)
    direct_trip_km: Mapped[float] = mapped_column(Float, default=0.0)

    estimated_revenue: Mapped[float] = mapped_column(Float, default=0.0)
    estimated_cost_shipper: Mapped[float] = mapped_column(Float, default=0.0)
    baseline_full_truck_cost: Mapped[float] = mapped_column(Float, default=0.0)
    cost_savings_amount: Mapped[float] = mapped_column(Float, default=0.0)
    cost_savings_pct: Mapped[float] = mapped_column(Float, default=0.0)
    estimated_co2_saved_kg: Mapped[float] = mapped_column(Float, default=0.0)
    is_osrm_fallback: Mapped[bool] = mapped_column(Boolean, default=False)

    status: Mapped[MatchStatus] = mapped_column(SQLEnum(MatchStatus), default=MatchStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    trip: Mapped["Trip"] = relationship("Trip", back_populates="matches")
    shipment: Mapped["Shipment"] = relationship("Shipment", back_populates="matches")
    booking: Mapped["Booking"] = relationship("Booking", back_populates="match", uselist=False, cascade="all, delete-orphan")
