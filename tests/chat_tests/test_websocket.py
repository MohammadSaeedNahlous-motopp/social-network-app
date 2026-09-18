import pytest


# =========================================================
# Helper
# =========================================================


def create_websocket_token(
    client,
    user,
):
    response = client.post(
        "/auth/login",
        data={
            "username": user.email,
            "password": "password123",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


# =========================================================
# WebSocket Authentication Tests
# =========================================================


def test_websocket_connects_with_valid_token(
    client,
    create_test_user,
):
    user = create_test_user(
        email="websocket_user@example.com",
        name="WebSocket User",
    )

    token = create_websocket_token(
        client,
        user,
    )

    with client.websocket_connect(f"/ws?token={token}") as websocket:
        assert websocket is not None


def test_websocket_rejects_missing_token(
    client,
):
    with pytest.raises(Exception):
        with client.websocket_connect("/ws"):
            pass


def test_websocket_rejects_invalid_token(
    client,
):
    invalid_token = "this-is-not-a-valid-session-token"

    with pytest.raises(Exception):
        with client.websocket_connect(f"/ws?token={invalid_token}"):
            pass


def test_websocket_rejects_non_existing_session(
    client,
):
    invalid_token = "non_existing_access_token"

    with pytest.raises(Exception):
        with client.websocket_connect(f"/ws?token={invalid_token}"):
            pass


def test_websocket_rejects_inactive_user(
    client,
    create_test_user,
    db,
):
    user = create_test_user(
        email="inactive@example.com",
        name="Inactive User",
    )

    user.is_active = False
    db.commit()

    token = create_websocket_token(
        client,
        user,
    )

    with pytest.raises(Exception):
        with client.websocket_connect(f"/ws?token={token}"):
            pass


# =========================================================
# WebSocket Messaging Tests
# =========================================================


def test_websocket_message_between_friends(
    client,
    create_test_user,
    db,
):
    sender = create_test_user(
        email="ws_sender@example.com",
        name="Sender",
    )

    recipient = create_test_user(
        email="ws_recipient@example.com",
        name="Recipient",
    )

    from models.friend import DBFriend

    friendship = DBFriend(
        user_id=sender.id,
        friend_id=recipient.id,
    )

    db.add(friendship)
    db.commit()

    sender_token = create_websocket_token(
        client,
        sender,
    )

    recipient_token = create_websocket_token(
        client,
        recipient,
    )

    with client.websocket_connect(f"/ws?token={sender_token}") as sender_ws:
        with client.websocket_connect(f"/ws?token={recipient_token}") as recipient_ws:
            sender_ws.send_json(
                {
                    "type": "message",
                    "recipient_id": recipient.id,
                    "content": "Hello!",
                }
            )

            # Sender receives the message.
            sender_message = sender_ws.receive_json()

            # Recipient receives the message.
            recipient_message = recipient_ws.receive_json()

            # Recipient also receives a notification.
            recipient_notification = recipient_ws.receive_json()

            assert sender_message["type"] == "message"
            assert sender_message["content"] == "Hello!"
            assert sender_message["sender_id"] == sender.id

            assert recipient_message["type"] == "message"
            assert recipient_message["content"] == "Hello!"
            assert recipient_message["sender_id"] == sender.id

            assert recipient_notification["type"] == "notification"
            assert recipient_notification["message"] == "Sender Sent You A Message!"


def test_websocket_message_to_non_friend(
    client,
    create_test_user,
):
    sender = create_test_user(
        email="ws_nonfriend_sender@example.com",
        name="Sender",
    )

    recipient = create_test_user(
        email="ws_nonfriend_recipient@example.com",
        name="Recipient",
    )

    sender_token = create_websocket_token(
        client,
        sender,
    )

    with client.websocket_connect(f"/ws?token={sender_token}") as websocket:
        websocket.send_json(
            {
                "type": "message",
                "recipient_id": recipient.id,
                "content": "Hello!",
            }
        )

        response = websocket.receive_json()

        assert response == {"error": "You can only message your friends."}


def test_websocket_message_to_self(
    client,
    create_test_user,
):
    user = create_test_user(
        email="ws_self@example.com",
        name="User",
    )

    token = create_websocket_token(
        client,
        user,
    )

    with client.websocket_connect(f"/ws?token={token}") as websocket:
        websocket.send_json(
            {
                "type": "message",
                "recipient_id": user.id,
                "content": "Hello myself!",
            }
        )

        response = websocket.receive_json()

        assert response == {"error": "You cannot send a message to yourself."}


def test_websocket_message_to_non_existing_user(
    client,
    create_test_user,
):
    user = create_test_user(
        email="ws_invalid_recipient@example.com",
        name="Sender",
    )

    token = create_websocket_token(
        client,
        user,
    )

    with client.websocket_connect(f"/ws?token={token}") as websocket:
        websocket.send_json(
            {
                "type": "message",
                "recipient_id": 999999,
                "content": "Hello!",
            }
        )

        response = websocket.receive_json()

        assert response == {"error": "Recipient not found."}


def test_websocket_empty_message(
    client,
    create_test_user,
):
    sender = create_test_user(
        email="ws_empty_sender@example.com",
        name="Sender",
    )

    recipient = create_test_user(
        email="ws_empty_recipient@example.com",
        name="Recipient",
    )

    token = create_websocket_token(
        client,
        sender,
    )

    with client.websocket_connect(f"/ws?token={token}") as websocket:
        websocket.send_json(
            {
                "type": "message",
                "recipient_id": recipient.id,
                "content": "",
            }
        )

        response = websocket.receive_json()

        assert response == {"error": "Message cannot be empty."}
