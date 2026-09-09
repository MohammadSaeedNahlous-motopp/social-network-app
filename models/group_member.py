from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Integer

from db.database import Base

class DBGroupMember(Base):
    __tablename__ = "group_members"
    __table_args__ = (
        UniqueConstraint(
            "group_id",
            "user_id",
            name="uq_group_member",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    group = relationship("DBGroup", back_populates="members")

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("DBUser", back_populates="group_memberships")

    role_id = Column(Integer, ForeignKey("group_roles.id"), nullable=False)
    role = relationship("DBGroupRole")

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
    