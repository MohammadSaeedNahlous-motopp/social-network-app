from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth import oauth2
from db.database import get_db
from db.hash import Hash
from models.user import DBUser
from schemas.user import UserDisplay, UserBase, UserLogin
from db import user

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login")
def get_token(
    request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(DBUser).filter(DBUser.email == request.username).first()

    if not user or not Hash.verify(user.password, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = oauth2.create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "user_email": user.email,
        "user_name": user.name,
    }


@router.post("/register", response_model=UserDisplay)
def create_user(request: UserBase, db: Session = Depends(get_db)):
    return user.register_user(request, db)


@router.post("/logout")
def logout_user():
    return {"message": "Successfully logged out"}
