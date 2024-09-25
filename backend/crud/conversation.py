from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.conversation import Conversation
from ..models.message import Message


async def save_conversation(
    db: AsyncSession, user_id: UUID, user_message: str, bot_response: str
):
    conversation = Conversation(user_id=user_id)
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    user_msg = Message(
        conversation_id=conversation.id, sender="user", content=user_message
    )
    bot_msg = Message(
        conversation_id=conversation.id, sender="bot", content=bot_response
    )
    db.add_all([user_msg, bot_msg])
    await db.commit()
