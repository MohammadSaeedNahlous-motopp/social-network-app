import hashlib
import secrets
from datetime import datetime, timezone, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.session import DBSession


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)


def create_session(user_id: int, db: Session):
    session_token = secrets.token_urlsafe(32)
    refresh_token = secrets.token_urlsafe(32)

    session_hash = hash_token(session_token)
    refresh_hash = hash_token(refresh_token)

    new_session = DBSession(
        user_id=user_id,
        session_hash=session_hash,
        refresh_hash=refresh_hash,
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return new_session, session_token, refresh_token


def get_session_by_token(session_token: str, db: Session):

    session_hash = hash_token(session_token)

    searched_session = (
        db.query(DBSession).filter(DBSession.session_hash == session_hash).first()
    )

    return searched_session


def refresh_session(refresh_token: str, db: Session):
    refresh_hash = hash_token(refresh_token)

    searched_session = (
        db.query(DBSession).filter(DBSession.refresh_hash == refresh_hash).first()
    )

    if searched_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if searched_session.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Session has been revoked",
        )

    now = datetime.now(timezone.utc)

    refresh_expires_at = ensure_utc(searched_session.refresh_expires_at)

    if refresh_expires_at <= now:
        searched_session.revoked_at = now
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Session expired",
        )

    session_token = secrets.token_urlsafe(32)
    session_hash = hash_token(session_token)

    searched_session.session_hash = session_hash
    searched_session.session_expires_at = now + timedelta(minutes=30)

    db.commit()
    db.refresh(searched_session)

    return searched_session, session_token, refresh_token


def revoke_session(session_token: str, db: Session):
    session_hash = hash_token(session_token)

    session = db.query(DBSession).filter(DBSession.session_hash == session_hash).first()

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if session.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Session has already been revoked",
        )

    session.revoked_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(session)

    return session


def revoke_all_sessions(user_id: int, db: Session):
    user_sessions = db.query(DBSession).filter(DBSession.user_id == user_id).all()

    now = datetime.now(timezone.utc)

    for session in user_sessions:
        if session.revoked_at is None:
            session.revoked_at = now

    db.commit()

    return True
