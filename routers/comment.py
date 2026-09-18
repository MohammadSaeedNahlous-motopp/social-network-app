from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user
from db import comment as db_comment
from db.database import get_db
from models.user import DBUser
from schemas.comment import CommentCreate, CommentResponse


router = APIRouter(
    prefix="/comments",
    tags=["comments"]
)


@router.post(
    "/posts/{post_id}",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a comment on a post",
    description=(
        "Creates a comment on a personal or group post. "
        "For a personal post, the authenticated user must be the post owner "
        "or a friend of the post owner. For a group post, the authenticated "
        "user must be a member of the group."
    ),
    response_description="The newly created comment.",
    responses={
        201: {"description": "Comment created successfully."},
        401: {"description": "Authentication is required to create a comment."},
        403: {"description": "The user does not have permission to comment."},
        404: {"description": "The post was not found."},
    },
)
def create_comment(
    post_id: int,
    request: CommentCreate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    """Create a comment on a personal or group post."""

    results = db_comment.create_comment(
        db=db,
        post_id=post_id,
        request=request,
        user_id=current_user.id
    )
    return results


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a comment",
    description=(
        "Soft deletes a comment. For a personal post, the comment can be "
        "removed by the comment owner or post owner. For a group post, "
        "the comment can be removed by the comment owner, post owner, "
        "or a group administrator."
    ),
    response_description="Confirmation that the comment was deleted.",
    responses={
        200: {"description": "Comment deleted successfully."},
        401: {"description": "Authentication is required to delete a comment."},
        403: {"description": "The user does not have permission to delete the comment."},
        404: {"description": "The comment or post was not found."},
    },
)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    """Soft delete a comment when the authenticated user has permission."""

    db_comment.delete_comment(
        db=db,
        comment_id=comment_id,
        user_id=current_user.id
    )

    return {"message": "Comment deleted successfully."}