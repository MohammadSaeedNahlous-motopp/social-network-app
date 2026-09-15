from datetime import datetime
from pydantic import BaseModel, ConfigDict

from models.enums import NotificationType


class NotificationCreate(BaseModel):
    user_id: int
    type: NotificationType
    message: str


class NotificationResponse(BaseModel):
    id: int
    type: NotificationType
    message: str
    created_at: datetime
    is_read: bool

    model_config = ConfigDict(from_attributes=True)
