from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.schemas.common import UTCDateTime
from app.models.notification import NotificationType

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    type: NotificationType
    message: str
    related_entity_id: Optional[str] = None
    is_read: bool
    created_at: UTCDateTime

    model_config = ConfigDict(from_attributes=True)
