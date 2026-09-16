import pytest

from models.enums import NotificationType
from websocket.message import handle_message


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


# ============================================================
# EXISTING PRIVATE CHAT
# ============================================================


@pytest.mark.asyncio
async def test_send_message_to_existing_private_chat(
    db,
    create_test_user,
):
    user1 = create_test_user(
        email="existing_sender@example.com",
        name="Sender",
    )

    user2 = create_test_user(
        email="existing_recipient@example.com",
        name="Recipient",
    )

    from models.friend import DBFriend

    friendship = DBFriend(
        user_id=user1.id,
        friend_id=user2.id,
    )

    db.add(friendship)
    db.commit()

    from db.chat import create_chat
    from schemas.chat import ChatCreate
    from models.enums import ChatType

    chat = create_chat(
        ChatCreate(
            user_ids=[user1.id, user2.id],
            name="Private Chat",
            description="",
            type=ChatType.private,
        ),
        db,
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

    assert len(manager.sent_messages) == 3

    assert manager.sent_messages[0]["user_id"] == user1.id
    assert manager.sent_messages[0]["message"]["type"] == "message"

    assert manager.sent_messages[1]["user_id"] == user2.id
    assert manager.sent_messages[1]["message"]["type"] == "message"

    assert manager.sent_messages[2]["user_id"] == user2.id
    assert manager.sent_messages[2]["message"]["type"] == "notification"


# ============================================================
# NO PRIVATE CHAT
# ============================================================


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

    assert len(manager.sent_messages) == 3

    assert manager.sent_messages[0]["user_id"] == user1.id
    assert manager.sent_messages[0]["message"]["type"] == "message"

    assert manager.sent_messages[1]["user_id"] == user2.id
    assert manager.sent_messages[1]["message"]["type"] == "message"

    assert manager.sent_messages[2]["user_id"] == user2.id
    assert manager.sent_messages[2]["message"]["type"] == "notification"


# ============================================================
# SEND MESSAGE TO FRIEND
# ============================================================


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

    # Sender receives the message
    sender_message = manager.sent_messages[0]

    assert sender_message["user_id"] == user1.id
    assert sender_message["message"]["type"] == "message"
    assert sender_message["message"]["sender_id"] == user1.id
    assert sender_message["message"]["content"] == "Hello!"

    # Recipient receives the message
    recipient_message = manager.sent_messages[1]

    assert recipient_message["user_id"] == user2.id
    assert recipient_message["message"]["type"] == "message"
    assert recipient_message["message"]["sender_id"] == user1.id
    assert recipient_message["message"]["content"] == "Hello!"

    # Recipient receives the notification
    recipient_notification = manager.sent_messages[2]

    assert recipient_notification["user_id"] == user2.id
    assert recipient_notification["message"]["type"] == "notification"
    assert (
        recipient_notification["message"]["notification_type"]
        == NotificationType.new_message
    )
    assert recipient_notification["message"]["message"] == "Sender Sent You A Message!"

    # Only three messages are sent:
    # sender -> message
    # recipient -> message
    # recipient -> notification
    assert len(manager.sent_messages) == 3


# ============================================================
# NON-FRIEND
# ============================================================


@pytest.mark.asyncio
async def test_send_message_to_non_friend(
    db,
    create_test_user,
):
    user1 = create_test_user(
        email="non_friend_sender@example.com",
        name="Sender",
    )

    user2 = create_test_user(
        email="non_friend_recipient@example.com",
        name="Recipient",
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

    assert len(manager.sent_messages) == 0

    assert websocket.sent_messages == [{"error": "You can only message your friends."}]


# ============================================================
# SELF MESSAGE
# ============================================================


@pytest.mark.asyncio
async def test_send_message_to_self(
    db,
    create_test_user,
):
    user = create_test_user(
        email="self_message@example.com",
        name="User",
    )

    websocket = FakeWebSocket()
    manager = FakeConnectionManager()

    data = {
        "type": "message",
        "recipient_id": user.id,
        "content": "Hello!",
    }

    await handle_message(
        data,
        user.id,
        websocket,
        manager,
        db,
    )

    assert manager.sent_messages == []

    assert websocket.sent_messages == [
        {"error": "You cannot send a message to yourself."}
    ]


# ============================================================
# RECIPIENT NOT FOUND
# ============================================================


@pytest.mark.asyncio
async def test_send_message_to_non_existing_recipient(
    db,
    create_test_user,
):
    user = create_test_user(
        email="missing_recipient_sender@example.com",
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

    assert manager.sent_messages == []

    assert websocket.sent_messages == [{"error": "Recipient not found."}]


# ============================================================
# EMPTY MESSAGE
# ============================================================


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
        "content": "",
    }

    await handle_message(
        data,
        user1.id,
        websocket,
        manager,
        db,
    )

    assert manager.sent_messages == []

    assert websocket.sent_messages == [{"error": "Message cannot be empty."}]


# ============================================================
# WHITESPACE ONLY MESSAGE
# ============================================================


@pytest.mark.asyncio
async def test_send_whitespace_only_message(
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
        "content": "     ",
    }

    await handle_message(
        data,
        user1.id,
        websocket,
        manager,
        db,
    )

    assert manager.sent_messages == []

    assert websocket.sent_messages == [{"error": "Message cannot be empty."}]


# ============================================================
# NONE CONTENT
# ============================================================


@pytest.mark.asyncio
async def test_send_none_content(
    db,
    create_test_user,
):
    user1 = create_test_user(
        email="none_content_sender@example.com",
        name="Sender",
    )

    user2 = create_test_user(
        email="none_content_recipient@example.com",
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
        "content": None,
    }

    await handle_message(
        data,
        user1.id,
        websocket,
        manager,
        db,
    )

    assert manager.sent_messages == []

    assert websocket.sent_messages == [{"error": "Message cannot be empty."}]


# ============================================================
# MISSING RECIPIENT
# ============================================================


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

    assert manager.sent_messages == []

    assert websocket.sent_messages == [{"error": "Recipient is required."}]


# ============================================================
# STRIP MESSAGE WHITESPACE
# ============================================================


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

    # Message to sender
    sender_message = manager.sent_messages[0]

    assert sender_message["user_id"] == user1.id
    assert sender_message["message"]["type"] == "message"
    assert sender_message["message"]["content"] == "Hello!"

    # Message to recipient
    recipient_message = manager.sent_messages[1]

    assert recipient_message["user_id"] == user2.id
    assert recipient_message["message"]["type"] == "message"
    assert recipient_message["message"]["content"] == "Hello!"

    # Notification to recipient
    recipient_notification = manager.sent_messages[2]

    assert recipient_notification["user_id"] == user2.id
    assert recipient_notification["message"]["type"] == "notification"
    assert (
        recipient_notification["message"]["notification_type"]
        == NotificationType.new_message
    )
    assert recipient_notification["message"]["message"] == "Sender Sent You A Message!"

    assert len(manager.sent_messages) == 3
