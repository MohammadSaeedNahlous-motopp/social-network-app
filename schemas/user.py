from pydantic import BaseModel, ConfigDict

from models.enums import Gender


# Full User Base/Type - Used For Creating A User
class UserBase(BaseModel):
    name: str
    email: str
    password: str
    bio: str | None = None
    phone: str | None = None
    profile_img: str | None = None
    location: str | None = None
    gender: Gender | None = None

# Update User Base/Type Without Password
class UserUpdate(BaseModel):
    name: str
    email: str
    bio: str | None = None
    phone: str | None = None
    profile_img: str | None = None
    location: str | None = None
    gender: Gender | None = None


# Display User Base/Type
class UserDisplay(BaseModel):
    name: str
    email: str
    bio: str | None = None
    phone: str | None = None
    profile_img: str | None = None
    location: str | None = None
    gender: Gender | None = None

    model_config = ConfigDict(from_attributes=True)