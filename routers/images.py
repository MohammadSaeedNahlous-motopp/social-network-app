import mimetypes
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse

from auth.oauth2 import get_current_user
from db.database import get_db
from models.user import DBUser

router = APIRouter(prefix="/images", tags=["images"])

@router.get("/me",tags=["users"], status_code=status.HTTP_200_OK)
async def get_my_profile(current_user: DBUser = Depends(get_current_user)):
    filepath = Path(current_user.profile_img)
    filename = filepath.name
    media_type, _ = mimetypes.guess_type(filepath.name)

    return FileResponse(
        path=filepath,
        filename=filename,
        media_type=media_type or "application/octet-stream",
    )


