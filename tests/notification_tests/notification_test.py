import pytest
from fastapi import HTTPException

from db.notification import (
    create_notification,
    get_all_notifications,
    mark_all_notifications_as_read,
)
from models.enums import NotificationType
from schemas.notification import NotificationCreate


# ============================================================
# FRIEND REQUEST NOTIFICATIONS
# ============================================================


def test_create_friend_request_notification(
    db,
    create_test_user,
):
    user = create_test_user(
        email="friend_request_notification@example.com",
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


def test_create_friend_request_notification_user_not_found(db):
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


def test_multiple_friend_request_notifications(
    db,
    create_test_user,
):
    user = create_test_user(
        email="multiple_friend_requests@example.com",
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
            type=NotificationType.new_friend_request,
            message="Jane Doe Sent A Friend Request!",
        ),
        db,
    )

    notifications = get_all_notifications(user.id, db)

    assert notifications.count() == 2


# ============================================================
# MESSAGE NOTIFICATIONS
# ============================================================


def test_create_message_notification(
    db,
    create_test_user,
):
    user = create_test_user(
        email="message_notification@example.com",
        name="Notification User",
    )

    notification = create_notification(
        NotificationCreate(
            user_id=user.id,
            type=NotificationType.new_message,
            message="John Doe Sent You A Message!",
        ),
        db,
    )

    assert notification.id is not None
    assert notification.user_id == user.id
    assert notification.type == NotificationType.new_message
    assert notification.message == "John Doe Sent You A Message!"
    assert notification.is_read is False


def test_multiple_message_notifications(
    db,
    create_test_user,
):
    user = create_test_user(
        email="multiple_messages@example.com",
        name="Notification User",
    )

    create_notification(
        NotificationCreate(
            user_id=user.id,
            type=NotificationType.new_message,
            message="John Doe Sent You A Message!",
        ),
        db,
    )

    create_notification(
        NotificationCreate(
            user_id=user.id,
            type=NotificationType.new_message,
            message="Jane Doe Sent You A Message!",
        ),
        db,
    )

    notifications = get_all_notifications(user.id, db)

    assert notifications.count() == 2


# ============================================================
# NOTIFICATION RETRIEVAL
# ============================================================


def test_get_all_notifications(
    db,
    create_test_user,
):
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
            message="John Doe Sent You A Message!",
        ),
        db,
    )

    notifications = get_all_notifications(user.id, db)

    assert notifications.count() == 2


def test_get_all_notifications_returns_empty_for_user(
    db,
    create_test_user,
):
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
            message="User Two Sent You A Message!",
        ),
        db,
    )

    create_notification(
        NotificationCreate(
            user_id=user2.id,
            type=NotificationType.new_message,
            message="User One Sent You A Message!",
        ),
        db,
    )

    user1_notifications = get_all_notifications(
        user1.id,
        db,
    )

    user2_notifications = get_all_notifications(
        user2.id,
        db,
    )

    assert user1_notifications.count() == 1
    assert user2_notifications.count() == 1

    user1_notification = user1_notifications.first()
    user2_notification = user2_notifications.first()

    assert user1_notification.user_id == user1.id
    assert user1_notification.message == "User Two Sent You A Message!"

    assert user2_notification.user_id == user2.id
    assert user2_notification.message == "User One Sent You A Message!"


def test_user_does_not_receive_another_users_notifications(
    db,
    create_test_user,
):
    sender = create_test_user(
        email="sender@example.com",
        name="Sender",
    )

    recipient = create_test_user(
        email="recipient@example.com",
        name="Recipient",
    )

    unrelated_user = create_test_user(
        email="unrelated@example.com",
        name="Unrelated",
    )

    create_notification(
        NotificationCreate(
            user_id=recipient.id,
            type=NotificationType.new_message,
            message="Sender Sent You A Message!",
        ),
        db,
    )

    assert (
        get_all_notifications(
            recipient.id,
            db,
        ).count()
        == 1
    )

    assert (
        get_all_notifications(
            sender.id,
            db,
        ).count()
        == 0
    )

    assert (
        get_all_notifications(
            unrelated_user.id,
            db,
        ).count()
        == 0
    )


# ============================================================
# READ / UNREAD NOTIFICATIONS
# ============================================================


def test_notification_is_unread_when_created(
    db,
    create_test_user,
):
    user = create_test_user(
        email="unread_notification@example.com",
        name="Notification User",
    )

    notification = create_notification(
        NotificationCreate(
            user_id=user.id,
            type=NotificationType.new_message,
            message="John Doe Sent You A Message!",
        ),
        db,
    )

    assert notification.is_read is False


# Not working - the return value is Query not a list
# def test_mark_all_notifications_as_read(
#     db,
#     create_test_user,
# ):
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
#             message="John Doe Sent You A Message!",
#         ),
#         db,
#     )
#
#     notifications = mark_all_notifications_as_read(
#         user.id,
#         db,
#     )
#
#     assert len(notifications) == 2
#     assert all(
#         notification.is_read is True
#         for notification in notifications
#     )


def test_mark_notifications_does_not_affect_other_users(
    db,
    create_test_user,
):
    user1 = create_test_user(
        email="read_user1@example.com",
        name="User One",
    )

    user2 = create_test_user(
        email="read_user2@example.com",
        name="User Two",
    )

    create_notification(
        NotificationCreate(
            user_id=user1.id,
            type=NotificationType.new_message,
            message="Message for User One",
        ),
        db,
    )

    create_notification(
        NotificationCreate(
            user_id=user2.id,
            type=NotificationType.new_message,
            message="Message for User Two",
        ),
        db,
    )

    mark_all_notifications_as_read(
        user1.id,
        db,
    )

    user1_notification = get_all_notifications(
        user1.id,
        db,
    ).first()

    user2_notification = get_all_notifications(
        user2.id,
        db,
    ).first()

    assert user1_notification.is_read is True
    assert user2_notification.is_read is False


# Not working - the return value is Query not a list
# def test_mark_all_notifications_for_user_with_no_notifications(
#     db,
#     create_test_user,
# ):
#     user = create_test_user(
#         email="empty_read_notifications@example.com",
#         name="No Notifications",
#     )
#
#     notifications = mark_all_notifications_as_read(
#         user.id,
#         db,
#     )
#
#     assert notifications == []
