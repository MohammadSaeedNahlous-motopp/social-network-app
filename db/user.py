from datetime import datetime, timezone

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth import oauth2
from db.hash import Hash
from models.user import DBUser
from schemas.user import UserBase, UserUpdate


def get_user_by_email(db: Session, email: str):
    return db.query(DBUser).filter(DBUser.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(DBUser).filter(DBUser.id == user_id).first()


def get_token(
    db: Session,
    request: OAuth2PasswordRequestForm,
):
    searched_user = get_user_by_email(db, request.username)

    if not searched_user or not Hash.verify(
        searched_user.password,
        request.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    searched_user.last_login_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(searched_user)

    access_token = oauth2.create_access_token(data={"sub": str(searched_user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": searched_user.id,
        "user_email": searched_user.email,
        "user_name": searched_user.name,
    }


def register_user(
    request: UserBase,
    db: Session,
    image_path: str | None,
):
    user_with_same_email = get_user_by_email(
        db,
        request.email,
    )

    if user_with_same_email is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    if request.password != request.repeat_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords don't match",
        )

    new_user = DBUser(
        name=request.name,
        password=Hash.hash(request.password),
        email=request.email,
        bio=request.bio,
        phone=request.phone,
        profile_img=image_path,
        location=request.location,
        gender=request.gender,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def edit_user(
    request: UserUpdate,
    image_path: str | None,
    db: Session,
    user_id: int,
    remove_profile_img: bool = False,
):
    searched_user = get_user_by_id(db, user_id)

    if not searched_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found!",
        )

    if request.email is not None:
        user_with_same_email = (
            db.query(DBUser)
            .filter(
                DBUser.email == request.email,
                DBUser.id != user_id,
            )
            .first()
        )

        if user_with_same_email is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered!",
            )

    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(searched_user, key, value)

    if remove_profile_img:
        searched_user.profile_img = None
    elif image_path is not None:
        searched_user.profile_img = image_path

    db.commit()
    db.refresh(searched_user)

    return searched_user


def edit_user_active_state(
    db: Session,
    user_id: int,
):
    searched_user = get_user_by_id(db, user_id)

    if not searched_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found!",
        )

    searched_user.is_active = not searched_user.is_active

    db.commit()
    db.refresh(searched_user)

    return {
        "is_active": searched_user.is_active,
    }
