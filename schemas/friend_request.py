from pydantic import BaseModel, ConfigDict

from models.enums import FriendRequestStatus
from models.user import DBUser


class User(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class FriendRequestBase(BaseModel):
    receiver_id: int


class FriendRequestDisplayBase(BaseModel):
    id: int
    receiver: User
    sender: User
    status: FriendRequestStatus

    model_config = ConfigDict(from_attributes=True)
