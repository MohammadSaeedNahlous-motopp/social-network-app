from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user
from db import chat
from db.database import get_db
from models.user import DBUser
from schemas.chat import ChatCreate


router = APIRouter(
    prefix="/chat",
    tags=["Chats"],
)


@router.get(
    "/",
    summary="Get user's chats",
    description=(
        "Returns all chats that the currently authenticated user is a member of."
    ),
    response_description="A list of chats belonging to the current user.",
)
def get_user_chats(
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return chat.get_user_chats(
        current_user.id,
        db,
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a chat",
    description=(
        "Creates a new chat using the provided chat information. "
        "The users included in the request will be added as chat members."
    ),
    response_description="The newly created chat.",
)
def create_chat(
    request: ChatCreate,
    db: Session = Depends(get_db),
):
    return chat.create_chat(
        request,
        db,
    )


@router.get(
    "/messages/{chat_id}",
    summary="Get chat messages",
    description=("Returns all messages belonging to the specified chat."),
    response_description="A list of messages in the specified chat.",
)
def get_chat_messages(
    chat_id: int,
    page: int,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    return chat.get_chat_messages(
        chat_id,
        current_user.id,
        page,
        limit,
        db,
    )


@router.get(
    "/private/{user_id}",
    summary="Get private chat",
    description=(
        "Returns the private chat between the currently authenticated user "
        "and the specified user."
    ),
    response_description="The private chat between the two users.",
)
def get_private_chat(
    user_id: int,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return chat.get_private_chat(
        user_id,
        current_user.id,
        db,
    )


@router.get(
    "/{chat_id}",
    summary="Get chat by ID",
    description=(
        "Returns the specified chat if the currently authenticated user "
        "has access to it."
    ),
    response_description="The requested chat.",
)
def get_chat_by_id(
    chat_id: int,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return chat.get_chat_by_id(
        chat_id,
        current_user.id,
        db,
    )
