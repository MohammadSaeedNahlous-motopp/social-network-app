from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import String, Integer, Boolean

from db.database import Base

class DBGroup(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("DBUser", back_populates="groups")

    background_img = Column(String, nullable=True)
    profile_img = Column(String, nullable=True)

    is_public = Column(Boolean, nullable=False, default=True)

    members = relationship("DBGroupMember", back_populates="group", cascade="all, delete-orphan")

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )