from db.chat import create_chat, get_private_chat
from db.chat_member import get_chat_members_by_chat_id
from db.friend import is_friend_with
from db.message import create_message
from db.notification import create_notification
from db.user import get_user_by_id
from models.enums import ChatType, NotificationType
from schemas.chat import ChatCreate
from schemas.message import MessageCreate
from schemas.notification import NotificationCreate
from service.encryption_methods import (
    generate_aes_key,
    encrypt_message,
    encrypt_aes_key,
    decrypt_chat_message,
)
from websocket.connection_manager import ConnectionManager
import base64


async def handle_message(
    data,
    user_id,
    websocket,
    manager: ConnectionManager,
    db,
):
    content = data.get("content")
    recipient_id = data.get("recipient_id")

    if recipient_id is None:
        await websocket.send_json({"error": "Recipient is required."})
        return

    if recipient_id == user_id:
        await websocket.send_json({"error": "You cannot send a message to yourself."})
        return

    recipient = get_user_by_id(db, recipient_id)

    if recipient is None:
        await websocket.send_json({"error": "Recipient not found."})
        return

    if content is None or not content.strip():
        await websocket.send_json({"error": "Message cannot be empty."})
        return

    if not is_friend_with(recipient_id, user_id, db):
        await websocket.send_json({"error": "You can only message your friends."})
        return

    # Get the authenticated sender
    sender = get_user_by_id(db, user_id)
    aes_message_key = generate_aes_key()
    ciphertext, nonce = encrypt_message(
        content.strip(),
        aes_message_key,
    )

    encrypted_aes_message_key = encrypt_aes_key(
        aes_message_key,
        recipient.public_key,
    )

    ciphertext = base64.b64encode(ciphertext).decode("utf-8")
    nonce = base64.b64encode(nonce).decode("utf-8")
    encrypted_aes_message_key = base64.b64encode(encrypted_aes_message_key).decode(
        "utf-8"
    )

    chat = get_private_chat(
        user_id,
        recipient_id,
        db,
    )

    if chat is None:
        chat = create_chat(
            ChatCreate(
                user_ids=[user_id, recipient_id],
                name="Private Chat",
                description="",
                type=ChatType.private,
            ),
            db,
        )

    message = create_message(
        MessageCreate(
            chat_id=chat.id,
            ciphertext=ciphertext,
            nonce=nonce,
            encrypted_aes_key=encrypted_aes_message_key,
        ),
        user_id,
        db,
    )
    message_data_for_sender = {
        "type": "message",
        "id": message.id,
        "chat_id": message.chat_id,
        "sender_id": message.sender_id,
        "content": content.strip(),
    }

    members = get_chat_members_by_chat_id(
        chat.id,
        db,
    )

    for member in members:
        if member.user_id == user_id:
            await manager.send_to_user(
                member.user_id,
                message_data_for_sender,
            )
            continue

        member_user = get_user_by_id(
            db,
            member.user_id,
        )

        decrypted_chat_message = decrypt_chat_message(
            message,
            member_user,
        )

        message_data = {
            "type": "message",
            "id": message.id,
            "chat_id": message.chat_id,
            "sender_id": message.sender_id,
            "content": decrypted_chat_message,
        }

        await manager.send_to_user(
            member.user_id,
            message_data,
        )

        notification = create_notification(
            NotificationCreate(
                user_id=member.user_id,
                type=NotificationType.new_message,
                message=f"{sender.name} Sent You A Message!",
            ),
            db,
        )

        await manager.send_to_user(
            member.user_id,
            {
                "type": "notification",
                "id": notification.id,
                "notification_type": notification.type,
                "message": notification.message,
            },
        )
