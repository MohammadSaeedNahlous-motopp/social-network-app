from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from db import post as db_post
from schemas.post import PostCreate, PostUpdate, PostResponse


router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    request: PostCreate,
    db: Session = Depends(get_db)
):
    user_id = 1

    return db_post.create_post(
        db=db,
        request=request,
        user_id=user_id
    )



@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    post = db_post.get_post(db, post_id)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found."
        )

    return post


@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    request: PostUpdate,
    db: Session = Depends(get_db)
):
    post = db_post.update_post(
        db=db,
        post_id=post_id,
        request=request
    )

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found."
        )

    return post


@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    deleted = db_post.delete_post(db, post_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found."
        )

    return {"message": "Post deleted successfully."}