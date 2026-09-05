from datetime import datetime

from pydantic import BaseModel, ConfigDict

from schemas.user import UserDisplay


# Group Base/Type - Used For Creating A User
class GroupBase(BaseModel):
    name: str
    description: str
    background_img: str | None = None
    profile_img: str | None = None
    is_public: bool

# Group view model - Used for displaying group data
class GroupView(BaseModel):
    id: int
    name: str
    description: str | None
    owner: UserDisplay
    background_img: str | None
    profile_img: str | None
    is_public: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Group update model - Used for updating group values
class GroupUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    background_img: str | None = None
    profile_img: str | None = None
    is_public: bool | None = None

# Group search model - Used for searching group based on model params
class GroupSearch(BaseModel):
    name: str | None = None
    description: str | None = None