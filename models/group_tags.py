from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Integer

from db.database import Base


class DBGroupTag(Base):
    __tablename__ = "group_tags"
    __table_args__ = (
        UniqueConstraint(
            "group_id",
            "tag_id",
            name="uq_group_tag",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    group = relationship("DBGroup", back_populates="tags")

    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)
    tag = relationship("DBTag")

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
