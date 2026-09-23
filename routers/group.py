from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    responses,
    UploadFile,
    File,
    Query,
)
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user

from db.database import get_db
from db import group
from models.enums import ImageType
from models.user import DBUser
from schemas.group import GroupView, GroupSearch, GroupBase, GroupUpdate
from service.image import save_image
from service.pagination import PaginatedResponse

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=GroupView)
async def create_group(
    request_model: GroupBase = Depends(GroupBase.as_form),
    group_img: UploadFile | None = File(None),
    group_background_img: UploadFile | None = File(None),
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    group_img_path = None

    if group_img is not None:
        group_img_path = await save_image(group_img, ImageType.group_picture)

    group_background_img_path = None

    if group_background_img is not None:
        group_background_img_path = await save_image(
            group_background_img, ImageType.group_background_picture
        )

    new_group = group.create_group(
        db, request_model, current_user.id, group_img_path, group_background_img_path
    )

    return new_group


@router.get(
    "/search",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedResponse[GroupView],
)
def get_searched_groups(
    request_model: GroupSearch = Depends(),
    page: int = Query(1, ge=1),
    page_size: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    tag_id_list: list[int] | None = (
        [int(tag.strip()) for tag in request_model.tag_ids.split(",")]
        if request_model.tag_ids
        else None
    )

    query = group.get_groups(db=db, request_model=request_model, tags=tag_id_list)

    return PaginatedResponse.from_query(query=query, page=page, page_size=page_size)


@router.get("/{group_id}", status_code=status.HTTP_200_OK, response_model=GroupView)
def get_group_by_id(group_id: int, db: Session = Depends(get_db)):
    searched_group = group.get_group_by_id(db, group_id)

    return searched_group


@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=PaginatedResponse[GroupView]
)
def get_all_groups(
    page: int = Query(1, ge=1),
    page_size: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = group.get_all_groups(db)

    return PaginatedResponse.from_query(query=query, page=page, page_size=page_size)


@router.put(
    "/edit/{group_id}", status_code=status.HTTP_200_OK, response_model=GroupView
)
async def edit_group(
    group_id: int,
    request_model: GroupUpdate = Depends(GroupUpdate.as_form),
    group_img: UploadFile | None = File(None),
    group_background_img: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    group_img_path = None

    if group_img is not None:
        group_img_path = await save_image(group_img, ImageType.group_picture)

    group_background_img_path = None

    if group_background_img is not None:
        group_background_img_path = await save_image(
            group_background_img, ImageType.group_background_picture
        )

    updated_group = group.update_group(
        db=db,
        request_model=request_model,
        group_id=group_id,
        user_id=current_user.id,
        group_picture_path=group_img_path,
        group_background_picture_path=group_background_img_path,
    )

    return updated_group


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    group.delete_group(db, group_id, current_user.id)
