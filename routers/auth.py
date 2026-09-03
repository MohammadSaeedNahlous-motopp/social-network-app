from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

from db import auth
from db.database import get_db
from schemas.user import UserDisplay, UserBase, UserLogin

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserDisplay)
def create_user(request: UserBase, db: Session = Depends(get_db)):
    return auth.register_user(request, db)


@router.post("/login")
def login_user(request: UserLogin, db: Session = Depends(get_db)):
    return auth.login_user(request,db)


@router.get("/logout")
def logout_user():
    pass
