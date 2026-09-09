from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user
from db.database import get_db
from db import post_group as db_group_post
from models.user import DBUser
from schemas.post import PostCreate, PostResponse, PostUpdate
from service.post_image import save_post_image

router = APIRouter(
    prefix="/groups",
    tags=["group posts"],
)


@router.post(
    "/{group_id}/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_group_post(
    group_id: int,
    title: str = Form(...),
    content: str = Form(...),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    image_url = None

    if image is not None:
        image_url = await save_post_image(image)

    request = PostCreate(
        title=title,
        content=content,
    )

    return db_group_post.create_group_post(
        db=db,
        group_id=group_id,
        request=request,
        user_id=current_user.id,
        image_url=image_url,
    )


@router.put(
    "/{group_id}/posts/{post_id}",
    response_model=PostResponse,
)
def update_group_post(
    group_id: int,
    post_id: int,
    request: PostUpdate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    return db_group_post.update_group_post(
        db=db,
        group_id=group_id,
        post_id=post_id,
        request=request,
        user_id=current_user.id,
    )



@router.delete(
    "/{group_id}/posts/{post_id}",
)
def delete_group_post(
    group_id: int,
    post_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    db_group_post.delete_group_post(
        db=db,
        group_id=group_id,
        post_id=post_id,
        user_id=current_user.id,
    )

    return {
        "message": "Group post deleted successfully."
    }



