from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user
from db import chat
from db.database import get_db
from models.user import DBUser
from schemas.chat import ChatCreate, ChatResponse
from schemas.message import MessageResponse, DecryptedMessageResponse
from service import pagination

router = APIRouter(
    prefix="/chat",
    tags=["Chats"],
)


@router.get(
    "/",
    summary="Get user's chats",
    response_model=list[ChatResponse],
    responses={
        200: {
            "description": (
                "Successfully retrieved all chats belonging to the authenticated user."
            ),
        },
        401: {
            "description": ("Authentication credentials are invalid or missing."),
        },
    },
    description=(
        "Returns all chats that the currently authenticated user is a "
        "member of. Only chats belonging to the authenticated user are "
        "returned."
    ),
    response_description=(
        "A list of chats in which the authenticated user is a member."
    ),
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
    response_model=ChatResponse,
    responses={
        201: {
            "description": ("Chat successfully created."),
        },
        400: {
            "description": ("Invalid chat data or the chat cannot be created."),
        },
        401: {
            "description": ("Authentication credentials are invalid or missing."),
        },
    },
    description=(
        "Creates a new chat using the provided chat information. "
        "The users specified in the request are added as members of "
        "the chat. The request must contain the required chat type "
        "and user information."
    ),
    response_description=(
        "The newly created chat, including its chat information and members."
    ),
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
    response_model=pagination.PaginatedResponse[DecryptedMessageResponse],
    responses={
        200: {
            "description": ("Successfully retrieved the paginated chat messages."),
        },
        401: {
            "description": ("Authentication credentials are invalid or missing."),
        },
        403: {
            "description": (
                "The authenticated user is not a member of the requested chat."
            ),
        },
        404: {
            "description": ("The requested chat was not found."),
        },
    },
    description=(
        "Returns a paginated list of messages belonging to the specified "
        "chat. The authenticated user must be a member of the chat. "
        "Messages are returned in descending order by creation time, "
        "with the newest messages appearing first. "
        "The page parameter specifies the requested page, while the "
        "limit parameter specifies the maximum number of messages "
        "returned per page. Encrypted message content is decrypted "
        "before being included in the response."
    ),
    response_description=(
        "A paginated list of decrypted messages belonging to the specified chat."
    ),
)
def get_chat_messages(
    chat_id: int,
    page: int = Query(
        1,
        ge=1,
        description="Page number to retrieve. Starts at 1.",
    ),
    page_size: int = Query(
        10,
        ge=1,
        le=100,
        description="Number of messages per page. Maximum is 100.",
    ),
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    messages = chat.get_encrypted_chat_messages(chat_id, current_user.id, db)
    query = chat.get_decrypted_chat_messages(messages, chat_id, current_user.id, db)
    total = len(query)

    paginated_query = pagination.paginate_list(
        query=query,
        page=page,
        page_size=page_size,
    )

    items = paginated_query

    result = {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": pagination.calculate_total_pages(
            total=total,
            page_size=page_size,
        ),
    }
    return result


@router.get(
    "/private/{user_id}",
    summary="Get private chat",
    response_model=ChatResponse,
    responses={
        200: {
            "description": ("Successfully retrieved the private chat."),
        },
        401: {
            "description": ("Authentication credentials are invalid or missing."),
        },
        404: {
            "description": (
                "No private chat exists between the authenticated user "
                "and the specified user."
            ),
        },
    },
    description=(
        "Returns the private one-to-one chat between the currently "
        "authenticated user and the specified user. Authentication "
        "is required. The endpoint searches for an existing private "
        "chat shared by the two users."
    ),
    response_description=(
        "The private chat shared by the authenticated user and the specified user."
    ),
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
    response_model=ChatResponse,
    responses={
        200: {
            "description": ("Successfully retrieved the requested chat."),
        },
        401: {
            "description": ("Authentication credentials are invalid or missing."),
        },
        403: {
            "description": (
                "The authenticated user does not have access to the requested chat."
            ),
        },
        404: {
            "description": ("The requested chat was not found."),
        },
    },
    description=(
        "Returns a specific chat by its ID. Authentication is required, "
        "and the currently authenticated user must have access to the "
        "requested chat."
    ),
    response_description=("The requested chat and its associated information."),
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
