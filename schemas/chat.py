from datetime import datetime

from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    id: int
    name: str
    profile_img: str | None

    model_config = ConfigDict(from_attributes=True)


class ChatCreate(BaseModel):
    user_ids: list[int]
    name: str
    description: str


class ChatResponse(BaseModel):
    id: int
    created_at: datetime
    name: str
    description: str
    members: [User]

    model_config = ConfigDict(from_attributes=True)
