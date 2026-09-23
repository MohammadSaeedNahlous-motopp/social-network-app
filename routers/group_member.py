from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user

from db.database import get_db
from db import group
from db import group_member
from models.enums import GroupRole
from models.user import DBUser
from schemas.group_member import GroupMembership
from schemas.group_request import GroupRequestDisplayBase
from schemas.user import UserDisplay
from service.pagination import PaginatedResponse

router = APIRouter(prefix="/group/{group_id}", tags=["groups"])


@router.get(
    "/members",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedResponse[tuple[UserDisplay, GroupRole]],
)
def get_group_members(
    group_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(0, ge=0),
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = group_member.get_group_members(
        db=db, group_id=group_id, requesting_user_id=current_user.id
    )

    return PaginatedResponse.from_query(query=query, page=page, page_size=page_size)


@router.get("/is_member/{user_id}", status_code=status.HTTP_200_OK)
def is_member(
    group_id: int,
    user_id: int,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Check if we had a permission to see user role
    searched_group = group.get_group_by_id(db=db, group_id=group_id)

    if searched_group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Group not found"
        )

    if not searched_group.is_public:
        current_user_role = group_member.get_group_member_role(
            db=db, group_id=group_id, user_id=current_user.id
        )

        if not current_user_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User can't see this group",
            )

    member_role = group_member.get_group_member_role(
        db=db, group_id=group_id, user_id=user_id
    )

    if not member_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not a group member"
        )

    return {"is_member": True, "role": member_role}


@router.post(
    "/join",
    response_model=GroupMembership | GroupRequestDisplayBase,
    status_code=status.HTTP_201_CREATED,
    summary="Joins a public group or creates a group join request for private one",
    description=(
            "Creates a request for the currently authenticated user to join "
            "the specified group. The requesting user is automatically "
            "determined from the authentication credentials and cannot be "
            "provided by the client."
    ),
    response_description="The User model or the newly created group join request.",
    responses={
        201: {"description": "User joins a public group or group join request created successfully."},
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
def join_group(
    group_id: int,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = group_member.join_group(db=db, group_id=group_id, user_id=current_user.id)

    return result


@router.post("/leave", status_code=status.HTTP_204_NO_CONTENT)
def leave_group(
    group_id: int,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    group_member.leave_group(db=db, group_id=group_id, user_id=current_user.id)

    member_role = group_member.get_group_member_role(
        db=db, group_id=group_id, user_id=current_user.id
    )
    return {"is_member": member_role is not None}


@router.put("/change_role/{user_id}/{new_role}", status_code=status.HTTP_200_OK)
def change_role(
    group_id: int,
    user_id: int,
    new_role: GroupRole,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    membership = group_member.change_user_role(
        db=db,
        group_id=group_id,
        user_id=user_id,
        new_role=new_role,
        current_user_id=current_user.id,
    )

    return {"updated_role": membership.role.name}
