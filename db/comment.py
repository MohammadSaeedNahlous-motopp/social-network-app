from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from db.friend import is_friend_with
from db.group_member import get_group_member_role
from db.post import get_post
from models.comment import DBComment
from schemas.comment import CommentCreate, CommentResponse
from models.enums import GroupRole
from models.user import DBUser

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
    offset: int = 0
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
        .limit(11)
        .all()
    )

    has_more = len(comments) > 10
    comments = comments[:10]

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

    next_offset = offset + 10 if has_more else None

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

