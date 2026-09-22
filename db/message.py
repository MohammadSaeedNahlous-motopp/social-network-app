from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from db.chat import get_chat_by_id
from db.chat_member import is_chat_member, get_chat_members_by_chat_id
from db.user import get_user_by_id
from models.chat import DBChat
from models.chat_member import DBChatMember
from models.message import DBMessage
from schemas.message import MessageCreate
from service.encryption_methods import decrypt_chat_message
from service.permissions import validate_can_get_message


def create_message(request: MessageCreate, user_id: int, db: Session):
    new_message = DBMessage(
        chat_id=request.chat_id,
        ciphertext=request.ciphertext,
        nonce=request.nonce,
        encrypted_aes_key=request.encrypted_aes_key,
        sender_id=user_id,
    )

    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return new_message


def get_message_by_id(message_id: int, user_id: int, db: Session):
    searched_message = db.query(DBMessage).filter(DBMessage.id == message_id).first()

    if searched_message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found!",
        )

    validate_can_get_message(user_id=user_id, chat_id=searched_message.chat_id, db=db)

    members = get_chat_members_by_chat_id(
        searched_message.chat_id,
        db,
    )





    recipient_id = next(
        member.user_id
        for member in members
        if member.user_id != searched_message.sender_id
    )

    recipient = get_user_by_id(db, recipient_id)

    decrypted_message = decrypt_chat_message(
        searched_message,
        recipient.encrypted_private_key,
    )

    return {
        "id": searched_message.id,
        "chat_id": searched_message.chat_id,
        "sender_id": searched_message.sender_id,
        "content": decrypted_message,
        "created_at": searched_message.created_at,
    }
