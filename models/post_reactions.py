from datetime import datetime, timezone

from sqlalchemy import Column, Enum as SQLEnum, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Integer

from db.database import Base
from models.enums import PostReactionType


class DBPostReaction(Base):
    __tablename__ = "post_reactions"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "post_id",
            name="uq_user_post_reaction",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    post_id = Column(
        Integer,
        ForeignKey("post.id"),
        nullable=False,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    reaction_type = Column(
        SQLEnum(PostReactionType),
        nullable=False,
    )

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
        back_populates="post_reactions",
    )

    post = relationship(
        "DBPost",
        back_populates="reactions",
    )
