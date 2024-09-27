from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .. import logger
from ..core.database import get_session
from ..crud.conversation import save_conversation
from ..models.user import User
from ..routers.auth import get_current_active_user
from ..schemas.chatbot import ChatRequest, ChatResponse
from ..services.chatbot_service import ChatbotService
from .auth import oauth2_scheme

chatbot_service = ChatbotService()

router = APIRouter(
    prefix="/api/v1/chatbot",
    tags=["Chatbot"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    chat_request: ChatRequest,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    try:
        result = await chatbot_service.process_request(
            user_input=chat_request.prompt.strip(),
            workflow_type=chat_request.agent_type,
            history=chat_request.history,
        )

        response_text = str(result).strip()

        # Save the conversation
        await save_conversation(db, current_user.id, chat_request.prompt, response_text)

        return ChatResponse(response=response_text, metadata=chat_request.metadata)

    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request.",
        )
