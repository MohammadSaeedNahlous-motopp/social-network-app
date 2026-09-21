from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from db.user import get_user_by_id
from models.enums import NotificationType
from models.notification import DBNotification
from schemas.notification import NotificationCreate


def create_notification(request: NotificationCreate, db: Session):
    searched_user = get_user_by_id(db, request.user_id)

    if not searched_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found!",
        )

    new_notification = DBNotification(
        user_id=request.user_id,
        message=request.message,
        type=request.type,
    )

    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)

    return new_notification


def get_all_notifications(user_id: int, db: Session):
    all_notifications = db.query(DBNotification).filter(
        DBNotification.user_id == user_id
    )

    return all_notifications


def mark_all_notifications_as_read(user_id: int, db: Session):
    all_notifications = get_all_notifications(user_id, db)

    for notification in all_notifications:
        notification.is_read = True

    db.commit()

    return all_notifications
