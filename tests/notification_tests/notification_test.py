import pytest
from fastapi import HTTPException

from db.notification import (
    create_notification,
    get_all_notifications,
    mark_all_notifications_as_read,
)
from models.enums import NotificationType
from schemas.notification import NotificationCreate


def test_create_notification(db, create_test_user):
    user = create_test_user(
        email="notification_user@example.com",
        name="Notification User",
    )

    notification = create_notification(
        NotificationCreate(
            user_id=user.id,
            type=NotificationType.new_friend_request,
            message="John Doe Sent A Friend Request!",
        ),
        db,
    )

    assert notification.id is not None
    assert notification.user_id == user.id
    assert notification.type == NotificationType.new_friend_request
    assert notification.message == "John Doe Sent A Friend Request!"
    assert notification.is_read is False


def test_create_notification_user_not_found(db):
    with pytest.raises(HTTPException) as exc_info:
        create_notification(
            NotificationCreate(
                user_id=999999,
                type=NotificationType.new_friend_request,
                message="John Doe Sent A Friend Request!",
            ),
            db,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found!"


def test_get_all_notifications(db, create_test_user):
    user = create_test_user(
        email="notification_list@example.com",
        name="Notification User",
    )

    create_notification(
        NotificationCreate(
            user_id=user.id,
            type=NotificationType.new_friend_request,
            message="John Doe Sent A Friend Request!",
        ),
        db,
    )

    create_notification(
        NotificationCreate(
            user_id=user.id,
            type=NotificationType.new_message,
            message="Hello, how are you?",
        ),
        db,
    )

    notifications = get_all_notifications(user.id, db)

    assert notifications.count() == 2


def test_get_all_notifications_returns_empty_for_user(db, create_test_user):
    user = create_test_user(
        email="no_notifications@example.com",
        name="No Notifications",
    )

    notifications = get_all_notifications(user.id, db)

    assert notifications.count() == 0


def test_get_all_notifications_only_returns_users_notifications(
    db,
    create_test_user,
):
    user1 = create_test_user(
        email="notification_user1@example.com",
        name="User One",
    )

    user2 = create_test_user(
        email="notification_user2@example.com",
        name="User Two",
    )

    create_notification(
        NotificationCreate(
            user_id=user1.id,
            type=NotificationType.new_message,
            message="Message for user one",
        ),
        db,
    )

    create_notification(
        NotificationCreate(
            user_id=user2.id,
            type=NotificationType.new_message,
            message="Message for user two",
        ),
        db,
    )

    notifications = get_all_notifications(user1.id, db)

    assert notifications.count() == 1

    notification = notifications.first()

    assert notification.user_id == user1.id
    assert notification.message == "Message for user one"


# Not working Yet
# def test_mark_all_notifications_as_read(db, create_test_user):
#     user = create_test_user(
#         email="mark_notifications@example.com",
#         name="Notification User",
#     )
#
#     create_notification(
#         NotificationCreate(
#             user_id=user.id,
#             type=NotificationType.new_friend_request,
#             message="John Doe Sent A Friend Request!",
#         ),
#         db,
#     )
#
#     create_notification(
#         NotificationCreate(
#             user_id=user.id,
#             type=NotificationType.new_message,
#             message="Hello!",
#         ),
#         db,
#     )
#
#     notifications = mark_all_notifications_as_read(user.id, db)
#
#     assert len(notifications) == 2
#     assert all(
#         notification.is_read is True
#         for notification in notifications
#     )
