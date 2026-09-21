from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from db.post import get_post
from models.enums import PostReactionType
from models.post_reactions import DBPostReaction
from schemas.post_reaction import PostReactionCreate
from service.permissions import can_see_post


def get_reaction_score(reaction_type: PostReactionType) -> int:
    if reaction_type == PostReactionType.like:
        return 1

    return -1


def handle_post_reaction(
    post_id: int,
    user_id: int,
    req: PostReactionCreate,
    db: Session,
):
    post = get_post(db, post_id)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    if not can_see_post(
        requesting_user_id=user_id,
        post=post,
        db=db,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reacting to this post is forbidden",
        )

    existing_reaction = get_user_post_reaction(
        post_id=post_id,
        user_id=user_id,
        db=db,
    )

    if existing_reaction:
        # Remove reaction
        if existing_reaction.reaction_type == req.reaction_type:
            post.score -= get_reaction_score(existing_reaction.reaction_type)

            db.delete(existing_reaction)
            db.commit()

            return True

        # Change reaction
        post.score -= get_reaction_score(existing_reaction.reaction_type)

        post.score += get_reaction_score(req.reaction_type)

        existing_reaction.reaction_type = req.reaction_type

        db.commit()
        db.refresh(existing_reaction)

        return existing_reaction

    # Create new reaction
    new_reaction = DBPostReaction(
        post_id=post_id,
        user_id=user_id,
        reaction_type=req.reaction_type,
    )

    db.add(new_reaction)

    post.score += get_reaction_score(req.reaction_type)

    db.commit()
    db.refresh(new_reaction)

    return new_reaction


def get_post_reactions(
    post_id: int,
    requesting_user_id: int,
    db: Session,
):
    post = get_post(db, post_id)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    if not can_see_post(
        requesting_user_id=requesting_user_id,
        post=post,
        db=db,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Retrieving post reactions is forbidden",
        )

    reactions_query = db.query(DBPostReaction).filter(
        DBPostReaction.post_id == post_id,
    )

    return reactions_query


def get_user_post_reaction(
    post_id: int,
    user_id: int,
    db: Session,
):
    return (
        db.query(DBPostReaction)
        .filter(
            DBPostReaction.post_id == post_id,
            DBPostReaction.user_id == user_id,
        )
        .first()
    )
