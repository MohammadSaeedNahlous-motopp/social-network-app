from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.chat import DBChat
from models.chat_member import DBChatMember
from models.message import DBMessage
from schemas.message import MessageCreate


def create_message(request: MessageCreate, user_id: int, db: Session):
    new_message = DBMessage(
        chat_id=request.chat_id, content=request.content, sender_id=user_id
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

    searched_chat = (
        db.query(DBChat).filter(DBChat.id == searched_message.chat_id).first()
    )

    if searched_chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found!",
        )

    is_a_chat_member = (
        db.query(DBChatMember)
        .filter(
            DBChatMember.user_id == user_id,
            DBChatMember.chat_id == searched_message.chat_id,
        )
        .first()
    )

    if is_a_chat_member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to view this message!",
        )

    return searched_message


def get_message_by_id(message_id: int, user_id: int, db: Session):
    searched_message = db.query(DBMessage).filter(DBMessage.id == message_id).first()

    if searched_message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found!",
        )

    searched_chat = (
        db.query(DBChat).filter(DBChat.id == searched_message.chat_id).first()
    )

    if searched_chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found!",
        )

    is_a_chat_member = (
        db.query(DBChatMember)
        .filter(
            DBChatMember.user_id == user_id,
            DBChatMember.chat_id == searched_message.chat_id,
        )
        .first()
    )

    if is_a_chat_member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to view this message!",
        )

    return searched_message
