from fastapi import HTTPException, status
from sqlalchemy.orm.session import Session
from models.post import DBPost
from schemas.post import PostCreate, PostUpdate

def create_post(db: Session, request: PostCreate, user_id: int):
    new_post = DBPost(
        user_id=user_id,
        title=request.title,
        content=request.content,
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


