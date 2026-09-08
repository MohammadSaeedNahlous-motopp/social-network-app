from datetime import datetime, timezone
from sqlalchemy import Column, Enum as SQLEnum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import String, Integer, Boolean
from db.database import Base
from models.enums import FriendRequestStatus


class DBFriendRequest(Base):
    __tablename__ = "friend_requests"
    id = Column(Integer, unique=True, primary_key=True, index=True)
    sender_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )
    receiver_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )
    status = Column(
        SQLEnum(FriendRequestStatus), nullable=False, default=FriendRequestStatus.pending
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

    sender = relationship(
        "DBUser", foreign_keys=[sender_id], back_populates="sent_friend_requests"
    )
    receiver = relationship(
        "DBUser", foreign_keys=[receiver_id], back_populates="received_friend_requests"
    )
