from datetime import datetime, timezone
from db.database import Base
from sqlalchemy import Column, DateTime
from sqlalchemy.sql.sqltypes import Integer, String


class DBTag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

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
