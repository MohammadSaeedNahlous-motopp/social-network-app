from fastapi import Form, Request

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from schemas.user import UserDisplay


# Group Base/Type - Used For Creating A User
class GroupBase(BaseModel):
    name: str
    description: str | None = None
    is_public: bool
    tags: list[int] | None = None

    @classmethod
    async def as_form(
        cls,
        request: Request,
        name: str = Form(...),
        is_public: bool = Form(...),
        description: str | None = Form(None),
        tags: str | None = Form(None),
    ):

        form = await request.form()

        data = {}
        if "name" in form:
            data["name"] = name

        if "description" in form:
            data["description"] = description

        if "is_public" in form:
            data["is_public"] = is_public

        if "tags" in form:
            data["tags"] = (
                [int(tag.strip()) for tag in tags.split(",")] if tags else None
            )

        return cls(**data)


# Group view model - Used for displaying group data
class GroupView(BaseModel):
    id: int
    name: str
    description: str | None
    owner: UserDisplay
    is_public: bool
    created_at: datetime
    tags: list[TagView] = Field(validation_alias="tag_list")

    model_config = ConfigDict(from_attributes=True)


# Group update model - Used for updating group values
class GroupUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_public: bool | None = None

    @classmethod
    async def as_form(
        cls,
        request: Request,
        name: str | None = Form(None),
        is_public: bool | None = Form(None),
        description: str | None = Form(None),
    ):
        form = await request.form()

        data = {}
        if "name" in form:
            data["name"] = name

        if "description" in form:
            data["description"] = description

        if "is_public" in form:
            data["is_public"] = is_public

        return cls(**data)


# Group search model - Used for searching group based on model params
class GroupSearch(BaseModel):
    name: str | None = None
    description: str | None = None
    tag_ids: str | None = None


class TagView(BaseModel):
    id: int
    name: str
    description: str | None = None
