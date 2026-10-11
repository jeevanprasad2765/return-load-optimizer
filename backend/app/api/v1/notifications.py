from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.services.notification_service import (
    get_user_notifications, mark_notification_read, mark_all_notifications_read
)

router = APIRouter()

@router.get("", response_model=List[NotificationResponse])
async def list_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves notifications for the current authenticated user."""
    return await get_user_notifications(db, current_user.id)

@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def read_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    notif = await mark_notification_read(db, notification_id, current_user.id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notif

@router.post("/read-all", status_code=status.HTTP_200_OK)
async def read_all_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await mark_all_notifications_read(db, current_user.id)
    return {"message": "All notifications marked as read"}
