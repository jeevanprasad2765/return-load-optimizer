import enum
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, UTCDateTime

class NotificationType(str, enum.Enum):
    NEW_MATCH = "new_match"
    BOOKING_REQUEST = "booking_request"
    BOOKING_STATUS_CHANGE = "booking_status_change"

class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    type: Mapped[NotificationType] = mapped_column(SQLEnum(NotificationType), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    related_entity_id: Mapped[str] = mapped_column(String, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user: Mapped["User"] = relationship("User", backref="notifications")
