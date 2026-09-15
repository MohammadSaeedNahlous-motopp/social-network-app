from jose import jwt, JWTError

from auth.oauth2 import SECRET_KEY, ALGORITHM
from models.user import DBUser


async def authenticate_websocket(websocket, db):
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        return None

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = int(payload["sub"])

    except (JWTError, KeyError, ValueError):
        await websocket.close(code=1008)
        return None

    user = db.query(DBUser).filter(DBUser.id == user_id).first()

    if user is None or not user.is_active:
        await websocket.close(code=1008)
        return None

    return user
