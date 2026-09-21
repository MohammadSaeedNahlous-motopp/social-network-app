from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from db.friend import is_friend_with
from db.notification import create_notification
from models.enums import RequestStatus, NotificationType
from models.friend_request import DBFriendRequest
from models.user import DBUser
from models.friend import DBFriend
from schemas.friend_request import FriendRequestBase
from schemas.notification import NotificationCreate
from websocket.connection_manager import manager
from service.permissions import can_change_friend_request_status


def get_user_pending_friend_requests(user_id: int, db: Session):
    pending_friend_requests = db.query(DBFriendRequest).filter(
        DBFriendRequest.receiver_id == user_id,
        DBFriendRequest.status == RequestStatus.pending,
    )

    return pending_friend_requests


async def create_friend_request(
    request: FriendRequestBase,
    user_id: int,
    user_name: str,
    db: Session,
):
    # Check that the user is not sending a request to themselves
    if user_id == request.receiver_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot send a friend request to yourself!",
        )

    # Check that the receiver exists and is active
    receiver = (
        db.query(DBUser)
        .filter(
            DBUser.id == request.receiver_id,
            DBUser.is_active,
        )
        .first()
    )

    if not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found!",
        )

    # Check for an existing pending request in either direction
    existing_request = (
        db.query(DBFriendRequest)
        .filter(
            (
                (DBFriendRequest.sender_id == user_id)
                & (DBFriendRequest.receiver_id == request.receiver_id)
            )
            | (
                (DBFriendRequest.sender_id == request.receiver_id)
                & (DBFriendRequest.receiver_id == user_id)
            ),
            DBFriendRequest.status == RequestStatus.pending,
        )
        .first()
    )

    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A pending friend request already exists between these users!",
        )

    # Check for an existing friendship in either direction
    are_friends = is_friend_with(user_id, request.receiver_id, db)

    if are_friends:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can not send friend request to a friend",
        )
    new_friend_request = DBFriendRequest(
        sender_id=user_id,
        receiver_id=request.receiver_id,
    )

    db.add(new_friend_request)
    db.commit()
    db.refresh(new_friend_request)

    notification = create_notification(
        NotificationCreate(
            user_id=request.receiver_id,
            type=NotificationType.new_friend_request,
            message=f"{user_name} Sent A Friend Request!",
        ),
        db,
    )

    await manager.send_to_user(
        request.receiver_id,
        {
            "type": "notification",
            "id": notification.id,
            "notification_type": notification.type,
            "message": notification.message,
        },
    )

    return new_friend_request


def change_friend_request_status(
    friend_request_id: int,
    user_id: int,
    new_status: RequestStatus,
    db: Session,
):
    searched_friend_request = (
        db.query(DBFriendRequest)
        .filter(
            DBFriendRequest.id == friend_request_id,
        )
        .first()
    )

    if not searched_friend_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friend request not found!",
        )

    if not can_change_friend_request_status(
        user_id=user_id,
        friend_request=searched_friend_request,
        cancellation=new_status is RequestStatus.canceled,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied!",
        )

    if searched_friend_request.status != RequestStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This friend request has already been processed!",
        )

    if new_status in (
        RequestStatus.canceled,
        RequestStatus.declined,
    ):
        db.delete(searched_friend_request)

    elif new_status == RequestStatus.accepted:
        new_friendship = DBFriend(
            user_id=searched_friend_request.sender_id,
            friend_id=searched_friend_request.receiver_id,
        )

        db.add(new_friendship)
        db.delete(searched_friend_request)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid friend request status!",
        )

    db.commit()

    return True
