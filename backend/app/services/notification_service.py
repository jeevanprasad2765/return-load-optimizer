import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.notification import Notification, NotificationType

async def create_notification(
    db: AsyncSession,
    user_id: str,
    notification_type: NotificationType,
    message: str,
    related_entity_id: Optional[str] = None
) -> Notification:
    notif = Notification(
        id=str(uuid.uuid4()),
        user_id=user_id,
        type=notification_type,
        message=message,
        related_entity_id=related_entity_id,
        is_read=False
    )
    db.add(notif)
    await db.commit()
    await db.refresh(notif)
    return notif

async def get_user_notifications(
    db: AsyncSession,
    user_id: str,
    limit: int = 20
) -> List[Notification]:
    stmt = (
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
    )
    res = await db.execute(stmt)
    return res.scalars().all()

async def mark_notification_read(
    db: AsyncSession,
    notification_id: str,
    user_id: str
) -> Optional[Notification]:
    stmt = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == user_id
    )
    res = await db.execute(stmt)
    notif = res.scalar_one_or_none()
    if notif:
        notif.is_read = True
        await db.commit()
        await db.refresh(notif)
    return notif

async def mark_all_notifications_read(
    db: AsyncSession,
    user_id: str
):
    stmt = (
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read == False)
        .values(is_read=True)
    )
    await db.execute(stmt)
    await db.commit()
