from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from db.chat_member import create_chat_member
from db.user import get_user_by_id
from models.chat import DBChat
from models.chat_member import DBChatMember
from models.enums import ChatType
from models.message import DBMessage
from schemas.chat import ChatCreate
from schemas.chat_member import ChatMemberCreate
from sqlalchemy import and_, func


def create_chat(request: ChatCreate, db: Session):
    new_chat = DBChat(
        name=request.name, description=request.description, type=request.type
    )

    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    for user_id in request.user_ids:
        create_chat_member(ChatMemberCreate(user_id=user_id), new_chat.id, db, False)

    db.commit()

    return new_chat


def get_chat_by_id(chat_id: int, user_id: int, db: Session):
    searched_chat = db.query(DBChat).filter(DBChat.id == chat_id).first()

    if searched_chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found!",
        )

    is_chat_member = (
        db.query(DBChatMember)
        .filter(DBChatMember.chat_id == chat_id, DBChatMember.user_id == user_id)
        .first()
    )

    if is_chat_member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to view this chat!",
        )

    return searched_chat


def get_private_chat(user_id: int, recipient_id: int, db: Session):
    searched_user = get_user_by_id(db, user_id)

    if not searched_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found!",
        )

    searched_chat = (
        db.query(DBChat)
        .join(DBChatMember)
        .filter(
            DBChat.type == ChatType.private,
            DBChatMember.user_id.in_([user_id, recipient_id]),
        )
        .group_by(DBChat.id)
        .having(func.count(DBChatMember.user_id) == 2)
        .first()
    )

    return searched_chat


def get_user_chats(user_id: int, db: Session):
    chat_list = []
    chat_memberships = (
        db.query(DBChatMember).filter(DBChatMember.user_id == user_id).all()
    )
    for chat_membership in chat_memberships:
        searched_chat = get_chat_by_id(chat_membership.chat_id, user_id, db)
        chat_list.append(
            {
                "id": chat_membership.chat_id,
                "name": searched_chat.name,
                "description": searched_chat.description,
                "members": [member.user for member in searched_chat.members],
            }
        )
    return chat_list


def get_chat_messages(chat_id: int, user_id: int, db: Session):
    searched_chat = db.query(DBChat).filter(DBChat.id == chat_id).first()

    if searched_chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found!",
        )

    is_chat_member = (
        db.query(DBChatMember)
        .filter(DBChatMember.chat_id == chat_id, DBChatMember.user_id == user_id)
        .first()
    )

    if is_chat_member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to view these messages!",
        )

    messages = db.query(DBMessage).filter(DBMessage.chat_id == chat_id).all()

    return messages
