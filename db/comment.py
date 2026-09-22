from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from db.post import get_post
from models.comment import DBComment
from schemas.comment import CommentCreate, CommentResponse
from models.user import DBUser
from service.permissions import can_see_post, can_delete_post


def get_comment(
    db: Session,
    comment_id: int
) -> DBComment | None:
    """Return a visible comment by its ID."""

    return (
        db.query(DBComment)
        .filter(
            DBComment.id == comment_id,
            DBComment.is_visible.is_(True)
        )
        .first()
    )

def create_comment(
    db: Session,
    post_id: int,
    request: CommentCreate,
    user_id: int
):
    """Create a comment when the user has permission to comment on the post."""

    post = get_post(
        db=db,
        post_id=post_id
    )

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found."
        )

    if not can_see_post(requesting_user_id=user_id, post=post, db=db):
        # Personal post
        if post.group_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the post owner or their friends can comment on this post.",
            )

        # Group post
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be a group member to comment on this post.",
            )

    new_comment = DBComment(
        user_id=user_id,
        post_id=post_id,
        content=request.content
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    user = (
        db.query(DBUser)
        .filter(DBUser.id == new_comment.user_id)
        .first()
    )

    result = CommentResponse(
        id=new_comment.id,
        user_id=new_comment.user_id,
        name=user.name,
        post_id=new_comment.post_id,
        content=new_comment.content,
        is_visible=new_comment.is_visible,
        created_at=new_comment.created_at,
        updated_at=new_comment.updated_at
    )

    return result


def get_comments_by_post(
    db: Session,
    post_id: int,
    requesting_user_id: int,
    limit: int = 10,
    offset: int = 0,
):
    """Return visible comments for a personal or group post."""

    post = get_post(
        db=db,
        post_id=post_id,
    )

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found."
        )

    if not can_see_post(requesting_user_id=requesting_user_id, post=post, db=db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have permission to view the post.")

    comments = (
        db.query(
            DBComment,
            DBUser.name
        )
        .join(
            DBUser,
            DBComment.user_id == DBUser.id
        )
        .filter(
            DBComment.post_id == post_id,
            DBComment.is_visible.is_(True)
        )
        .order_by(DBComment.created_at.asc())
        .offset(offset)
        .limit(limit + 1)
        .all()
    )

    has_more = len(comments) > limit
    comments = comments[:limit]

    results = []

    for comment, name in comments:
        result = CommentResponse(
            id=comment.id,
            user_id=comment.user_id,
            name=name,
            post_id=comment.post_id,
            content=comment.content,
            is_visible=comment.is_visible,
            created_at=comment.created_at,
            updated_at=comment.updated_at
        )

        results.append(result)

    next_offset = offset + limit if has_more else None

    return results, has_more, next_offset


def delete_comment(
    db: Session,
    comment_id: int,
    user_id: int,
):
    """Soft delete a comment when the user has permission."""

    comment = get_comment(
        db=db,
        comment_id=comment_id,
    )

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found.",
        )

    post = get_post(
        db=db,
        post_id=comment.post_id,
    )

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    is_comment_owner = comment.user_id == user_id

    if (not can_delete_post(user_id=user_id, post=post, group_id=post.group_id, db=db)
        and not is_comment_owner):
        # Personal post
        if post.group_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the comment owner or post owner can delete this comment.",
            )

        # Group post
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Only the comment owner, post owner, or group "
                    "administrator can delete this comment."
                ),
            )

    comment.is_visible = False

    db.commit()
    db.refresh(comment)

    return comment

