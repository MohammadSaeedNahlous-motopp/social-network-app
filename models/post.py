from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class DBPost(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)

    title = Column(String(200), nullable=False)

    content = Column(Text, nullable=False)

    image_url: Mapped[str | None] = mapped_column(String, nullable=True)

    score = Column(Integer, default=0, nullable=False)

    is_visible = Column(Boolean, default=True, nullable=False)

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
