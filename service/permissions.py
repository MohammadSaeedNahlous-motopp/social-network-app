from fastapi import HTTPException, status
from sqlalchemy import exists, or_, true
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from models.enums import GroupRole, PostVisibility
from models.friend import DBFriend
from models.friend_request import DBFriendRequest
from models.group import DBGroup
from models.group_member import DBGroupMember
from models.group_request import DBGroupRequest
from models.post import DBPost


def can_see_chat(user_id: int, chat_id: int, db: Session) -> bool:
    from db.chat_member import is_chat_member

    has_membership = is_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        db=db,
    )

    return has_membership


def can_delete_friendship(
    user_id: int,
    friendship: DBFriend,
) -> bool:
    return friendship.user_id == user_id


def can_change_friend_request_status(
    user_id: int,
    friend_request: DBFriendRequest,
    cancellation: bool = False,
) -> bool:
    if cancellation:
        return friend_request.sender_id == user_id

    return friend_request.receiver_id == user_id


def can_change_group_request_status(
    user_id: int,
    group_id: int,
    group_request: DBGroupRequest,
    cancellation: bool,
    db: Session,
) -> bool:
    if cancellation:
        return group_request.sender_id == user_id

    from db.group_member import get_group_member_role

    role = get_group_member_role(
        db=db,
        group_id=group_id,
        user_id=user_id,
    )

    return role is GroupRole.administrator


def can_edit_group(
    user_id: int,
    group_id: int,
    db: Session,
) -> bool:
    from db.group_member import get_group_member_role

    role = get_group_member_role(
        db=db,
        group_id=group_id,
        user_id=user_id,
    )

    return role is GroupRole.administrator


def can_delete_group(
    user_id: int,
    group: DBGroup,
) -> bool:
    return group.owner_id == user_id


def can_see_group_details(
    user_id: int,
    group: DBGroup,
    db: Session,
) -> bool:
    if group.is_public:
        return True

    req_user_membership = (
        db.query(DBGroupMember)
        .filter(
            DBGroupMember.group_id == group.id,
            DBGroupMember.user_id == user_id,
        )
        .first()
    )

    return req_user_membership is not None


def can_see_user_membership_of_group_query_filter(
    requesting_user_id: int,
    user_id: int,
    group_id: int,
) -> ColumnElement[bool]:
    """
    Return a SQLAlchemy expression determining whether the requesting
    user can see the given user's membership in a group.
    """

    if requesting_user_id == user_id:
        return true()

    return or_(
        DBGroup.is_public.is_(True),
        exists().where(
            DBGroupMember.group_id == group_id,
            DBGroupMember.user_id == requesting_user_id,
        ),
    )


def validate_can_change_user_membership_role(
    requesting_user_id: int,
    user_id: int,
    new_role: GroupRole,
    group: DBGroup,
    db: Session,
) -> None:
    from db.group_member import get_group_member_role

    user_role = get_group_member_role(
        db,
        group.id,
        user_id,
    )

    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a group member.",
        )

    current_user_membership = get_group_member_role(
        db,
        group.id,
        requesting_user_id,
    )

    if not current_user_membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Issuer is not a group member.",
        )

    if current_user_membership != GroupRole.administrator:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Issuer does not have permission to change the role.",
        )

    if user_role == new_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has the role.",
        )

    if user_id == group.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Issuer cannot change the role. "
                f"Group owner role can only be '{GroupRole.administrator}'"
            ),
        )

    if user_role == GroupRole.administrator and requesting_user_id != group.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only group owner can change the role.",
        )


def validate_can_get_message(
    user_id: int,
    chat_id: int,
    db: Session,
) -> None:
    from db.chat_member import is_chat_member

    is_member = is_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        db=db,
    )

    if is_member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to view this message!",
        )


def get_user_post_visibility_filter(
    requesting_user_id: int,
    user_id: int,
    are_friends: bool,
) -> ColumnElement[bool]:
    if requesting_user_id == user_id:
        return true()

    if are_friends:
        return or_(
            DBPost.visibility == PostVisibility.public,
            DBPost.visibility == PostVisibility.friends_only,
        )

    return DBPost.visibility == PostVisibility.public


def can_see_post(
    requesting_user_id: int,
    post: DBPost,
    db: Session,
) -> bool:
    if not post.group_id:
        if requesting_user_id == post.user_id:
            return True

        from db.friend import is_friend_with

        if post.visibility == PostVisibility.friends_only and is_friend_with(
            db=db,
            user_id=post.user_id,
            current_user_id=requesting_user_id,
        ):
            return True

        return post.visibility == PostVisibility.public

    from db.group import get_group_by_id

    group = get_group_by_id(
        db=db,
        group_id=post.group_id,
    )

    if group.is_public:
        return True

    from db.group_member import get_group_member_role

    user_role = get_group_member_role(
        db=db,
        group_id=post.group_id,
        user_id=requesting_user_id,
    )

    return user_role is not None


def can_edit_post(
    user_id: int,
    post: DBPost,
    group_id: int | None = None,
    db: Session | None = None,
) -> bool:
    if not group_id:
        return post.user_id == user_id

    if not db:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    from db.group_member import get_group_member_role

    return (
        post.user_id == user_id
        and post.group_id == group_id
        and get_group_member_role(
            db=db,
            group_id=group_id,
            user_id=user_id,
        )
        is not None
    )


def can_delete_post(
    user_id: int,
    post: DBPost,
    group_id: int | None = None,
    db: Session | None = None,
) -> bool:
    if not group_id:
        return post.user_id == user_id

    if not db:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    from db.group_member import get_group_member_role

    user_role = get_group_member_role(
        db=db,
        group_id=group_id,
        user_id=user_id,
    )

    condition1 = post.group_id == group_id
    condition2_a = post.user_id == user_id and user_role is not None
    condition2_b = user_role is GroupRole.administrator

    print(
        f"condition1: {condition1}\t"
        f"condition2_a: {condition2_a}\t"
        f"condition2_b: {condition2_b}"
    )

    result = condition1 and (condition2_a or condition2_b)

    print(f"result is {result}")

    return result
