from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user
from db import message
from db.database import get_db
from models.user import DBUser
from schemas.message import MessageCreate, MessageResponse, DecryptedMessageResponse

router = APIRouter(
    prefix="/messages",
    tags=["Messages"],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a message",
    response_model=MessageResponse,
    responses={
        201: {
            "description": ("Message successfully created and stored."),
        },
        400: {
            "description": ("Invalid message data or the message cannot be created."),
        },
        401: {
            "description": ("Authentication credentials are invalid or missing."),
        },
        403: {
            "description": (
                "The authenticated user is not allowed to send a message "
                "in the specified chat."
            ),
        },
        404: {
            "description": ("The specified chat or recipient was not found."),
        },
    },
    description=(
        "Creates a new message for the specified chat. "
        "The sender is automatically determined from the currently "
        "authenticated user and cannot be provided by the client. "
        "The message is associated with the authenticated user as its "
        "sender. Access to the chat is validated before the message "
        "is created."
    ),
    response_description=("The newly created message."),
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
    response_model=DecryptedMessageResponse,
    responses={
        200: {
            "description": ("Successfully retrieved the requested message."),
        },
        401: {
            "description": ("Authentication credentials are invalid or missing."),
        },
        403: {
            "description": (
                "The authenticated user does not have access to this message."
            ),
        },
        404: {
            "description": ("The requested message was not found."),
        },
    },
    description=(
        "Returns a specific message by its ID. "
        "Authentication is required. The authenticated user's access "
        "to the message is validated before the message is returned."
    ),
    response_description=("The requested message."),
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
