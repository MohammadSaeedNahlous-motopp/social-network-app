import mimetypes
from pathlib import Path

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse

from auth.oauth2 import get_current_user
from db.database import get_db
from db.user import get_user_by_id
from models.user import DBUser

router = APIRouter(prefix="/images", tags=["images"])

@router.get("/me",tags=["users"], status_code=status.HTTP_200_OK)
async def get_my_profile(current_user: DBUser = Depends(get_current_user)):
    if not current_user.profile_img:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User image not found")

    filepath = Path(current_user.profile_img)
    filename = filepath.name
    media_type, _ = mimetypes.guess_type(filepath.name)

    return FileResponse(
        path=filepath,
        filename=filename,
        media_type=media_type or "application/octet-stream",
    )


@router.get("/profile/{user_id}",tags=["users"], status_code=status.HTTP_200_OK)
async def get_profile(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db=db, user_id=user_id)

    if not user.profile_img:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User image not found")

    filepath = Path(user.profile_img)
    filename = filepath.name
    media_type, _ = mimetypes.guess_type(filepath.name)

    return FileResponse(
        path=filepath,
        filename=filename,
        media_type=media_type or "application/octet-stream",
    )
