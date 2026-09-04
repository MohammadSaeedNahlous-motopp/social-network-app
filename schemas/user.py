from fastapi import Form, Request
from pydantic import BaseModel, ConfigDict

from models.enums import Gender


# Full User Base/Type - Used For Creating A User
class UserBase(BaseModel):
    name: str
    email: str
    password: str
    bio: str | None = None
    phone: str | None = None
    location: str | None = None
    gender: Gender = Gender.prefer_not_to_say

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        bio: str | None = Form(None),
        phone: str | None = Form(None),
        location: str | None = Form(None),
        gender: Gender = Form(Gender.prefer_not_to_say),
    ):
        return cls(
            name=name,
            email=email,
            password=password,
            bio=bio or None,
            phone=phone or None,
            location=location or None,
            gender=gender,
        )


# Update User Base/Type Without Password
class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    bio: str | None = None
    phone: str | None = None
    location: str | None = None
    gender: Gender | None = None

    @classmethod
    async def as_form(
        cls,
        request: Request,
        name: str | None = Form(None),
        email: str | None = Form(None),
        bio: str | None = Form(None),
        phone: str | None = Form(None),
        location: str | None = Form(None),
        gender: Gender | None = Form(None),
    ):
        form = await request.form()

        data = {}

        if "name" in form:
            data["name"] = name

        if "email" in form:
            data["email"] = email

        if "bio" in form:
            data["bio"] = bio or None

        if "phone" in form:
            data["phone"] = phone or None

        if "location" in form:
            data["location"] = location or None

        if "gender" in form:
            data["gender"] = gender

        return cls(**data)


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


class UserLogin(BaseModel):
    email: str
    password: str
