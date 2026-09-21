from fastapi import HTTPException, status
from sqlalchemy.orm.session import Session

from models.friend import DBFriend
from models.post import DBPost
from schemas.post import PostCreate, PostUpdate

from db.friend import is_friend_with
from models.group_member import DBGroupMember
from sqlalchemy import or_
from service.permissions import (
    get_user_post_visibility_filter,
    can_delete_post,
    can_edit_post,
)


def create_post(
    db: Session,
    request: PostCreate,
    user_id: int,
    image_url: str | None = None,
):
    """Create and save a new post for a user."""

    new_post = DBPost(
        user_id=user_id,
        title=request.title,
        content=request.content,
        image_url=image_url,
        visibility=request.visibility,
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

def get_feed(
    db: Session,
    user_id: int,
):
    """Return posts for the authenticated user's feed."""

    friend_ids = (
        db.query(DBFriend.friend_id)
        .filter(DBFriend.user_id == user_id)
    )

    group_ids = (
        db.query(DBGroupMember.group_id)
        .filter(DBGroupMember.user_id == user_id)
    )

    query = db.query(DBPost).filter(
        DBPost.is_visible.is_(True),
        or_(
            # User's own personal posts
            (
                (DBPost.user_id == user_id)
                & DBPost.group_id.is_(None)
            ),

            # Friends' personal posts
            (
                DBPost.user_id.in_(friend_ids)
                & DBPost.group_id.is_(None)
            ),

            # Posts from groups the user belongs to
            DBPost.group_id.in_(group_ids),
        ),
    )

    return query.order_by(DBPost.created_at.desc())


def get_post(db: Session, post_id: int) -> DBPost | None:
    """Return a visible post by its ID."""

    result = (
        db.query(DBPost)
        .filter(
            DBPost.id == post_id,
            DBPost.is_visible.is_(True),
        )
        .first()
    )

    return result


def update_post(
    db: Session,
    post_id: int,
    request: PostUpdate,
    user_id: int,
):
    """Update the title or content of a post owned by the user."""
    post = get_post(db=db, post_id=post_id)

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if not can_edit_post(user_id=user_id, post=post):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if request.title is not None:
        post.title = request.title

    if request.content is not None:
        post.content = request.content

    db.commit()
    db.refresh(post)

    return post


def delete_post(db: Session, post_id: int, user_id: int):
    """Delete a post owned by the user."""
    post = get_post(db=db, post_id=post_id)

    if post is None:
        return None

    if not can_delete_post(user_id=user_id, post=post):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    db.delete(post)
    db.commit()

    return post


def get_posts_by_user(
    db: Session,
    user_id: int,
    current_user_id: int,
):
    """Return posts the current user is allowed to see on a user's wall."""

    query = db.query(DBPost).filter(
        DBPost.user_id == user_id,
        DBPost.group_id.is_(None),
        DBPost.is_visible.is_(True),
    )

    # Check friendship using the existing method
    are_friends = is_friend_with(
        user_id=user_id, current_user_id=current_user_id, db=db
    )

    # Non-friends can only see public posts
    query = query.filter(
        get_user_post_visibility_filter(
            requesting_user_id=current_user_id, user_id=user_id, are_friends=are_friends
        )
    )

    return query
