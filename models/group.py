from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer, Boolean

from db.database import Base

class DBGroup(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id"))

    background_img = Column(String, nullable=True)
    profile_img = Column(String, nullable=True)

    is_public = Column(Boolean, nullable=False, default=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )