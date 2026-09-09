from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.group import DBGroup
from models.group_member import DBGroupMember
from models.post import DBPost
from db.group_member import get_group_member_role
from models.enums import GroupRole

from schemas.post import PostCreate, PostUpdate

def check_group_member(
    db: Session,
    group_id: int,
    user_id: int,
) -> None:
    membership = (
        db.query(DBGroupMember)
        .filter(
            DBGroupMember.group_id == group_id,
            DBGroupMember.user_id == user_id,
        )
        .first()
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a group member.",
        )


def create_group_post(
    db: Session,
    group_id: int,
    request: PostCreate,
    user_id: int,
    image_url: str | None = None,
):
    group = (
        db.query(DBGroup)
        .filter(DBGroup.id == group_id)
        .first()
    )

    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found.",
        )

    check_group_member(
        db=db,
        group_id=group_id,
        user_id=user_id,
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
    check_group_member(
        db=db,
        group_id=group_id,
        user_id=user_id,
    )

    post = (
        db.query(DBPost)
        .filter(
            DBPost.id == post_id,
            DBPost.group_id == group_id,
            DBPost.user_id == user_id,
        )
        .first()
    )

    if post is None:
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
            detail="You must be a group member to delete a post.",
        )

    post = (
        db.query(DBPost)
        .filter(
            DBPost.id == post_id,
            DBPost.group_id == group_id,
        )
        .first()
    )

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group post not found.",
        )

    is_post_owner = post.user_id == user_id
    is_group_admin = user_role == GroupRole.administrator

    if not is_post_owner and not is_group_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this post.",
        )

    db.delete(post)
    db.commit()

    return post



