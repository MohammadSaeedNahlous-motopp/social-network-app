from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from websocket.connection_manager import ConnectionManager


router = APIRouter()

manager = ConnectionManager()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()

            print(data)

    except WebSocketDisconnect:
        manager.disconnect(user_id)
