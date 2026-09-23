from pydantic import BaseModel, ConfigDict


class TagBase(BaseModel):
    name: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)


class TagView(TagBase):
    id: int
    name: str
    description: str | None
