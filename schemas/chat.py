from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChatCreate(BaseModel):
    user_ids: list[int]


class ChatResponse(BaseModel):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
