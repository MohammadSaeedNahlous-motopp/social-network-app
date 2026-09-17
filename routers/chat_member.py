from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user
from db import chat_member
from db.database import get_db
from models.user import DBUser
from schemas.chat_member import ChatMemberCreate, ChatMemberResponse

router = APIRouter(
    prefix="/chat-member",
    tags=["Chat Members"],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Add members to a chat",
    response_model=ChatMemberResponse,
    responses={
        201: {
            "description": ("Chat member successfully added to the chat."),
        },
        400: {
            "description": ("Invalid chat member data or the user cannot be added."),
        },
        401: {
            "description": ("Authentication credentials are invalid or missing."),
        },
        404: {
            "description": ("The specified chat or user was not found."),
        },
    },
    description=(
        "Adds the specified user or users as members of an existing chat. "
        "The chat_id identifies the chat to which the members will be added. "
        "The request body contains the user information required to create "
        "the chat membership. "
        "A chat member record is created and returned after the operation "
        "is successfully completed."
    ),
    response_description=("The newly created chat member record."),
)
def create_chat_member(
    request: ChatMemberCreate,
    chat_id: int,
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
    response_model=list[ChatMemberResponse],
    responses={
        200: {
            "description": ("Successfully retrieved all members of the chat."),
        },
        401: {
            "description": ("Authentication credentials are invalid or missing."),
        },
        404: {
            "description": ("The specified chat was not found."),
        },
    },
    description=(
        "Returns all members belonging to the specified chat. "
        "The chat_id identifies the chat whose membership records "
        "should be retrieved. "
        "The response contains the users associated with the chat "
        "through their chat membership records."
    ),
    response_description=(
        "A list of chat member records belonging to the specified chat."
    ),
)
def get_chat_members_by_chat_id(
    chat_id: int,
    db: Session = Depends(get_db),
):
    return chat_member.get_chat_members_by_chat_id(
        chat_id,
        db,
    )
