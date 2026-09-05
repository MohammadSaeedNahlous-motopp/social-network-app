from pydantic import BaseModel, ConfigDict

from models.enums import FriendRequestStatus
from models.user import DBUser


class User(BaseModel):
    id:int
    name:str
    email:str

    model_config = ConfigDict(from_attributes=True)


class FriendRequestBase(BaseModel):
    receiver_id:int

class FriendRequestSDisplayBase(BaseModel):
    receiver:User
    sender:User
    status:FriendRequestStatus
