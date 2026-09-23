from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user
from db.database import get_db
from models.user import DBUser
from schemas.post_reaction import (
    PostReactionCreate,
    PostReactionResponse,
)
from db import post_reaction
from service.pagination import PaginatedResponse

router = APIRouter(
    prefix="/posts",
    tags=["Post Reactions"],
)


@router.post(
    "/{post_id}/reactions",
    response_model=PostReactionResponse | bool,
    status_code=status.HTTP_200_OK,
    summary="Create, change, or remove a post reaction",
    description="""
Handle the authenticated user's reaction to a post.

The behavior depends on the user's existing reaction:

- If the user has no reaction, a new reaction is created.
- If the user sends the same reaction they already have, the existing reaction is removed.
- If the user sends a different reaction, the existing reaction is changed.
- The post score is automatically updated accordingly.

The authenticated user is used as the reaction owner.
The `user_id` must not be provided by the client.

The authenticated user must have permission to see the post
in order to react to it.
""",
    responses={
        200: {
            "description": (
                "Reaction successfully created, changed, or removed. "
                "When a reaction is created or changed, the response contains "
                "the reaction object. When the reaction is removed, the response "
                "is `true`."
            ),
        },
        403: {
            "description": (
                "The authenticated user is not allowed to interact with the post."
            ),
        },
        404: {
            "description": "Post not found.",
        },
    },
)
def handle_post_reaction(
    post_id: int,
    request: PostReactionCreate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    return post_reaction.handle_post_reaction(
        post_id=post_id,
        user_id=current_user.id,
        req=request,
        db=db,
    )


@router.get(
    "/{post_id}/reactions",
    response_model=PaginatedResponse[PostReactionResponse],
    status_code=status.HTTP_200_OK,
    summary="Get reactions for a post",
    description="""
Retrieve reactions belonging to a post using pagination.

The authenticated user must have permission to see the post.

Pagination parameters:

- `page`: Page number, starting from 1.
- `page_size`: Maximum number of reactions returned per page.
""",
    responses={
        200: {
            "description": "Paginated list of reactions for the post.",
        },
        403: {
            "description": (
                "The authenticated user is not allowed to view the post reactions."
            ),
        },
        404: {
            "description": "Post not found.",
        },
    },
)
def get_post_reactions(
    post_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=0, le=100),
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    query = post_reaction.get_post_reactions(
        post_id=post_id,
        requesting_user_id=current_user.id,
        db=db,
    )

    return PaginatedResponse.from_query(query=query, page=page, page_size=page_size)
