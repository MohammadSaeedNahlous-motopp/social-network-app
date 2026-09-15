from datetime import datetime, timezone

from sqlalchemy import Column, Enum as SQLEnum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import String, Integer, Boolean

from db.database import Base


class DBChatMember(Base):
    __tablename__ = "chat_members"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

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

    user = relationship(
        "DBUser",
        back_populates="chat_memberships",
    )

    chat = relationship(
        "DBChat",
        back_populates="members",
    )
