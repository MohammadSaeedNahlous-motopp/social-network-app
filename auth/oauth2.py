from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from db import user
from dotenv import load_dotenv
import os

from sqlalchemy.orm.session import Session

from db.database import get_db
from db.session import get_session_by_token

load_dotenv()

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    session_token: str = Depends(oauth2_schema),
    db: Session = Depends(get_db),
):

    session = get_session_by_token(session_token, db)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    searched_user = user.get_user_by_id(db, session.user_id)

    if searched_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return searched_user
