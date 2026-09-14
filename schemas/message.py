from datetime import datetime
from pydantic import BaseModel, ConfigDict


class MessageCreate(BaseModel):
    chat_id: int
    content: str


class MessageResponse(BaseModel):
    id: int
    content: str
    sender_id: int
    chat_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
