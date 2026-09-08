from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PostCreate(BaseModel):
    title: str
    content: str


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class PostResponse(BaseModel):
    id: int
    user_id: int
    group_id: int | None = None
    title: str
    content: str
    image_url: str | None = None
    score: int
    is_visible: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
