from datetime import datetime

from pydantic import BaseModel, ConfigDict

from models.enums import PostReactionType


class User(BaseModel):
    id: int
    name: str
    profile_img: str | None

    model_config = ConfigDict(from_attributes=True)


class PostReactionCreate(BaseModel):
    reaction_type: PostReactionType


class PostReactionResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    user: User
    reaction_type: PostReactionType
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
