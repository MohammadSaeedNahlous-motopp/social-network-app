from sqlalchemy.orm import Session

from models.enums import GroupRole
from models.group_role import DBGroupRole


def seed_group_roles(db: Session) -> None:
    for role in GroupRole:
        existing_role = (
            db.query(DBGroupRole)
            .filter(DBGroupRole.name == role)
            .first()
        )

        if existing_role is None:
            db.add(
                DBGroupRole(
                    name=role,
                )
            )

    db.commit()
