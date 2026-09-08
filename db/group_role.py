from fastapi import HTTPException, status
from sqlalchemy.orm.session import Session

from models.enums import GroupRole
from models.group_role import DBGroupRole


def get_role_obj(role: GroupRole, db: Session) -> DBGroupRole:
    member_role = (
        db.query(DBGroupRole)
        .filter(DBGroupRole.name == role)
        .first()
    )

    if not member_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group member role not found.")

    return member_role
