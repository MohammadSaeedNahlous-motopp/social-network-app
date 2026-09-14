from datetime import datetime, timezone

from sqlalchemy import Column, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Integer

from db.database import Base


class DBChat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)

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
        "ChatMember",
        back_populates="chat",
    )
