from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, UTCDateTime

class Truck(Base):
    __tablename__ = "trucks"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    carrier_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    registration_number: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    vehicle_type: Mapped[str] = mapped_column(String, nullable=False)  # open, closed, refrigerated, flatbed, container
    max_capacity_kg: Mapped[float] = mapped_column(Float, nullable=False)
    model_name: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    carrier: Mapped["User"] = relationship("User", back_populates="trucks")
    trips: Mapped[list["Trip"]] = relationship("Trip", back_populates="truck", cascade="all, delete-orphan")
