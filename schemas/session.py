from datetime import datetime

from pydantic import BaseModel, ConfigDict
from pydantic import EmailStr

from models.enums import ChatType


class SessionBase(BaseModel):
    user_id: int
    session_hash: str | None = None
    refresh_hash: str | None = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class MessageResponse(BaseModel):
    message: str
    model_config = ConfigDict(from_attributes=True)


class SessionResponse(BaseModel):
    id: int
    user_id: int
    session_expires_at: datetime
    refresh_expires_at: datetime
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    model_config = ConfigDict(from_attributes=True)


class GetTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user_id: int
    user_email: EmailStr
    user_name: str
    model_config = ConfigDict(from_attributes=True)
