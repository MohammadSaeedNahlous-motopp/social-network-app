from datetime import datetime, timezone
from sqlalchemy import Column, Enum as SQLEnum
from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Integer

from db.database import Base
from models.enums import ChatType


class DBChat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    type = Column(SQLEnum(ChatType), nullable=False, default=ChatType.private)
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

    members = relationship(
        "DBChatMember",
        back_populates="chat",
    )
