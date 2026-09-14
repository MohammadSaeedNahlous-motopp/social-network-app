from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from db.user import get_user_by_id
from models.friend import DBFriend


def get_friends(user_id: int, db: Session):
    friends_list = db.query(DBFriend).filter(DBFriend.user_id == user_id)
    return friends_list


def delete_friend(
    user_id: int,
    friendship_id: int,
    db: Session,
):
    searched_friendship = (
        db.query(DBFriend)
        .filter(
            DBFriend.user_id == user_id,
            DBFriend.id == friendship_id,
        )
        .first()
    )

    if not searched_friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friendship not found!",
        )

    reverse_friendship = (
        db.query(DBFriend)
        .filter(
            DBFriend.user_id == searched_friendship.friend_id,
            DBFriend.friend_id == user_id,
        )
        .first()
    )

    db.delete(searched_friendship)

    if reverse_friendship:
        db.delete(reverse_friendship)

    db.commit()

    return {"message": "Friendship was deleted!"}


def is_friend_with(user_id: int, current_user_id: int, db: Session):
    searched_user = get_user_by_id(db, user_id)

    if not searched_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found!",
        )

    are_friends = (
        db.query(DBFriend)
        .filter(
            DBFriend.user_id == current_user_id,
            DBFriend.friend_id == user_id,
        )
        .first()
    )

    if are_friends is None:
        are_friends = (
            db.query(DBFriend)
            .filter(
                DBFriend.user_id == user_id,
                DBFriend.friend_id == current_user_id,
            )
            .first()
        )

    return are_friends is not None
