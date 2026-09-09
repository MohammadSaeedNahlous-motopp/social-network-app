from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user
from db.database import get_db
from db import post_group as db_group_post
from models.user import DBUser
from schemas.post import PostCreate, PostResponse, PostUpdate
from service.post_image import save_post_image

router = APIRouter(
    prefix="/group_posts",
    tags=["group posts"],
)


@router.post(
    "/{group_id}/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a post inside a group",
    description=(
        "Creates a new post inside a specific group. "
        "The authenticated user must be a member of the group. "
        "The post can contain a title, content, and an optional image."
    ),
    response_description="The newly created group post.",
    responses={
        201: {"description": "Group post created successfully."},
        400: {"description": "The uploaded image is invalid."},
        401: {"description": "Authentication is required to create a group post."},
        403: {"description": "The user is not a member of the group."},
        404: {"description": "The group was not found."},
    },
)
async def create_group_post(
    group_id: int,
    title: str = Form(...),
    content: str = Form(...),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    """Create a new post inside a group for an authenticated group member."""

    image_url = None

    if image is not None:
        image_url = await save_post_image(image)

    request = PostCreate(
        title=title,
        content=content,
    )

    return db_group_post.create_group_post(
        db=db,
        group_id=group_id,
        request=request,
        user_id=current_user.id,
        image_url=image_url,
    )


@router.put(
    "/{group_id}/posts/{post_id}",
    response_model=PostResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a post inside a group",
    description=(
        "Updates an existing post inside a specific group. "
        "The authenticated user must be a member of the group "
        "and must be the owner of the post."
    ),
    response_description="The updated group post.",
    responses={
        200: {"description": "Group post updated successfully."},
        401: {"description": "Authentication is required to update a group post."},
        403: {"description": "The user does not have permission to update the post."},
        404: {"description": "The group post was not found."},
    },
)
def update_group_post(
    group_id: int,
    post_id: int,
    request: PostUpdate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    """Update a group post owned by the authenticated group member."""

    return db_group_post.update_group_post(
        db=db,
        group_id=group_id,
        post_id=post_id,
        request=request,
        user_id=current_user.id,
    )


@router.delete(
    "/{group_id}/posts/{post_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a post inside a group",
    description=(
        "Permanently deletes a post inside a specific group. "
        "The post can be deleted by its owner or by a group administrator."
    ),
    response_description="Confirmation that the group post was deleted.",
    responses={
        200: {"description": "Group post deleted successfully."},
        401: {"description": "Authentication is required to delete a group post."},
        403: {"description": "The user does not have permission to delete the post."},
        404: {"description": "The group post was not found."},
    },
)
def delete_group_post(
    group_id: int,
    post_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    """Delete a group post as the post owner or a group administrator."""

    db_group_post.delete_group_post(
        db=db,
        group_id=group_id,
        post_id=post_id,
        user_id=current_user.id,
    )

    return {
        "message": "Group post deleted successfully."
    }