from datetime import datetime

from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    id: int
    name: str
    profile_img: str | None

    model_config = ConfigDict(from_attributes=True)


class ChatMemberCreate(BaseModel):
    user_id: int


class ChatMemberResponse(BaseModel):
    id: int
    chat_id: int
    user_id: int
    created_at: datetime
    user: User
    model_config = ConfigDict(from_attributes=True)
