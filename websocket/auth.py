from fastapi import HTTPException

from db.session import get_session_by_token
from db.user import get_user_by_id


async def authenticate_websocket(websocket, db):
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        return None

    try:
        searched_session = get_session_by_token(
            token,
            db,
        )
    except HTTPException:
        await websocket.close(code=1008)
        return None

    user = get_user_by_id(
        db,
        searched_session.user_id,
    )

    if user is None or not user.is_active:
        await websocket.close(code=1008)
        return None

    return user
