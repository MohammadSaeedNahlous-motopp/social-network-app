from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from websocket.auth import authenticate_websocket
from websocket.connection_manager import ConnectionManager
from websocket.message import handle_message


router = APIRouter()

manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    db: Session = Depends(get_db),
):
    user = await authenticate_websocket(websocket, db)

    if user is None:
        return

    await manager.connect(user.id, websocket)

    try:
        while True:
            data = await websocket.receive_json()

            if data["type"] == "message":
                await handle_message(data, user.id, websocket, manager, db)

            # elif data["type"] == "typing":
            #     pass
            #
            # elif data["type"] == "read":
            #     pass

    except WebSocketDisconnect:
        manager.disconnect(user.id)
