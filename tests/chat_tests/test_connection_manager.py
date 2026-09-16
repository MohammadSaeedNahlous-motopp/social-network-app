import pytest

from websocket.connection_manager import ConnectionManager


class FakeWebSocket:
    def __init__(self):
        self.accepted = False
        self.sent_messages = []

    async def accept(self):
        self.accepted = True

    async def send_json(self, message):
        self.sent_messages.append(message)


# ============================================================
# CONNECTION TESTS
# ============================================================


@pytest.mark.asyncio
async def test_connect_user():
    manager = ConnectionManager()
    websocket = FakeWebSocket()

    await manager.connect(1, websocket)

    assert websocket.accepted is True
    assert manager.active_connections[1] is websocket


@pytest.mark.asyncio
async def test_disconnect_user():
    manager = ConnectionManager()
    websocket = FakeWebSocket()

    await manager.connect(1, websocket)

    manager.disconnect(1)

    assert 1 not in manager.active_connections


@pytest.mark.asyncio
async def test_disconnect_non_existing_user():
    manager = ConnectionManager()

    manager.disconnect(999)

    assert manager.active_connections == {}


@pytest.mark.asyncio
async def test_multiple_users_can_connect():
    manager = ConnectionManager()

    websocket1 = FakeWebSocket()
    websocket2 = FakeWebSocket()

    await manager.connect(1, websocket1)
    await manager.connect(2, websocket2)

    assert len(manager.active_connections) == 2
    assert manager.active_connections[1] is websocket1
    assert manager.active_connections[2] is websocket2


@pytest.mark.asyncio
async def test_reconnecting_user_replaces_old_connection():
    manager = ConnectionManager()

    old_websocket = FakeWebSocket()
    new_websocket = FakeWebSocket()

    await manager.connect(1, old_websocket)
    await manager.connect(1, new_websocket)

    assert len(manager.active_connections) == 1
    assert manager.active_connections[1] is new_websocket


# ============================================================
# MESSAGE DELIVERY TESTS
# ============================================================


@pytest.mark.asyncio
async def test_send_message_to_connected_user():
    manager = ConnectionManager()
    websocket = FakeWebSocket()

    await manager.connect(1, websocket)

    message = {
        "id": 1,
        "chat_id": 10,
        "sender_id": 2,
        "content": "Hello!",
    }

    await manager.send_to_user(1, message)

    assert websocket.sent_messages == [message]


@pytest.mark.asyncio
async def test_send_message_to_disconnected_user():
    manager = ConnectionManager()

    message = {
        "id": 1,
        "chat_id": 10,
        "sender_id": 2,
        "content": "Hello!",
    }

    await manager.send_to_user(1, message)

    # Nothing should happen because the user is not connected.
    assert manager.active_connections == {}


@pytest.mark.asyncio
async def test_messages_are_sent_to_correct_users():
    manager = ConnectionManager()

    websocket1 = FakeWebSocket()
    websocket2 = FakeWebSocket()

    await manager.connect(1, websocket1)
    await manager.connect(2, websocket2)

    message_for_user1 = {"content": "Message for user 1"}

    message_for_user2 = {"content": "Message for user 2"}

    await manager.send_to_user(
        1,
        message_for_user1,
    )

    await manager.send_to_user(
        2,
        message_for_user2,
    )

    assert websocket1.sent_messages == [message_for_user1]

    assert websocket2.sent_messages == [message_for_user2]
