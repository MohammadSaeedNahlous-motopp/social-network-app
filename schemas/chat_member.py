from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChatMemberCreate(BaseModel):
    user_id: int


class ChatMemberResponse(BaseModel):
    id: int
    chat_id: int
    user_id: int
    joined_at: datetime
    model_config = ConfigDict(from_attributes=True)
