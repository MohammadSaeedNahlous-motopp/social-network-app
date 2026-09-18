from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Integer

from db.database import Base
from models.enums import RequestStatus


class DBGroupRequest(Base):
    __tablename__ = "group_requests"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    sender_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    group_id = Column(
        Integer,
        ForeignKey("groups.id"),
        nullable=False,
    )

    status = Column(
        SQLEnum(RequestStatus),
        nullable=False,
        default=RequestStatus.pending,
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

    sender = relationship(
        "DBUser",
        foreign_keys=[sender_id],
        back_populates="sent_group_requests",
    )

    group = relationship(
        "DBGroup",
        foreign_keys=[group_id],
        back_populates="group_requests",
    )
