from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user
from db import comment as db_comment
from db.database import get_db
from models.user import DBUser
from schemas.comment import CommentCreate, CommentResponse, CommentListResponse


router = APIRouter(prefix="/comments", tags=["comments"])


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
    current_user: DBUser = Depends(get_current_user),
):
    """Create a comment on a personal or group post."""

    results = db_comment.create_comment(
        db=db, post_id=post_id, request=request, user_id=current_user.id
    )
    return results


@router.get(
    "/posts/{post_id}",
    response_model=CommentListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get comments for a post",
    description=(
        "Retrieves visible comments for a post in batches. "
        "Each request returns up to 10 comments."
    ),
    response_description="A batch of comments for the post.",
    responses={
        200: {"description": "Comments retrieved successfully."},
        404: {"description": "The post was not found."},
    },
)
def get_post_comments(
    post_id: int,
    limit: int = Query(1, ge=1),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    """Return visible comments for a post using load-more pagination."""

    comments, has_more, next_offset = db_comment.get_comments_by_post(
        db=db,
        post_id=post_id,
        requesting_user_id=current_user.id,
        limit=limit,
        offset=offset,
    )

    return CommentListResponse(
        items=comments, has_more=has_more, next_offset=next_offset
    )


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
        403: {
            "description": "The user does not have permission to delete the comment."
        },
        404: {"description": "The comment or post was not found."},
    },
)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    """Soft delete a comment when the authenticated user has permission."""

    db_comment.delete_comment(db=db, comment_id=comment_id, user_id=current_user.id)

    return {"message": "Comment deleted successfully."}
