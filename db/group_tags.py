from fastapi import HTTPException, status

from sqlalchemy.orm import Query
from sqlalchemy.orm.session import Session

from models.group_tags import DBGroupTag
from models.tag import DBTag
from service.permissions import can_edit_group


def get_all_tags(db: Session, group_id: int | None = None) -> Query[DBGroupTag]:
    if group_id is None:
        return db.query(DBTag)

    return db.query(DBGroupTag).filter(DBGroupTag.group_id == group_id)


def add_tags(tags: list[int], group_id: int, current_user_id: int, db: Session) -> None:
    if not can_edit_group(user_id=current_user_id, group_id=group_id, db=db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User can't edit this group")

    # check if all keys are valid
    tags: set[int] = set(tags)
    if len(tags) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag list is empty")

    if db.query(DBTag.id).filter(DBTag.id.in_(tags)).count() != len(tags):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid tag IDs")

    # check if some tags where already added
    existing_tags = {
        tag_id
        for (tag_id,) in db.query(DBGroupTag.tag_id)
        .filter(DBGroupTag.group_id == group_id)
        .all()
    }

    tags_to_add = tags - existing_tags

    if len(tags_to_add) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="These tags are already associated with a group")

    tag_list:list[DBGroupTag] = []
    for tag_id in tags_to_add:
        tag_list.append(DBGroupTag(group_id=group_id, tag_id=tag_id))

    db.add_all(tag_list)
    db.commit()


def remove_tags(tags: list[int], group_id: int, current_user_id: int, db: Session):
    if not can_edit_group(user_id=current_user_id, group_id=group_id, db=db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User can't edit this group")

    # check if all keys are valid
    tags: set[int] = set(tags)
    if len(tags) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag list is empty")

    if db.query(DBTag.id).filter(DBTag.id.in_(tags)).count() != len(tags):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid tag IDs")

    #get only tags that are associated with a group
    existing_tags = {
        tag_id
        for (tag_id,) in db.query(DBGroupTag.tag_id)
        .filter(DBGroupTag.group_id == group_id)
        .all()
    }

    tags_to_remove = tags & existing_tags # tags that we requested to remove and that are associated with a group

    if len(tags_to_remove) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="These tags are already not associated with a group")

    db.query(DBGroupTag).filter(DBGroupTag.group_id == group_id and DBGroupTag.tag_id.in_(tags_to_remove)).delete()