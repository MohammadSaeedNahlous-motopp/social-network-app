from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user
from db.database import get_db
from models.user import DBUser
from schemas.friend_request import FriendRequestBase
from db import friend_request

router=APIRouter(prefix="/friend-requests",tags=["Friend Requests"])

@router.post("/create")
def create_friend_request(request:FriendRequestBase,db:Session = Depends(get_db),current_user: DBUser = Depends(get_current_user)):
    return friend_request.create_friend_request(request,current_user.id,db)