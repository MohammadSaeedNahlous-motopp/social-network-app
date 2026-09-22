from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user
from db.database import get_db
from db.group_tags import get_all_tags, add_tags, remove_tags
from schemas.tag import TagView
from service.pagination import PaginatedResponse

router = APIRouter(prefix="/tags", tags=["tags"])

@router.get("/",
            status_code=status.HTTP_200_OK,
            response_model=PaginatedResponse[TagView])
def get_tags(
        page: int = Query(1, ge=1),
        page_size: int = Query(0, ge=0),
        db: Session = Depends(get_db)):

    query = get_all_tags(db=db)

    return PaginatedResponse.from_query(
        query=query,
        page=page,
        page_size=page_size
    )

@router.get("/{group_id}", tags=["groups"],
            status_code=status.HTTP_200_OK,
            response_model=PaginatedResponse[TagView])
def get_group_tags(
        group_id: int,
        page: int = Query(1, ge=1),
        page_size: int = Query(0, ge=0),
        db: Session = Depends(get_db)
):
    query = get_all_tags(db=db, group_id=group_id)

    return PaginatedResponse.from_query(
        query=query,
        page=page,
        page_size=page_size
    )


@router.put("/{group_id}/add", tags=["groups"], status_code=status.HTTP_200_OK)
def add_group_tags(group_id: int, tags: list[int],
                   db: Session = Depends(get_db), current_user = Depends(get_current_user)):

    add_tags(tags=tags, group_id=group_id, current_user_id=current_user.id, db=db)

    return {"message": "Tags successfully added"}


@router.put("/{group_id}/remove", tags=["groups"], status_code=status.HTTP_200_OK)
def remove_group_tags(group_id: int, tags: list[int],
                   db: Session = Depends(get_db), current_user=Depends(get_current_user)):

    remove_tags(tags=tags, group_id=group_id, current_user_id=current_user.id, db=db)

    return {"message": "Tags successfully removed"}
