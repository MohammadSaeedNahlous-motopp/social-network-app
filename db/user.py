from fastapi import HTTPException, status

from sqlalchemy.orm.session import Session

from db.hash import Hash
from models.user import DBUser
from schemas import user


def register_user(request: user.UserBase, db: Session):
    user_with_same_email = get_user_by_email(db, request.email)
    if user_with_same_email is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    new_user = DBUser(
        name=request.name,
        password=Hash.hash(request.password),
        email=request.email,
        bio=request.bio,
        phone=request.phone,
        profile_img=request.profile_img,
        location=request.location,
        gender=request.gender,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def login_user(request: user.UserLogin, db: Session):
    searched_user = db.query(DBUser).filter(DBUser.email == request.email).first()

    if not searched_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    verified_password = Hash.verify(searched_user.password, request.password)

    if not verified_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    return {"message": "Success!"}


def get_user_by_email(db: Session, email: str):
    searched_user = db.query(DBUser).filter(DBUser.email == email).first()

    return searched_user

def edit_user(request: user.UserUpdate, db: Session, user_id: int):
    searched_user = db.query(DBUser).filter(
        DBUser.id == user_id
    ).first()

    if searched_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found!"
        )

    for key, value in request.model_dump().items():
        setattr(searched_user, key, value)

    db.commit()
    db.refresh(searched_user)

    return searched_user

def edit_user_active_state(db: Session, user_id: int):
    searched_user = db.query(DBUser).filter(
        DBUser.id == user_id
    ).first()

    if searched_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found!"
        )

    searched_user.is_active = not searched_user.is_active

    db.commit()
    db.refresh(searched_user)

    return {
        "is_active":searched_user.is_active
    }