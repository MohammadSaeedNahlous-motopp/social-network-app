from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum as SQLEnum
from sqlalchemy.sql.sqltypes import Integer

from db.database import Base
from models.enums import GroupRole

class DBGroupRole(Base):
    __tablename__ = "group_roles"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(SQLEnum(GroupRole), default=GroupRole.member, nullable=False, unique=True)

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
