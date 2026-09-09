from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from db.group import get_group_by_id
from models.post import DBPost
from db.group_member import get_group_member_role
from db.post import get_post
from models.enums import GroupRole

from schemas.post import PostCreate, PostUpdate



def create_group_post(
    db: Session,
    group_id: int,
    request: PostCreate,
    user_id: int,
    image_url: str | None = None,
):
    get_group_by_id(
        db=db,
        group_id=group_id,
    )

    user_role = get_group_member_role(
        db=db,
        group_id=group_id,
        user_id=user_id,
    )

    if user_role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a group member.",
        )

    new_post = DBPost(
        user_id=user_id,
        group_id=group_id,
        title=request.title,
        content=request.content,
        image_url=image_url,
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


def update_group_post(
    db: Session,
    group_id: int,
    post_id: int,
    request: PostUpdate,
    user_id: int,
):
    user_role = get_group_member_role(
        db=db,
        group_id=group_id,
        user_id=user_id,
    )

    if user_role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a group member.",
        )

    post = get_post(
        db=db,
        post_id=post_id,
    )

    if (
        post is None
        or post.group_id != group_id
        or post.user_id != user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group post not found.",
        )

    if request.title is not None:
        post.title = request.title

    if request.content is not None:
        post.content = request.content

    db.commit()
    db.refresh(post)

    return post


def delete_group_post(
    db: Session,
    group_id: int,
    post_id: int,
    user_id: int,
):
    user_role = get_group_member_role(
        db=db,
        group_id=group_id,
        user_id=user_id,
    )

    if user_role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a group administrator or the owner of the post to delete this post.",
        )

    post = get_post(
        db=db,
        post_id=post_id,
    )

    if post is None or post.group_id != group_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group post not found.",
        )

    is_post_owner = post.user_id == user_id
    is_group_admin = user_role == GroupRole.administrator

    if not is_post_owner and not is_group_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only a group administrator or the post owner can delete this post."
            ),
        )

    db.delete(post)
    db.commit()

    return post