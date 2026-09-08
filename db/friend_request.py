from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.enums import FriendRequestStatus
from models.friend_request import DBFriendRequest
from models.user import DBUser
from models.friend import DBFriend
from schemas.friend_request import FriendRequestBase


def get_user_pending_friend_requests(user_id: int, db: Session):
    pending_friend_requests = db.query(DBFriendRequest).filter(
        DBFriendRequest.receiver_id == user_id,
        DBFriendRequest.status == FriendRequestStatus.pending,
    )

    return pending_friend_requests


def create_friend_request(
    request: FriendRequestBase,
    user_id: int,
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
            DBFriendRequest.status == FriendRequestStatus.pending,
        )
        .first()
    )

    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A pending friend request already exists between these users!",
        )

    new_friend_request = DBFriendRequest(
        sender_id=user_id,
        receiver_id=request.receiver_id,
    )

    db.add(new_friend_request)
    db.commit()
    db.refresh(new_friend_request)

    return new_friend_request


def change_friend_request_status(
    friend_request_id: int,
    user_id: int,
    new_status: FriendRequestStatus,
    db: Session,
):
    if new_status == FriendRequestStatus.canceled:
        searched_friend_request = (
            db.query(DBFriendRequest)
            .filter(
                DBFriendRequest.id == friend_request_id,
                DBFriendRequest.sender_id == user_id,
            )
            .first()
        )
    elif new_status in (
        FriendRequestStatus.accepted,
        FriendRequestStatus.declined,
    ):
        searched_friend_request = (
            db.query(DBFriendRequest)
            .filter(
                DBFriendRequest.id == friend_request_id,
                DBFriendRequest.receiver_id == user_id,
            )
            .first()
        )

    if not searched_friend_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friend request not found!",
        )

    if searched_friend_request.status != FriendRequestStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This friend request has already been processed!",
        )

    searched_friend_request.status = new_status
    if new_status == FriendRequestStatus.accepted:
        new_friendship = DBFriend(
            user_id=searched_friend_request.sender_id,
            friend_id=searched_friend_request.receiver_id,
        )
        db.add(new_friendship)
        db.commit()
        db.refresh(new_friendship)

    db.commit()
    db.refresh(searched_friend_request)

    return searched_friend_request
