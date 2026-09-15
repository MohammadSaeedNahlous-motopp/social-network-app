from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from db.chat import get_chat_by_id
from db.chat_member import is_chat_member
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

    # searched_chat = get_chat_by_id(searched_message.chat_id, user_id,db)
    #
    # if searched_chat is None:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="Chat not found!",
    #     )

    is_member = is_chat_member(searched_message.chat_id)

    if is_member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to view this message!",
        )

    return searched_message
