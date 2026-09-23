from datetime import datetime, timezone
from models.post_reactions import DBPostReaction
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Boolean,
    Enum, select, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, column_property

from db.database import Base
from models.enums import PostVisibility


class DBPost(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)

    title = Column(String(200), nullable=False)

    content = Column(Text, nullable=False)

    image_url: Mapped[str | None] = mapped_column(
        String, nullable=True, info={"file_field": True}
    )

    score = Column(Integer, default=0, nullable=False)

    is_visible = Column(Boolean, default=True, nullable=False)

    visibility = Column(
        Enum(PostVisibility),
        default=PostVisibility.public,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    reactions = relationship(
        "DBPostReaction",
        foreign_keys="DBPostReaction.post_id",
        back_populates="post",
    )

    reactions_count = column_property(
        select(func.count(DBPostReaction.id))
        .where(DBPostReaction.post_id == id)
        .correlate_except(DBPostReaction)
        .scalar_subquery()
    )
