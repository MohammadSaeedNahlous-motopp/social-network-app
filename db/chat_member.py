from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.chat_member import DBChatMember
from models.chat import DBChat
from schemas.chat_member import ChatMemberCreate


def create_chat_member(
    request: ChatMemberCreate, chat_id: int, db: Session, add_commit: bool = True
):
    searched_chat = db.query(DBChat).filter(DBChat.id == chat_id).first()

    if searched_chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found!",
        )

    new_chat_member = DBChatMember(user_id=request.user_id, chat_id=chat_id)

    db.add(new_chat_member)

    if add_commit:
        db.commit()
        db.refresh(new_chat_member)

    return new_chat_member


def is_chat_member(chat_id: int, user_id: int, db: Session):
    membership = (
        db.query(DBChatMember)
        .filter(
            DBChatMember.chat_id == chat_id,
            DBChatMember.user_id == user_id,
        )
        .first()
    )

    return membership is not None


def get_chat_members_by_chat_id(chat_id: int, db: Session):
    searched_chat = db.query(DBChat).filter(DBChat.id == chat_id).first()

    if searched_chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found!",
        )

    chat_memberships = db.query(DBChatMember).filter(DBChatMember.chat_id == chat_id)

    return chat_memberships
