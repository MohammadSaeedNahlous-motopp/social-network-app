from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user

from db.database import get_db
from db import group
from db import group_member
from models.enums import GroupRole
from models.user import DBUser
from schemas.user import UserDisplay

router = APIRouter(prefix="/group/{group_id}", tags=["groups"])

@router.get("/members", response_model=List[tuple[UserDisplay, GroupRole]])
def get_group_members(group_id: int, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    group_members = group_member.get_group_members(db=db, group_id=group_id, requesting_user_id=current_user.id)

    return group_members

@router.get("/is_member/{user_id}")
def is_member(group_id: int, user_id: int, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if we had a permission to see user role
    searched_group = group.get_group_by_id(db=db, group_id=group_id)

    if searched_group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    if not searched_group.is_public:
        current_user_role = group_member.get_group_member_role(db=db, group_id=group_id, user_id=current_user.id)

        if not current_user_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User can't see this group")


    member_role = group_member.get_group_member_role(db=db, group_id=group_id, user_id=user_id)

    if not member_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not a group member")

    return {"is_member": True, "role": member_role}

@router.post("/join",response_model=UserDisplay)
def join_group(group_id: int, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    member = group_member.join_group(db=db, group_id=group_id, user_id=current_user.id)

    return member.user

@router.post("/leave")
def leave_group(group_id: int, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    group_member.leave_group(db=db, group_id=group_id, user_id=current_user.id)

    member_role = group_member.get_group_member_role(db=db, group_id=group_id, user_id=current_user.id)
    return {"is_member": member_role is not None}

@router.put("/change_role/{user_id}/{new_role}")
def change_role(group_id: int, user_id: int, new_role: GroupRole, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    membership = group_member.change_user_role(db=db, group_id=group_id, user_id=user_id, new_role=new_role, current_user_id=current_user.id)

    return {"updated_role": membership.role.name}