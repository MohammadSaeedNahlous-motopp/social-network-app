class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        self.active_connections.pop(user_id, None)

    async def send_to_user(self, user_id: int, message: dict):
        websocket = self.active_connections.get(user_id)

        print("Sending to:", user_id)
        print("Connected users:", self.active_connections.keys())

        if websocket:
            await websocket.send_json(message)
            print("Message sent!")
        else:
            print("User is not connected!")
