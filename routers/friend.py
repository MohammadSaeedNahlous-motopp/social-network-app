from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user
from db import friend
from db.database import get_db
from models.user import DBUser
from schemas.friend import FriendDisplayBase


router = APIRouter(
    prefix="/friends",
    tags=["Friends"],
)


@router.get(
    "/",
    response_model=list[FriendDisplayBase],
    status_code=status.HTTP_200_OK,
    summary="Get the authenticated user's friends",
    description=(
        "Returns a list of all friends belonging to the authenticated user. "
        "Each friendship record includes the friend's basic profile information "
        "and the date when the friendship was created."
    ),
    response_description="A list of the authenticated user's friends.",
    responses={
        200: {
            "description": "Friends retrieved successfully.",
        },
        401: {
            "description": "Could not authenticate the user.",
        },
    },
)
def get_friends(
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return friend.get_friends(current_user.id, db)


@router.delete(
    "/{friendship_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a friendship",
    description=(
        "Deletes a friendship belonging to the authenticated user. "
        "The friendship is removed for both users."
    ),
    response_description="The friendship was deleted successfully.",
    responses={
        200: {
            "description": "Friendship deleted successfully.",
        },
        401: {
            "description": "Could not authenticate the user.",
        },
        404: {
            "description": (
                "Friendship was not found or does not belong to the authenticated user."
            ),
        },
    },
)
def delete_friend(
    friendship_id: int,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return friend.delete_friend(
        current_user.id,
        friendship_id,
        db,
    )
