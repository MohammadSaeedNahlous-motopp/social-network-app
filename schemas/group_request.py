from pydantic import BaseModel, ConfigDict

from models.enums import RequestStatus


class User(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class Group(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class GroupRequestDisplayBase(BaseModel):
    id: int
    group: Group
    sender: User
    status: RequestStatus

    model_config = ConfigDict(from_attributes=True)
