from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CommentCreate(BaseModel):
    content: str


class CommentUpdate(BaseModel):
    content: str | None = None


class CommentResponse(BaseModel):
    id: int
    user_id: int
    post_id: int
    content: str
    is_visible: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)