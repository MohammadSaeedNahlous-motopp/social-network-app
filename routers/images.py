import mimetypes
from pathlib import Path

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse

from auth.oauth2 import get_current_user
from db.database import get_db
from db.group import get_group_by_id
from db.user import get_user_by_id
from models.user import DBUser

router = APIRouter(prefix="/images", tags=["images"])

def generate_file_response(filepath: Path) -> FileResponse:
    filename = filepath.name
    media_type, _ = mimetypes.guess_type(filepath.name)

    return FileResponse(
        path=filepath,
        filename=filename,
        media_type=media_type or "application/octet-stream",
    )

@router.get("/me",tags=["users"], status_code=status.HTTP_200_OK)
def get_my_profile(current_user: DBUser = Depends(get_current_user)):
    if not current_user.profile_img:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User image not found")

    return generate_file_response(Path(current_user.profile_img))


@router.get("/profile/{user_id}",tags=["users"], status_code=status.HTTP_200_OK)
def get_profile(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db=db, user_id=user_id)

    if not user.profile_img:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User image not found")

    return generate_file_response(Path(user.profile_img))


@router.get("/group/{group_id}/icon",tags=["groups"], status_code=status.HTTP_200_OK)
def get_group_icon(group_id: int, db: Session = Depends(get_db)):
    group = get_group_by_id(db=db, group_id=group_id)

    if not group.icon_img:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group icon image not found")

    return generate_file_response(Path(group.profile_img))


@router.get("/group/{group_id}/background", tags=["groups"], status_code=status.HTTP_200_OK)
def get_group_background(group_id: int, db: Session = Depends(get_db)):
    group = get_group_by_id(db=db, group_id=group_id)

    if not group.background_img:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group background image not found")

    return generate_file_response(Path(group.background_img))


@router.get("/post/{post_id}/image", tags=["posts", "group posts"], status_code=status.HTTP_200_OK)
def get_post_image(post_id: int, current_user: DBUser = Depends(get_current_user),  db: Session = Depends(get_db)):

    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Retrieving post images are not implemented yet")
