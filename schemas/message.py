from datetime import datetime
from pydantic import BaseModel, ConfigDict


class MessageSend(BaseModel):
    recipient_id: int
    content: str


class MessageCreate(BaseModel):
    chat_id: int
    ciphertext: str
    nonce: str
    encrypted_aes_key: str


class MessageResponse(BaseModel):
    id: int
    ciphertext: str
    sender_id: int
    chat_id: int
    nonce: str
    encrypted_aes_key: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DecryptedMessageResponse(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
