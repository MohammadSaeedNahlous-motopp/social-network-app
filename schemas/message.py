from datetime import datetime
from pydantic import BaseModel, ConfigDict


class MessageCreate(BaseModel):
    chat_id: int
    text: str


class MessageResponse(BaseModel):
    id: int
    text: str
    sender_id: int
    chat_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
