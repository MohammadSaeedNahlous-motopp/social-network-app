from datetime import datetime, timezone, timedelta

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from db.database import Base


class DBSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    session_hash = Column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )

    refresh_hash = Column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )

    session_expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc) + timedelta(minutes=30),
    )

    refresh_expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc) + timedelta(days=30),
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    revoked_at = Column(DateTime(timezone=True), nullable=True, default=None)
