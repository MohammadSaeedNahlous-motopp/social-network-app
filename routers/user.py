from typing import List

from fastapi import APIRouter, Depends, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user
from db.database import get_db
from models.enums import ImageType
from models.user import DBUser
from schemas.group import GroupView
from schemas.user import UserUpdate, UserDisplay
from schemas.post import PostResponse
from db import post as db_post
from db import user, group_member
from service.image import save_image


router = APIRouter(prefix="/users", tags=["users"])


@router.put(
    "/edit",
    response_model=UserDisplay,
    status_code=status.HTTP_200_OK,
    summary="Update the current user's profile",
    description=(
        "Updates the profile information of the currently authenticated user. "
        "The user can update their name, email address, biography, phone number, "
        "location, and gender. A new profile image can also be uploaded optionally. "
        "The profile image must be a valid JPG, PNG, or WEBP image and must not "
        "exceed the maximum allowed file size."
    ),
    response_description="The updated user profile.",
    responses={
        200: {"description": "User profile updated successfully."},
        400: {
            "description": (
                "The request contains invalid data, the email address is already "
                "registered by another user, or the uploaded profile image is invalid."
            )
        },
        401: {"description": "Authentication is required to update a user profile."},
        404: {"description": "The authenticated user could not be found."},
    },
)
async def edit_user(
    request: UserUpdate = Depends(UserUpdate.as_form),
    profile_img: UploadFile | None = File(None),
    remove_profile_img: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    image_path = None

    if profile_img is not None:
        image_path = await save_image(profile_img, ImageType.profile_picture)

    return user.edit_user(
        request,
        image_path,
        db,
        current_user.id,
        remove_profile_img,
    )


@router.patch(
    "/toggle-active",
    status_code=status.HTTP_200_OK,
    summary="Toggle the current user's active status",
    description=(
        "Toggles the active status of the currently authenticated user. "
        "If the account is currently active, it will be deactivated. "
        "If the account is inactive, it will be activated."
    ),
    response_description="The user's new active status.",
    responses={
        200: {"description": "User active status updated successfully."},
        401: {"description": "Authentication is required to change account status."},
        404: {"description": "The authenticated user could not be found."},
    },
)
def edit_user_active_state(
    db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)
):
    return user.edit_user_active_state(db, current_user.id)


@router.get("/{user_id}/membership", response_model=List[GroupView])
def get_user_groups(user_id: int, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    group_list = group_member.get_user_membership(db=db, user_id=user_id, current_user_id=current_user.id)

    return group_list

@router.get(
    "/{user_id}/posts",
    response_model=list[PostResponse],
    status_code=status.HTTP_200_OK,
    summary="View a user's personal wall",
    description=(
        "Retrieves the published posts of a specific user. "
        "The personal wall contains only posts created by that user."
    ),
    response_description="The user's published posts.",
    responses={
        200: {"description": "User posts retrieved successfully."},
    },
)
def get_user_posts(
    user_id: int,
    db: Session = Depends(get_db),
):
    """Return the published posts belonging to a specific user."""

    return db_post.get_posts_by_user(
        db=db,
        user_id=user_id,
    )
