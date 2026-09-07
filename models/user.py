from datetime import datetime, timezone

from sqlalchemy import Column, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import String, Integer, Boolean

from db.database import Base
from models.enums import Gender


class DBUser(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)

    bio = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    profile_img = Column(String, nullable=True)
    location = Column(String, nullable=True)
    gender = Column(SQLEnum(Gender), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    last_login_at = Column(DateTime, nullable=True)
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

    sent_friend_requests = relationship(
        "DBFriendRequest",
        foreign_keys="DBFriendRequest.sender_id",
        back_populates="sender",
    )

    received_friend_requests = relationship(
        "DBFriendRequest",
        foreign_keys="DBFriendRequest.receiver_id",
        back_populates="receiver",
    )

    friends = relationship(
        "DBFriend", foreign_keys="DBFriend.user_id", back_populates="user"
    )
    friend_of = relationship(
        "DBFriend", foreign_keys="DBFriend.friend_id", back_populates="friend"
    )
