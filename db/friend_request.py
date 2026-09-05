from sqlalchemy.orm import Session

from models.friend_request import DBFriendRequest
from schemas.friend_request import FriendRequestBase


def create_friend_request(request:FriendRequestBase,user_id:int,db:Session):
    new_friend_request = DBFriendRequest(
        sender_id = user_id,
        receiver_id = request.receiver_id,
    )

    db.add(new_friend_request)
    db.commit()
    db.refresh(new_friend_request)

    return new_friend_request