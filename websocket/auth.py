from db.session import get_session_by_token
from db.user import get_user_by_id


async def authenticate_websocket(websocket, db):
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        return None

    searched_session = get_session_by_token(token, db)
    searched_user = get_user_by_id(db, searched_session.user_id)

    if searched_user is None or not searched_user.is_active:
        await websocket.close(code=1008)
        return None

    return searched_user
