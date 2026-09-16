from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from db.chat_member import (
    create_chat_member,
    is_chat_member,
    get_chat_members_by_chat_id,
)
from db.user import get_user_by_id
from models.chat import DBChat
from models.chat_member import DBChatMember
from models.enums import ChatType
from models.message import DBMessage
from schemas.chat import ChatCreate
from schemas.chat_member import ChatMemberCreate
from sqlalchemy import and_, func

from service.encryption_methods import decrypt_chat_message
from service.pagination import paginate


def create_chat(request: ChatCreate, db: Session):

    for user_id in request.user_ids:
        searched_user = get_user_by_id(db, user_id)
        if not searched_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found!",
            )
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

    is_member = is_chat_member(chat_id, user_id, db)

    if is_member is None:
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


def get_chat_messages(chat_id: int, user_id: int, page: int, limit: int, db: Session):
    is_member = is_chat_member(chat_id, user_id, db)

    if is_member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to view these messages!",
        )
    chat = get_chat_by_id(chat_id, user_id, db)
    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat Not Found!",
        )
    messages = (
        db.query(DBMessage)
        .filter(DBMessage.chat_id == chat_id)
        .order_by(DBMessage.created_at.desc())
    )

    messages = paginate(messages, page, limit)

    result = []

    members = get_chat_members_by_chat_id(chat_id, db)

    for message in messages:
        recipient_id = next(
            member.user_id for member in members if member.user_id != message.sender_id
        )

        recipient = get_user_by_id(recipient_id, db)

        decrypted_message = decrypt_chat_message(
            message,
            recipient,
        )

        result.append(
            {
                "id": message.id,
                "chat_id": message.chat_id,
                "sender_id": message.sender_id,
                "content": decrypted_message,
                "created_at": message.created_at,
            }
        )

    return result
