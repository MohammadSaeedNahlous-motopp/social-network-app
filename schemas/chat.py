from datetime import datetime

from pydantic import BaseModel, ConfigDict

from models.enums import ChatType


class User(BaseModel):
    id: int
    name: str
    profile_img: str | None

    model_config = ConfigDict(from_attributes=True)


class ChatCreate(BaseModel):
    user_ids: list[int]
    name: str | None = None
    description: str | None = None
    type: ChatType


class ChatResponse(BaseModel):
    id: int
    created_at: datetime
    name: str | None = None
    description: str | None = None
    type: ChatType
    members: list[User]

    model_config = ConfigDict(from_attributes=True)
