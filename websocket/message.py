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
from websocket.connection_manager import ConnectionManager


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
            content=content.strip(),
        ),
        user_id,
        db,
    )

    message_data = {
        "type": "message",
        "id": message.id,
        "chat_id": message.chat_id,
        "sender_id": message.sender_id,
        "content": message.content,
    }

    members = get_chat_members_by_chat_id(
        chat.id,
        db,
    )

    for member in members:
        # Send the chat message to everyone
        await manager.send_to_user(
            member.user_id,
            message_data,
        )

        # Don't create a notification for the sender
        if member.user_id == user_id:
            continue

        # Create notification for the recipient
        notification = create_notification(
            NotificationCreate(
                user_id=member.user_id,
                type=NotificationType.new_message,
                message=f"{sender.name} Sent You A Message!",
            ),
            db,
        )

        # Send notification to the recipient
        await manager.send_to_user(
            member.user_id,
            {
                "type": "notification",
                "id": notification.id,
                "notification_type": notification.type,
                "message": notification.message,
            },
        )
