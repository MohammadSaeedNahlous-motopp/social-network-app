from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user
from db.database import get_db
from models.enums import FriendRequestStatus
from models.user import DBUser
from schemas.friend_request import (
    FriendRequestBase,
    FriendRequestDisplayBase,
)
from db import friend_request


router = APIRouter(
    prefix="/friend-requests",
    tags=["Friend Requests"],
)


@router.get(
    "/",
    response_model=list[FriendRequestDisplayBase],
    status_code=status.HTTP_200_OK,
    summary="Get pending friend requests",
    description=(
        "Retrieves all pending friend requests received by the currently "
        "authenticated user. Only friend requests with a pending status "
        "are returned."
    ),
    response_description="List of pending friend requests.",
    responses={
        200: {"description": "Pending friend requests retrieved successfully."},
        401: {"description": "Could not authenticate the user."},
    },
)
def get_user_pending_friend_requests(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    return friend_request.get_user_pending_friend_requests(
        current_user.id,
        db,
    )


@router.post(
    "/create",
    response_model=FriendRequestDisplayBase,
    status_code=status.HTTP_201_CREATED,
    summary="Create a friend request",
    description=(
        "Creates a new friend request from the currently authenticated user "
        "to the specified receiver. The sender is automatically determined "
        "from the authentication token and cannot be provided by the client."
    ),
    response_description="The newly created friend request.",
    responses={
        201: {"description": "Friend request created successfully."},
        400: {
            "description": (
                "The friend request could not be created due to invalid "
                "request data or business rules."
            )
        },
        401: {"description": "Could not authenticate the user."},
        404: {"description": "Receiver user was not found."},
    },
)
def create_friend_request(
    request: FriendRequestBase,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    return friend_request.create_friend_request(
        request,
        current_user.id,
        db,
    )


@router.patch(
    "/{friend_request_id}/decline",
    response_model=FriendRequestDisplayBase,
    status_code=status.HTTP_200_OK,
    summary="Decline a friend request",
    description=(
        "Declines a pending friend request. Only the authenticated user who "
        "received the friend request is allowed to decline it."
    ),
    response_description="The declined friend request.",
    responses={
        200: {"description": "Friend request declined successfully."},
        400: {"description": "The friend request has already been processed."},
        401: {"description": "Could not authenticate the user."},
        404: {
            "description": (
                "Friend request was not found or does not belong to the "
                "authenticated user."
            )
        },
    },
)
def decline_friend_request(
    friend_request_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    return friend_request.change_friend_request_status(
        friend_request_id,
        current_user.id,
        FriendRequestStatus.declined,
        db,
    )


@router.patch(
    "/{friend_request_id}/accept",
    response_model=FriendRequestDisplayBase,
    status_code=status.HTTP_200_OK,
    summary="Accept a friend request",
    description=(
        "Accepts a pending friend request. Only the authenticated user who "
        "received the friend request is allowed to accept it."
    ),
    response_description="The accepted friend request.",
    responses={
        200: {"description": "Friend request accepted successfully."},
        400: {"description": "The friend request has already been processed."},
        401: {"description": "Could not authenticate the user."},
        404: {
            "description": (
                "Friend request was not found or does not belong to the "
                "authenticated user."
            )
        },
    },
)
def accept_friend_request(
    friend_request_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    return friend_request.change_friend_request_status(
        friend_request_id,
        current_user.id,
        FriendRequestStatus.accepted,
        db,
    )


@router.patch(
    "/{friend_request_id}/cancel",
    response_model=FriendRequestDisplayBase,
    status_code=status.HTTP_200_OK,
    summary="Cancel a friend request",
    description=(
        "Cancels a pending friend request. Only the authenticated user who "
        "sent the friend request is allowed to cancel it."
    ),
    response_description="The canceled friend request.",
    responses={
        200: {"description": "Friend request canceled successfully."},
        400: {"description": "The friend request has already been processed."},
        401: {"description": "Could not authenticate the user."},
        404: {
            "description": (
                "Friend request was not found or does not belong to the "
                "authenticated user."
            )
        },
    },
)
def cancel_friend_request(
    friend_request_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    return friend_request.change_friend_request_status(
        friend_request_id,
        current_user.id,
        FriendRequestStatus.canceled,
        db,
    )
