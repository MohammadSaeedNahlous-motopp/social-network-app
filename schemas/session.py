from datetime import datetime

from pydantic import BaseModel, ConfigDict

from models.enums import ChatType


class SessionBase(BaseModel):
    user_id: int
    session_hash: str | None = None
    refresh_hash: str | None = None


class SessionResponse(BaseModel):
    id: int
    user_id: int
    session_expires_at: datetime
    refresh_expires_at: datetime
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    session_token: str
    refresh_token: str
