from fastapi import HTTPException, status

from sqlalchemy.orm import Query
from sqlalchemy.orm.session import Session

from db.group_role import get_role_obj
from models.enums import GroupRole
from models.group_member import DBGroupMember

from models.group import DBGroup
from models.group_role import DBGroupRole

from models.user import DBUser

from db.group import get_group_by_id
from service.permissions import can_see_group_members, can_see_user_membership_of_group_query_filter, \
    validate_can_change_user_membership_role


# Add pagination for member list
def get_group_members(db: Session, group_id: int, requesting_user_id: int) -> Query:
    """
    Return a list of all users who are member of group, and their roles
    :param db: database session
    :param group_id: id of group
    :param requesting_user_id: id of user who requested the group member list
    :return: a pair of user and its role **Query[tuple[DBUser, GroupRole]]**
    """
    searched_group = get_group_by_id(db, group_id)

    if not can_see_group_members(user_id=requesting_user_id, group=searched_group, db=db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has no permission to read list of group members",
        )

    group_members = (
        db.query(DBUser, DBGroupRole.name)
        .join(DBGroupMember, DBGroupMember.user_id == DBUser.id)
        .join(DBGroupRole, DBGroupRole.id == DBGroupMember.role_id)
        .filter(DBGroupMember.group_id == group_id)
    )

    return group_members


def get_user_membership(
    db: Session, user_id: int, current_user_id: int
) -> Query[DBGroup]:
    """
    Return a list of groups a user is member of
    :param db: database session
    :param user_id:  id of user
    :param current_user_id: id of current user
    :return: a query of groups that the user is member of
    """

    received_groups = (
        db.query(DBGroup)
        .join(DBGroupMember, DBGroupMember.group_id == DBGroup.id)
        .filter(DBGroupMember.user_id == user_id)
        .filter(can_see_user_membership_of_group_query_filter(
            requesting_user_id=current_user_id,
            user_id=user_id,
            group_id=DBGroup.id)
        )
    )

    return received_groups


def get_group_member_role(db: Session, group_id: int, user_id: int) -> GroupRole | None:
    """
    Check if a user is a member of a group
    :param db: database session
    :param group_id: id of group
    :param user_id: id of a user
    :return: GroupRole | None - if user is a group member returns its role, otherwise *None*
    """
    member = (
        db.query(DBGroupMember)
        .filter(DBGroupMember.group_id == group_id, DBGroupMember.user_id == user_id)
        .first()
    )

    result = member.role.name if member else None

    return result


def join_group(db: Session, group_id: int, user_id: int) -> DBGroupMember:
    searched_group = get_group_by_id(db, group_id)

    if not searched_group.is_public:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Join request for private groups is not implemented",
        )

    # Check if user is already a member
    existing_membership = (
        db.query(DBGroupMember)
        .filter(DBGroupMember.group_id == group_id, DBGroupMember.user_id == user_id)
        .first()
    )
    if existing_membership:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already has joined a group.",
        )

    new_membership = DBGroupMember(
        group_id=group_id,
        user_id=user_id,
        role=get_role_obj(db=db, role=GroupRole.member),
    )

    db.add(new_membership)
    db.commit()
    db.refresh(new_membership)

    return new_membership


def leave_group(db: Session, group_id: int, user_id: int) -> None:
    searched_group = get_group_by_id(db, group_id)

    if searched_group.owner_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User cannot leave group he owns.",
        )

    deleted_count = (
        db.query(DBGroupMember)
        .filter(
            DBGroupMember.group_id == group_id,
            DBGroupMember.user_id == user_id,
        )
        .delete()
    )

    if deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not a member of this group.",
        )

    db.commit()


def change_user_role(
    db: Session, group_id: int, user_id: int, new_role: GroupRole, current_user_id: int
) -> DBGroupMember:
    """
    Change the role of a user in a group
    :param db: database session
    :param group_id: id of group
    :param user_id: id of user whose role will be changed
    :param new_role: new role that will be assigned
    :param current_user_id: id of user who will execute role change operation
    :return: DBGroupMember model
    """
    searched_group = get_group_by_id(db, group_id)

    if not searched_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Group not found."
        )

    validate_can_change_user_membership_role(requesting_user_id=current_user_id, new_role=new_role, user_id=user_id, group=searched_group, db=db)

    membership = (
        db.query(DBGroupMember)
        .filter(
            DBGroupMember.group_id == group_id,
            DBGroupMember.user_id == user_id,
        )
        .first()
    )

    membership.role = get_role_obj(db=db, role=new_role)

    db.add(membership)
    db.commit()

    db.refresh(membership)

    return membership
