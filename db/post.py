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



def get_post(db: Session, post_id: int) -> DBPost | None:
    return db.query(DBPost).filter(DBPost.id == post_id).first()


def update_post(db: Session, post_id: int, request: PostUpdate):
    post = get_post(db, post_id)

    if post is None:
        return None

    if request.title is not None:
        post.title = request.title

    if request.content is not None:
        post.content = request.content

    if request.image_url is not None:
        post.image_url = request.image_url

    db.commit()
    db.refresh(post)

    return post



def delete_post(db: Session, post_id: int):
    post = get_post(db, post_id)

    if post is None:
        return False

    db.delete(post)
    db.commit()

    return True