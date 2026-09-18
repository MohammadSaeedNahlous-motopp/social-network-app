from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from db.friend import is_friend_with
from db.group_member import get_group_member_role
from db.post import get_post
from models.comment import DBComment
from schemas.comment import CommentCreate
from models.enums import GroupRole

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

    # Personal post
    if post.group_id is None:

        # The post owner can comment on their own post
        if post.user_id != user_id:
            are_friends = is_friend_with(
                user_id=post.user_id,
                current_user_id=user_id,
                db=db
            )

            if not are_friends:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the post owner or their friends can comment on this post.",
                )

    # Group post
    else:
        user_role = get_group_member_role(
            db=db,
            group_id=post.group_id,
            user_id=user_id
        )

        if user_role is None:
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

    return new_comment

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
    is_post_owner = post.user_id == user_id

    # Personal post
    if post.group_id is None:
        if not is_comment_owner and not is_post_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the comment owner or post owner can delete this comment.",
            )

    # Group post
    else:
        user_role = get_group_member_role(
            db=db,
            group_id=post.group_id,
            user_id=user_id,
        )

        is_group_admin = user_role == GroupRole.administrator

        if (
            not is_comment_owner
            and not is_post_owner
            and not is_group_admin
        ):
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

