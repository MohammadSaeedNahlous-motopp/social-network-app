import pytest

from db.chat import create_chat, get_private_chat
from models.enums import ChatType
from schemas.chat import ChatCreate
from websocket.message import handle_message


# =========================================================
# Fake WebSocket / Connection Manager
# =========================================================


class FakeWebSocket:
    def __init__(self):
        self.sent_messages = []

    async def send_json(self, message):
        self.sent_messages.append(message)


class FakeConnectionManager:
    def __init__(self):
        self.sent_messages = []

    async def send_to_user(self, user_id, message):
        self.sent_messages.append(
            {
                "user_id": user_id,
                "message": message,
            }
        )


# =========================================================
# Private Chat Tests
# =========================================================


def test_get_private_chat_returns_existing_chat(
    db,
    create_test_user,
):
    user1 = create_test_user(
        email="chat_user1@example.com",
        name="User One",
    )

    user2 = create_test_user(
        email="chat_user2@example.com",
        name="User Two",
    )

    chat = create_chat(
        ChatCreate(
            user_ids=[user1.id, user2.id],
            name="Private Chat",
            description="",
            type=ChatType.private,
        ),
        db,
    )

    result = get_private_chat(
        user1.id,
        user2.id,
        db,
    )

    assert result is not None
    assert result.id == chat.id
    assert result.type == ChatType.private


def test_get_private_chat_returns_none_when_chat_does_not_exist(
    db,
    create_test_user,
):
    user1 = create_test_user(
        email="chat_user3@example.com",
        name="User Three",
    )

    user2 = create_test_user(
        email="chat_user4@example.com",
        name="User Four",
    )

    result = get_private_chat(
        user1.id,
        user2.id,
        db,
    )

    assert result is None


def test_get_private_chat_works_in_reverse_order(
    db,
    create_test_user,
):
    user1 = create_test_user(
        email="chat_user5@example.com",
        name="User Five",
    )

    user2 = create_test_user(
        email="chat_user6@example.com",
        name="User Six",
    )

    chat = create_chat(
        ChatCreate(
            user_ids=[user1.id, user2.id],
            name="Private Chat",
            description="",
            type=ChatType.private,
        ),
        db,
    )

    result = get_private_chat(
        user2.id,
        user1.id,
        db,
    )

    assert result is not None
    assert result.id == chat.id


# =========================================================
# WebSocket Message Validation Tests
# =========================================================


@pytest.mark.asyncio
async def test_send_message_to_non_friend(
    db,
    create_test_user,
):
    user1 = create_test_user(
        email="sender_nonfriend@example.com",
        name="Sender",
    )

    user2 = create_test_user(
        email="nonfriend@example.com",
        name="Non Friend",
    )

    websocket = FakeWebSocket()
    manager = FakeConnectionManager()

    data = {
        "type": "message",
        "recipient_id": user2.id,
        "content": "Hello!",
    }

    await handle_message(
        data,
        user1.id,
        websocket,
        manager,
        db,
    )

    assert websocket.sent_messages == [{"error": "You can only message your friends."}]

    assert manager.sent_messages == []


@pytest.mark.asyncio
async def test_send_message_to_self(
    db,
    create_test_user,
):
    user = create_test_user(
        email="self_message@example.com",
        name="Self User",
    )

    websocket = FakeWebSocket()
    manager = FakeConnectionManager()

    data = {
        "type": "message",
        "recipient_id": user.id,
        "content": "Hello myself!",
    }

    await handle_message(
        data,
        user.id,
        websocket,
        manager,
        db,
    )

    assert websocket.sent_messages == [
        {"error": "You cannot send a message to yourself."}
    ]

    assert manager.sent_messages == []


@pytest.mark.asyncio
async def test_send_message_to_non_existing_user(
    db,
    create_test_user,
):
    user = create_test_user(
        email="invalid_recipient@example.com",
        name="Sender",
    )

    websocket = FakeWebSocket()
    manager = FakeConnectionManager()

    data = {
        "type": "message",
        "recipient_id": 999999,
        "content": "Hello!",
    }

    await handle_message(
        data,
        user.id,
        websocket,
        manager,
        db,
    )

    assert websocket.sent_messages == [{"error": "Recipient not found."}]

    assert manager.sent_messages == []


@pytest.mark.asyncio
async def test_send_empty_message(
    db,
    create_test_user,
):
    user1 = create_test_user(
        email="empty_sender@example.com",
        name="Sender",
    )

    user2 = create_test_user(
        email="empty_recipient@example.com",
        name="Recipient",
    )

    websocket = FakeWebSocket()
    manager = FakeConnectionManager()

    data = {
        "type": "message",
        "recipient_id": user2.id,
        "content": "",
    }

    await handle_message(
        data,
        user1.id,
        websocket,
        manager,
        db,
    )

    assert websocket.sent_messages == [{"error": "Message cannot be empty."}]

    assert manager.sent_messages == []


@pytest.mark.asyncio
async def test_send_whitespace_message(
    db,
    create_test_user,
):
    user1 = create_test_user(
        email="whitespace_sender@example.com",
        name="Sender",
    )

    user2 = create_test_user(
        email="whitespace_recipient@example.com",
        name="Recipient",
    )

    websocket = FakeWebSocket()
    manager = FakeConnectionManager()

    data = {
        "type": "message",
        "recipient_id": user2.id,
        "content": "     ",
    }

    await handle_message(
        data,
        user1.id,
        websocket,
        manager,
        db,
    )

    assert websocket.sent_messages == [{"error": "Message cannot be empty."}]

    assert manager.sent_messages == []


