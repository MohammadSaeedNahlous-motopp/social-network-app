from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from db.friend import is_friend_with
from db.group_member import is_group_member
from db.notification import create_notification
from models.enums import RequestStatus, NotificationType
from models.friend_request import DBFriendRequest
from models.group_member import DBGroupMember
from models.group_request import DBGroupRequest
from models.user import DBUser
from models.group import DBGroup
from models.friend import DBFriend
from schemas.friend_request import FriendRequestBase
from schemas.group_request import GroupRequestBase
from schemas.notification import NotificationCreate
from websocket.connection_manager import manager
from service.permissions import (
    can_change_friend_request_status,
    can_change_group_request_status,
    can_view_group_requests,
)


def get_group_pending_join_requests(group_id: int, user_id: int, db: Session):
    can_view = can_view_group_requests(user_id, group_id, db)
    if not can_view:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You Are Not Allowed To View Group Request",
        )

    pending_group_requests = db.query(DBGroupRequest).filter(
        DBGroupRequest.group_id == group_id,
        DBGroupRequest.status == RequestStatus.pending,
    )

    return pending_group_requests


async def create_group_request(
    request: GroupRequestBase,
    user_id: int,
    db: Session,
):

    # Check that the receiver exists and is active
    group = (
        db.query(DBGroup)
        .filter(
            DBGroup.id == request.group_id,
            not DBUser.is_public,
        )
        .first()
    )

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found!",
        )

    # Check for an existing pending request
    existing_request = (
        db.query(DBGroupRequest)
        .filter(
            DBGroupRequest.sender_id == user_id,
            DBGroupRequest.group_id == request.group_id,
            DBGroupRequest.status == RequestStatus.pending,
        )
        .first()
    )

    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A pending group joining request already exists!",
        )

    # Check for an existing membership
    already_group_member = is_group_member(user_id, request.group_id, db)

    if already_group_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can not send group joining request to already joined group",
        )
    new_group_request = DBGroupRequest(
        sender_id=user_id,
        group_id=request.group_id,
    )

    db.add(new_group_request)
    db.commit()
    db.refresh(new_group_request)

    return new_group_request


def change_group_request_status(
    group_request_id: int,
    user_id: int,
    new_status: RequestStatus,
    db: Session,
):
    searched_group_request = (
        db.query(DBGroupRequest)
        .filter(
            DBGroupRequest.id == group_request_id,
        )
        .first()
    )

    if not searched_group_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group joining request not found!",
        )

    if not can_change_group_request_status(
        user_id=user_id,
        group_id=searched_group_request.group_id,
        group_request=searched_group_request,
        cancellation=new_status is RequestStatus.canceled,
        db=db,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied!",
        )

    if searched_group_request.status != RequestStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This group request has already been processed!",
        )

    if new_status in (
        RequestStatus.canceled,
        RequestStatus.declined,
    ):
        db.delete(searched_group_request)

    elif new_status == RequestStatus.accepted:
        new_membership = DBGroupMember(
            user_id=searched_group_request.sender_id,
            group_id=searched_group_request.group_id,
        )

        db.add(new_membership)
        db.delete(searched_group_request)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid group request status!",
        )

    db.commit()

    return True
