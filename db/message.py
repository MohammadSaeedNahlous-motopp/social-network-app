from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.message import DBMessage
from schemas.message import MessageCreate
from service.permissions import validate_can_get_message


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

    validate_can_get_message(user_id=user_id, chat_id=searched_message.chat_id, db=db)

    return searched_message
