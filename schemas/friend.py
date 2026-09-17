from datetime import datetime

from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class FriendDisplayBase(BaseModel):
    id: int
    friend: User
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
