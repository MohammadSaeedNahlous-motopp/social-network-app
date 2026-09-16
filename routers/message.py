from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user
from db import message
from db.database import get_db
from models.user import DBUser
from schemas.message import MessageCreate


router = APIRouter(
    prefix="/messages",
    tags=["Messages"],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a message",
    description=(
        "Creates a new message for the specified chat. "
        "The sender is automatically determined from the currently "
        "authenticated user and cannot be provided by the client."
    ),
    response_description="The newly created message.",
)
def create_message(
    request: MessageCreate,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return message.create_message(
        request,
        current_user.id,
        db,
    )


@router.get(
    "/{message_id}",
    summary="Get message by ID",
    description=(
        "Returns the specified message if it exists and the currently "
        "authenticated user has access to it."
    ),
    response_description="The requested message.",
)
def get_message_by_id(
    message_id: int,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return message.get_message_by_id(
        message_id,
        current_user.id,
        db,
    )
