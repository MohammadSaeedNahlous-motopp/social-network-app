from datetime import datetime, timezone
from sqlalchemy import Enum as SQLEnum, ForeignKey, Boolean
from sqlalchemy import Column, DateTime, String

from sqlalchemy.sql.sqltypes import Integer

from db.database import Base
from models.enums import NotificationType


class DBNotification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(SQLEnum(NotificationType), nullable=False)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
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
