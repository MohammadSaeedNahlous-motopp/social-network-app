from sqlalchemy.orm.session import Session
from models.post import DBPost
from schemas.post import PostCreate, PostUpdate
from service.pagination import paginate, calculate_total_pages


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
    user_id: int,
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
    page: int,
    page_size: int,
):
    """Return paginated visible posts published by a specific user."""
    query = (
        db.query(DBPost)
        .filter(
            DBPost.user_id == user_id,
            DBPost.is_visible.is_(True),
        )
        .order_by(DBPost.created_at.desc())
    )

    total = query.count()

    paginated_query = paginate(
        query=query,
        page=page,
        page_size=page_size,
    )

    items = paginated_query.all()

    result = {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": calculate_total_pages(
            total=total,
            page_size=page_size,
        ),
    }

    return result


