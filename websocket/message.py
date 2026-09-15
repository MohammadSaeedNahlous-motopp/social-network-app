from db.chat import create_chat, get_private_chat
from db.chat_member import get_chat_members_by_chat_id
from db.friend import is_friend_with
from db.message import create_message
from db.user import get_user_by_id
from models.enums import ChatType
from schemas.chat import ChatCreate
from schemas.message import MessageCreate
from websocket.connection_manager import ConnectionManager


async def handle_message(data, user_id, websocket, manager: ConnectionManager, db):
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

    chat = get_private_chat(user_id, recipient_id, db)

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

    chat_id = chat.id

    message = create_message(
        MessageCreate(
            chat_id=chat.id,
            content=content.strip(),
        ),
        user_id,
        db,
    )

    message_data = {
        "id": message.id,
        "chat_id": message.chat_id,
        "sender_id": message.sender_id,
        "content": message.content,
    }

    members = get_chat_members_by_chat_id(chat_id, db)

    for member in members:
        await manager.send_to_user(member.user_id, message_data)
