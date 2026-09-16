from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user
from db import chat_member
from db.database import get_db
from models.user import DBUser
from schemas.chat_member import ChatMemberCreate


router = APIRouter(
    prefix="/chat-member",
    tags=["Chat Members"],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Add members to a chat",
    description=(
        "Adds the specified users as members of the selected chat. "
        "The chat ID identifies the chat to which the users will be added."
    ),
    response_description="The newly created chat member records.",
)
def create_chat_member(
    request: ChatMemberCreate,
    chat_id: int,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    add_commit: bool = True,
):
    return chat_member.create_chat_member(
        request,
        chat_id,
        db,
        add_commit,
    )


@router.get(
    "/{chat_id}",
    summary="Get chat members",
    description=("Returns all members belonging to the specified chat."),
    response_description="A list of members belonging to the chat.",
)
def get_chat_members_by_chat_id(
    chat_id: int,
    db: Session = Depends(get_db),
):
    return chat_member.get_chat_members_by_chat_id(
        chat_id,
        db,
    )
