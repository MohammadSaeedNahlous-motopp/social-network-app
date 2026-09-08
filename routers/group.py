from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, responses
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user

from db.database import get_db
from db import group
from models.user import DBUser
from schemas.group import GroupView, GroupSearch, GroupBase, GroupUpdate

router = APIRouter(prefix="/groups", tags=["groups"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=GroupView)
def create_group(request_model: GroupBase, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    new_group = group.create_group(db, request_model, current_user.id)

    return new_group

@router.get("/search", status_code=status.HTTP_200_OK, response_model=List[GroupView])
def get_searched_groups(request_model: GroupSearch = Depends(), db: Session = Depends(get_db)):
    searched_groups = group.get_groups(db, request_model)

    return searched_groups

@router.get("/{group_id}", status_code=status.HTTP_200_OK, response_model=GroupView)
def get_group_by_id(group_id: int, db: Session = Depends(get_db)):
    searched_group = group.get_group_by_id(db, group_id)

    return searched_group

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[GroupView])
def get_all_groups(db: Session = Depends(get_db)):
    all_groups = group.get_all_groups(db)

    return all_groups

@router.put("/edit/{group_id}", status_code=status.HTTP_200_OK, response_model=GroupView)
def edit_group(group_id: int, request_model: GroupUpdate, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    updated_group = group.update_group(db, request_model, group_id, current_user.id)

    return updated_group

@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(group_id: int, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    group.delete_group(db, group_id, current_user.id)