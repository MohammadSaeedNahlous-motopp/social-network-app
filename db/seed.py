from sqlalchemy.orm import Session

from models.enums import GroupRole
from models.group_role import DBGroupRole
from models.tag import DBTag

TAGS = [
    {
        "name": "Python",
        "description": "Python programming language",
    },
    {
        "name": "JavaScript",
        "description": "JavaScript programming language",
    },
    {
        "name": "Backend",
        "description": "Backend development",
    },
    {
        "name": "Frontend",
        "description": "Frontend development",
    },
    {
        "name": "Database",
        "description": "Database-related topics",
    },
]


def seed_group_roles(db: Session) -> None:
    for role in GroupRole:
        existing_role = db.query(DBGroupRole).filter(DBGroupRole.name == role).first()

        if existing_role is None:
            db.add(
                DBGroupRole(
                    name=role,
                )
            )

    db.commit()


def seed_tags(db: Session) -> None:
    for tag_data in TAGS:
        existing_tag = db.query(DBTag).filter(DBTag.name == tag_data["name"]).first()

        if existing_tag is None:
            db.add(DBTag(**tag_data))

    db.commit()
