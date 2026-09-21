from sqlalchemy.orm.session import Session
from models.post import DBPost
from schemas.post import PostCreate, PostUpdate
from models.enums import PostVisibility
from models.friend import DBFriend
from db.friend import is_friend_with
from models.group_member import DBGroupMember
from sqlalchemy import or_, select


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
        visibility=request.visibility
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


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
    post = (
        db.query(DBPost)
        .filter(
            DBPost.id == post_id,
            DBPost.user_id == user_id,
            DBPost.is_visible.is_(True),
        )
        .first()
    )

    if post is None:
        return None

    if request.title is not None:
        post.title = request.title

    if request.content is not None:
        post.content = request.content

    db.commit()
    db.refresh(post)

    return post


def delete_post(
    db: Session,
    post_id: int,
    user_id: int
):
    """Delete a post owned by the user."""
    post = (
        db.query(DBPost)
        .filter(
            DBPost.id == post_id,
            DBPost.user_id == user_id,
        )
        .first()
    )

    if post is None:
        return None

    db.delete(post)
    db.commit()

    return post

def get_posts_by_user(
    db: Session,
    user_id: int,
    current_user_id: int,
):
    """Return posts the current user is allowed to see on a user's wall."""

    query = (
        db.query(DBPost)
        .filter(
            DBPost.user_id == user_id,
            DBPost.is_visible.is_(True),
        )
        .order_by(DBPost.created_at.desc())
    )

    # The user is viewing their own wall
    if current_user_id == user_id:
        return query

    # Check friendship using the existing method
    are_friends = is_friend_with(
        user_id=user_id,
        current_user_id=current_user_id,
        db=db
    )

    # Friends can see both public and friends-only posts
    if are_friends:
        return query

    # Non-friends can only see public posts
    query = query.filter(
        DBPost.visibility == PostVisibility.public
    )

    return query


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