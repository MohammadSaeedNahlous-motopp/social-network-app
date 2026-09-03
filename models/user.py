from enum import Enum

from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import String, Integer, DateTime

from db.database import Base
from models.enums import Gender


class DBUser(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)

    bio = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    profile_img = Column(String, nullable=True)
    location = Column(String, nullable=True)
    gender = Column(Enum(Gender), nullable=True)

    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)