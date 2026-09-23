from pydantic import BaseModel, ConfigDict, field_validator

from models.enums import GroupRole

class GroupMembership(BaseModel):
    id: int
    group_id: int
    user_id: int
    role: GroupRole

    model_config = ConfigDict(from_attributes=True)

    @field_validator("role", mode="before")
    @classmethod
    def extract_role_name(cls, value):
        if hasattr(value, "name"):
            return value.name
        return value