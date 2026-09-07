from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Query
from sqlalchemy.orm.session import Session

from db.group_role import get_role_obj
from models.enums import GroupRole
from models.group import DBGroup
from models.group_member import DBGroupMember
from schemas import group

def create_group(db: Session, group_model: group.GroupBase, owner_id: int) -> DBGroup:
    """
    Create a new group
    :param db: database session
    :param group_model: group model
    :param owner_id: id of a user who creates a new group
    :return: newly created group
    """
    new_group = DBGroup(
        name=group_model.name,
        description=group_model.description,
        owner_id=owner_id,
        background_img=group_model.background_img,
        profile_img=group_model.profile_img,
        is_public=group_model.is_public,
    )

    db.add(new_group)
    db.flush()

    owner_membership = DBGroupMember(
        group_id=new_group.id,
        user_id=owner_id,
        role=get_role_obj(role=GroupRole.administrator, db=db),
    )

    db.add(owner_membership)

    db.commit()
    db.refresh(new_group)

    return new_group

def get_group_by_id(db: Session, group_id: int) -> DBGroup:
    searched_group = db.query(DBGroup).filter(DBGroup.id == group_id).first()

    if searched_group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    return searched_group

def get_all_groups(db: Session) -> Query[DBGroup]:
    return db.query(DBGroup)

def get_groups(db: Session, request_model: group.GroupSearch) -> Query[DBGroup]:
    """
    Return all groups that match the search criteria
    :param db: database session
    :param request_model: request model
    :return: query with all matching groups
    """
    search_data = request_model.model_dump(exclude_unset=True)

    if (not search_data or
            request_model.name is None and request_model.description is None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be provided for search",
        )

    query = db.query(DBGroup)

    if request_model.name:
        query = query.filter(DBGroup.name.ilike(f"%{request_model.name}%"))

    if request_model.description:
        query = query.filter(
            DBGroup.description.ilike(f"%{request_model.description}%")
        )

    return query

def update_group(db: Session, request_model: group.GroupUpdate, group_id: int, user_id: int) -> DBGroup:
    """
    Update an existing group
    :param db: database session
    :param request_model: group model with updated data
    :param group_id: id of a group we want to update
    :param user_id: id of user who updates an existing group
    :return: if update was successful return updated group otherwise return original group
    """

    searched_group = db.query(DBGroup).filter(DBGroup.id == group_id).first()

    if searched_group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    # Needs an extend to support of admins in future
    if searched_group.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User has no permission to edit group")

    update_data = request_model.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be provided for update",
        )

    for key, value in update_data.items():
        setattr(searched_group, key, value)

    db.commit()
    db.refresh(searched_group)

    return searched_group

def delete_group(db: Session, group_id: int, user_id: int):
    """
    Delete an existing group
    :param db: database session
    :param group_id: id of a group we want to delete
    :param user_id: id of user who wants to delete an existing group
    """
    searched_group = db.query(DBGroup).filter(DBGroup.id == group_id).first()

    if not searched_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    if searched_group.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User has no permission to delete group")

    db.delete(searched_group)
    db.commit()