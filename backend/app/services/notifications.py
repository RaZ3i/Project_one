from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationType


async def create_notification(
    db: AsyncSession,
    *,
    user_id: UUID,
    type: NotificationType,
    title: str,
    message: str,
    related_lesson_id: UUID | None = None,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        related_lesson_id=related_lesson_id,
    )
    db.add(notification)
    await db.flush()
    return notification