@pytest.mark.asyncio
async def test_send_none_message(
    db,
    create_test_user,
):
    user1 = create_test_user(
        email="none_sender@example.com",
        name="Sender",
    )

    user2 = create_test_user(
        email="none_recipient@example.com",
        name="Recipient",
    )

    websocket = FakeWebSocket()
    manager = FakeConnectionManager()

    data = {
        "type": "message",
        "recipient_id": user2.id,
        "content": None,
    }

    await handle_message(
        data,
        user1.id,
        websocket,
        manager,
        db,
    )

    assert websocket.sent_messages == [{"error": "Message cannot be empty."}]

    assert manager.sent_messages == []


@pytest.mark.asyncio
async def test_send_message_without_recipient(
    db,
    create_test_user,
):
    user = create_test_user(
        email="missing_recipient@example.com",
        name="Sender",
    )

    websocket = FakeWebSocket()
    manager = FakeConnectionManager()

    data = {
        "type": "message",
        "content": "Hello!",
    }

    await handle_message(
        data,
        user.id,
        websocket,
        manager,
        db,
    )

    assert websocket.sent_messages == [{"error": "Recipient is required."}]

    assert manager.sent_messages == []


# =========================================================
# Successful Message Tests
# =========================================================


@pytest.mark.asyncio
async def test_send_message_to_friend(
    db,
    create_test_user,
):
    user1 = create_test_user(
        email="friend_sender@example.com",
        name="Sender",
    )

    user2 = create_test_user(
        email="friend_recipient@example.com",
        name="Recipient",
    )

    from models.friend import DBFriend

    friendship = DBFriend(
        user_id=user1.id,
        friend_id=user2.id,
    )

    db.add(friendship)
    db.commit()

    websocket = FakeWebSocket()
    manager = FakeConnectionManager()

    data = {
        "type": "message",
        "recipient_id": user2.id,
        "content": "Hello!",
    }

    await handle_message(
        data,
        user1.id,
        websocket,
        manager,
        db,
    )

    assert len(manager.sent_messages) == 2

    sent_user_ids = {item["user_id"] for item in manager.sent_messages}

    assert sent_user_ids == {
        user1.id,
        user2.id,
    }

    for item in manager.sent_messages:
        assert item["message"]["sender_id"] == user1.id
        assert item["message"]["content"] == "Hello!"


@pytest.mark.asyncio
async def test_send_message_creates_private_chat(
    db,
    create_test_user,
):
    user1 = create_test_user(
        email="new_chat_sender@example.com",
        name="Sender",
    )

    user2 = create_test_user(
        email="new_chat_recipient@example.com",
        name="Recipient",
    )

    from models.friend import DBFriend

    friendship = DBFriend(
        user_id=user1.id,
        friend_id=user2.id,
    )

    db.add(friendship)
    db.commit()

    assert (
        get_private_chat(
            user1.id,
            user2.id,
            db,
        )
        is None
    )

    websocket = FakeWebSocket()
    manager = FakeConnectionManager()

    data = {
        "type": "message",
        "recipient_id": user2.id,
        "content": "First message",
    }

    await handle_message(
        data,
        user1.id,
        websocket,
        manager,
        db,
    )

    chat = get_private_chat(
        user1.id,
        user2.id,
        db,
    )

    assert chat is not None
    assert chat.type == ChatType.private


@pytest.mark.asyncio
async def test_send_message_reuses_existing_private_chat(
    db,
    create_test_user,
):
    user1 = create_test_user(
        email="reuse_sender@example.com",
        name="Sender",
    )

    user2 = create_test_user(
        email="reuse_recipient@example.com",
        name="Recipient",
    )

    from models.friend import DBFriend

    friendship = DBFriend(
        user_id=user1.id,
        friend_id=user2.id,
    )

    db.add(friendship)
    db.commit()

    websocket = FakeWebSocket()
    manager = FakeConnectionManager()

    data = {
        "type": "message",
        "recipient_id": user2.id,
        "content": "Hello!",
    }

    await handle_message(
        data,
        user1.id,
        websocket,
        manager,
        db,
    )

    first_chat = get_private_chat(
        user1.id,
        user2.id,
        db,
    )

    await handle_message(
        data,
        user1.id,
        websocket,
        manager,
        db,
    )

    second_chat = get_private_chat(
        user1.id,
        user2.id,
        db,
    )

    assert first_chat.id == second_chat.id


@pytest.mark.asyncio
async def test_send_message_strips_whitespace(
    db,
    create_test_user,
):
    user1 = create_test_user(
        email="strip_sender@example.com",
        name="Sender",
    )

    user2 = create_test_user(
        email="strip_recipient@example.com",
        name="Recipient",
    )

    from models.friend import DBFriend

    friendship = DBFriend(
        user_id=user1.id,
        friend_id=user2.id,
    )

    db.add(friendship)
    db.commit()

    websocket = FakeWebSocket()
    manager = FakeConnectionManager()

    data = {
        "type": "message",
        "recipient_id": user2.id,
        "content": "   Hello!   ",
    }

    await handle_message(
        data,
        user1.id,
        websocket,
        manager,
        db,
    )

    assert len(manager.sent_messages) == 2

    for item in manager.sent_messages:
        assert item["message"]["content"] == "Hello!"
