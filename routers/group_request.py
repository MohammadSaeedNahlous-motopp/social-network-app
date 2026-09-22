from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user
from db import group_request
from db.database import get_db
from models.enums import RequestStatus
from models.user import DBUser
from schemas.group_request import GroupRequestDisplayBase, GroupRequestBase
from service.pagination import PaginatedResponse

router = APIRouter(
    prefix="/group-requests",
    tags=["Group Requests"],
)


@router.get(
    "/",
    response_model=PaginatedResponse[GroupRequestDisplayBase],
    status_code=status.HTTP_200_OK,
    summary="Get pending group join requests",
    description=(
        "Retrieves all pending requests to join the specified group. "
        "The authenticated user must have permission to view the group's "
        "pending join requests."
    ),
    response_description="List of pending group join requests.",
    responses={
        200: {"description": "Pending group join requests retrieved successfully."},
        401: {"description": "Authentication credentials are invalid or missing."},
        403: {
            "description": (
                "The authenticated user is not allowed to view "
                "the group's join requests."
            )
        },
        404: {"description": "The specified group was not found."},
    },
)
def get_group_pending_group_requests(
    group_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    query = group_request.get_group_pending_join_requests(
        group_id,
        current_user.id,
        db,
    )

    return PaginatedResponse.from_query(
        query=query,
        page=page,
        page_size=page_size
    )


@router.post(
    "/create",
    response_model=GroupRequestDisplayBase,
    status_code=status.HTTP_201_CREATED,
    summary="Create a group join request",
    description=(
        "Creates a request for the currently authenticated user to join "
        "the specified group. The requesting user is automatically "
        "determined from the authentication credentials and cannot be "
        "provided by the client."
    ),
    response_description="The newly created group join request.",
    responses={
        201: {"description": "Group join request created successfully."},
        400: {
            "description": (
                "The group join request could not be created because "
                "the request data is invalid or a business rule prevents "
                "creating the request."
            )
        },
        401: {"description": "Authentication credentials are invalid or missing."},
        404: {"description": "The specified group was not found."},
    },
)
async def create_group_request(
    request: GroupRequestBase,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    group_request_obj = await group_request.create_group_request(
        request,
        current_user.id,
        db,
    )

    return group_request_obj


@router.delete(
    "/{group_request_id}/decline",
    response_model=bool,
    status_code=status.HTTP_200_OK,
    summary="Decline a group join request",
    description=(
        "Declines a pending group join request. Only a group "
        "administrator is allowed to decline a request. The request "
        "is removed after it is declined."
    ),
    response_description=("True if the group join request was successfully declined."),
    responses={
        200: {"description": "Group join request declined successfully."},
        400: {
            "description": (
                "The group join request has already been processed "
                "or the request status is invalid."
            )
        },
        401: {"description": "Authentication credentials are invalid or missing."},
        403: {
            "description": (
                "The authenticated user does not have permission "
                "to decline this group join request."
            )
        },
        404: {"description": "The group join request was not found."},
    },
)
def decline_group_request(
    group_request_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    return group_request.change_group_request_status(
        group_request_id,
        current_user.id,
        RequestStatus.declined,
        db,
    )


@router.delete(
    "/{group_request_id}/accept",
    response_model=bool,
    status_code=status.HTTP_200_OK,
    summary="Accept a group join request",
    description=(
        "Accepts a pending group join request. Only a group "
        "administrator is allowed to accept a request. When accepted, "
        "the requesting user is added as a member of the group and the "
        "join request is removed."
    ),
    response_description=("True if the group join request was successfully accepted."),
    responses={
        200: {"description": "Group join request accepted successfully."},
        400: {
            "description": (
                "The group join request has already been processed "
                "or the request status is invalid."
            )
        },
        401: {"description": "Authentication credentials are invalid or missing."},
        403: {
            "description": (
                "The authenticated user does not have permission "
                "to accept this group join request."
            )
        },
        404: {"description": "The group join request was not found."},
    },
)
def accept_group_request(
    group_request_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    return group_request.change_group_request_status(
        group_request_id,
        current_user.id,
        RequestStatus.accepted,
        db,
    )


@router.delete(
    "/{group_request_id}/cancel",
    response_model=bool,
    status_code=status.HTTP_200_OK,
    summary="Cancel a group join request",
    description=(
        "Cancels a pending group join request. Only the user who "
        "created the request is allowed to cancel it. The request "
        "is removed after it is canceled."
    ),
    response_description=("True if the group join request was successfully canceled."),
    responses={
        200: {"description": "Group join request canceled successfully."},
        400: {
            "description": (
                "The group join request has already been processed "
                "or the request status is invalid."
            )
        },
        401: {"description": "Authentication credentials are invalid or missing."},
        403: {
            "description": (
                "The authenticated user is not the sender of the group join request."
            )
        },
        404: {"description": "The group join request was not found."},
    },
)
def cancel_group_request(
    group_request_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    return group_request.change_group_request_status(
        group_request_id,
        current_user.id,
        RequestStatus.canceled,
        db,
    )
