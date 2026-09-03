from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user
from db.database import get_db
from models.user import DBUser
from schemas.user import UserUpdate, UserDisplay
from db import user

router = APIRouter(prefix="/users", tags=["users"])

@router.put('/edit',response_model=UserDisplay)
def edit_user(request: UserUpdate, db:Session = Depends(get_db), current_user:DBUser = Depends(get_current_user)):
    updated_user = user.edit_user(
        request,
        db,
        current_user.id
    )

    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found!"
        )

    return updated_user

@router.patch("/toggle-active")
def edit_user_active_state(db:Session = Depends(get_db), current_user:DBUser = Depends(get_current_user)):
    return user.edit_user_active_state(db,current_user.id)

